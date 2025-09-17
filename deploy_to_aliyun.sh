#!/bin/bash

# 阿里云服务器部署脚本
# 使用方法: ./deploy_to_aliyun.sh [服务器IP] [用户名]

set -e

# 参数检查
if [ $# -ne 2 ]; then
    echo "使用方法: $0 <服务器IP> <用户名>"
    echo "示例: $0 47.100.123.45 root"
    exit 1
fi

SERVER_IP=$1
USERNAME=$2
PROJECT_DIR="/home/$USERNAME/trading_bot"
BACKUP_DIR="/home/$USERNAME/backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=================================="
echo "阿里云服务器部署脚本"
echo "目标服务器: $USERNAME@$SERVER_IP"
echo "项目目录: $PROJECT_DIR"
echo "备份目录: $BACKUP_DIR"
echo "=================================="

# 检查本地文件
if [ ! -f "enhanced_monitor.py" ]; then
    echo "错误: enhanced_monitor.py 文件不存在"
    exit 1
fi

if [ ! -f "config.py" ]; then
    echo "错误: config.py 文件不存在"
    exit 1
fi

if [ ! -f "telegram_config.py" ]; then
    echo "错误: telegram_config.py 文件不存在"
    exit 1
fi

# 创建打包文件
echo "正在创建部署包..."
DEPLOY_PACKAGE="trading_bot_deploy_$DATE.tar.gz"
tar -czf $DEPLOY_PACKAGE \
    enhanced_monitor.py \
    database_manager.py \
    config.py \
    telegram_config.py \
    logger_manager.py \
    check_change_rate.py \
    setup_telegram.py \
    data/ \
    logs/ \
    aliyun_deployment_guide.md \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="*.log.*" \
    2>/dev/null

echo "部署包创建完成: $DEPLOY_PACKAGE"

# 连接测试
echo "正在测试服务器连接..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "echo '连接成功'" || {
    echo "错误: 无法连接到服务器 $SERVER_IP"
    rm -f $DEPLOY_PACKAGE
    exit 1
}

# 创建远程目录结构
echo "正在创建远程目录结构..."
ssh $USERNAME@$SERVER_IP << EOF
    # 创建项目目录
    mkdir -p $PROJECT_DIR
    mkdir -p $PROJECT_DIR/data
    mkdir -p $PROJECT_DIR/logs
    mkdir -p $BACKUP_DIR

    # 如果项目已存在，先备份
    if [ -f "$PROJECT_DIR/enhanced_monitor.py" ]; then
        echo "备份现有项目..."
        cd $PROJECT_DIR/..
        tar -czf $BACKUP_DIR/trading_bot_backup_
        $(date +%Y%m%d_%H%M%S).tar.gz trading_bot/ 2>/dev/null || true
    fi

    # 设置目录权限
    chown -R $USERNAME:$USERNAME $PROJECT_DIR
    chown -R $USERNAME:$USERNAME $BACKUP_DIR
EOF

# 上传部署包
echo "正在上传部署包到服务器..."
scp $DEPLOY_PACKAGE $USERNAME@$SERVER_IP:/tmp/

# 解压部署包
echo "正在解压部署包..."
ssh $USERNAME@$SERVER_IP << EOF
    cd $PROJECT_DIR
    tar -xzf /tmp/$DEPLOY_PACKAGE
    rm -f /tmp/$DEPLOY_PACKAGE

    # 设置文件权限
    chmod 600 telegram_config.py
    chmod 755 *.py

    echo "部署包解压完成"
EOF

# 清理本地部署包
rm -f $DEPLOY_PACKAGE

# 安装Python依赖
echo "正在安装Python依赖..."
ssh $USERNAME@$SERVER_IP << EOF
    cd $PROJECT_DIR

    # 检查Python3是否安装
    if ! command -v python3 &> /dev/null; then
        echo "安装Python3..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    fi

    # 创建虚拟环境
    echo "创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    # 安装依赖包
    echo "安装依赖包..."
    pip install --upgrade pip
    pip install requests
    pip install python-telegram-bot

    echo "依赖安装完成"
EOF

echo "=================================="
echo "部署完成！"
echo "=================================="
echo "后续操作："
echo "1. SSH到服务器: ssh $USERNAME@$SERVER_IP"
echo "2. 进入项目目录: cd $PROJECT_DIR"
echo "3. 激活虚拟环境: source venv/bin/activate"
echo "4. 测试程序: python3 enhanced_monitor.py"
echo "5. 查看日志: tail -f logs/enhanced_binance_monitor.log"
echo "=================================="
echo "如需设置系统服务，请查看 aliyun_deployment_guide.md"