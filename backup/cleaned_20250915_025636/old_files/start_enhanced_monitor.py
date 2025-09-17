#!/usr/bin/env python3
"""
简化版增强型Binance监控器启动脚本
"""

import argparse
import sys
import os
import signal
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_monitor import EnhancedBinanceMonitor, MonitoringConfig
from database_manager import DatabaseManager

# 全局监控器实例
monitor_instance = None

def signal_handler(signum, frame):
    """处理中断信号"""
    print(f"\n[{datetime.now()}] 收到信号 {signum}，正在优雅关闭监控器...")
    if monitor_instance:
        monitor_instance.shutdown()
    print("[{datetime.now()}] 监控器已停止")
    sys.exit(0)

def show_database_stats(db_path):
    """显示数据库统计信息"""
    try:
        print(f"[{datetime.now()}] 正在获取数据库统计信息: {db_path}")
        db = DatabaseManager(db_path=db_path)
        stats = db.get_database_stats()

        if stats:
            print("\n=== 数据库统计信息 ===")
            print(f"持仓量历史记录: {stats.get('oi_history_records', 0):,}")
            print(f"警报记录: {stats.get('alert_records', 0):,}")
            print(f"错误日志: {stats.get('error_logs', 0):,}")
            print(f"性能指标: {stats.get('performance_metrics', 0):,}")
            print(f"数据库大小: {stats.get('database_size_mb', 0):.2f} MB")
            print(f"数据库路径: {stats.get('database_path', '未知')}")
            print(f"最新数据时间: {stats.get('latest_data_time', '无数据')}")
            print("=" * 30)
        else:
            print("无法获取数据库统计信息")

    except Exception as e:
        print(f"[{datetime.now()}] 获取数据库统计信息失败: {e}")
        sys.exit(1)

def perform_cleanup(db_path, data_retention_days, alert_retention_days):
    """执行数据清理"""
    try:
        print(f"[{datetime.now()}] 正在执行数据清理...")
        db = DatabaseManager(db_path=db_path)

        stats_before = db.get_database_stats()
        cleanup_result = db.cleanup_old_data(
            data_retention_days=data_retention_days,
            alert_retention_days=alert_retention_days
        )
        stats_after = db.get_database_stats()

        print("\n=== 数据清理结果 ===")
        print(f"清理的持仓量记录: {cleanup_result.get('oi_records_deleted', 0):,}")
        print(f"清理的警报记录: {cleanup_result.get('alert_records_deleted', 0):,}")
        print(f"清理的错误日志: {cleanup_result.get('error_logs_deleted', 0):,}")
        print(f"清理的性能指标: {cleanup_result.get('performance_metrics_deleted', 0):,}")
        print(f"数据库大小变化: {stats_before.get('database_size_mb', 0):.2f} MB -> {stats_after.get('database_size_mb', 0):.2f} MB")
        print("=" * 30)

    except Exception as e:
        print(f"[{datetime.now()}] 数据清理失败: {e}")
        sys.exit(1)

def run_monitor(args):
    """运行监控器"""
    try:
        global monitor_instance

        # 创建配置
        config = MonitoringConfig(
            oi_change_threshold=args.oi_threshold,
            price_change_threshold=args.price_threshold,
            monitor_interval_minutes=args.interval,
            data_retention_days=args.data_retention_days,
            alert_retention_days=args.alert_retention_days,
            cleanup_interval_hours=args.cleanup_interval_hours,
            telegram_enabled=args.telegram_enabled,
            max_requests_per_minute=args.max_requests_per_minute
        )

        print(f"[{datetime.now()}] 启动Binance永续合约监控器")
        print(f"监控配置: OI变化≥{config.oi_change_threshold*100:.1f}% 且 价格变化≥{config.price_change_threshold*100:.1f}%")
        print(f"监控间隔: {config.monitor_interval_minutes} 分钟")
        print(f"数据保留: 监控数据{config.data_retention_days}天, 警报记录{config.alert_retention_days}天")
        print(f"Telegram推送: {'启用' if config.telegram_enabled else '禁用'}")

        # 创建监控器
        monitor_instance = EnhancedBinanceMonitor(config)

        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 运行监控
        monitor_instance.run(interval_minutes=config.monitor_interval_minutes)

    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] 用户中断监控")
    except Exception as e:
        print(f"[{datetime.now()}] 监控器运行失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Binance永续合约持仓量监控器 - 增强版",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 基本配置
    parser.add_argument('--interval', '-i', type=int, default=15, help='Monitoring interval in minutes')
    parser.add_argument('--oi-threshold', '-o', type=float, default=0.08, help='OI change threshold')
    parser.add_argument('--price-threshold', '-p', type=float, default=0.02, help='Price change threshold')

    # 数据保留配置
    parser.add_argument('--data-retention-days', type=int, default=30, help='Monitoring data retention days')
    parser.add_argument('--alert-retention-days', type=int, default=90, help='Alert records retention days')
    parser.add_argument('--cleanup-interval-hours', type=int, default=24, help='Data cleanup interval in hours')

    # 数据库操作
    parser.add_argument('--db-stats', action='store_true', help='Show database statistics')
    parser.add_argument('--cleanup', action='store_true', help='Perform data cleanup')
    parser.add_argument('--db-path', type=str, default='data/binance_monitor.db', help='Database file path')

    # Telegram配置
    parser.add_argument('--telegram-enabled', action='store_true', default=False, help='Enable Telegram notifications')
    parser.add_argument('--no-telegram', action='store_true', help='Disable Telegram notifications')

    # 性能配置
    parser.add_argument('--max-requests-per-minute', type=int, default=1200, help='Max API requests per minute')

    # 其他选项
    parser.add_argument('--test', action='store_true', help='Test run once and exit')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual alerts sent)')

    args = parser.parse_args()

    # 处理Telegram配置冲突
    if args.no_telegram:
        args.telegram_enabled = False

    # 数据库操作
    if args.db_stats:
        show_database_stats(args.db_path)
        return

    if args.cleanup:
        perform_cleanup(args.db_path, args.data_retention_days, args.alert_retention_days)
        return

    # 测试模式
    if args.test:
        print(f"[{datetime.now()}] 运行测试模式...")
        config = MonitoringConfig(
            oi_change_threshold=args.oi_threshold,
            price_change_threshold=args.price_threshold,
            telegram_enabled=False,  # 测试模式禁用Telegram
            max_requests_per_minute=args.max_requests_per_minute
        )

        monitor = EnhancedBinanceMonitor(config)
        monitor.monitor_once()
        print(f"[{datetime.now()}] 测试完成")
        return

    # 运行监控
    run_monitor(args)

if __name__ == "__main__":
    main()