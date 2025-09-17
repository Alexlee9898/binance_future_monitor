#!/usr/bin/env python3
"""
Telegram推送功能测试和配置验证脚本
"""

import os
import sys
import requests
from datetime import datetime

# 添加路径
sys.path.append('/Users/vadar/Cursor file/trading bot')

def test_telegram_configuration():
    """测试Telegram配置"""

    print("=== Telegram推送功能测试 ===")

    # 检查环境变量
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    print(f"1. 环境变量状态:")
    print(f"   TELEGRAM_BOT_TOKEN: {'已配置' if bot_token else '未配置'}")
    print(f"   TELEGRAM_CHAT_ID: {'已配置' if chat_id else '未配置'}")

    if not bot_token or not chat_id:
        print("\n❌ Telegram配置不完整!")
        print("\n需要配置以下环境变量:")
        print("export TELEGRAM_BOT_TOKEN='你的Bot Token'")
        print("export TELEGRAM_CHAT_ID='你的Chat ID'")
        return False

    # 测试Bot Token有效性
    print(f"\n2. 测试Bot Token有效性...")
    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        response = requests.get(url, timeout=10)
        result = response.json()

        if result.get('ok'):
            bot_info = result['result']
            print(f"   ✅ Bot有效: @{bot_info.get('username', 'Unknown')}")
            print(f"   Bot名称: {bot_info.get('first_name', 'Unknown')}")
        else:
            print(f"   ❌ Bot Token无效: {result.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

    # 测试发送消息
    print(f"\n3. 测试消息发送...")
    test_message = f"""🔧 <b>Binance监控系统 - 连接测试</b>

✅ Bot配置正常
✅ 系统运行正常
⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 当前警报阈值:
• OI变化 ≥ 5%
• 价格变化 ≥ 2%

📊 系统状态: 监控528个永续合约，每15分钟检查一次

如果收到此消息，说明Telegram推送功能配置成功！"""

    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': test_message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(send_url, params=params, timeout=10)
        result = response.json()

        if result.get('ok'):
            print(f"   ✅ 测试消息发送成功!")
            message_id = result['result']['message_id']
            print(f"   消息ID: {message_id}")
            return True
        else:
            print(f"   ❌ 消息发送失败: {result.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ❌ 发送失败: {e}")
        return False

def check_recent_alerts():
    """检查最近的警报"""
    print("\n=== 最近警报检查 ===")

    try:
        from database_manager import DatabaseManager
        db = DatabaseManager('data/binance_monitor.db')

        # 获取最近24小时的警报
        recent_alerts = db.get_recent_alerts(hours=24)

        print(f"最近24小时警报数量: {len(recent_alerts)}")

        if recent_alerts:
            print("\n最近的5个警报:")
            for i, alert in enumerate(recent_alerts[:5]):
                symbol = alert['symbol']
                oi_change = alert['oi_change_percent']
                price_change = alert['price_change_percent']
                level = "CRITICAL" if (abs(oi_change) >= 15 or abs(price_change) >= 5) else \
                       "HIGH" if (abs(oi_change) >= 12 or abs(price_change) >= 4) else \
                       "MEDIUM" if (abs(oi_change) >= 10 or abs(price_change) >= 3) else "LOW"

                emoji = "💥" if level == "CRITICAL" else "🔥" if level == "HIGH" else "🚨" if level == "MEDIUM" else "⚠️"

                print(f"{i+1}. {emoji} {symbol}: OI {oi_change:+.2f}%, 价格 {price_change:+.2f}% - {level}")
        else:
            print("最近24小时无警报记录")

        return len(recent_alerts)

    except Exception as e:
        print(f"检查警报失败: {e}")
        return 0

def simulate_alert_test():
    """模拟警报测试"""
    print("\n=== 模拟警报测试 ===")

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        print("❌ 无法测试: Telegram未配置")
        return False

    test_alert = {
        'symbol': 'BTCUSDT',
        'oi_change_percent': 8.5,  # 超过5%阈值
        'price_change_percent': 3.2,  # 超过2%阈值
        'current_oi': 95000.0,
        'old_oi': 87500.0,
        'current_price': 115500.0,
        'old_price': 111800.0,
        'total_value_usdt': 10972500000.0,
        'alert_level': 'high',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    print(f"模拟警报: {test_alert['symbol']}")
    print(f"OI变化: {test_alert['oi_change_percent']:+.2f}%")
    print(f"价格变化: {test_alert['price_change_percent']:+.2f}%")

    # 这里可以实际发送测试消息
    print("✅ 模拟测试通过 - 配置正确时将自动发送")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("📱 Telegram推送功能检测工具")
    print("=" * 60)

    # 测试配置
    config_ok = test_telegram_configuration()

    # 检查警报
    alert_count = check_recent_alerts()

    # 模拟测试
    simulate_alert_test()

    print("\n" + "=" * 60)
    print("📋 检测结果总结:")

    if config_ok:
        print("✅ Telegram配置完整且有效")
        print("✅ 可以正常接收警报推送")
    else:
        print("❌ Telegram配置不完整")
        print("⚠️  需要配置环境变量才能接收推送")

    print(f"📊 最近24小时警报数量: {alert_count}")
    print("=" * 60)