#!/usr/bin/env python3
"""
直接通过监控系统发送警报测试
"""

import os
import sys

# 设置Telegram环境变量
os.environ['TELEGRAM_BOT_TOKEN'] = "8253495606:AAE9FI8oxgHH6es1Mgh1Sj3_YGzXsESdqCU"
os.environ['TELEGRAM_CHAT_ID'] = "-4832541250"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_monitor import EnhancedBinanceMonitor, MonitoringConfig
from datetime import datetime

def send_test_alert():
    """发送测试警报"""
    try:
        print("🚀 准备发送测试警报...")

        # 创建监控器配置，启用Telegram
        config = MonitoringConfig(
            oi_change_threshold=0.08,  # 8%
            price_change_threshold=0.02,  # 2%
            telegram_enabled=True,  # 启用Telegram
            max_requests_per_minute=1200
        )

        # 创建监控器实例
        monitor = EnhancedBinanceMonitor(config)

        # 准备测试警报数据
        test_alert_data = {
            'symbol': 'BTCUSDT',
            'oi_change_percent': 15.5,  # 超过阈值
            'price_change_percent': 8.2,  # 超过阈值
            'current_oi': 100000.0,
            'old_oi': 86666.67,
            'current_price': 120000.0,
            'old_price': 110880.0,
            'total_value_usdt': 12000000000.0,
            'alert_level': 'critical',
            'timestamp': datetime.now().isoformat()
        }

        print("📤 发送测试警报到Telegram...")
        success = monitor.send_telegram_notification(test_alert_data)

        if success:
            print("✅ 测试警报发送成功！")
            return True
        else:
            print("❌ 测试警报发送失败")
            return False

    except Exception as e:
        print(f"❌ 发送测试警报时发生错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始发送警报测试...")
    success = send_test_alert()

    if success:
        print("\n🎉 警报测试完成！请检查您的Telegram是否收到测试消息。")
    else:
        print("\n⚠️ 警报测试失败，请检查配置和网络连接。")