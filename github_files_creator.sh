#!/bin/bash

# GitHub仓库文件创建器
# 创建所有必要的文件用于GitHub上传

REPO_DIR="trading-bot-aliyun"

echo "=== 创建GitHub仓库文件 ==="

# 创建仓库目录
mkdir -p $REPO_DIR
cd $REPO_DIR

# 创建主要程序文件
echo "创建主程序文件..."

cat > enhanced_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
增强版币安持仓监控程序 - 阿里云部署版
支持OpenInterest数据获取和自动监控
"""

import requests
import sqlite3
import time
import logging
import signal
import sys
from datetime import datetime
from typing import List, Optional

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
    def __init__(self, db_path: str = "binance_monitor.db"):
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

    def save_data(self, symbol: str, open_interest: float, price: float, value_usdt: float):
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

        # 主要交易对 - 可根据需要调整
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT",
            "XRPUSDT", "UNIUSDT", "LTCUSDT", "LINKUSDT", "BCHUSDT",
            "XLMUSDT", "DOGEUSDT", "VETUSDT", "FILUSDT", "TRXUSDT",
            "EOSUSDT", "ATOMUSDT", "XTZUSDT", "ALGOUSDT", "XMRUSDT"
        ]

    def get_open_interest(self, symbol: str) -> Optional[dict]:
        """获取持仓数据"""
        try:
            url = f"{self.base_url}/fapi/v1/openInterest"
            response = requests.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取{symbol}持仓数据失败: {e}")
            return None

    def get_price(self, symbol: str) -> Optional[dict]:
        """获取价格"""
        try:
            url = f"{self.base_url}/fapi/v1/ticker/price"
            response = requests.get(url, params={'symbol': symbol}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取{symbol}价格失败: {e}")
            return None

    def monitor_symbol(self, symbol: str) -> bool:
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
    monitor = BinanceMonitor()
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

# 创建Telegram配置文件模板
cat > telegram_config.py << 'EOF'
# Telegram Bot配置文件
# 请妥善保管此文件，不要上传到版本控制系统

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
EOF

echo "✅ Telegram配置文件模板创建完成"

# 创建依赖文件
cat > requirements.txt << 'EOF'
requests>=2.25.1
urllib3>=1.26.0
EOF

echo "✅ 依赖文件创建完成"

# 创建启动脚本
cat > start_bot.sh << 'EOF'
#!/bin/bash

# 交易机器人启动脚本
# 使用方法: ./start_bot.sh [test|production]

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
pip install -r requirements.txt

# 启动程序
echo "启动程序..."
if [ "$ENV" = "test" ]; then
    echo "测试模式启动..."
    python3 enhanced_monitor.py
else
    echo "生产模式启动..."
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
    echo "📊 日志文件大小: $LOG_SIZE"
    echo "📝 最近3条日志:"
    tail -3 logs/enhanced_binance_monitor.log 2>/dev/null || echo "暂无日志"
fi

# 检查数据文件
if [ -f "binance_monitor.db" ]; then
    DB_SIZE=$(du -h binance_monitor.db | cut -f1)
    echo "💾 数据库大小: $DB_SIZE"
fi

# 检查配置
echo "🔧 配置状态:"
if [ -f "telegram_config.py" ]; then
    if grep -q "YOUR_BOT_TOKEN_HERE" telegram_config.py; then
        echo "   Telegram配置: 需要配置"
    else
        echo "   Telegram配置: 已配置"
    fi
else
    echo "   Telegram配置: 未找到文件"
fi

echo "========================"
EOF

# 创建系统服务安装脚本
cat > install_service.sh << 'EOF'
#!/bin/bash

# 系统服务安装脚本
# 使用方法: sudo ./install_service.sh

SERVICE_NAME="trading-bot"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER=$(whoami)

echo "安装系统服务: $SERVICE_NAME"

# 创建服务文件
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOL
[Unit]
Description=Trading Bot Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/start_bot.sh production
ExecStop=$PROJECT_DIR/stop_bot.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable $SERVICE_NAME

echo "服务安装完成！"
echo "使用方法:"
echo "  启动服务: sudo systemctl start $SERVICE_NAME"
echo "  停止服务: sudo systemctl stop $SERVICE_NAME"
echo "  查看状态: sudo systemctl status $SERVICE_NAME"
echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
EOF

# 创建README.md
cat > README.md << 'EOF'
# 币安持仓监控机器人 - 阿里云部署版

这是一个用于监控币安交易所持仓数据(OI)的自动化程序，支持阿里云服务器部署。

## 🚀 功能特性

- ✅ 实时监控币安期货持仓数据
- ✅ 支持20+主流交易对
- ✅ 自动数据存储和分析
- ✅ 阿里云服务器优化
- ✅ 系统服务支持
- ✅ 完善的日志记录
- ✅ 简单的状态检查

## 📋 系统要求

- Python 3.8+
- SQLite3
- 网络连接（访问币安API）
- Linux系统（推荐CentOS/Alibaba Cloud Linux）

## 🛠️ 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/trading-bot-aliyun.git
cd trading-bot-aliyun
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置Telegram（可选）
编辑 `telegram_config.py` 文件，填入您的Bot Token和Chat ID。

### 5. 测试运行
```bash
./start_bot.sh test
```

### 6. 生产部署
```bash
./start_bot.sh production
```

## 📊 管理命令

```bash
# 检查状态
./check_status.sh

# 停止程序
./stop_bot.sh

# 查看日志
tail -f logs/enhanced_binance_monitor.log

# 安装系统服务（需要sudo）
sudo ./install_service.sh
sudo systemctl start trading-bot
```

## 📁 文件结构

```
trading-bot-aliyun/
├── enhanced_monitor.py          # 主监控程序
├── config.py                    # 配置文件
├── telegram_config.py          # Telegram配置模板
├── requirements.txt            # Python依赖
├── start_bot.sh               # 启动脚本
├── stop_bot.sh                # 停止脚本
├── check_status.sh            # 状态检查脚本
├── install_service.sh         # 系统服务安装脚本
├── logs/                      # 日志目录
├── data/                      # 数据目录
├── binance_monitor.db         # 数据库文件（自动生成）
└── README.md                  # 本文件
```

## 🔧 配置说明

### 基础配置
程序默认不需要额外配置即可运行。如需Telegram通知功能，请配置：

1. 复制 `telegram_config.py.template` 为 `telegram_config.py`
2. 填入您的Bot Token和Chat ID
3. 重新启动程序

### 数据库
程序会自动创建SQLite数据库文件 `binance_monitor.db` 来存储监控数据。

### 日志
日志文件位于 `logs/enhanced_binance_monitor.log`，会自动轮转保存。

## 📈 监控数据

程序监控以下数据：
- 持仓量 (Open Interest)
- 当前价格
- 持仓价值 (USDT)
- 时间戳

数据更新频率：每15分钟
监控交易对：20+主流币种

## 🚨 故障排除

### 程序无法启动
- 检查Python版本：`python3 --version`
- 检查依赖安装：`pip list | grep requests`
- 检查日志文件：`tail logs/enhanced_binance_monitor.log`

### 无法获取数据
- 检查网络连接：`ping api.binance.com`
- 检查防火墙设置
- 查看错误日志

### 数据库问题
- 检查文件权限：`ls -la binance_monitor.db`
- 如损坏可删除重建：`rm binance_monitor.db`

## 🔒 安全建议

1. **API密钥保护**：妥善保管telegram_config.py文件
2. **文件权限**：设置适当的文件权限
3. **防火墙**：只开放必要的端口
4. **定期备份**：定期备份数据库和配置文件

## 📞 技术支持

如遇到问题：
1. 查看日志文件获取错误信息
2. 使用`./check_status.sh`检查状态
3. 确保网络连接正常
4. 验证Python环境正确

## 📄 许可证

MIT License - 详见LICENSE文件

## 🙋‍♂️ 贡献

欢迎提交Issue和Pull Request！
EOF

# 创建部署指南
cat > DEPLOYMENT_GUIDE.md << 'EOF'
# 阿里云部署指南

## 🚀 阿里云服务器部署步骤

### 步骤1：服务器准备
1. 购买阿里云ECS实例
2. 选择操作系统：CentOS 7/8 或 Alibaba Cloud Linux
3. 配置安全组：开放22端口(SSH)
4. 获取公网IP地址

### 步骤2：连接服务器
```bash
ssh root@your-server-ip
```

### 步骤3：系统初始化
```bash
# 更新系统
yum update -y

# 安装基础软件
yum install -y python3 python3-pip git curl wget vim

# 设置时区
timedatectl set-timezone Asia/Shanghai
```

### 步骤4：部署程序
```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/trading-bot-aliyun.git
cd trading-bot-aliyun

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置Telegram（可选）
vim telegram_config.py
```

### 步骤5：运行程序
```bash
# 测试运行
./start_bot.sh test

# 生产部署
./start_bot.sh production

# 检查状态
./check_status.sh
```

### 步骤6：系统服务（可选）
```bash
# 安装为系统服务
sudo ./install_service.sh

# 管理服务
sudo systemctl start trading-bot
sudo systemctl enable trading-bot
sudo systemctl status trading-bot
```

### 步骤7：防火墙配置（可选）
```bash
# 如果启用了防火墙
systemctl start firewalld
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload
```

## 📊 日常维护

### 查看日志
```bash
tail -f logs/enhanced_binance_monitor.log
```

### 检查状态
```bash
./check_status.sh
```

### 重启程序
```bash
./stop_bot.sh
./start_bot.sh production
```

### 备份数据
```bash
# 备份数据库
cp binance_monitor.db backup/binance_monitor_$(date +%Y%m%d).db

# 备份配置
cp telegram_config.py backup/telegram_config_$(date +%Y%m%d).py
```

## 🔧 故障排除

### 常见问题

1. **程序无法启动**
   - 检查Python版本：`python3 --version`
   - 检查依赖：`pip list`
   - 查看日志：`tail logs/enhanced_binance_monitor.log`

2. **无法连接币安API**
   - 检查网络：`ping api.binance.com`
   - 检查防火墙设置
   - 验证DNS解析

3. **权限问题**
   - 确保脚本有执行权限：`chmod +x *.sh`
   - 检查文件所有权：`ls -la`

4. **数据库问题**
   - 检查数据库文件：`ls -la binance_monitor.db`
   - 如损坏可删除重建：`rm binance_monitor.db`

## 🛡️ 安全配置

### 用户权限
建议创建专用用户运行程序：
```bash
useradd -m tradingbot
passwd tradingbot
usermod -aG wheel tradingbot
```

### 文件权限
```bash
chmod 600 telegram_config.py
chmod +x *.sh
```

### SSH安全
- 修改SSH端口
- 禁用root远程登录
- 使用密钥认证

## 📈 性能优化

### 数据库优化
- 定期清理旧数据
- 优化查询性能
- 监控磁盘空间

### 系统优化
- 调整系统参数
- 优化网络设置
- 监控资源使用

EOF

# 创建目录结构
mkdir -p logs data backup

# 设置执行权限
chmod +x *.sh

echo "✅ 所有GitHub仓库文件创建完成！"
echo "文件结构："
tree -L 2 || find . -type f -name "*.py" -o -name "*.sh" -o -name "*.txt" -o -name "*.md" | sort
echo ""
echo "🎯 下一步："
echo "1. 初始化Git仓库: git init"
echo "2. 添加文件: git add ."
echo "3. 提交: git commit -m 'Initial commit'"
echo "4. 推送到GitHub"
echo "5. 在阿里云服务器上克隆"
echo ""
echo "📁 当前目录: $(pwd)"
echo "=== GitHub文件创建完成 ==="