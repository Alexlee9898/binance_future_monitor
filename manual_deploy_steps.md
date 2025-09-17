# 阿里云手动部署步骤

## 第一步：连接服务器

```bash
ssh root@8.134.103.197
```

输入密码后进入服务器

## 第二步：服务器初始化

在服务器上依次执行以下命令：

### 1. 更新系统
```bash
apt update && apt upgrade -y
```

### 2. 安装基础软件
```bash
apt install -y python3 python3-pip python3-venv curl wget vim htop git ufw
```

### 3. 创建专用用户
```bash
# 创建用户
useradd -m -s /bin/bash tradingbot

# 设置密码（请输入一个安全密码）
passwd tradingbot

# 添加到sudo组
usermod -aG sudo tradingbot
```

### 4. 创建目录结构
```bash
mkdir -p /home/tradingbot/trading_bot/{data,logs,backup,scripts}
chown -R tradingbot:tradingbot /home/tradingbot
```

### 5. 配置防火墙
```bash
ufw allow ssh
ufw allow 22
echo "y" | ufw enable
ufw status
```

### 6. 设置时区
```bash
timedatectl set-timezone Asia/Shanghai
```

## 第三步：上传程序文件

### 在新终端中执行（不要退出当前SSH连接）：

1. 首先确认本地有部署包：
```bash
ls -la trading_bot_aliyun_20250917_055629.tar.gz
```

2. 上传文件到服务器：
```bash
scp trading_bot_aliyun_20250917_055629.tar.gz root@8.134.103.197:/tmp/
```

3. 回到服务器的SSH终端，移动文件：
```bash
mv /tmp/trading_bot_aliyun_*.tar.gz /home/tradingbot/
cd /home/tradingbot/
```

4. 解压文件：
```bash
tar -xzf trading_bot_aliyun_*.tar.gz
```

5. 整理文件：
```bash
mv aliyun_trading_bot_package/* trading_bot/
rm -rf aliyun_trading_bot_package/
rm -f trading_bot_aliyun_*.tar.gz
```

6. 设置权限：
```bash
chown -R tradingbot:tradingbot /home/tradingbot/trading_bot
chmod +x /home/tradingbot/trading_bot/*.sh
```

## 第四步：切换到tradingbot用户

```bash
su - tradingbot
cd /home/tradingbot/trading_bot
```

## 第五步：配置环境

### 1. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install --upgrade pip
pip install requests
```

### 3. 检查文件结构
```bash
ls -la
```

## 第六步：配置Telegram

### 编辑配置文件：
```bash
vim telegram_config.py
```

### 按i进入编辑模式，修改以下内容：
```python
# Telegram Bot配置文件
# 请妥善保管此文件，不要上传到版本控制系统

TELEGRAM_BOT_TOKEN = "你的机器人Token"
TELEGRAM_CHAT_ID = "你的聊天ID"
```

### 保存退出：
- 按 `ESC`
- 输入 `:wq`
- 按 `Enter`

## 第七步：测试运行

### 1. 测试模式运行
```bash
./start_bot.sh test
```

### 2. 如果看到正常运行信息，按 Ctrl+C 停止测试

### 3. 正式后台运行
```bash
./start_bot.sh production
```

## 第八步：验证部署

### 1. 检查状态
```bash
./check_status.sh
```

### 2. 查看日志
```bash
tail -f logs/enhanced_binance_monitor.log
```

### 3. 检查进程
```bash
ps aux | grep python
```

## 第九步：系统服务安装（可选）

如果需要设置为系统服务：
```bash
exit  # 先退出tradingbot用户
sudo /home/tradingbot/trading_bot/install_service.sh
sudo systemctl start trading-bot
sudo systemctl enable trading-bot
```

## 🔧 常用管理命令

```bash
# 启动程序
./start_bot.sh production

# 停止程序
./stop_bot.sh

# 检查状态
./check_status.sh

# 查看日志
tail -f logs/enhanced_binance_monitor.log

# 查看系统服务状态
sudo systemctl status trading-bot
```

## 📞 故障排除

如果遇到问题，请检查：
1. 网络连接：`ping api.binance.com`
2. 磁盘空间：`df -h`
3. 内存使用：`free -h`
4. 进程状态：`ps aux | grep python`

获取帮助信息：
```bash
./check_status.sh
tail -20 logs/enhanced_binance_monitor.log
```

## ✅ 部署完成检查清单

- [ ] 成功连接到服务器
- [ ] 系统已更新
- [ ] tradingbot用户已创建
- [ ] 文件已上传并解压
- [ ] 依赖已安装
- [ ] telegram_config.py已配置
- [ ] 程序测试运行正常
- [ ] 程序已在后台运行
- [ ] 状态检查显示正常

---

🎉 **恭喜！完成这些步骤后，您的交易机器人就成功部署到阿里云服务器了！**