#!/bin/bash

# 阿里云部署助手脚本
# 使用方法: ./connect_and_deploy.sh

SERVER_IP="8.134.103.197"
USERNAME="root"
PACKAGE_FILE="trading_bot_aliyun_20250917_055629.tar.gz"

echo "=================================="
echo "阿里云交易机器人部署助手"
echo "目标服务器: $USERNAME@$SERVER_IP"
echo "=================================="

# 检查部署包是否存在
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "错误: 部署包 $PACKAGE_FILE 不存在"
    echo "请先运行 ./package_for_aliyun.sh 创建部署包"
    exit 1
fi

echo ""
echo "📋 部署步骤预览："
echo "1. 连接服务器并初始化环境"
echo "2. 创建交易机器人专用用户"
echo "3. 上传程序文件"
echo "4. 安装依赖和配置环境"
echo "5. 配置Telegram参数"
echo "6. 测试程序运行"
echo "7. 设置后台运行"
echo ""

read -p "按回车键开始部署，或按 Ctrl+C 取消..."

echo ""
echo "🔐 正在连接服务器..."
echo "请输入服务器密码进行连接"

# 创建临时部署脚本
cat > /tmp/deploy_commands.sh << 'EOF'
#!/bin/bash

set -e

echo "✅ 成功连接到阿里云服务器"
echo ""

# 更新系统
echo "📦 正在更新系统..."
apt update && apt upgrade -y

# 安装基础软件
echo "🛠️ 正在安装基础软件..."
apt install -y python3 python3-pip python3-venv curl wget vim htop

# 创建专用用户
echo "👤 创建交易机器人专用用户..."
if ! id "tradingbot" &>/dev/null; then
    useradd -m -s /bin/bash tradingbot
    echo "tradingbot:TradingBot2025!" | chpasswd
    echo "✅ 用户 tradingbot 已创建，密码: TradingBot2025!"
    usermod -aG sudo tradingbot
else
    echo "用户 tradingbot 已存在"
fi

# 创建项目目录
mkdir -p /home/tradingbot/trading_bot
mkdir -p /home/tradingbot/backup
chown -R tradingbot:tradingbot /home/tradingbot

echo "✅ 环境初始化完成"
echo ""
echo "📁 目录结构已创建："
ls -la /home/tradingbot/
EOF

# 执行初始化命令
ssh $USERNAME@$SERVER_IP 'bash -s' < /tmp/deploy_commands.sh

# 上传文件
echo ""
echo "📤 正在上传程序文件..."
scp $PACKAGE_FILE $USERNAME@$SERVER_IP:/tmp/

# 解压并设置文件
echo "📂 正在解压和设置文件..."
ssh $USERNAME@$SERVER_IP << 'ENDSSH'
    # 移动到项目目录
    mv /tmp/trading_bot_aliyun_*.tar.gz /home/tradingbot/
    cd /home/tradingbot/

    # 解压文件
    tar -xzf trading_bot_aliyun_*.tar.gz

    # 移动文件到正确位置
    mv aliyun_trading_bot_package/* trading_bot/
    rm -rf aliyun_trading_bot_package/
    rm -f trading_bot_aliyun_*.tar.gz

    # 设置权限
    chown -R tradingbot:tradingbot /home/tradingbot/trading_bot
    chmod +x /home/tradingbot/trading_bot/*.sh

    echo "✅ 文件上传和设置完成"
ENDSSH

# 安装Python依赖
echo ""
echo "🐍 正在安装Python依赖..."
ssh tradingbot@$SERVER_IP << 'ENDSSH'
    cd /home/tradingbot/trading_bot

    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate

    # 安装依赖
    pip install --upgrade pip
    pip install requests

    echo "✅ Python依赖安装完成"
ENDSSH

echo ""
echo "🎉 基础部署完成！"
echo ""
echo "下一步操作："
echo "1. 登录服务器: ssh tradingbot@$SERVER_IP"
echo "2. 进入目录: cd /home/tradingbot/trading_bot"
echo "3. 配置Telegram: 编辑 telegram_config.py 文件"
echo "4. 测试运行: ./start_bot.sh test"
echo "5. 正式部署: ./start_bot.sh production"
echo ""
echo "默认用户名: tradingbot"
echo "默认密码: TradingBot2025!"
echo ""
echo "需要立即登录服务器进行Telegram配置吗？"
read -p "按回车键继续，或按 Ctrl+C 退出..."

# 自动登录到服务器
echo "正在登录到服务器..."
ssh tradingbot@$SERVER_IP