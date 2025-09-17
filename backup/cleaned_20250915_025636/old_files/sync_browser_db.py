#!/usr/bin/env python3
"""
定期同步浏览器兼容数据库
"""

import sqlite3
import os
import time
import shutil
from datetime import datetime

def sync_browser_database():
    """同步浏览器兼容数据库"""

    source_db = 'data/binance_monitor.db'
    target_db = 'data/binance_monitor_browser.db'
    temp_db = 'data/binance_monitor_browser_temp.db'

    try:
        # 创建临时数据库
        if os.path.exists(temp_db):
            os.remove(temp_db)

        # 复制并转换数据库
        shutil.copy2(source_db, temp_db)

        # 连接到临时数据库并设置传统模式
        temp_conn = sqlite3.connect(temp_db)
        temp_conn.execute('PRAGMA journal_mode=DELETE')
        temp_conn.commit()
        temp_conn.close()

        # 删除WAL文件
        for ext in ['-wal', '-shm']:
            wal_file = temp_db + ext
            if os.path.exists(wal_file):
                os.remove(wal_file)

        # 原子替换目标数据库
        if os.path.exists(target_db):
            os.remove(target_db)
        os.rename(temp_db, target_db)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据库同步完成")
        return True

    except Exception as e:
        print(f"同步失败: {e}")
        # 清理临时文件
        if os.path.exists(temp_db):
            os.remove(temp_db)
        return False

def main():
    """主函数"""
    print("浏览器数据库同步工具")
    print("按 Ctrl+C 停止同步")

    try:
        while True:
            sync_browser_database()
            # 每30秒同步一次
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n同步已停止")

if __name__ == "__main__":
    main()