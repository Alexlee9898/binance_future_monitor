# 阿里云服务器部署指南

## 程序已停止
✅ 已成功停止所有正在运行的监控程序
✅ 已清理所有PID文件

## 阿里云部署准备清单

### 1. 服务器环境要求
```bash
# 系统要求
- Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- Python 3.8+
- 至少2GB内存
- 10GB可用磁盘空间
```

### 2. 依赖安装
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 创建虚拟环境
python3 -m venv trading_bot_env
source trading_bot_env/bin/activate
```

### 3. Python依赖包
```bash
# 安装主要依赖
pip install requests
pip install sqlite3
pip install logging
pip install json
pip install time
pip install datetime
pip install threading
pip install urllib.parse
```

### 4. 文件上传清单
需要上传以下文件到服务器：
- ✅ enhanced_monitor.py (主监控程序)
- ✅ database_manager.py (数据库管理)
- ✅ config.py (配置文件)
- ✅ logger_manager.py (日志管理)
- ✅ telegram_config.py (Telegram配置)
- ✅ check_change_rate.py (变化率检查)
- ✅ setup_telegram.py (Telegram设置)
- ✅ data/ (数据目录)
- ✅ logs/ (日志目录)

### 5. 配置文件设置
```bash
# 需要修改config.py中的以下设置
- API密钥和密钥
- Telegram机器人令牌
- 数据库路径（使用绝对路径）
- 日志文件路径（使用绝对路径）
```

### 6. 部署步骤
```bash
# 1. 上传文件到服务器
scp -r /本地路径/交易机器人/ 用户名@服务器IP:/home/用户名/

# 2. 设置权限
chmod +x enhanced_monitor.py

# 3. 创建日志和数据目录
mkdir -p logs data

# 4. 测试运行
python3 enhanced_monitor.py

# 5. 后台运行（使用nohup或screen）
nohup python3 enhanced_monitor.py > output.log 2>&1 &
```

### 7. 系统服务设置（可选）
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/trading-bot.service

# 添加以下内容
[Unit]
Description=Trading Bot Monitor
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/交易机器人
ExecStart=/home/你的用户名/trading_bot_env/bin/python3 enhanced_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 8. 安全设置
```bash
# 设置防火墙
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw enable

# 设置文件权限
chmod 600 telegram_config.py
chmod 600 config.py
```

### 9. 监控和日志
```bash
# 查看运行状态
sudo systemctl status trading-bot

# 查看日志
sudo journalctl -u trading-bot -f

# 查看程序日志
tail -f logs/enhanced_binance_monitor.log
```

### 10. 备份策略
```bash
# 设置定期备份
# 备份数据库和配置文件
0 2 * * * tar -czf /backup/trading_bot_$(date +\%Y\%m\%d).tar.gz /home/用户名/交易机器人/
```

## 注意事项
⚠️ 确保API密钥安全，不要上传到公共代码仓库
⚠️ 设置适当的文件权限，保护敏感信息
⚠️ 配置防火墙规则，只允许必要的端口
⚠️ 定期检查磁盘空间，日志文件可能会很大
⚠️ 设置监控告警，及时了解程序运行状态

## 下一步操作
1. 准备阿里云服务器
2. 按照上述清单配置环境
3. 上传文件并测试运行
4. 配置系统服务和自动启动