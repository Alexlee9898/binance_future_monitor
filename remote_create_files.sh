#!/bin/bash

# CentOS/Alibaba Cloud Linux 文件创建脚本
# 在当前用户目录下创建所有程序文件

echo "=== 开始创建交易机器人文件 ==="

# 进入项目目录
cd ~/trading_bot

# 创建主监控程序
cat > enhanced_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
增强版币安持仓监控程序
支持OpenInterest数据获取和变化率计算
"""

import requests
import sqlite3
import time
import json
import logging
import signal
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

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

@dataclass
class MonitoringData:
    symbol: str
    open_interest: float
    price: float
    value_usdt: float
    oi_change_percent: float
    price_change_percent: float
    timestamp: datetime

class DatabaseManager:
    def __init__(self, db_path: str = "binance_monitor.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建监控数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    open_interest REAL NOT NULL,
                    price REAL NOT NULL,
                    value_usdt REAL NOT NULL,
                    oi_change_percent REAL NOT NULL,
                    price_change_percent REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp
                ON monitoring_data(symbol, timestamp)
            ''')

            conn.commit()
            logger.info("数据库初始化完成")

    def save_monitoring_data(self, data: MonitoringData):
        """保存监控数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_data
                    (symbol, open_interest, price, value_usdt, oi_change_percent, price_change_percent, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.symbol, data.open_interest, data.price,
                    data.value_usdt, data.oi_change_percent,
                    data.price_change_percent, data.timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"保存数据失败: {e}")

class BinanceOpenInterestMonitor:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.db_manager = DatabaseManager()
        self.monitoring_symbols = self.get_top_symbols()

    def get_top_symbols(self) -> List[str]:
        """获取热门交易对"""
        return [
            "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT",
            "XRPUSDT", "UNIUSDT", "LTCUSDT", "LINKUSDT", "BCHUSDT",
            "XLMUSDT", "DOGEUSDT", "VETUSDT", "FILUSDT", "TRXUSDT",
            "EOSUSDT", "ATOMUSDT", "XTZUSDT", "ALGOUSDT", "XMRUSDT",
            "NEOUSDT", "MIOTAUSDT", "DASHUSDT", "ZECUSDT", "HBARUSDT",
            "ICXUSDT", "WAVESUSDT", "OMGUSDT", "ZRXUSDT", "BATUSDT",
            "ENJUSDT", "ONTUSDT", "RVNUSDT", "ZILUSDT", "IOSTUSDT",
            "CELRUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "TOMOUSDT",
            "PERLUSDT", "DUSKUSDT", "MFTUSDT", "KEYUSDT", "STORMUSDT",
            "DOCKUSDT", "WANUSDT", "FUNUSDT", "CVCUSDT", "BTTUSDT"
        ]

    def get_open_interest(self, symbol: str) -> Optional[Dict]:
        """获取指定交易对的持仓数据"""
        try:
            url = f"{self.base_url}/fapi/v1/openInterest"
            params = {'symbol': symbol}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 获取价格信息
            price_data = self.get_symbol_price(symbol)
            if price_data:
                data['price'] = float(price_data['price'])
                data['value_usdt'] = float(data['openInterest']) * data['price']
            else:
                data['price'] = 0.0
                data['value_usdt'] = 0.0

            return data

        except Exception as e:
            logger.error(f"获取{symbol}持仓数据失败: {e}")
            return None

    def get_symbol_price(self, symbol: str) -> Optional[Dict]:
        """获取交易对价格"""
        try:
            url = f"{self.base_url}/fapi/v1/ticker/price"
            params = {'symbol': symbol}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"获取{symbol}价格失败: {e}")
            return None

    def calculate_change_rate(self, current_oi: float, current_price: float, symbol: str) -> Tuple[float, float]:
        """计算变化率（简化版本）"""
        # 这里应该查询历史数据，暂时使用模拟数据
        # 实际应用中需要实现历史数据查询
        return (0.0, 0.0)  # (oi_change_percent, price_change_percent)

    def monitor_symbol(self, symbol: str) -> Optional[MonitoringData]:
        """监控单个交易对"""
        try:
            oi_data = self.get_open_interest(symbol)
            if not oi_data:
                return None

            open_interest = float(oi_data['openInterest'])
            price = float(oi_data.get('price', 0))
            value_usdt = float(oi_data.get('value_usdt', 0))

            # 计算变化率
            oi_change, price_change = self.calculate_change_rate(open_interest, price, symbol)

            monitoring_data = MonitoringData(
                symbol=symbol,
                open_interest=open_interest,
                price=price,
                value_usdt=value_usdt,
                oi_change_percent=oi_change,
                price_change_percent=price_change,
                timestamp=datetime.now()
            )

            # 保存到数据库
            self.db_manager.save_monitoring_data(monitoring_data)

            logger.info(f"✅ {symbol}: OI={open_interest:,.0f}, Price={price:.4f}, Value={value_usdt:,.2f}USDT")
            return monitoring_data

        except Exception as e:
            logger.error(f"监控{symbol}失败: {e}")
            return None

    def monitor_all_symbols(self):
        """监控所有交易对"""
        logger.info(f"开始监控 {len(self.monitoring_symbols)} 个交易对")

        success_count = 0
        fail_count = 0
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self.monitor_symbol, symbol): symbol
                for symbol in self.monitoring_symbols
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    logger.error(f"监控{symbol}异常: {e}")
                    fail_count += 1

        elapsed_time = time.time() - start_time
        logger.info(f"监控完成: 成功 {success_count} 个, 失败 {fail_count} 个, 耗时 {elapsed_time:.2f}秒")

        return success_count, fail_count, elapsed_time

    def run(self):
        """主运行循环"""
        logger.info("🚀 增强版币安持仓监控程序启动")

        # 设置信号处理
        def signal_handler(signum, frame):
            logger.info("接收到终止信号，正在退出...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            while True:
                try:
                    success, fail, elapsed = self.monitor_all_symbols()

                    # 等待15分钟后进行下一次监控
                    wait_time = 900  # 15分钟
                    logger.info(f"等待 {wait_time//60} 分钟后进行下一次监控...")
                    time.sleep(wait_time)

                except KeyboardInterrupt:
                    logger.info("用户中断，程序退出")
                    break
                except Exception as e:
                    logger.error(f"监控循环异常: {e}")
                    time.sleep(60)  # 等待1分钟后重试

        except Exception as e:
            logger.error(f"程序运行异常: {e}")
            sys.exit(1)

if __name__ == "__main__":
    monitor = BinanceOpenInterestMonitor()
    monitor.run()
EOF

echo "✅ 主程序文件创建完成"

# 创建配置文件
cat > config.py << 'EOF'
#!/usr/bin/env python3
"""
配置文件 - 存储配置信息
"""

import os
from typing import Optional

class Config:
    """配置管理类"""

    # Telegram Bot配置
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置"""
        cls.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        cls.TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    @classmethod
    def load_from_file(cls, config_file: str = 'telegram_config.py'):
        """从配置文件加载"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("telegram_config", config_file)
            if spec and spec.loader:
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)

                if hasattr(config_module, 'TELEGRAM_BOT_TOKEN'):
                    cls.TELEGRAM_BOT_TOKEN = config_module.TELEGRAM_BOT_TOKEN
                if hasattr(config_module, 'TELEGRAM_CHAT_ID'):
                    cls.TELEGRAM_CHAT_ID = config_module.TELEGRAM_CHAT_ID

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    @classmethod
    def get_telegram_config(cls) -> tuple:
        """获取Telegram配置"""
        cls.load_from_env()
        cls.load_from_file()
        return cls.TELEGRAM_BOT_TOKEN, cls.TELEGRAM_CHAT_ID

    @classmethod
    def is_telegram_configured(cls) -> bool:
        """检查Telegram是否已配置"""
        bot_token, chat_id = cls.get_telegram_config()
        return bool(bot_token and chat_id)
EOF

echo "✅ 配置文件创建完成"

# 创建数据库管理器
cat > database_manager.py << 'EOF'
#!/usr/bin/env python3
"""
数据库管理模块
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class MonitoringData:
    symbol: str
    open_interest: float
    price: float
    value_usdt: float
    oi_change_percent: float
    price_change_percent: float
    timestamp: datetime

class DatabaseManager:
    def __init__(self, db_path: str = "binance_monitor.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 创建监控数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoring_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        open_interest REAL NOT NULL,
                        price REAL NOT NULL,
                        value_usdt REAL NOT NULL,
                        oi_change_percent REAL NOT NULL,
                        price_change_percent REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_symbol_timestamp
                    ON monitoring_data(symbol, timestamp)
                ''')

                conn.commit()
                logger.info("数据库初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def save_monitoring_data(self, data: MonitoringData):
        """保存监控数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_data
                    (symbol, open_interest, price, value_usdt, oi_change_percent, price_change_percent, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.symbol, data.open_interest, data.price,
                    data.value_usdt, data.oi_change_percent,
                    data.price_change_percent, data.timestamp
                ))
                conn.commit()
                logger.debug(f"数据已保存: {data.symbol}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
EOF

echo "✅ 数据库管理器创建完成"

# 创建启动脚本
cat > start_bot.sh << 'EOF'
#!/bin/bash

# 交易机器人启动脚本
# 使用方法: ./start_bot.sh [环境]

ENV=${1:-production}
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$PROJECT_DIR/logs/bot_start.log"

echo "$(date): 开始启动交易机器人..." >> $LOG_FILE

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查依赖包..."
pip install requests

# 设置环境变量
export TELEGRAM_BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" telegram_config.py | cut -d'"' -f2)
export TELEGRAM_CHAT_ID=$(grep "TELEGRAM_CHAT_ID" telegram_config.py | cut -d'"' -f2)

# 启动程序
echo "启动程序..."
if [ "$ENV" = "test" ]; then
    python3 enhanced_monitor.py
else
    nohup python3 enhanced_monitor.py > logs/output.log 2>&1 &
    echo $! > bot.pid
    echo "程序已在后台启动，PID: $(cat bot.pid)"
fi

echo "$(date): 启动完成" >> $LOG_FILE
EOF

# 创建停止脚本
cat > stop_bot.sh << 'EOF'
#!/bin/bash

# 交易机器人停止脚本

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

# 状态检查脚本

echo "=== 交易机器人状态检查 ==="

# 检查进程
if pgrep -f "enhanced_monitor.py" > /dev/null; then
    echo "✅ 程序正在运行"
    echo "PID: $(pgrep -f "enhanced_monitor.py")"
else
    echo "❌ 程序未运行"
fi

# 检查日志文件
if [ -f "logs/enhanced_binance_monitor.log" ]; then
    LOG_SIZE=$(du -h logs/enhanced_binance_monitor.log | cut -f1)
    echo "📊 主日志文件大小: $LOG_SIZE"
    echo "📝 最近5条日志:"
    tail -5 logs/enhanced_binance_monitor.log 2>/dev/null | grep "message" | tail -5 || echo "暂无日志"
fi

# 检查数据文件
if [ -f "binance_monitor.db" ]; then
    DB_SIZE=$(du -h binance_monitor.db | cut -f1)
    echo "💾 数据库大小: $DB_SIZE"
fi

# 检查配置
echo "🔧 配置状态:"
if [ -f "telegram_config.py" ]; then
    echo "   Telegram配置: 已设置"
else
    echo "   Telegram配置: 未设置"
fi

echo "========================"
EOF

# 设置执行权限
chmod +x *.sh

echo "✅ 所有文件创建完成！"
echo "文件列表："
ls -la
echo ""
echo "📁 当前目录: $(pwd)"
echo "=== 文件创建完成 ==="EOF