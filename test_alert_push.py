#!/usr/bin/env python3
"""
测试警报推送到Telegram的功能
"""
import sys
sys.path.append('/Users/vadar/Cursor file/trading bot')
import sqlite3
from datetime import datetime
import requests
from config import Config

def test_latest_alert_push():
    """测试最新警报的Telegram推送"""

    # 获取Telegram配置
    bot_token, chat_id = Config.get_telegram_config()

    if not bot_token or not chat_id:
        print('⚠️ Telegram配置未设置')
        config_info = Config.get_config_info()
        print(f'   Bot Token: {"已设置" if config_info["bot_token_set"] else "未设置"}')
        print(f'   Chat ID: {"已设置" if config_info["chat_id_set"] else "未设置"}')
        print()
        print('请使用以下命令之一进行配置：')
        print('1. 运行: python3 setup_telegram.py')
        print('2. 设置环境变量：')
        print('   export TELEGRAM_BOT_TOKEN="你的_bot_token"')
        print('   export TELEGRAM_CHAT_ID="你的_chat_id"')
        return False

    # 检查最新的警报并发送推送测试
    conn = sqlite3.connect('/Users/vadar/Cursor file/trading bot/data/binance_monitor.db')
    cursor = conn.cursor()

    # 获取最近的一条警报
    cursor.execute('SELECT * FROM alerts ORDER BY alert_time DESC LIMIT 1')
    latest_alert = cursor.fetchone()
    conn.close()

    if latest_alert:
        # 构建警报消息
        alert_time = datetime.fromisoformat(latest_alert[9])
        message = f"""🚨 交易警报推送测试

📈 交易对：{latest_alert[1]}
📊 OI变化：{latest_alert[2]:+.2f}%
💰 价格变化：{latest_alert[3]:+.2f}%
📋 当前OI：{latest_alert[4]:,.0f}
📋 之前OI：{latest_alert[5]:,.0f}
💵 当前价格：${latest_alert[6]:.4f}
💵 之前价格：${latest_alert[7]:.4f}
💎 总价值：${latest_alert[8]:,.2f}
⏰ 警报时间：{alert_time.strftime('%Y-%m-%d %H:%M:%S')}

✅ 警报推送系统正常工作！"""

        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            if response.json().get('ok'):
                print(f'✅ 最新警报已推送到Telegram！')
                print(f'📊 交易对：{latest_alert[1]}')
                print(f'📈 OI变化：{latest_alert[2]:+.2f}%')
                print(f'💰 价格变化：{latest_alert[3]:+.2f}%')
                return True
            else:
                print(f'❌ 推送失败：{response.json()}')
                return False
        except Exception as e:
            print(f'❌ 推送异常：{e}')
            return False
    else:
        print('⚠️ 数据库中暂无警报记录')
        return False

def test_telegram_directly(bot_token: str = None, chat_id: str = None):
    """直接测试Telegram配置"""
    if not bot_token or not chat_id:
        bot_token, chat_id = Config.get_telegram_config()

    if not bot_token or not chat_id:
        print("❌ Telegram配置不完整")
        return False

    try:
        import requests
        message = "🧪 Telegram配置测试\n\n如果收到此消息，说明配置正确！"
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, params=params, timeout=30)
        if response.json().get('ok'):
            print("✅ Telegram测试消息发送成功！")
            return True
        else:
            print(f"❌ Telegram测试失败：{response.json()}")
            return False
    except Exception as e:
        print(f"❌ Telegram测试异常：{e}")
        return False

if __name__ == '__main__':
    test_latest_alert_push()