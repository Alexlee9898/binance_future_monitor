#!/bin/bash

# 打包脚本 - 为阿里云部署准备文件
# 使用方法: ./package_for_aliyun.sh

set -e

echo "=================================="
echo "阿里云部署打包脚本"
echo "=================================="

# 创建临时目录
PACKAGE_DIR="aliyun_trading_bot_package"
DATE=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="trading_bot_aliyun_$DATE.tar.gz"

# 清理旧的打包目录
if [ -d "$PACKAGE_DIR" ]; then
    rm -rf $PACKAGE_DIR
fi

# 创建打包目录结构
mkdir -p $PACKAGE_DIR
echo "创建打包目录结构..."

# 复制核心文件
echo "复制核心程序文件..."
cp enhanced_monitor.py $PACKAGE_DIR/
cp database_manager.py $PACKAGE_DIR/
cp config.py $PACKAGE_DIR/
cp telegram_config.py $PACKAGE_DIR/
cp logger_manager.py $PACKAGE_DIR/
cp check_change_rate.py $PACKAGE_DIR/
cp setup_telegram.py $PACKAGE_DIR/

# 复制其他重要文件
cp aliyun_deployment_guide.md $PACKAGE_DIR/
cp deploy_to_aliyun.sh $PACKAGE_DIR/
cp setup_telegram.py $PACKAGE_DIR/

# 创建必要的目录
echo "创建必要目录..."
mkdir -p $PACKAGE_DIR/data
mkdir -p $PACKAGE_DIR/logs
mkdir -p $PACKAGE_DIR/config
mkdir -p $PACKAGE_DIR/scripts

# 复制配置文件模板
cp telegram_config_sample.py $PACKAGE_DIR/config/ 2>/dev/null || true
cp telegram_config_guide.md $PACKAGE_DIR/config/ 2>/dev/null || true

# 创建requirements.txt文件
echo "创建依赖文件..."
cat > $PACKAGE_DIR/requirements.txt << EOF
requests
python-telegram-bot
urllib3
EOF

# 创建启动脚本
echo "创建启动脚本..."
cat > $PACKAGE_DIR/start_bot.sh << 'EOF'
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

# 检查依赖
echo "检查依赖包..."
pip install -r requirements.txt

# 设置环境变量
export TELEGRAM_BOT_TOKEN=$(cat telegram_config.py | grep "TELEGRAM_BOT_TOKEN" | cut -d'"' -f2)
export TELEGRAM_CHAT_ID=$(cat telegram_config.py | grep "TELEGRAM_CHAT_ID" | cut -d'"' -f2)

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

chmod +x $PACKAGE_DIR/start_bot.sh

# 创建停止脚本
cat > $PACKAGE_DIR/stop_bot.sh << 'EOF'
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

chmod +x $PACKAGE_DIR/stop_bot.sh

# 创建状态检查脚本
cat > $PACKAGE_DIR/check_status.sh << 'EOF'
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
    tail -5 logs/enhanced_binance_monitor.log | grep -o '"message": "[^"]*"' | tail -5
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

chmod +x $PACKAGE_DIR/check_status.sh

# 创建系统服务安装脚本
cat > $PACKAGE_DIR/install_service.sh << 'EOF'
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

chmod +x $PACKAGE_DIR/install_service.sh

# 创建README文件
cat > $PACKAGE_DIR/README.md << 'EOF'
# 交易机器人阿里云部署包

## 文件说明
- `enhanced_monitor.py` - 主监控程序
- `database_manager.py` - 数据库管理
- `config.py` - 配置文件
- `telegram_config.py` - Telegram配置
- `start_bot.sh` - 启动脚本
- `stop_bot.sh` - 停止脚本
- `check_status.sh` - 状态检查脚本
- `install_service.sh` - 系统服务安装脚本
- `requirements.txt` - Python依赖

## 快速开始

### 1. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置Telegram
编辑 `telegram_config.py` 文件，填入你的Bot Token和Chat ID。

### 3. 启动程序
```bash
# 测试模式
./start_bot.sh test

# 生产模式（后台运行）
./start_bot.sh production
```

### 4. 检查状态
```bash
./check_status.sh
```

### 5. 停止程序
```bash
./stop_bot.sh
```

### 6. 安装为系统服务（可选）
```bash
sudo ./install_service.sh
sudo systemctl start trading-bot
sudo systemctl enable trading-bot
```

## 日志查看
```bash
# 实时查看日志
tail -f logs/enhanced_binance_monitor.log

# 查看系统服务日志
sudo journalctl -u trading-bot -f
```

## 注意事项
- 确保已正确配置telegram_config.py
- 定期检查磁盘空间，日志文件可能很大
- 建议设置日志轮转
EOF

# 打包
echo "创建压缩包..."
tar -czf $PACKAGE_NAME $PACKAGE_DIR/

# 清理临时目录
rm -rf $PACKAGE_DIR/

echo "=================================="
echo "打包完成！"
echo "包文件: $PACKAGE_NAME"
echo "文件大小: $(du -h $PACKAGE_NAME | cut -f1)"
echo "=================================="
echo ""
echo "下一步操作："
echo "1. 上传 $PACKAGE_NAME 到阿里云服务器"
echo "2. 解压: tar -xzf $PACKAGE_NAME"
echo "3. 进入目录: cd $PACKAGE_DIR"
echo "4. 按照 README.md 进行配置和启动"
echo "=================================="