#!/usr/bin/env python3
"""
检查变化率计算 - 诊断警报系统
"""

import sqlite3
from datetime import datetime
import os

def check_change_rates():
    """手动计算变化率来诊断系统"""

    conn = sqlite3.connect('/Users/vadar/Cursor file/trading bot/data/binance_monitor.db')
    cursor = conn.cursor()

    # 获取AAVE最近的两条记录
    cursor.execute('''
        SELECT timestamp, open_interest, price
        FROM oi_history
        WHERE symbol = 'AAVEUSDT'
        ORDER BY timestamp DESC
        LIMIT 2
    ''')

    records = cursor.fetchall()

    if len(records) >= 2:
        latest_time, latest_oi, latest_price = records[0]
        previous_time, previous_oi, previous_price = records[1]

        print(f'币种: AAVEUSDT')
        print(f'最新时间: {latest_time}')
        print(f'最新 OI: {latest_oi:,.1f}')
        print(f'最新价格: ${latest_price:.2f}')
        print(f'前次时间: {previous_time}')
        print(f'前次 OI: {previous_oi:,.1f}')
        print(f'前次价格: ${previous_price:.2f}')

        # 计算变化率
        oi_change = ((latest_oi - previous_oi) / previous_oi) * 100
        price_change = ((latest_price - previous_price) / previous_price) * 100

        print(f'\n📊 变化率计算:')
        print(f'OI变化: {oi_change:+.2f}%')
        print(f'价格变化: {price_change:+.2f}%')

        # 检查是否满足警报条件
        oi_threshold = 5.0  # 5%
        price_threshold = 2.0  # 2%

        print(f'\n🎯 警报条件检查:')
        print(f'OI ≥ {oi_threshold}%: {"✅" if abs(oi_change) >= oi_threshold else "❌"}')
        print(f'价格 ≥ {price_threshold}%: {"✅" if abs(price_change) >= price_threshold else "❌"}')
        print(f'满足警报条件: {"✅" if (abs(oi_change) >= oi_threshold and abs(price_change) >= price_threshold) else "❌"}')

        # 检查更多币种
        print(f'\n' + '='*50)
        print("检查更多币种的变化率...")

        cursor.execute('''
            SELECT symbol,
                   (SELECT open_interest FROM oi_history h2 WHERE h2.symbol = h1.symbol ORDER BY timestamp DESC LIMIT 1) as latest_oi,
                   (SELECT open_interest FROM oi_history h3 WHERE h3.symbol = h1.symbol ORDER BY timestamp DESC LIMIT 1 OFFSET 1) as prev_oi,
                   (SELECT price FROM oi_history h4 WHERE h4.symbol = h1.symbol ORDER BY timestamp DESC LIMIT 1) as latest_price,
                   (SELECT price FROM oi_history h5 WHERE h5.symbol = h1.symbol ORDER BY timestamp DESC LIMIT 1 OFFSET 1) as prev_price
            FROM (SELECT DISTINCT symbol FROM oi_history WHERE timestamp > datetime('now', '-2 hours')) h1
            HAVING latest_oi IS NOT NULL AND prev_oi IS NOT NULL AND latest_price IS NOT NULL AND prev_price IS NOT NULL
            LIMIT 10
        ''')

        results = cursor.fetchall()

        found_alerts = 0
        for symbol, latest_oi, prev_oi, latest_price, prev_price in results:
            if latest_oi and prev_oi and latest_price and prev_price:
                oi_change = ((latest_oi - prev_oi) / prev_oi) * 100
                price_change = ((latest_price - prev_price) / prev_price) * 100

                # 检查是否满足警报条件
                if abs(oi_change) >= 5.0 and abs(price_change) >= 2.0:
                    found_alerts += 1
                    print(f'\n🚨 {symbol}:')
                    print(f'  OI变化: {oi_change:+.2f}%')
                    print(f'  价格变化: {price_change:+.2f}%')
                    print(f'  状态: ✅ 满足警报条件')

        if found_alerts == 0:
            print(f'\n📊 在检查的{len(results)}个币种中，没有满足警报条件的')
            print(f'📈 最高OI变化: {max([((r[1] - r[2]) / r[2]) * 100 for r in results if r[1] and r[2]], key=abs):+.2f}%')
            print(f'💹 最高价格变化: {max([((r[3] - r[4]) / r[4]) * 100 for r in results if r[3] and r[4]], key=abs):+.2f}%')
            print(f'\n🎯 当前警报门槛: OI ≥ 5.0% 且 价格 ≥ 2.0%')

    else:
        print('❌ 数据不足，无法计算变化率')

    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Binance监控器 - 变化率诊断工具")
    print("=" * 60)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    check_change_rates()

    print("\n" + "=" * 60)
    print("📋 诊断完成")
    print("=" * 60)