#!/usr/bin/env python3
"""
创建兼容DB Browser的数据库文件
将现有WAL模式数据库转换为传统模式
"""

import sqlite3
import os
import sys
from datetime import datetime

def create_compatible_database():
    """创建兼容DB Browser的数据库"""
    try:
        print("🔄 开始创建兼容DB Browser的数据库...")

        # 源数据库路径
        source_db = "data/binance_monitor.db"
        target_db = "data/binance_monitor_browser_compatible.db"

        # 确保目标目录存在
        os.makedirs("data", exist_ok=True)

        # 连接到源数据库
        print(f"📖 读取源数据库: {source_db}")
        source_conn = sqlite3.connect(source_db)
        source_conn.execute("PRAGMA journal_mode=DELETE;")  # 确保使用传统模式
        source_cursor = source_conn.cursor()

        # 连接到目标数据库
        print(f"📝 创建目标数据库: {target_db}")
        target_conn = sqlite3.connect(target_db)
        target_conn.execute("PRAGMA journal_mode=DELETE;")  # 使用传统模式
        target_cursor = target_conn.cursor()

        # 获取所有表的结构
        source_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = source_cursor.fetchall()

        print(f"📊 发现 {len(tables)} 个表需要复制")

        for table_name, create_sql in tables:
            print(f"🔄 复制表: {table_name}")

            # 在目标数据库中创建表
            target_cursor.execute(create_sql)

            # 获取表数据
            source_cursor.execute(f"SELECT * FROM {table_name};")
            rows = source_cursor.fetchall()

            if rows:
                # 获取列信息
                source_cursor.execute(f"PRAGMA table_info({table_name});")
                columns = source_cursor.fetchall()
                column_names = [col[1] for col in columns]

                # 构建插入语句
                placeholders = ', '.join(['?' for _ in column_names])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders});"

                # 批量插入数据
                target_cursor.executemany(insert_sql, rows)
                print(f"   ✅ 复制了 {len(rows)} 条记录")
            else:
                print(f"   ℹ️  表 {table_name} 为空")

        # 复制索引
        print("🔍 复制索引...")
        source_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = source_cursor.fetchall()

        for index_name, create_sql in indexes:
            if create_sql:  # 某些索引可能没有SQL
                try:
                    target_cursor.execute(create_sql)
                    print(f"   ✅ 创建索引: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  索引 {index_name} 创建失败: {e}")

        # 提交事务
        target_conn.commit()

        # 获取统计信息
        target_cursor.execute("SELECT COUNT(*) FROM oi_history;")
        oi_count = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM alerts;")
        alert_count = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM performance_metrics;")
        metric_count = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM error_logs;")
        error_count = target_cursor.fetchone()[0]

        # 关闭连接
        source_conn.close()
        target_conn.close()

        # 验证数据库
        print("\n🔍 验证目标数据库...")
        test_conn = sqlite3.connect(target_db)
        test_conn.execute("PRAGMA journal_mode=DELETE;")  # 确保使用传统模式
        test_cursor = test_conn.cursor()

        test_cursor.execute("PRAGMA journal_mode;")
        journal_mode = test_cursor.fetchone()[0]
        print(f"   日志模式: {journal_mode}")

        test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = test_cursor.fetchall()
        print(f"   表数量: {len(tables)}")

        test_conn.close()

        # 获取文件大小
        import os
        target_size = os.path.getsize(target_db)
        source_size = os.path.getsize(source_db)

        print(f"\n📊 复制完成统计:")
        print(f"   持仓量历史记录: {oi_count:,}")
        print(f"   警报记录: {alert_count:,}")
        print(f"   性能指标: {metric_count:,}")
        print(f"   错误日志: {error_count:,}")
        print(f"   源数据库大小: {source_size:,} 字节")
        print(f"   目标数据库大小: {target_size:,} 字节")
        print(f"   目标数据库路径: {target_db}")

        print(f"\n✅ 兼容数据库创建完成！")
        print(f"📝 您现在可以在DB Browser中打开: {target_db}")

        return True

    except Exception as e:
        print(f"❌ 创建兼容数据库失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始创建DB Browser兼容的数据库...")
    success = create_compatible_database()

    if success:
        print("\n🎉 兼容数据库创建成功！")
    else:
        print("\n❌ 兼容数据库创建失败")