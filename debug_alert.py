#!/usr/bin/env python3
"""
调试警报逻辑 - 检查为什么满足条件的警报没有被触发
"""

import sqlite3
import os
from datetime import datetime
import json

def check_athusdt_data():
    """检查ATHUSDT的数据情况"""
    db_path = "binance_monitor.db"

    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== ATHUSDT 数据分析 ===")

    # 检查最新的数据
    cursor.execute("""
        SELECT symbol, timestamp, open_interest, price, value_usdt
        FROM oi_history
        WHERE symbol = 'ATHUSDT'
        ORDER BY timestamp DESC
        LIMIT 5
    """)

    recent_data = cursor.fetchall()
    print(f"\n最新数据记录 ({len(recent_data)} 条):")
    for row in recent_data:
        print(f"时间: {row['timestamp']}")
        print(f"持仓量: {row['open_interest']:,.0f}")
        print(f"价格: {row['price']}")
        print(f"价值: {row['value_usdt']:,.2f}")
        print("---")

    # 检查15分钟前的数据
    if recent_data:
        current_time = recent_data[0]['timestamp']
        cursor.execute("""
            SELECT symbol, timestamp, open_interest, price, value_usdt
            FROM oi_history
            WHERE symbol = 'ATHUSDT'
            AND timestamp < ?
            ORDER BY timestamp DESC
            LIMIT 5
        """, (current_time,))

        historical_data = cursor.fetchall()
        print(f"\n历史数据记录 ({len(historical_data)} 条):")
        for row in historical_data:
            print(f"时间: {row['timestamp']}")
            print(f"持仓量: {row['open_interest']:,.0f}")
            print(f"价格: {row['price']}")
            print("---")

        # 手动计算变化率
        if historical_data:
            current = recent_data[0]
            historical = historical_data[0]

            oi_change_rate = (current['open_interest'] - historical['open_interest']) / historical['open_interest']
            price_change_rate = (current['price'] - historical['price']) / historical['price']

            print(f"\n手动计算变化率:")
            print(f"持仓量变化率: {oi_change_rate:.4f} ({oi_change_rate*100:.2f}%)")
            print(f"价格变化率: {price_change_rate:.4f} ({price_change_rate*100:.2f}%)")

            # 检查是否满足警报条件
            oi_threshold = 0.05  # 5%
            price_threshold = 0.02  # 2%

            oi_change_percent = abs(oi_change_rate * 100)
            price_change_percent = abs(price_change_rate * 100)

            print(f"\n警报条件检查:")
            print(f"持仓量变化: {oi_change_percent:.2f}% >= {oi_threshold*100}%: {oi_change_percent >= oi_threshold*100}")
            print(f"价格变化: {price_change_percent:.2f}% >= {price_threshold*100}%: {price_change_percent >= price_threshold*100}")
            print(f"是否应触发警报: {oi_change_percent >= oi_threshold*100 and price_change_percent >= price_threshold*100}")

    conn.close()

def check_alert_logs():
    """检查警报日志"""
    db_path = "binance_monitor.db"

    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n=== 警报记录 ===")
    cursor.execute("SELECT COUNT(*) as count FROM alerts")
    alert_count = cursor.fetchone()['count']
    print(f"总警报数量: {alert_count}")

    if alert_count > 0:
        cursor.execute("SELECT * FROM alerts ORDER BY alert_time DESC LIMIT 5")
        alerts = cursor.fetchall()
        print("\n最近警报:")
        for alert in alerts:
            print(f"时间: {alert['alert_time']}")
            print(f"交易对: {alert['symbol']}")
            print(f"持仓量变化: {alert['oi_change_percent']:.2f}%")
            print(f"价格变化: {alert['price_change_percent']:.2f}%")
            print("---")

    conn.close()

if __name__ == "__main__":
    print("开始调试警报逻辑...")
    check_athusdt_data()
    check_alert_logs()
    print("调试完成。")