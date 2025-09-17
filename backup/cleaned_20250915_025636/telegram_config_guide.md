# Telegram推送配置指南

## 🚨 当前状态
- **Telegram推送**: 未启用 (环境变量未配置)
- **警报触发**: 正常 (27个警报已记录)
- **新阈值**: ✅ OI ≥ 5% 且价格 ≥ 2%

## 📱 配置步骤

### 步骤1: 创建Telegram Bot
1. 打开Telegram，搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 输入bot名称，例如: `Binance监控警报`
4. 输入bot用户名，必须以`bot`结尾，例如: `binance_monitor_alert_bot`
5. 保存返回的Bot Token (格式: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 步骤2: 获取Chat ID
1. 在Telegram中搜索你刚创建的bot
2. 发送任意消息给bot，例如: `/start`
3. 在浏览器访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 在返回的JSON中找到 `chat.id` 字段

### 步骤3: 配置环境变量
在终端执行以下命令:
```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

### 步骤4: 重启监控系统
```bash
# 停止当前监控进程
pkill -f enhanced_monitor.py

# 重新启动监控
python3 enhanced_monitor.py
```

## 🔧 立即测试配置

### 选项1: 临时配置测试
```bash
# 设置环境变量并立即测试
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"

# 运行测试
python3 test_telegram_setup.py
```

### 选项2: 手动发送测试消息
```bash
# 使用测试脚本发送测试消息
python3 -c "
import os
os.environ['TELEGRAM_BOT_TOKEN'] = '你的Bot Token'
os.environ['TELEGRAM_CHAT_ID'] = '你的Chat ID'

# 这里可以添加发送测试消息的代码
"
```

## 📊 当前警报数据

最近的数据库警报记录:
- **UBUSDT**: OI +14.97%, 价格 +39.32% (HIGH级别)
- **XPINUSDT**: OI +49.77%, 价格 -8.06% (CRITICAL级别)
- **HOLOUSDT**: OI +10.81%, 价格 +2.11% (MEDIUM级别)

## 🎯 警报级别说明

- **💥 CRITICAL**: OI变化≥15% 或 价格变化≥5%
- **🔥 HIGH**: OI变化≥12% 或 价格变化≥4%
- **🚨 MEDIUM**: OI变化≥10% 或 价格变化≥3%
- **⚠️ LOW**: OI变化≥5% 或 价格变化≥2%

## 📝 消息格式示例

当警报触发时，你会收到这样的消息:

```
💥 <b>Binance永续合约异常警报</b>

📊 <b>交易对:</b> BTCUSDT

📈 <b>持仓量变化:</b> +15.50%
💰 <b>当前持仓量:</b> 91,000
📊 <b>15分钟前持仓量:</b> 78,900

💹 <b>价格变化:</b> +8.20%
💰 <b>当前价格:</b> $115,500.00
📊 <b>15分钟前价格:</b> $106,700.00

💎 <b>当前持仓总价值:</b> 10,510,500,000.00 USDT

⏰ <b>检测时间:</b> 2025-09-15 02:45:30

⚠️  请注意风险控制！
```

## ⚠️ 重要提醒

1. **Token安全**: 不要分享你的Bot Token
2. **Chat ID**: 确保使用正确的Chat ID
3. **网络连接**: 确保服务器可以访问Telegram API
4. **测试验证**: 配置完成后务必测试

## 🔍 故障排除

如果配置后仍无法接收消息:

1. **检查Token有效性**: 使用测试脚本验证
2. **确认Chat ID**: 确保bot和chat ID匹配
3. **查看日志**: 检查系统日志中的TELEGRAM_ERROR
4. **网络问题**: 确认能访问api.telegram.org

## 📞 技术支持

配置完成后，系统会自动:
- ✅ 监控528个永续合约
- ✅ 每15分钟检查一次
- ✅ 自动判断警报级别
- ✅ 发送格式化消息到Telegram

当前系统运行正常，只需要配置Telegram即可开始接收推送！"}