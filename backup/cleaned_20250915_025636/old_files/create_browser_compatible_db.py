#!/usr/bin/env python3
"""
创建兼容DB Browser的数据库文件
"""

import sqlite3
import os
import sys
from datetime import datetime

def create_browser_compatible_db():
    """创建兼容DB Browser的数据库"""
    try:
        print("🔄 开始创建兼容DB Browser的数据库...")

        # 源数据库路径
        source_db = "data/binance_monitor.db"
        target_db = "data/binance_monitor_browser.db"

        # 确保目标目录存在
        os.makedirs("data", exist_ok=True)

        print(f"📖 读取源数据库: {source_db}")
        print(f"📊 源数据库统计:")

        # 先检查源数据库
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()

        # 获取表统计
        tables = ['oi_history', 'alerts', 'performance_metrics', 'error_logs', 'system_status']
        for table in tables:
            try:
                source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = source_cursor.fetchone()[0]
                print(f"   {table}: {count:,} 条记录")
            except:
                print(f"   {table}: 表不存在或无法访问")

        source_conn.close()

        # 创建新的兼容数据库
        print(f"\n📝 创建兼容数据库: {target_db}")
        target_conn = sqlite3.connect(target_db)
        target_conn.execute("PRAGMA journal_mode=DELETE;")  # 使用传统模式
        target_cursor = target_conn.cursor()

        # 重新连接源数据库
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()

        # 复制oi_history表
        print("🔄 复制 oi_history 表...")
        source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='oi_history';")
        create_sql = source_cursor.fetchone()[0]
        target_cursor.execute(create_sql)

        source_cursor.execute("SELECT * FROM oi_history;")
        rows = source_cursor.fetchall()
        if rows:
            target_cursor.executemany("INSERT INTO oi_history VALUES (?, ?, ?, ?, ?, ?, ?);", rows)
            print(f"   ✅ 复制了 {len(rows):,} 条持仓量历史记录")

        # 复制alerts表
        print("🔄 复制 alerts 表...")
        try:
            source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='alerts';")
            create_sql = source_cursor.fetchone()[0]
            target_cursor.execute(create_sql)

            source_cursor.execute("SELECT * FROM alerts;")
            rows = source_cursor.fetchall()
            if rows:
                placeholders = ', '.join(['?' for _ in range(len(rows[0]))])
                target_cursor.executemany(f"INSERT INTO alerts VALUES ({placeholders});", rows)
                print(f"   ✅ 复制了 {len(rows):,} 条警报记录")
            else:
                print("   ℹ️  alerts 表为空")
        except Exception as e:
            print(f"   ⚠️  alerts 表复制失败: {e}")

        # 复制其他表...
        for table in ['performance_metrics', 'error_logs', 'system_status']:
            try:
                print(f"🔄 复制 {table} 表...")
                source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
                result = source_cursor.fetchone()
                if result:
                    create_sql = result[0]
                    target_cursor.execute(create_sql)

                    source_cursor.execute(f"SELECT * FROM {table};")
                    rows = source_cursor.fetchall()
                    if rows:
                        placeholders = ', '.join(['?' for _ in range(len(rows[0]))])
                        target_cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders});", rows)
                        print(f"   ✅ 复制了 {len(rows):,} 条记录")
                    else:
                        print(f"   ℹ️  {table} 表为空")
            except Exception as e:
                print(f"   ⚠️  {table} 表复制失败: {e}")

        # 复制索引
        print("🔍 复制索引...")
        source_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = source_cursor.fetchall()
        for index_name, create_sql in indexes:
            if create_sql:
                try:
                    target_cursor.execute(create_sql)
                    print(f"   ✅ 创建索引: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  索引 {index_name} 创建失败: {e}")

        # 提交事务
        target_conn.commit()

        # 验证数据库
        print("\n🔍 验证目标数据库...")
        target_cursor.execute("PRAGMA journal_mode;")
        journal_mode = target_cursor.fetchone()[0]
        print(f"   日志模式: {journal_mode}")

        target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = target_cursor.fetchall()
        print(f"   表数量: {len(tables)}")

        # 获取文件大小
        target_conn.close()
        source_conn.close()

        target_size = os.path.getsize(target_db)

        print(f"\n📊 复制完成:")
        print(f"   目标数据库: {target_db}")
        print(f"   文件大小: {target_size:,} 字节 ({target_size/1024/1024:.2f} MB)")
        print(f"   日志模式: 传统模式 (兼容DB Browser)")

        print(f"\n✅ 兼容数据库创建完成！")
        print(f"📝 您现在可以在DB Browser中打开: {target_db}")

        return True

    except Exception as e:
        print(f"❌ 创建兼容数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始创建DB Browser兼容的数据库...")
    success = create_browser_compatible_db()

    if success:
        print("\n🎉 兼容数据库创建成功！")
    else:
        print("\n❌ 兼容数据库创建失败")