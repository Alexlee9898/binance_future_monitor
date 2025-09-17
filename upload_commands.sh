#!/bin/bash

# 文件上传脚本
# 使用方法: ./upload_commands.sh

SERVER_IP="8.134.103.197"
USERNAME="root"
PACKAGE_FILE="trading_bot_aliyun_20250917_055629.tar.gz"

echo "=== 文件上传步骤 ==="

# 检查部署包
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "错误: 部署包 $PACKAGE_FILE 不存在"
    exit 1
fi

echo "📤 正在上传文件到服务器..."
echo "这将在新终端中执行以下命令："
echo ""
echo "scp $PACKAGE_FILE $USERNAME@$SERVER_IP:/tmp/"
echo ""

echo "请执行以下命令上传文件："
cat << EOF

# 上传文件命令
scp $PACKAGE_FILE $USERNAME@$SERVER_IP:/tmp/

# 然后登录服务器并执行设置
ssh $USERNAME@$SERVER_IP

# 在服务器上执行以下命令：
# 移动文件到正确位置
mv /tmp/trading_bot_aliyun_*.tar.gz /home/tradingbot/
cd /home/tradingbot/

# 解压文件
tar -xzf trading_bot_aliyun_*.tar.gz

# 移动文件到交易机器人目录
mv aliyun_trading_bot_package/* trading_bot/
rm -rf aliyun_trading_bot_package/
rm -f trading_bot_aliyun_*.tar.gz

# 设置权限
chown -R tradingbot:tradingbot /home/tradingbot/trading_bot
chmod +x /home/tradingbot/trading_bot/*.sh

# 切换到tradingbot用户
su - tradingbot

# 进入项目目录
cd /home/tradingbot/trading_bot

# 查看文件结构
ls -la

EOF

echo ""
echo "上传完成后，请继续执行配置步骤"