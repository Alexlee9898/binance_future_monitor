#!/usr/bin/env python3
"""
增强版监控器配置文件
包含所有可配置参数和环境变量设置
"""

import os
import sys
from typing import Optional

# =============================================================================
# 基本配置
# =============================================================================

# 监控模式
MONITOR_MODE = os.environ.get('MONITOR_MODE', 'enhanced').lower()  # enhanced, standard, websocket

# 调试模式
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'

# =============================================================================
# Telegram配置
# =============================================================================

# Telegram Bot配置 - 从环境变量读取
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 是否启用Telegram推送
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# Telegram推送配置
TELEGRAM_RETRY_COUNT = int(os.environ.get('TELEGRAM_RETRY_COUNT', '3'))
TELEGRAM_RETRY_DELAY = int(os.environ.get('TELEGRAM_RETRY_DELAY', '5'))

# =============================================================================
# 监控参数配置
# =============================================================================

# 持仓量变化阈值 (8%)
OI_CHANGE_THRESHOLD = float(os.environ.get('OI_CHANGE_THRESHOLD', '0.08'))

# 价格变化阈值 (2%)
PRICE_CHANGE_THRESHOLD = float(os.environ.get('PRICE_CHANGE_THRESHOLD', '0.02'))

# 监控间隔时间（分钟）
MONITOR_INTERVAL_MINUTES = int(os.environ.get('MONITOR_INTERVAL_MINUTES', '15'))

# 警报冷却时间（秒）
ALERT_COOLDOWN_SECONDS = int(os.environ.get('ALERT_COOLDOWN_SECONDS', '3600'))  # 1小时

# 最大每分钟API请求数
MAX_REQUESTS_PER_MINUTE = int(os.environ.get('MAX_REQUESTS_PER_MINUTE', '1200'))

# 数据保留时间（小时）
DATA_RETENTION_HOURS = int(os.environ.get('DATA_RETENTION_HOURS', '24'))

# =============================================================================
# 数据库配置
# =============================================================================

# 数据库文件路径
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/binance_monitor.db')

# 数据库连接池大小
DATABASE_MAX_CONNECTIONS = int(os.environ.get('DATABASE_MAX_CONNECTIONS', '5'))

# 数据库超时时间（秒）
DATABASE_TIMEOUT = int(os.environ.get('DATABASE_TIMEOUT', '30'))

# 数据保留配置
DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '30'))  # 监控数据
ALERT_RETENTION_DAYS = int(os.environ.get('ALERT_RETENTION_DAYS', '90'))  # 警报记录
ERROR_LOG_RETENTION_DAYS = int(os.environ.get('ERROR_LOG_RETENTION_DAYS', '7'))  # 错误日志
PERFORMANCE_METRIC_RETENTION_DAYS = int(os.environ.get('PERFORMANCE_METRIC_RETENTION_DAYS', '30'))  # 性能指标

# 数据库清理间隔（小时）
CLEANUP_INTERVAL_HOURS = int(os.environ.get('CLEANUP_INTERVAL_HOURS', '24'))

# =============================================================================
# 日志配置
# =============================================================================

# 日志文件目录
LOG_DIR = os.environ.get('LOG_DIR', 'logs')

# 日志文件最大大小（MB）
LOG_MAX_SIZE_MB = int(os.environ.get('LOG_MAX_SIZE_MB', '10'))

# 日志文件备份数量
LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))

# 控制台日志级别
CONSOLE_LOG_LEVEL = os.environ.get('CONSOLE_LOG_LEVEL', 'INFO')

# 文件日志级别
FILE_LOG_LEVEL = os.environ.get('FILE_LOG_LEVEL', 'DEBUG')

# 是否启用JSON格式日志
JSON_LOG_ENABLED = os.environ.get('JSON_LOG_ENABLED', 'true').lower() == 'true'

# =============================================================================
# WebSocket配置
# =============================================================================

# 是否启用WebSocket
WEBSOCKET_ENABLED = os.environ.get('WEBSOCKET_ENABLED', 'true').lower() == 'true'

# WebSocket连接数限制
WEBSOCKET_MAX_CONNECTIONS = int(os.environ.get('WEBSOCKET_MAX_CONNECTIONS', '5'))

# WebSocket重连间隔（秒）
WEBSOCKET_RECONNECT_INTERVAL = int(os.environ.get('WEBSOCKET_RECONNECT_INTERVAL', '60'))

# WebSocket数据超时时间（秒）
WEBSOCKET_DATA_TIMEOUT = int(os.environ.get('WEBSOCKET_DATA_TIMEOUT', '5'))

# =============================================================================
# 性能配置
# =============================================================================

# 是否启用批量API请求
BATCH_API_ENABLED = os.environ.get('BATCH_API_ENABLED', 'true').lower() == 'true'

# 批量请求大小
BATCH_REQUEST_SIZE = int(os.environ.get('BATCH_REQUEST_SIZE', '100'))

# 请求重试次数
API_RETRY_COUNT = int(os.environ.get('API_RETRY_COUNT', '3'))

# 请求重试间隔（秒）
API_RETRY_DELAY = int(os.environ.get('API_RETRY_DELAY', '1'))

# API请求超时时间（秒）
API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '10'))

# =============================================================================
# 警报配置
# =============================================================================

# 警报级别配置
ALERT_LEVEL_LOW_THRESHOLD = float(os.environ.get('ALERT_LEVEL_LOW_THRESHOLD', '0.08'))      # 8%
ALERT_LEVEL_MEDIUM_THRESHOLD = float(os.environ.get('ALERT_LEVEL_MEDIUM_THRESHOLD', '0.10'))  # 10%
ALERT_LEVEL_HIGH_THRESHOLD = float(os.environ.get('ALERT_LEVEL_HIGH_THRESHOLD', '0.12'))     # 12%
ALERT_LEVEL_CRITICAL_THRESHOLD = float(os.environ.get('ALERT_LEVEL_CRITICAL_THRESHOLD', '0.15')) # 15%

# 是否启用警报分级
ALERT_LEVEL_ENABLED = os.environ.get('ALERT_LEVEL_ENABLED', 'true').lower() == 'true'

# 是否启用警报声音
ALERT_SOUND_ENABLED = os.environ.get('ALERT_SOUND_ENABLED', 'false').lower() == 'true'

# =============================================================================
# 路径配置
# =============================================================================

# 数据目录
DATA_DIR = os.environ.get('DATA_DIR', 'data')

# 配置文件目录
CONFIG_DIR = os.environ.get('CONFIG_DIR', 'config')

# 临时文件目录
TEMP_DIR = os.environ.get('TEMP_DIR', 'temp')

# 备份目录
BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backup')

# =============================================================================
# 安全配置
# =============================================================================

# API密钥（如果需要）
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY', '')

# 是否启用API认证
API_AUTH_ENABLED = os.environ.get('API_AUTH_ENABLED', 'false').lower() == 'true'

# 请求速率限制（每秒）
RATE_LIMIT_PER_SECOND = int(os.environ.get('RATE_LIMIT_PER_SECOND', '20'))

# =============================================================================
# 监控指标配置
# =============================================================================

# 是否记录性能指标
PERFORMANCE_METRICS_ENABLED = os.environ.get('PERFORMANCE_METRICS_ENABLED', 'true').lower() == 'true'

# 性能指标记录间隔（秒）
PERFORMANCE_METRICS_INTERVAL = int(os.environ.get('PERFORMANCE_METRICS_INTERVAL', '300'))  # 5分钟

# 是否启用内存监控
MEMORY_MONITOR_ENABLED = os.environ.get('MEMORY_MONITOR_ENABLED', 'true').lower() == 'true'

# 内存使用警告阈值（MB）
MEMORY_WARNING_THRESHOLD_MB = int(os.environ.get('MEMORY_WARNING_THRESHOLD_MB', '500'))

# =============================================================================
# 系统配置
# =============================================================================

# 系统启动时是否进行环境检查
ENVIRONMENT_CHECK_ENABLED = os.environ.get('ENVIRONMENT_CHECK_ENABLED', 'true').lower() == 'true'

# 是否启用自动重启
AUTO_RESTART_ENABLED = os.environ.get('AUTO_RESTART_ENABLED', 'false').lower() == 'true'

# 自动重启间隔（分钟）
AUTO_RESTART_INTERVAL_MINUTES = int(os.environ.get('AUTO_RESTART_INTERVAL_MINUTES', '1440'))  # 24小时

# 最大运行时间（小时）
MAX_RUNTIME_HOURS = int(os.environ.get('MAX_RUNTIME_HOURS', '0'))  # 0表示无限制

# =============================================================================
# 网络配置
# =============================================================================

# 代理配置
HTTP_PROXY = os.environ.get('HTTP_PROXY', '')
HTTPS_PROXY = os.environ.get('HTTPS_PROXY', '')

# 是否启用代理
PROXY_ENABLED = os.environ.get('PROXY_ENABLED', 'false').lower() == 'true'

# 网络连接超时时间（秒）
NETWORK_TIMEOUT = int(os.environ.get('NETWORK_TIMEOUT', '30'))

# 网络重试次数
NETWORK_RETRY_COUNT = int(os.environ.get('NETWORK_RETRY_COUNT', '3'))

# =============================================================================
# 配置验证函数
# =============================================================================

def validate_config():
    """验证配置参数的有效性"""
    errors = []

    # 验证阈值参数
    if not (0.01 <= OI_CHANGE_THRESHOLD <= 1.0):
        errors.append("OI_CHANGE_THRESHOLD 必须在 0.01 到 1.0 之间")

    if not (0.01 <= PRICE_CHANGE_THRESHOLD <= 1.0):
        errors.append("PRICE_CHANGE_THRESHOLD 必须在 0.01 到 1.0 之间")

    # 验证时间参数
    if MONITOR_INTERVAL_MINUTES < 1:
        errors.append("MONITOR_INTERVAL_MINUTES 必须大于 0")

    if ALERT_COOLDOWN_SECONDS < 60:
        errors.append("ALERT_COOLDOWN_SECONDS 必须大于等于 60")

    # 验证API限制
    if MAX_REQUESTS_PER_MINUTE < 60:
        errors.append("MAX_REQUESTS_PER_MINUTE 必须大于等于 60")

    # 验证数据库配置
    if DATABASE_MAX_CONNECTIONS < 1:
        errors.append("DATABASE_MAX_CONNECTIONS 必须大于 0")

    if DATABASE_TIMEOUT < 5:
        errors.append("DATABASE_TIMEOUT 必须大于等于 5")

    # 验证日志配置
    if LOG_MAX_SIZE_MB < 1:
        errors.append("LOG_MAX_SIZE_MB 必须大于等于 1")

    if LOG_BACKUP_COUNT < 0:
        errors.append("LOG_BACKUP_COUNT 必须大于等于 0")

    # 验证警报级别阈值
    thresholds = [
        ALERT_LEVEL_LOW_THRESHOLD,
        ALERT_LEVEL_MEDIUM_THRESHOLD,
        ALERT_LEVEL_HIGH_THRESHOLD,
        ALERT_LEVEL_CRITICAL_THRESHOLD
    ]

    if not all(0.01 <= t <= 1.0 for t in thresholds):
        errors.append("所有警报级别阈值必须在 0.01 到 1.0 之间")

    if not thresholds == sorted(thresholds):
        errors.append("警报级别阈值必须按升序排列")

    # 验证网络配置
    if NETWORK_TIMEOUT < 5:
        errors.append("NETWORK_TIMEOUT 必须大于等于 5")

    if NETWORK_RETRY_COUNT < 0:
        errors.append("NETWORK_RETRY_COUNT 必须大于等于 0")

    # 验证路径
    required_dirs = [LOG_DIR, DATA_DIR, CONFIG_DIR, TEMP_DIR, BACKUP_DIR]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建目录 {dir_path}: {e}")

    return errors

def get_config_summary():
    """获取配置摘要信息"""
    return {
        'monitor_mode': MONITOR_MODE,
        'debug_mode': DEBUG_MODE,
        'telegram_enabled': TELEGRAM_ENABLED,
        'oi_change_threshold': OI_CHANGE_THRESHOLD,
        'price_change_threshold': PRICE_CHANGE_THRESHOLD,
        'monitor_interval_minutes': MONITOR_INTERVAL_MINUTES,
        'database_path': DATABASE_PATH,
        'log_dir': LOG_DIR,
        'websocket_enabled': WEBSOCKET_ENABLED,
        'batch_api_enabled': BATCH_API_ENABLED,
        'performance_metrics_enabled': PERFORMANCE_METRICS_ENABLED,
        'alert_level_enabled': ALERT_LEVEL_ENABLED
    }

def print_config_summary():
    """打印配置摘要"""
    print("=" * 50)
    print("📊 配置摘要")
    print("=" * 50)

    summary = get_config_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("=" * 50)

# =============================================================================
# 环境配置检查
# =============================================================================

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")

    # 检查Telegram配置
    if TELEGRAM_ENABLED:
        print("✅ Telegram推送: 已配置")
    else:
        print("⚠️  Telegram推送: 未配置")
        print("   设置环境变量: TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")

    # 检查数据库文件
    if os.path.exists(DATABASE_PATH):
        try:
            file_size = os.path.getsize(DATABASE_PATH) / (1024 * 1024)  # MB
            print(f"✅ 数据库文件: {DATABASE_PATH} ({file_size:.2f} MB)")
        except Exception as e:
            print(f"❌ 数据库文件检查失败: {e}")
    else:
        print(f"✅ 数据库文件: {DATABASE_PATH} (将自动创建)")

    # 检查日志目录
    if os.path.exists(LOG_DIR):
        print(f"✅ 日志目录: {LOG_DIR}")
    else:
        print(f"⚠️  日志目录: {LOG_DIR} (将自动创建)")

    # 检查数据目录
    if os.path.exists(DATA_DIR):
        print(f"✅ 数据目录: {DATA_DIR}")
    else:
        print(f"⚠️  数据目录: {DATA_DIR} (将自动创建)")

    # 检查网络连接
    import requests
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/ping", timeout=10)
        if response.status_code == 200:
            print("✅ Binance API连接: 正常")
        else:
            print(f"⚠️  Binance API连接: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Binance API连接失败: {e}")

    print("")

# =============================================================================
# 自动配置修复
# =============================================================================

def fix_configuration():
    """自动修复配置问题"""
    print("🔧 自动修复配置...")

    # 创建必要的目录
    required_dirs = [LOG_DIR, DATA_DIR, CONFIG_DIR, TEMP_DIR, BACKUP_DIR]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ 创建目录: {dir_path}")
            except Exception as e:
                print(f"❌ 创建目录失败 {dir_path}: {e}")

    print("✅ 配置修复完成")

# =============================================================================
# 主函数
# =============================================================================

if __name__ == "__main__":
    print("⚙️  增强版Binance监控系统配置")
    print("=" * 50)

    # 验证配置
    errors = validate_config()
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"   - {error}")
        print("\n🔧 尝试自动修复...")
        fix_configuration()
        errors = validate_config()
        if errors:
            print("❌ 自动修复失败，请手动修正配置")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)

    # 检查环境
    check_environment()

    # 打印配置摘要
    print_config_summary()

    print("✅ 配置检查完成")