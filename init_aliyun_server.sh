#!/bin/bash

# 阿里云服务器初始化脚本
# 在阿里云服务器上运行此脚本来准备环境

set -e

echo "=================================="
echo "阿里云服务器初始化脚本"
echo "=================================="

# 检查是否是root用户
if [ "$EUID" -ne 0 ]; then
    echo "请以root用户运行此脚本"
    echo "使用方法: sudo ./init_aliyun_server.sh"
    exit 1
fi

# 更新系统
echo "1. 更新系统包..."
apt update && apt upgrade -y

# 安装基础软件
echo "2. 安装基础软件..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    unzip \
    tar \
    htop \
    tree \
    vim \
    cron

# 安装监控工具
echo "3. 安装监控工具..."
apt install -y \
    nethogs \
    iftop \
    nload \
    vnstat

# 创建专用用户
echo "4. 创建交易机器人用户..."
USERNAME="tradingbot"
if ! id "$USERNAME" >/dev/null 2>&1; then
    useradd -m -s /bin/bash $USERNAME
    echo "用户 $USERNAME 已创建"
else
    echo "用户 $USERNAME 已存在"
fi

# 设置用户目录权限
mkdir -p /home/$USERNAME
cd /home/$USERNAME
chown -R $USERNAME:$USERNAME .

# 配置防火墙
echo "5. 配置防火墙..."
if command -v ufw >/dev/null 2>&1; then
    ufw allow ssh
    ufw allow 22
    ufw --force enable
    echo "防火墙已配置"
else
    apt install -y ufw
    ufw allow ssh
    ufw allow 22
    ufw --force enable
    echo "防火墙已安装并配置"
fi

# 配置时区
echo "6. 配置时区..."
timedatectl set-timezone Asia/Shanghai

# 配置系统限制
echo "7. 配置系统限制..."
cat >> /etc/security/limits.conf << EOF
# 交易机器人配置
$USERNAME soft nofile 65536
$USERNAME hard nofile 65536
$USERNAME soft nproc 32768
$USERNAME hard nproc 32768
EOF

# 配置内核参数
echo "8. 配置内核参数..."
cat >> /etc/sysctl.conf << EOF
# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
EOF

sysctl -p

# 创建日志轮转配置
echo "9. 配置日志轮转..."
cat > /etc/logrotate.d/trading-bot << EOF
/home/$USERNAME/trading_bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USERNAME $USERNAME
    postrotate
        systemctl reload trading-bot >/dev/null 2>&1 || true
    endscript
}
EOF

# 创建备份脚本
echo "10. 创建备份脚本..."
mkdir -p /home/$USERNAME/scripts
cat > /home/$USERNAME/scripts/backup_trading_bot.sh << EOF
#!/bin/bash
# 交易机器人备份脚本

BACKUP_DIR="/home/$USERNAME/backup"
PROJECT_DIR="/home/$USERNAME/trading_bot"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# 备份项目文件
tar -czf \$BACKUP_DIR/trading_bot_\$DATE.tar.gz -C \$PROJECT_DIR/.. trading_bot/ --exclude=logs/*.log.* 2>/dev/null

# 备份数据库
if [ -f "\$PROJECT_DIR/binance_monitor.db" ]; then
    cp \$PROJECT_DIR/binance_monitor.db \$BACKUP_DIR/binance_monitor_\$DATE.db
fi

# 删除30天前的备份
find \$BACKUP_DIR -name "trading_bot_*.tar.gz" -mtime +30 -delete
find \$BACKUP_DIR -name "binance_monitor_*.db" -mtime +30 -delete

echo "备份完成: \$BACKUP_DIR/trading_bot_\$DATE.tar.gz"
EOF

chmod +x /home/$USERNAME/scripts/backup_trading_bot.sh
chown -R $USERNAME:$USERNAME /home/$USERNAME/scripts

# 添加定时任务
echo "11. 配置定时任务..."
crontab -l > /tmp/current_cron 2>/dev/null || true
cat >> /tmp/current_cron << EOF
# 交易机器人备份任务
0 2 * * * /home/$USERNAME/scripts/backup_trading_bot.sh >> /home/$USERNAME/backup/backup.log 2>&1
# 清理日志
0 3 * * * find /home/$USERNAME/trading_bot/logs -name "*.log" -mtime +7 -delete
EOF
crontab /tmp/current_cron
rm -f /tmp/current_cron

# 创建系统监控脚本
echo "12. 创建系统监控脚本..."
cat > /home/$USERNAME/scripts/system_monitor.sh << EOF
#!/bin/bash
# 系统监控脚本

LOG_FILE="/home/$USERNAME/logs/system_monitor.log"
mkdir -p /home/$USERNAME/logs

echo "\$(date): 系统监控检查" >\u003e \$LOG_FILE

# 检查磁盘空间
DISK_USAGE=\$(df -h / | awk 'NR==2 {print \$5}' | sed 's/%//')
if [ \$DISK_USAGE -gt 80 ]; then
    echo "警告: 磁盘使用率超过80%，当前: \${DISK_USAGE}%" \u003e\u003e \$LOG_FILE
fi

# 检查内存使用
MEMORY_USAGE=\$(free | grep Mem | awk '{printf("%.1f", \$3/\$2 * 100.0)}')
echo "内存使用率: \${MEMORY_USAGE}%" \u003e\u003e \$LOG_FILE

# 检查CPU负载
CPU_LOAD=\$(uptime | awk -F'load average:' '{print \$2}' | awk '{print \$1}' | sed 's/,//')
echo "CPU负载: \$CPU_LOAD" \u003e\u003e \$LOG_FILE

# 检查网络连接
if ! ping -c 1 api.binance.com \u003e/dev/null 2\u003e\u00261; then
    echo "警告: 无法连接到Binance API" \u003e\u003e \$LOG_FILE
fi
EOF

chmod +x /home/$USERNAME/scripts/system_monitor.sh
chown -R $USERNAME:$USERNAME /home/$USERNAME/scripts

# 添加系统监控定时任务
sudo -u $USERNAME crontab -l > /tmp/user_cron 2>/dev/null || true
cat >> /tmp/user_cron << EOF
# 系统监控
*/10 * * * * /home/$USERNAME/scripts/system_monitor.sh
EOF
sudo -u $USERNAME crontab /tmp/user_cron
rm -f /tmp/user_cron

# 安装Node.js（可选，用于更高级的监控）
echo "13. 安装Node.js（可选）..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 创建监控网页（可选）
echo "14. 创建简单监控网页..."
mkdir -p /var/www/html/trading-bot
cat > /var/www/html/trading-bot/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>交易机器人监控</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>交易机器人监控面板</h1>
    <p>状态: <span id="status">检查中...</span></p>
    <p>最后更新: <span id="lastUpdate"></span></p>

    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                })
                .catch(error => {
                    document.getElementById('status').textContent = '连接失败';
                });
        }

        setInterval(updateStatus, 5000);
        updateStatus();
    </script>
</body>
</html>
EOF

# 设置权限
chown -R www-data:www-data /var/www/html/trading-bot

# 创建安装完成脚本
cat > /home/$USERNAME/scripts/install_complete.sh << EOF
#!/bin/bash

echo "=================================="
echo "阿里云服务器初始化完成！"
echo "=================================="
echo ""
echo "系统信息："
echo "- 主机名: \$(hostname)"
echo "- 公网IP: \$(curl -s ifconfig.me)"
echo "- 内网IP: \$(hostname -I | awk '{print \$1}')"
echo "- 系统版本: \$(lsb_release -d | cut -f2)"
echo "- Python版本: \$(python3 --version)"
echo "- 当前时间: \$(date)"
echo ""
echo "用户账户："
echo "- 交易机器人用户: $USERNAME"
echo "- 用户目录: /home/$USERNAME"
echo ""
echo "已安装的组件："
echo "- Python3 和 pip"
echo "- 虚拟环境支持"
echo "- 防火墙 (UFW)"
echo "- 系统监控工具"
echo "- 日志轮转"
echo "- 定时任务"
echo ""
echo "下一步操作："
echo "1. 切换到交易机器人用户: sudo su - $USERNAME"
echo "2. 上传交易机器人程序文件"
echo "3. 配置 telegram_config.py"
echo "4. 测试程序运行"
echo ""
echo "常用命令："
echo "- 查看系统状态: htop"
echo "- 查看网络状态: nload"
echo "- 查看磁盘使用: df -h"
echo "- 查看内存使用: free -h"
echo "- 查看服务状态: sudo systemctl status [服务名]"
echo ""
echo "监控页面: http://\$(curl -s ifconfig.me)/trading-bot/"
echo "=================================="
EOF

chmod +x /home/$USERNAME/scripts/install_complete.sh
chown -R $USERNAME:$USERNAME /home/$USERNAME/scripts

echo "=================================="
echo "阿里云服务器初始化完成！"
echo "=================================="
echo ""
echo "请运行以下命令查看详细信息："
echo "sudo /home/$USERNAME/scripts/install_complete.sh"
echo ""
echo "或者切换到交易机器人用户："
echo "sudo su - $USERNAME"
echo "=================================="