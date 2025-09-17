#!/usr/bin/env python3
"""
SQLite数据库管理器 - 高性能数据存储和清理
负责处理所有数据库相关操作，包括数据存储、查询和清理
"""

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import pytz

# 时区设置
UTC8 = pytz.timezone('Asia/Shanghai')

def get_utc8_time():
    """获取UTC+8当前时间"""
    return datetime.now(UTC8)

def convert_to_utc8(dt):
    """将时间转换为UTC+8"""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(UTC8)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite数据库管理器"""

    def __init__(self, db_path: str = "binance_monitor.db", max_connections: int = 5, use_wal: bool = True):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            use_wal: 是否使用WAL模式（默认True，设为False以便DB Browser查看）
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.use_wal = use_wal
        self._ensure_db_directory()
        self.init_database()

    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"创建数据库目录: {db_dir}")

    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30秒超时
                isolation_level=None,  # 自动提交模式
                check_same_thread=False  # 允许多线程访问
            )
            conn.row_factory = sqlite3.Row  # 允许以字典方式访问行
            if self.use_wal:
                conn.execute("PRAGMA journal_mode=WAL")  # 启用WAL模式提高并发性能
            else:
                conn.execute("PRAGMA journal_mode=DELETE")  # 使用传统日志模式，便于DB Browser查看
            conn.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全性
            conn.execute("PRAGMA cache_size=-10000")  # 10MB缓存
            conn.execute("PRAGMA temp_store=memory")  # 临时表存储在内存中
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """初始化数据库表结构和索引"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 创建监控数据表 - 存储持仓量和价格历史
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS oi_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        open_interest REAL NOT NULL,
                        price REAL NOT NULL,
                        value_usdt REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建警报记录表 - 存储触发的警报
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        oi_change_percent REAL NOT NULL,
                        price_change_percent REAL NOT NULL,
                        current_oi REAL NOT NULL,
                        old_oi REAL NOT NULL,
                        current_price REAL NOT NULL,
                        old_price REAL NOT NULL,
                        total_value_usdt REAL,
                        alert_time DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建系统状态表 - 存储系统运行状态
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        monitor_start_time DATETIME NOT NULL,
                        last_monitor_time DATETIME,
                        total_symbols_monitored INTEGER DEFAULT 0,
                        total_alerts_sent INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'running',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建错误日志表 - 存储运行时错误
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_type TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        symbol TEXT,
                        context TEXT,
                        error_time DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建性能指标表 - 存储监控性能数据
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        symbol TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建索引以提高查询性能
                self._create_indexes(cursor)

                logger.info("数据库表结构初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def _create_indexes(self, cursor):
        """创建数据库索引"""
        # 主表索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oi_symbol_timestamp ON oi_history(symbol, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oi_timestamp ON oi_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(alert_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_time ON error_logs(error_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_time ON performance_metrics(timestamp)')

        # 复合索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oi_symbol_created ON oi_history(symbol, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol_time ON alerts(symbol, alert_time)')

        logger.info("数据库索引创建完成")

    def save_oi_data(self, symbol: str, timestamp: datetime, open_interest: float,
                    price: float, value_usdt: Optional[float] = None,
                    price_change: Optional[float] = None, oi_change: Optional[float] = None) -> bool:
        """
        保存持仓量数据

        Args:
            symbol: 交易对符号
            timestamp: 数据时间戳
            open_interest: 持仓量
            price: 当前价格
            value_usdt: USDT价值（可选）
            price_change: 价格变化率（可选）
            oi_change: 持仓量变化率（可选）

        Returns:
            bool: 是否成功保存
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO oi_history
                    (symbol, timestamp, open_interest, price, value_usdt, price_change, oi_change)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (symbol, timestamp.isoformat(), open_interest, price, value_usdt,
                     price_change if price_change is not None else 0.0,
                     oi_change if oi_change is not None else 0.0)
                )
                return True
        except Exception as e:
            logger.error(f"保存持仓量数据失败 {symbol}: {e}")
            return False

    def get_recent_oi_data(self, symbol: str, minutes: int = 15) -> List[Dict[str, Any]]:
        """
        获取最近指定分钟数的持仓量数据，优化版确保有足够对比数据

        Args:
            symbol: 交易对符号
            minutes: 时间范围（分钟）

        Returns:
            List[Dict]: 历史数据列表，按时间升序排列
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 使用UTC+8时间确保一致性
                # 调整截止时间以解决微秒精度问题 - 向前调整2秒确保包含边界数据
                cutoff_time = (get_utc8_time() - timedelta(minutes=minutes) - timedelta(seconds=2)).isoformat()

                # 首先检查是否有足够的数据
                cursor.execute(
                    """SELECT COUNT(*) as count, MIN(timestamp) as oldest_time, MAX(timestamp) as newest_time
                    FROM oi_history
                    WHERE symbol = ? AND timestamp <= ?""",
                    (symbol, get_utc8_time().isoformat())
                )
                stats = cursor.fetchone()
                total_count = stats['count']
                oldest_time = stats['oldest_time']
                newest_time = stats['newest_time']

                if total_count == 0:
                    logger.debug(f"{symbol} 无历史数据")
                    return []

                # 如果最近15分钟数据不足，扩大时间范围到30分钟或60分钟
                cursor.execute(
                    """SELECT COUNT(*) as recent_count
                    FROM oi_history
                    WHERE symbol = ? AND timestamp >= ?""",
                    (symbol, cutoff_time)
                )
                recent_count = cursor.fetchone()['recent_count']

                if recent_count == 0:
                    # 扩大搜索范围到30分钟
                    extended_minutes = 30
                    extended_cutoff = (get_utc8_time() - timedelta(minutes=extended_minutes)).isoformat()
                    cursor.execute(
                        """SELECT COUNT(*) as extended_count
                        FROM oi_history
                        WHERE symbol = ? AND timestamp >= ?""",
                        (symbol, extended_cutoff)
                    )
                    extended_count = cursor.fetchone()['extended_count']

                    if extended_count > 0:
                        logger.info(f"{symbol} 最近{minutes}分钟无数据，使用{extended_minutes}分钟数据")
                        cutoff_time = extended_cutoff
                        minutes = extended_minutes
                    else:
                        # 再扩大到60分钟
                        extended_minutes = 60
                        extended_cutoff = (get_utc8_time() - timedelta(minutes=extended_minutes)).isoformat()
                        cursor.execute(
                            """SELECT COUNT(*) as extended_count
                            FROM oi_history
                            WHERE symbol = ? AND timestamp >= ?""",
                            (symbol, extended_cutoff)
                        )
                        extended_count = cursor.fetchone()['extended_count']

                        if extended_count > 0:
                            logger.info(f"{symbol} 最近{minutes}分钟无数据，使用{extended_minutes}分钟数据")
                            cutoff_time = extended_cutoff
                            minutes = extended_minutes
                        else:
                            logger.warning(f"{symbol} 最近60分钟内无数据，返回空结果")
                            return []

                # 获取数据，按时间升序排列（确保最老的数据在前）
                cursor.execute(
                    """SELECT timestamp, open_interest, price, value_usdt
                    FROM oi_history
                    WHERE symbol = ? AND timestamp >= ?
                    ORDER BY timestamp ASC""",
                    (symbol, cutoff_time)
                )
                rows = cursor.fetchall()

                # 如果没有找到足够的数据，使用一个更合理的回退策略
                if not rows and minutes > 15:
                    # 回退到使用最近的一条记录作为基准，而不是使用非常老的数据
                    cursor.execute(
                        """SELECT timestamp, open_interest, price, value_usdt
                        FROM oi_history
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT 1""",
                        (symbol,)
                    )
                    fallback_row = cursor.fetchone()
                    if fallback_row:
                        # 使用最近的一条记录，但将其时间戳调整为当前时间前15分钟
                        # 这样可以避免使用过老的数据作为基准
                        adjusted_timestamp = (get_utc8_time() - timedelta(minutes=15)).isoformat()
                        rows = [fallback_row]
                        logger.info(f"{symbol} 使用最近历史数据作为15分钟基准: {fallback_row['timestamp']}")

                result = []
                for row in rows:
                    result.append({
                        'timestamp': row['timestamp'],
                        'open_interest': row['open_interest'],
                        'price': row['price'],
                        'value_usdt': row['value_usdt']
                    })

                logger.debug(f"{symbol} 获取到 {len(result)} 条历史数据（{minutes}分钟内）")
                return result

        except Exception as e:
            logger.error(f"获取历史数据失败 {symbol}: {e}")
            return []

    def save_alert(self, symbol: str, oi_change_percent: float, price_change_percent: float,
                  current_oi: float, old_oi: float, current_price: float, old_price: float,
                  total_value_usdt: Optional[float] = None) -> bool:
        """
        保存警报记录

        Args:
            symbol: 交易对符号
            oi_change_percent: 持仓量变化百分比
            price_change_percent: 价格变化百分比
            current_oi: 当前持仓量
            old_oi: 历史持仓量
            current_price: 当前价格
            old_price: 历史价格
            total_value_usdt: 总价值（可选）

        Returns:
            bool: 是否成功保存
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO alerts
                    (symbol, oi_change_percent, price_change_percent, current_oi, old_oi,
                     current_price, old_price, total_value_usdt, alert_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (symbol, oi_change_percent, price_change_percent, current_oi, old_oi,
                     current_price, old_price, total_value_usdt, get_utc8_time().isoformat())
                )
                return True
        except Exception as e:
            logger.error(f"保存警报记录失败 {symbol}: {e}")
            return False

    def get_recent_alerts(self, symbol: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取最近的警报记录

        Args:
            symbol: 交易对符号（可选）
            hours: 时间范围（小时）

        Returns:
            List[Dict]: 警报记录列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cutoff_time = (get_utc8_time() - timedelta(hours=hours)).isoformat()

                if symbol:
                    cursor.execute(
                        """SELECT * FROM alerts
                        WHERE symbol = ? AND alert_time >= ?
                        ORDER BY alert_time DESC""",
                        (symbol, cutoff_time)
                    )
                else:
                    cursor.execute(
                        """SELECT * FROM alerts
                        WHERE alert_time >= ?
                        ORDER BY alert_time DESC""",
                        (cutoff_time,)
                    )

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取警报记录失败: {e}")
            return []

    def log_error(self, error_type: str, error_message: str, symbol: Optional[str] = None,
                 context: Optional[str] = None) -> bool:
        """
        记录错误日志

        Args:
            error_type: 错误类型
            error_message: 错误信息
            symbol: 相关交易对（可选）
            context: 错误上下文（可选）

        Returns:
            bool: 是否成功记录
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO error_logs
                    (error_type, error_message, symbol, context, error_time)
                    VALUES (?, ?, ?, ?, ?)""",
                    (error_type, error_message, symbol, context, get_utc8_time().isoformat())
                )
                return True
        except Exception as e:
            logger.error(f"记录错误日志失败: {e}")
            return False

    def record_metric(self, metric_name: str, metric_value: float, symbol: Optional[str] = None) -> bool:
        """
        记录性能指标

        Args:
            metric_name: 指标名称
            metric_value: 指标值
            symbol: 相关交易对（可选）

        Returns:
            bool: 是否成功记录
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO performance_metrics
                    (metric_name, metric_value, symbol, timestamp)
                    VALUES (?, ?, ?, ?)""",
                    (metric_name, metric_value, symbol, get_utc8_time().isoformat())
                )
                return True
        except Exception as e:
            logger.error(f"记录性能指标失败: {e}")
            return False

    def cleanup_old_data(self, data_retention_days: int = 30, alert_retention_days: int = 90) -> Dict[str, int]:
        """
        清理旧数据

        Args:
            data_retention_days: 监控数据保留天数
            alert_retention_days: 警报记录保留天数

        Returns:
            Dict[str, int]: 清理统计信息
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 清理oi_history表中的旧数据
                oi_cutoff = (get_utc8_time() - timedelta(days=data_retention_days)).isoformat()
                cursor.execute("DELETE FROM oi_history WHERE timestamp < ?", (oi_cutoff,))
                oi_deleted = cursor.rowcount

                # 清理alerts表中的旧数据
                alert_cutoff = (get_utc8_time() - timedelta(days=alert_retention_days)).isoformat()
                cursor.execute("DELETE FROM alerts WHERE alert_time < ?", (alert_cutoff,))
                alert_deleted = cursor.rowcount

                # 清理错误日志（保留7天）
                error_cutoff = (get_utc8_time() - timedelta(days=7)).isoformat()
                cursor.execute("DELETE FROM error_logs WHERE error_time < ?", (error_cutoff,))
                error_deleted = cursor.rowcount

                # 清理性能指标（保留30天）
                metric_cutoff = (get_utc8_time() - timedelta(days=30)).isoformat()
                cursor.execute("DELETE FROM performance_metrics WHERE timestamp < ?", (metric_cutoff,))
                metric_deleted = cursor.rowcount

                # 执行VACUUM以释放磁盘空间
                cursor.execute("VACUUM")

                result = {
                    'oi_records_deleted': oi_deleted,
                    'alert_records_deleted': alert_deleted,
                    'error_logs_deleted': error_deleted,
                    'performance_metrics_deleted': metric_deleted
                }

                logger.info(f"数据清理完成: {result}")
                return result

        except Exception as e:
            logger.error(f"清理旧数据时发生错误: {e}")
            return {'oi_records_deleted': 0, 'alert_records_deleted': 0, 'error_logs_deleted': 0, 'performance_metrics_deleted': 0}

    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息

        Returns:
            Dict: 数据库统计信息
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 获取各表记录数
                cursor.execute("SELECT COUNT(*) as count FROM oi_history")
                oi_count = cursor.fetchone()['count']

                cursor.execute("SELECT COUNT(*) as count FROM alerts")
                alert_count = cursor.fetchone()['count']

                cursor.execute("SELECT COUNT(*) as count FROM error_logs")
                error_count = cursor.fetchone()['count']

                cursor.execute("SELECT COUNT(*) as count FROM performance_metrics")
                metric_count = cursor.fetchone()['count']

                # 获取数据库文件大小
                import os
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

                # 获取最近的数据时间
                cursor.execute("SELECT MAX(timestamp) as latest FROM oi_history")
                latest_data = cursor.fetchone()['latest']

                return {
                    'oi_history_records': oi_count,
                    'alert_records': alert_count,
                    'error_logs': error_count,
                    'performance_metrics': metric_count,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'latest_data_time': latest_data,
                    'database_path': self.db_path
                }

        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {e}")
            return {}

    def optimize_database(self):
        """优化数据库性能"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 执行各种优化操作
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]

                cursor.execute("ANALYZE")  # 更新统计信息
                cursor.execute("VACUUM")   # 压缩数据库

                logger.info(f"数据库优化完成，完整性检查: {integrity_result}")
                return True

        except Exception as e:
            logger.error(f"数据库优化失败: {e}")
            return False