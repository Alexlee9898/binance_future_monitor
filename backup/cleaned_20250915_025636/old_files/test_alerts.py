#!/usr/bin/env python3
"""
测试警报系统
"""

from database_manager import DatabaseManager
from datetime import datetime, timedelta

def check_recent_alerts():
    """检查最近的警报记录"""

    # 获取最近24小时的警报
    db = DatabaseManager('data/binance_monitor.db')
    recent_alerts = db.get_recent_alerts(hours=24)

    print('=== 最近24小时警报记录 ===')
    if recent_alerts:
        for alert in recent_alerts[:10]:  # 显示最近10条
            print(f"时间: {alert['alert_time']}")
            print(f"交易对: {alert['symbol']}")
            print(f"OI变化: {alert['oi_change_percent']:.2f}%")
            print(f"价格变化: {alert['price_change_percent']:.2f}%")
            print(f"当前OI: {alert['current_oi']:,.0f}")
            print(f"当前价格: ${alert['current_price']:.6f}")
            print('---')
    else:
        print('最近24小时无警报记录')

    print(f"\n总警报数: {len(recent_alerts)}")

def check_telegram_config():
    """检查Telegram配置"""
    import os

    print('=== Telegram配置检查 ===')
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    print(f"TELEGRAM_BOT_TOKEN: {'已设置' if token else '未设置'}")
    print(f"TELEGRAM_CHAT_ID: {'已设置' if chat_id else '未设置'}")

    if token and chat_id:
        print("✅ Telegram配置完整")
        return True
    else:
        print("❌ Telegram配置不完整")
        return False

if __name__ == "__main__":
    check_recent_alerts()
    print()
    check_telegram_config()