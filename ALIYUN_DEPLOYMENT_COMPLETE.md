# 🚀 阿里云服务器完整部署指南

## 📋 部署前准备

### 1. 阿里云服务器要求
- **系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **配置**: 最低2GB内存，建议4GB以上
- **磁盘**: 至少20GB可用空间
- **网络**: 公网IP，开放22端口(SSH)

### 2. 已准备的文件
✅ `trading_bot_aliyun_20250917_055629.tar.gz` - 完整的部署包
✅ `deploy_to_aliyun.sh` - 自动部署脚本
✅ `init_aliyun_server.sh` - 服务器初始化脚本
✅ `aliyun_deployment_guide.md` - 详细部署指南

---

## 🎯 快速部署步骤

### 步骤1: 服务器初始化
```bash
# 登录阿里云服务器
ssh root@你的服务器IP

# 下载并运行初始化脚本
wget https://你的文件地址/init_aliyun_server.sh
sudo chmod +x init_aliyun_server.sh
sudo ./init_aliyun_server.sh
```

### 步骤2: 上传并解压程序包
```bash
# 在本地电脑上执行
# 上传部署包到服务器
scp trading_bot_aliyun_20250917_055629.tar.gz tradingbot@你的服务器IP:/home/tradingbot/

# 登录服务器
ssh tradingbot@你的服务器IP

# 解压文件
tar -xzf trading_bot_aliyun_20250917_055629.tar.gz
cd aliyun_trading_bot_package
```

### 步骤3: 配置程序
```bash
# 编辑配置文件
vim telegram_config.py

# 填入以下信息：
# TELEGRAM_BOT_TOKEN = "你的机器人Token"
# TELEGRAM_CHAT_ID = "你的聊天ID"
```

### 步骤4: 安装依赖并测试
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 测试运行（前台模式）
./start_bot.sh test
```

### 步骤5: 正式部署
```bash
# 后台模式启动
./start_bot.sh production

# 检查状态
./check_status.sh

# 查看日志
tail -f logs/enhanced_binance_monitor.log
```

---

## 🛠️ 高级配置

### 系统服务安装
```bash
# 安装为系统服务（需要sudo权限）
sudo ./install_service.sh

# 管理服务
sudo systemctl start trading-bot
sudo systemctl status trading-bot
sudo systemctl enable trading-bot  # 开机自启
```

### 防火墙配置
```bash
# 查看防火墙状态
sudo ufw status

# 如果需要开放其他端口
sudo ufw allow 8080  # 例如开放8080端口
```

### 日志管理
```bash
# 实时查看日志
tail -f logs/enhanced_binance_monitor.log

# 查看系统服务日志
sudo journalctl -u trading-bot -f

# 日志轮转已自动配置，保留7天日志
```

---

## 📊 监控和维护

### 日常检查命令
```bash
# 检查程序状态
./check_status.sh

# 检查系统资源
htop
free -h
df -h

# 检查网络
ping api.binance.com
```

### 备份和恢复
```bash
# 手动备份
/home/tradingbot/scripts/backup_trading_bot.sh

# 备份文件位置
ls -la /home/tradingbot/backup/

# 恢复备份
tar -xzf /home/tradingbot/backup/trading_bot_备份日期.tar.gz
```

---

## 🔧 故障排除

### 常见问题

#### 1. 程序无法启动
```bash
# 检查Python环境
python3 --version
which python3

# 检查依赖
source venv/bin/activate
pip list

# 检查配置文件
ls -la telegram_config.py
```

#### 2. Telegram无法发送消息
```bash
# 测试Telegram配置
python3 -c "
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
print(f'Token: {TELEGRAM_BOT_TOKEN[:10]}...')
print(f'Chat ID: {TELEGRAM_CHAT_ID}')
"
```

#### 3. 数据库问题
```bash
# 检查数据库文件
ls -la binance_monitor.db

# 如果数据库损坏，可以删除后重建
mv binance_monitor.db binance_monitor.db.backup
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 清理日志
find logs/ -name "*.log.*" -mtime +3 -delete
```

---

## 📈 性能优化

### 1. 数据库优化
```bash
# 定期清理旧数据
sqlite3 binance_monitor.db "DELETE FROM monitoring_data WHERE timestamp < datetime('now', '-7 days');"
```

### 2. 日志级别调整
编辑 `enhanced_monitor.py`，修改日志级别：
```python
# 将 INFO 改为 WARNING 减少日志量
logging.basicConfig(level=logging.WARNING)
```

### 3. 监控频率调整
在配置文件中调整监控间隔：
```python
MONITOR_INTERVAL = 900  # 15分钟，根据需求调整
```

---

## 🚨 安全建议

### 1. SSH安全
```bash
# 修改SSH端口
sudo vim /etc/ssh/sshd_config
# 修改 Port 22 为其他端口

# 重启SSH服务
sudo systemctl restart sshd
```

### 2. 用户权限
```bash
# 禁止root远程登录
sudo vim /etc/ssh/sshd_config
# 设置 PermitRootLogin no
```

### 3. 文件权限
```bash
# 保护配置文件
chmod 600 telegram_config.py
chmod 600 config.py
```

---

## 📞 技术支持

如果遇到问题，请提供以下信息：
1. 服务器系统版本：`lsb_release -a`
2. Python版本：`python3 --version`
3. 错误日志：`tail -50 logs/enhanced_binance_monitor.log`
4. 系统状态：`./check_status.sh`
5. 进程状态：`ps aux | grep python`

---

## ✅ 部署检查清单

- [ ] 服务器已初始化
- [ ] 程序包已上传并解压
- [ ] Telegram配置已完成
- [ ] 依赖已安装
- [ ] 程序测试运行正常
- [ ] 已设置为后台运行
- [ ] 系统服务已安装（可选）
- [ ] 防火墙已配置
- [ ] 备份策略已设置
- [ ] 监控告警已配置

---

**🎉 恭喜！您的交易机器人已成功部署到阿里云服务器！**