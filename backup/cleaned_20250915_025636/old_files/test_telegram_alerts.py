#!/usr/bin/env python3
"""
测试Telegram警报功能
"""

import os
import sys
sys.path.append('/Users/vadar/Cursor file/trading bot')

# 设置测试环境
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_456'

from enhanced_monitor import EnhancedBinanceMonitor
from datetime import datetime

def test_telegram_alerts():
    """测试Telegram警报功能"""

    print('=== 测试Telegram警报功能 ===')

    # 创建监控器实例
    monitor = EnhancedBinanceMonitor()

    print(f'Telegram配置状态: {monitor.config.telegram_enabled}')

    # 模拟警报数据
    test_alert_data = {
        'symbol': 'BTCUSDT',
        'oi_change_percent': 15.5,
        'price_change_percent': 8.2,
        'current_oi': 91000.0,
        'old_oi': 78900.0,
        'current_price': 115500.0,
        'old_price': 106700.0,
        'total_value_usdt': 10510500000.0,
        'alert_level': 'high',
        'timestamp': datetime.now().isoformat()
    }

    print('\n警报数据:')
    print(f'交易对: {test_alert_data["symbol"]}')
    print(f'OI变化: {test_alert_data["oi_change_percent"]:.2f}%')
    print(f'价格变化: {test_alert_data["price_change_percent"]:.2f}%')
    print(f'当前持仓量: {test_alert_data["current_oi"]:,.0f}')
    print(f'当前价格: ${test_alert_data["current_price"]:,.2f}')

    # 测试消息格式化（不实际发送）
    print('\n=== 测试消息格式化 ===')

    # 模拟Telegram消息格式
    symbol = test_alert_data['symbol']
    oi_change = test_alert_data['oi_change_percent']
    price_change = test_alert_data['price_change_percent']
    alert_level = 'HIGH'
    emoji = '🚨'

    message = f"""{emoji} <b>Binance永续合约异常警报</b>

📊 <b>交易对:</b> {symbol}

📈 <b>持仓量变化:</b> {oi_change:.2f}%
💰 <b>当前持仓量:</b> {test_alert_data['current_oi']:,.0f}
📊 <b>15分钟前持仓量:</b> {test_alert_data['old_oi']:,.0f}

💹 <b>价格变化:</b> {price_change:.2f}%
💰 <b>当前价格:</b> ${test_alert_data['current_price']:.6f}
📊 <b>15分钟前价格:</b> ${test_alert_data['old_price']:.6f}

💎 <b>当前持仓总价值:</b> {test_alert_data['total_value_usdt']:,.2f} USDT

⏰ <b>检测时间:</b> {test_alert_data['timestamp']}

⚠️  请注意风险控制！"""

    print("Telegram消息格式预览:")
    print(message)
    print("\n✅ 消息格式化测试完成！")

    return True

def check_real_alerts():
    """检查真实警报情况"""

    from database_manager import DatabaseManager

    print('\n=== 检查真实警报情况 ===')

    db = DatabaseManager('data/binance_monitor.db')
    recent_alerts = db.get_recent_alerts(hours=1)  # 最近1小时

    if recent_alerts:
        print(f"最近1小时有 {len(recent_alerts)} 个警报")

        # 显示警报级别分布
        alert_levels = {}
        for alert in recent_alerts:
            level = 'HIGH' if abs(alert['oi_change_percent']) >= 12 or abs(alert['price_change_percent']) >= 4 else 'MEDIUM'
            alert_levels[level] = alert_levels.get(level, 0) + 1

        print("警报级别分布:")
        for level, count in alert_levels.items():
            print(f"  {level}: {count}个")

        # 显示最严重的警报
        worst_alert = max(recent_alerts, key=lambda x: abs(x['oi_change_percent']) + abs(x['price_change_percent']))
        print(f"\n最严重的警报:")
        print(f"  交易对: {worst_alert['symbol']}")
        print(f"  OI变化: {worst_alert['oi_change_percent']:.2f}%")
        print(f"  价格变化: {worst_alert['price_change_percent']:.2f}%")

    else:
        print("最近1小时无警报")

if __name__ == "__main__":
    test_telegram_alerts()
    print()
    check_real_alerts()