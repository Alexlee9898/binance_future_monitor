#!/bin/bash

# 阿里云服务器初始化命令集合
# 请在登录服务器后，按顺序执行这些命令

echo "=== 开始阿里云服务器初始化 ==="

# 1. 更新系统
echo "📦 正在更新系统..."
apt update && apt upgrade -y

# 2. 安装基础软件
echo "🛠️ 正在安装基础软件..."
apt install -y python3 python3-pip python3-venv curl wget vim htop git

# 3. 创建专用用户
echo "👤 创建交易机器人专用用户..."
if ! id "tradingbot" >/dev/null 2>&1; then
    useradd -m -s /bin/bash tradingbot
    echo "请设置tradingbot用户的密码："
    passwd tradingbot
    usermod -aG sudo tradingbot
    echo "✅ 用户 tradingbot 已创建"
else
    echo "用户 tradingbot 已存在"
fi

# 4. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p /home/tradingbot/trading_bot/{data,logs,backup,scripts}
chown -R tradingbot:tradingbot /home/tradingbot

# 5. 配置防火墙
echo "🔥 配置防火墙..."
apt install -y ufw
ufw allow ssh
ufw allow 22
echo "y" | ufw enable
ufw status

# 6. 设置时区
echo "🕐 设置时区..."
timedatectl set-timezone Asia/Shanghai

echo "✅ 服务器初始化完成！"
echo ""
echo "下一步：上传程序文件"
echo "请在新终端中执行文件上传步骤"