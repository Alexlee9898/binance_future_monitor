#!/bin/bash

# 直接创建程序文件的脚本
# 请在服务器上逐行执行

echo "=== 开始创建交易机器人文件 ==="

# 确保在正确的目录
cd ~/trading_bot

# 创建主监控程序（简化版）
cat > enhanced_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
币安持仓监控程序 - 简化版
"""

import requests
import sqlite3
import time
import logging
import signal
import sys
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_binance_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('enhanced_binance_monitor')

class DatabaseManager:
    def __init__(self, db_path="binance_monitor.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoring_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        open_interest REAL NOT NULL,
                        price REAL NOT NULL,
                        value_usdt REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def save_data(self, symbol, open_interest, price, value_usdt):
        """保存监控数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_data (symbol, open_interest, price, value_usdt)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, open_interest, price, value_usdt))
                conn.commit()
        except Exception as e:
            logger.error(f"保存数据失败: {e}")

class BinanceMonitor:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.db = DatabaseManager()

        # 主要交易对
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT",
            "XRPUSDT", "UNIUSDT", "LTCUSDT", "LINKUSDT", "BCHUSDT",
            "XLMUSDT", "DOGEUSDT", "VETUSDT", "FILUSDT", "TRXUSDT"
        ]

    def get_open_interest(self, symbol):
        """获取持仓数据"""
        try:
            url = f"{self.base_url}/fapi/v1/openInterest"
            response = requests.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取{symbol}持仓数据失败: {e}")
            return None

    def get_price(self, symbol):
        """获取价格"""
        try:
            url = f"{self.base_url}/fapi/v1/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取{symbol}价格失败: {e}")
            return None

    def monitor_symbol(self, symbol):
        """监控单个交易对"""
        try:
            oi_data = self.get_open_interest(symbol)
            price_data = self.get_price(symbol)

            if oi_data and price_data:
                open_interest = float(oi_data['openInterest'])
                price = float(price_data['price'])
                value_usdt = open_interest * price

                # 保存数据
                self.db.save_data(symbol, open_interest, price, value_usdt)

                logger.info(f"✅ {symbol}: OI={open_interest:,.0f}, Price={price:.4f}, Value={value_usdt:,.2f}USDT")
                return True
            else:
                logger.warning(f"❌ {symbol}: 数据获取失败")
                return False

        except Exception as e:
            logger.error(f"监控{symbol}失败: {e}")
            return False

    def monitor_all(self):
        """监控所有交易对"""
        logger.info(f"开始监控 {len(self.symbols)} 个交易对")

        success_count = 0
        fail_count = 0
        start_time = time.time()

        for symbol in self.symbols:
            if self.monitor_symbol(symbol):
                success_count += 1
            else:
                fail_count += 1

            # 短暂延迟避免请求过快
            time.sleep(0.2)

        elapsed_time = time.time() - start_time
        logger.info(f"监控完成: 成功 {success_count} 个, 失败 {fail_count} 个, 耗时 {elapsed_time:.2f}秒")
        return success_count, fail_count, elapsed_time

    def run(self):
        """主运行循环"""
        logger.info("🚀 币安持仓监控程序启动")

        def signal_handler(signum, frame):
            logger.info("接收到终止信号，正在退出...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            while True:
                try:
                    success, fail, elapsed = self.monitor_all()

                    # 等待15分钟
                    wait_time = 900
                    logger.info(f"等待 {wait_time//60} 分钟后进行下一次监控...")
                    time.sleep(wait_time)

                except KeyboardInterrupt:
                    logger.info("用户中断，程序退出")
                    break
                except Exception as e:
                    logger.error(f"监控循环异常: {e}")
                    time.sleep(60)

        except Exception as e:
            logger.error(f"程序运行异常: {e}")
            sys.exit(1)

if __name__ == "__main__":
    monitor = BinanceMonitor()
    monitor.run()
EOF

echo "✅ 主程序文件创建完成"

# 创建配置文件模板
cat > telegram_config.py << 'EOF'
# Telegram Bot配置文件
# 请妥善保管此文件，不要上传到版本控制系统

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
EOF

echo "✅ 配置文件模板创建完成"

# 创建启动脚本
cat > start_bot.sh << 'EOF'
#!/bin/bash

# 交易机器人启动脚本
ENV=${1:-production}

echo "$(date): 开始启动交易机器人..."

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 启动程序
if [ "$ENV" = "test" ]; then
    echo "测试模式启动..."
    python3 enhanced_monitor.py
else
    echo "生产模式启动..."
    nohup python3 enhanced_monitor.py > logs/output.log 2>&1 &
    echo $! > bot.pid
    echo "程序已在后台启动，PID: $(cat bot.pid)"
fi

echo "$(date): 启动完成"
EOF

# 创建停止脚本
cat > stop_bot.sh << 'EOF'
#!/bin/bash

if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    echo "停止进程 $PID..."
    kill $PID 2>/dev/null
    rm -f bot.pid
    echo "程序已停止"
else
    echo "没有找到PID文件，尝试强制停止..."
    pkill -f "enhanced_monitor.py"
    echo "程序已停止"
fi
EOF

# 创建状态检查脚本
cat > check_status.sh << 'EOF'
#!/bin/bash

echo "=== 交易机器人状态检查 ==="

if pgrep -f "enhanced_monitor.py" > /dev/null; then
    echo "✅ 程序正在运行"
    echo "PID: $(pgrep -f "enhanced_monitor.py")"
else
    echo "❌ 程序未运行"
fi

if [ -f "logs/enhanced_binance_monitor.log" ]; then
    LOG_SIZE=$(du -h logs/enhanced_binance_monitor.log | cut -f1)
    echo "📊 日志文件大小: $LOG_SIZE"
    echo "📝 最近3条日志:"
    tail -3 logs/enhanced_binance_monitor.log 2>/dev/null || echo "暂无日志"
fi

if [ -f "binance_monitor.db" ]; then
    DB_SIZE=$(du -h binance_monitor.db | cut -f1)
    echo "💾 数据库大小: $DB_SIZE"
fi

echo "========================"
EOF

# 设置执行权限
chmod +x *.sh

echo ""
echo "🎉 所有基础文件创建完成！"
echo "当前目录: $(pwd)"
echo "文件列表:"
ls -la
echo ""
echo "✅ 下一步：配置Telegram参数"EOF

chmod +x /Users/vadar/Cursor file/trading bot/create_files_direct.sh