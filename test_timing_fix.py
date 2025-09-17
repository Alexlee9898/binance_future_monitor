#!/usr/bin/env python3
"""
测试时机修复 - 验证历史数据不会在警报中被重复包含
"""

import sqlite3
import os
from datetime import datetime, timedelta
import pytz

UTC8 = pytz.timezone('Asia/Shanghai')

def get_utc8_time():
    return datetime.now(UTC8)

def test_timing_fix():
    """测试时机修复逻辑"""
    db_path = "binance_monitor.db"

    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 清理现有数据
    cursor.execute("DELETE FROM oi_history WHERE symbol = 'TESTUSDT'")
    conn.commit()

    print("=== 测试时机修复 ===")

    # 模拟15分钟前的数据
    old_time = get_utc8_time() - timedelta(minutes=15)
    old_oi = 1000000
    old_price = 1.0

    # 插入历史数据
    cursor.execute("""
        INSERT INTO oi_history (symbol, timestamp, open_interest, price, value_usdt)
        VALUES (?, ?, ?, ?, ?)
    """, ('TESTUSDT', old_time.isoformat(), old_oi, old_price, old_oi * old_price))

    conn.commit()
    print(f"插入历史数据: {old_time} - OI: {old_oi}, Price: {old_price}")

    # 模拟当前数据（显著变化）
    current_time = get_utc8_time()
    current_oi = 1500000  # 50% 增长
    current_price = 1.15  # 15% 增长

    print(f"当前数据: {current_time} - OI: {current_oi}, Price: {current_price}")

    # 获取历史数据（模拟我们的修复逻辑）
    # 使用当前时间计算截止时间，但向前调整2秒以解决微秒精度问题
    cutoff_time = (get_utc8_time() - timedelta(minutes=15) - timedelta(seconds=2)).isoformat()
    print(f"查询截止时间: {cutoff_time}")
    print(f"历史数据时间: {old_time.isoformat()}")
    print(f"时间差: {(get_utc8_time() - old_time).total_seconds()} 秒")

    cursor.execute("""
        SELECT timestamp, open_interest, price, value_usdt
        FROM oi_history
        WHERE symbol = 'TESTUSDT'
        ORDER BY timestamp ASC
    """)

    all_data = cursor.fetchall()
    print(f"所有数据: {len(all_data)} 条")
    for row in all_data:
        print(f"  {row['timestamp']} - OI: {row['open_interest']}, Price: {row['price']}")

    cursor.execute("""
        SELECT timestamp, open_interest, price, value_usdt
        FROM oi_history
        WHERE symbol = 'TESTUSDT'
        AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (cutoff_time,))

    print(f"SQL查询: timestamp >= '{cutoff_time}'")
    print(f"比较: '{all_data[0]['timestamp']}' >= '{cutoff_time}' = {all_data[0]['timestamp'] >= cutoff_time}")

    historical_data = cursor.fetchall()
    print(f"\n获取到的历史数据: {len(historical_data)} 条")

    if historical_data:
        oldest_data = historical_data[0]
        print(f"最老的历史数据: {oldest_data['timestamp']}")
        print(f"历史持仓量: {oldest_data['open_interest']}")
        print(f"历史价格: {oldest_data['price']}")

        # 计算变化率
        oi_change_rate = (current_oi - oldest_data['open_interest']) / oldest_data['open_interest']
        price_change_rate = (current_price - oldest_data['price']) / oldest_data['price']

        print(f"\n计算的变化率:")
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

        # 现在保存当前数据（模拟我们的修复逻辑）
        cursor.execute("""
            INSERT INTO oi_history (symbol, timestamp, open_interest, price, value_usdt, price_change, oi_change)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('TESTUSDT', current_time.isoformat(), current_oi, current_price, current_oi * current_price, price_change_rate, oi_change_rate))

        conn.commit()
        print(f"\n✓ 已保存当前数据到数据库")

        # 再次获取历史数据，验证我们的修复
        cursor.execute("""
            SELECT timestamp, open_interest, price, value_usdt
            FROM oi_history
            WHERE symbol = 'TESTUSDT'
            AND timestamp >= ?
            ORDER BY timestamp ASC
        """, ((get_utc8_time() - timedelta(minutes=15)).isoformat(),))

        updated_historical_data = cursor.fetchall()
        print(f"\n保存当前数据后，再次获取历史数据: {len(updated_historical_data)} 条")

        if updated_historical_data:
            oldest_after_save = updated_historical_data[0]
            print(f"最老的历史数据: {oldest_after_save['timestamp']}")
            print(f"历史持仓量: {oldest_after_save['open_interest']}")
            print(f"历史价格: {oldest_after_save['price']}")

            # 验证历史数据没有被当前数据污染
            if oldest_after_save['timestamp'] == old_time.isoformat():
                print("\n✓ 修复成功！历史数据没有被当前数据污染")
                print("✓ 最老的历史数据仍然是之前保存的旧数据")
            else:
                print("\n✗ 修复失败！历史数据被当前数据污染")

    else:
        print("没有历史数据可用")

    conn.close()

if __name__ == "__main__":
    test_timing_fix()