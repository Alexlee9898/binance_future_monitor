#!/usr/bin/env python3
"""
增强版Binance持仓量监控器 - 集成SQLite数据库和日志轮转
结合高性能数据存储、日志管理和自动清理功能
"""

import requests
import time
import threading
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any
import websocket
import json
import os
import random
from dataclasses import dataclass
from enum import Enum

# 导入自定义模块
from database_manager import DatabaseManager
from logger_manager import get_logger_manager, get_logger

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

# 配置参数
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 监控参数
OI_CHANGE_THRESHOLD = 0.05  # 5%持仓量变化阈值
PRICE_CHANGE_THRESHOLD = 0.02  # 2%价格变化阈值
MONITOR_INTERVAL_MINUTES = 15  # 15分钟监控间隔
DATA_RETENTION_DAYS = 30  # 数据保留30天
ALERT_RETENTION_DAYS = 90  # 警报记录保留90天
CLEANUP_INTERVAL_HOURS = 24  # 24小时清理间隔

class AlertLevel(Enum):
    """警报级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MonitoringConfig:
    """监控配置"""
    oi_change_threshold: float = OI_CHANGE_THRESHOLD
    price_change_threshold: float = PRICE_CHANGE_THRESHOLD
    monitor_interval_minutes: int = MONITOR_INTERVAL_MINUTES
    data_retention_days: int = DATA_RETENTION_DAYS
    alert_retention_days: int = ALERT_RETENTION_DAYS
    cleanup_interval_hours: int = CLEANUP_INTERVAL_HOURS
    telegram_enabled: bool = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    max_requests_per_minute: int = 1200
    websocket_enabled: bool = True

class EnhancedBinanceMonitor:
    """增强版Binance持仓量监控器"""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        """
        初始化增强版监控器

        Args:
            config: 监控配置（可选，使用默认配置）
        """
        self.config = config or MonitoringConfig()

        # 初始化日志管理器
        self.logger_manager = get_logger_manager(
            name="enhanced_binance_monitor",
            log_dir="logs",
            max_bytes=10*1024*1024,  # 10MB
            backup_count=5,
            console_level="INFO",
            file_level="DEBUG"
        )
        self.logger = self.logger_manager.get_logger()

        # 初始化数据库管理器
        self.db = DatabaseManager(
            db_path="data/binance_monitor.db",
            max_connections=5
        )

        # API配置
        self.base_url = "https://fapi.binance.com"
        self.open_interest_endpoint = "/fapi/v1/openInterest"
        self.exchange_info_endpoint = "/fapi/v1/exchangeInfo"
        self.ticker_price_endpoint = "/fapi/v1/ticker/price"
        self.ws_base_url = "wss://fstream.binance.com/ws"

        # 运行时数据
        self.alert_cooldown: Dict[str, float] = {}
        self.cooldown_period = 3600  # 1小时冷却时间
        self.request_timestamps = []
        self.ws_connections = []
        self.ws_connected = False
        self.ws_price_data = {}
        self.ws_last_update = {}

        # 性能统计
        self.total_symbols_monitored = 0
        self.total_alerts_sent = 0
        self.last_cleanup_time = time.time()
        self.start_time = get_utc8_time()

        self.logger.info("增强版监控器初始化完成", extra={
            'config': self.config.__dict__,
            'telegram_enabled': self.config.telegram_enabled,
            'websocket_enabled': self.config.websocket_enabled
        })

    def get_all_perpetual_symbols(self) -> List[str]:
        """获取所有永续合约交易对"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{self.exchange_info_endpoint}", timeout=30)
            response.raise_for_status()
            data = response.json()

            symbols = []
            for symbol_info in data['symbols']:
                if (symbol_info['contractType'] == 'PERPETUAL' and
                    symbol_info['status'] == 'TRADING'):
                    symbols.append(symbol_info['symbol'])

            response_time = time.time() - start_time
            self.logger_manager.log_api_request(
                endpoint="exchangeInfo",
                symbol="ALL",
                response_time=response_time,
                status_code=response.status_code
            )

            self.logger.info(f"获取到 {len(symbols)} 个永续合约交易对")
            return symbols

        except requests.exceptions.RequestException as e:
            self.logger_manager.log_error_with_context(
                error_type="API_REQUEST_ERROR",
                error_message=str(e),
                context={"endpoint": "exchangeInfo"}
            )
            return []
        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="PARSE_ERROR",
                error_message=str(e),
                context={"endpoint": "exchangeInfo"}
            )
            return []

    def _make_rate_limited_request(self, url: str, params: dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """智能速率限制的请求方法，带指数退避重试"""
        # 清理过期的请求记录
        now = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]

        # 检查速率限制
        if len(self.request_timestamps) >= self.config.max_requests_per_minute:
            oldest_request = min(self.request_timestamps)
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                self.logger.warning(f"速率限制接近，等待 {wait_time:.2f} 秒")
                time.sleep(wait_time)
                now = time.time()
                self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]

        # 记录请求时间
        self.request_timestamps.append(time.time())

        # 指数退避重试机制
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)

                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    self.logger.warning(f"API速率限制触发，等待 {retry_after} 秒 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                wait_time = 2 ** attempt + (random.random() * 0.5)  # 指数退避 + 随机化
                self.logger.error(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}，等待 {wait_time:.1f} 秒后重试")

                if attempt < max_retries - 1:  # 不是最后一次尝试
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"请求失败，已达到最大重试次数 {max_retries}")
                    return None

        return None

    def get_open_interest(self, symbol: str) -> Optional[float]:
        """获取指定交易对的持仓量"""
        url = f"{self.base_url}{self.open_interest_endpoint}"
        params = {'symbol': symbol}

        start_time = time.time()
        response = self._make_rate_limited_request(url, params)

        if response is None:
            return None

        try:
            data = response.json()
            result = float(data['openInterest'])

            response_time = time.time() - start_time
            self.logger_manager.log_api_request(
                endpoint="openInterest",
                symbol=symbol,
                response_time=response_time,
                status_code=response.status_code
            )

            return result

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="PARSE_ERROR",
                error_message=str(e),
                symbol=symbol,
                context={"endpoint": "openInterest"}
            )
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """获取指定交易对的当前价格"""
        url = f"{self.base_url}{self.ticker_price_endpoint}"
        params = {'symbol': symbol}

        start_time = time.time()
        response = self._make_rate_limited_request(url, params)

        if response is None:
            return None

        try:
            data = response.json()
            result = float(data['price'])

            response_time = time.time() - start_time
            self.logger_manager.log_api_request(
                endpoint="ticker_price",
                symbol=symbol,
                response_time=response_time,
                status_code=response.status_code
            )

            return result

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="PARSE_ERROR",
                error_message=str(e),
                symbol=symbol,
                context={"endpoint": "ticker_price"}
            )
            return None

    def get_all_prices(self) -> Optional[Dict[str, float]]:
        """批量获取所有交易对的最新价格"""
        url = f"{self.base_url}/fapi/v1/ticker/24hr"

        start_time = time.time()
        response = self._make_rate_limited_request(url)

        if response is None:
            return None

        try:
            data = response.json()
            prices = {item['symbol']: float(item['lastPrice']) for item in data if 'lastPrice' in item}

            response_time = time.time() - start_time
            self.logger_manager.log_api_request(
                endpoint="ticker_24hr",
                symbol="ALL",
                response_time=response_time,
                status_code=response.status_code
            )

            self.logger.info(f"成功获取 {len(prices)} 个交易对的最新价格")
            return prices

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="PARSE_ERROR",
                error_message=str(e),
                context={"endpoint": "ticker_24hr"}
            )
            return None

    def calculate_oi_change_rate(self, symbol: str, current_oi: float) -> Optional[float]:
        """计算持仓量变化率"""
        historical_data = self.db.get_recent_oi_data(symbol, minutes=15)

        if not historical_data:
            self.logger.debug(f"{symbol} 无历史数据，无法计算变化率")
            return None

        # 使用最早的历史数据作为基准
        oldest_data = historical_data[0]
        old_oi = oldest_data['open_interest']

        if old_oi == 0:
            self.logger.debug(f"{symbol} 历史持仓量为0，无法计算变化率")
            return None

        change_rate = (current_oi - old_oi) / old_oi
        return change_rate

    def calculate_price_change_rate(self, symbol: str, current_price: float) -> Optional[float]:
        """计算价格变化率"""
        historical_data = self.db.get_recent_oi_data(symbol, minutes=15)

        if not historical_data:
            self.logger.debug(f"{symbol} 无历史数据，无法计算价格变化率")
            return None

        # 使用最早的历史数据作为基准
        oldest_data = historical_data[0]
        old_price = oldest_data['price']

        if old_price == 0:
            self.logger.debug(f"{symbol} 历史价格为0，无法计算价格变化率")
            return None

        price_change_rate = (current_price - old_price) / old_price
        return price_change_rate

    def should_alert(self, symbol: str) -> bool:
        """判断是否应该发出警告"""
        current_time = time.time()

        if symbol not in self.alert_cooldown:
            return True

        last_alert_time = self.alert_cooldown[symbol]
        return (current_time - last_alert_time) > self.cooldown_period

    def determine_alert_level(self, oi_change_percent: float, price_change_percent: float) -> AlertLevel:
        """确定警报级别"""
        if oi_change_percent >= 0.15 or price_change_percent >= 0.05:
            return AlertLevel.CRITICAL
        elif oi_change_percent >= 0.12 or price_change_percent >= 0.04:
            return AlertLevel.HIGH
        elif oi_change_percent >= 0.10 or price_change_percent >= 0.03:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW

    def send_alert(self, symbol: str, oi_change_rate: float, price_change_rate: float,
                  current_oi: float, old_oi: float, current_price: float, old_price: float,
                  total_value_usdt: Optional[float] = None):
        """发送警报"""
        oi_change_percent = oi_change_rate * 100
        price_change_percent = price_change_rate * 100
        alert_level = self.determine_alert_level(abs(oi_change_percent), abs(price_change_percent))

        # 准备警报数据
        alert_data = {
            'symbol': symbol,
            'oi_change_percent': oi_change_percent,
            'price_change_percent': price_change_percent,
            'current_oi': current_oi,
            'old_oi': old_oi,
            'current_price': current_price,
            'old_price': old_price,
            'total_value_usdt': total_value_usdt,
            'alert_level': alert_level.value,
            'timestamp': get_utc8_time().isoformat()
        }

        # 记录结构化警报日志
        self.logger_manager.log_monitor_event(
            event_type="alert_triggered",
            symbol=symbol,
            data=alert_data,
            level="WARNING" if alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL] else "INFO"
        )

        # 保存到数据库
        self.db.save_alert(
            symbol, oi_change_percent, price_change_percent,
            current_oi, old_oi, current_price, old_price, total_value_usdt
        )

        # 发送Telegram通知
        if self.config.telegram_enabled:
            self.send_telegram_notification(alert_data)

        # 更新冷却时间
        self.alert_cooldown[symbol] = time.time()
        self.total_alerts_sent += 1

    def send_telegram_notification(self, alert_data: Dict[str, Any]) -> bool:
        """发送Telegram通知"""
        try:
            symbol = alert_data['symbol']
            oi_change = alert_data['oi_change_percent']
            price_change = alert_data['price_change_percent']
            alert_level = AlertLevel(alert_data['alert_level'])

            # 根据警报级别选择不同的表情符号
            level_emoji = {
                AlertLevel.LOW: "⚠️",
                AlertLevel.MEDIUM: "🚨",
                AlertLevel.HIGH: "🔥",
                AlertLevel.CRITICAL: "💥"
            }

            emoji = level_emoji.get(alert_level, "🚨")

            message = (
                f"{emoji} \u003cb\u003eBinance永续合约异常警报\u003c/b\u003e\n\n"
                f"📊 \u003cb\u003e交易对:\u003c/b\u003e {symbol}\n\n"
                f"📈 \u003cb\u003e持仓量变化:\u003c/b\u003e {oi_change:.2f}%\n"
                f"💰 \u003cb\u003e当前持仓量:\u003c/b\u003e {alert_data['current_oi']:,.0f}\n"
                f"📊 \u003cb\u003e15分钟前持仓量:\u003c/b\u003e {alert_data['old_oi']:,.0f}\n\n"
                f"💹 \u003cb\u003e价格变化:\u003c/b\u003e {price_change:.2f}%\n"
                f"💰 \u003cb\u003e当前价格:\u003c/b\u003e ${alert_data['current_price']:.6f}\n"
                f"📊 \u003cb\u003e15分钟前价格:\u003c/b\u003e ${alert_data['old_price']:.6f}\n"
            )

            if alert_data.get('total_value_usdt'):
                message += f"💎 \u003cb\u003e当前持仓总价值:\u003c/b\u003e {alert_data['total_value_usdt']:,.2f} USDT\n"

            message += (
                f"⏰ \u003cb\u003e检测时间:\u003c/b\u003e {alert_data['timestamp']}\n\n"
                f"⚠️  请注意风险控制！"
            )

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            params = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            self.logger.info(f"Telegram警报消息已发送: {symbol}")
            return True

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="TELEGRAM_ERROR",
                error_message=str(e),
                symbol=symbol
            )
            return False

    def perform_periodic_cleanup(self):
        """执行定期数据清理"""
        current_time = time.time()
        if current_time - self.last_cleanup_time < self.config.cleanup_interval_hours * 3600:
            return

        cleanup_start = time.time()
        self.logger.info("开始定期数据清理")

        try:
            # 执行数据库清理
            cleanup_stats = self.db.cleanup_old_data(
                data_retention_days=self.config.data_retention_days,
                alert_retention_days=self.config.alert_retention_days
            )

            # 记录性能指标
            cleanup_duration = time.time() - cleanup_start
            self.db.record_metric("cleanup_duration", cleanup_duration)

            # 记录清理操作
            self.logger_manager.log_cleanup_operation(
                operation_type="periodic_cleanup",
                records_deleted=sum(cleanup_stats.values()),
                duration=cleanup_duration
            )

            self.logger.info(f"定期数据清理完成: {cleanup_stats}")
            self.last_cleanup_time = current_time

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="CLEANUP_ERROR",
                error_message=str(e)
            )

    def monitor_once(self) -> bool:
        """执行一次监控循环"""
        self.logger.info("开始监控循环")
        start_time = time.time()

        try:
            # 执行定期清理
            self.perform_periodic_cleanup()

            # 获取所有永续合约交易对
            symbols = self.get_all_perpetual_symbols()
            if not symbols:
                self.logger.error("无法获取交易对列表")
                return False

            self.total_symbols_monitored = len(symbols)

            # 批量获取价格
            all_prices = self.get_all_prices() or {}

            success_count = 0
            error_count = 0

            for symbol in symbols:
                try:
                    # 获取持仓量
                    current_oi = self.get_open_interest(symbol)
                    if current_oi is None:
                        error_count += 1
                        continue

                    # 获取价格（优先使用批量获取的价格）
                    current_price = all_prices.get(symbol)
                    if current_price is None:
                        current_price = self.get_current_price(symbol)

                    if current_price is None:
                        self.logger.warning(f"无法获取 {symbol} 的价格，跳过")
                        continue

                    # 计算USDT价值
                    total_value_usdt = current_oi * current_price
                    current_time = get_utc8_time()

                    # 保存数据到数据库
                    self.db.save_oi_data(symbol, current_time, current_oi, current_price, total_value_usdt)

                    # 计算变化率
                    oi_change_rate = self.calculate_oi_change_rate(symbol, current_oi)
                    price_change_rate = self.calculate_price_change_rate(symbol, current_price)

                    if oi_change_rate is not None and price_change_rate is not None:
                        oi_change_percent = abs(oi_change_rate * 100)
                        price_change_percent = abs(price_change_rate * 100)

                        # 检查警报条件
                        if (oi_change_percent >= (self.config.oi_change_threshold * 100) and
                            price_change_percent >= (self.config.price_change_threshold * 100)):

                            if self.should_alert(symbol):
                                # 获取历史数据用于警报
                                historical_data = self.db.get_recent_oi_data(symbol, minutes=15)
                                if historical_data:
                                    oldest_data = historical_data[0]
                                    self.send_alert(
                                        symbol, oi_change_rate, price_change_rate,
                                        current_oi, oldest_data['open_interest'],
                                        current_price, oldest_data['price'], total_value_usdt
                                    )
                            else:
                                self.logger.info(
                                    f"{symbol} 满足警报条件但在冷却期，不发送警报",
                                    extra={
                                        'symbol': symbol,
                                        'oi_change_percent': oi_change_percent,
                                        'price_change_percent': price_change_percent
                                    }
                                )
                        else:
                            # 记录正常数据更新
                            self.logger_manager.log_monitor_event(
                                event_type="data_update",
                                symbol=symbol,
                                data={
                                    'open_interest': current_oi,
                                    'price': current_price,
                                    'value_usdt': total_value_usdt,
                                    'oi_change_percent': oi_change_percent,
                                    'price_change_percent': price_change_percent
                                }
                            )

                    success_count += 1

                    # 记录性能指标
                    self.db.record_metric("api_request_success", 1, symbol)

                    # 添加微小延迟避免请求过快
                    time.sleep(0.05)

                except Exception as e:
                    error_count += 1
                    self.logger_manager.log_error_with_context(
                        error_type="MONITOR_ERROR",
                        error_message=str(e),
                        symbol=symbol
                    )
                    continue

            # 记录监控循环统计
            cycle_duration = time.time() - start_time
            self.db.record_metric("monitor_cycle_duration", cycle_duration)
            self.db.record_metric("symbols_processed", success_count)
            self.db.record_metric("symbols_failed", error_count)

            self.logger.info(
                f"监控循环完成: 成功 {success_count} 个, 失败 {error_count} 个, 耗时 {cycle_duration:.2f}秒"
            )

            return True

        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="MONITOR_CYCLE_ERROR",
                error_message=str(e)
            )
            return False

    def run(self, interval_minutes: Optional[int] = None):
        """运行持续监控"""
        if interval_minutes is None:
            interval_minutes = self.config.monitor_interval_minutes

        self.logger.info(f"开始持续监控，间隔时间: {interval_minutes} 分钟")

        try:
            while True:
                self.monitor_once()
                self.logger.info(f"等待 {interval_minutes} 分钟后进行下一次监控...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            self.logger.info("用户中断监控")
            self.shutdown()
        except Exception as e:
            self.logger_manager.log_error_with_context(
                error_type="FATAL_ERROR",
                error_message=str(e)
            )
            self.shutdown()

    def shutdown(self):
        """优雅关闭"""
        self.logger.info("正在关闭监控器...")

        try:
            # 获取最终统计信息
            db_stats = self.db.get_database_stats()
            log_stats = self.logger_manager.get_log_files_info()

            runtime_duration = (get_utc8_time() - self.start_time).total_seconds() / 3600  # 小时

            shutdown_info = {
                'runtime_hours': round(runtime_duration, 2),
                'total_symbols_monitored': self.total_symbols_monitored,
                'total_alerts_sent': self.total_alerts_sent,
                'database_stats': db_stats,
                'log_stats': log_stats
            }

            self.logger.info("监控器关闭完成", extra=shutdown_info)

        except Exception as e:
            self.logger.error(f"关闭过程中发生错误: {e}")

if __name__ == "__main__":
    # 创建监控器实例
    monitor = EnhancedBinanceMonitor()

    # 运行监控
    monitor.run()