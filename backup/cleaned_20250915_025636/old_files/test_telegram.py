#!/usr/bin/env python3
"""
Telegram测试推送脚本
发送测试消息到配置的Telegram频道
"""

import requests
import os
from datetime import datetime
import pytz

def send_test_telegram_message():
    """发送测试Telegram消息"""

    # 获取环境变量
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        print("❌ 错误: 未找到Telegram环境变量")
        print("请确保设置了 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        return False

    # 获取当前时间（北京时间）
    utc8 = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(utc8).strftime('%Y-%m-%d %H:%M:%S')

    # 构建测试消息
    message = (
        "🧪 <b>Binance监控器 - 测试推送</b>\n\n"
        "✅ Telegram集成配置成功！\n"
        "📊 系统运行正常\n"
        "🔄 实时监控已启用\n\n"
        f"⏰ 测试时间: {current_time}\n\n"
        "📱 此后将接收实际的市场异常警报"
    )

    # Telegram API URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        print(f"🚀 正在发送测试消息到 Telegram...")
        print(f"📞 Bot Token: {bot_token[:10]}...")
        print(f"💬 Chat ID: {chat_id}")

        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get('ok'):
            print("✅ 测试消息发送成功！")
            print(f"📨 消息ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Telegram API返回错误: {result}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ 发送失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("📱 Telegram 测试推送工具")
    print("=" * 50)

    # 设置环境变量
    os.environ['TELEGRAM_BOT_TOKEN'] = '8253495606:AAE9FI8oxgHH6es1Mgh1Sj3_YGzXsESdqCU'
    os.environ['TELEGRAM_CHAT_ID'] = '-4832541250'
    
    print("🔄 使用配置的Telegram凭证:")
    print(f"Bot Token: {os.environ['TELEGRAM_BOT_TOKEN'][:10]}...")
    print(f"Chat ID: {os.environ['TELEGRAM_CHAT_ID']}")
    
    # 发送测试消息
    print("\n📤 发送测试消息...")
    if send_test_telegram_message():
        print("\n✅ 测试消息发送成功！请检查您的Telegram接收消息。")
    else:
        print("\n❌ 测试消息发送失败")

    print("\n" + "=" * 50)
