# Telegram警报配置指南

## 测试结果总结

✅ **警报系统运行完全正常！**

### 当前状态
- 📊 系统正在持续监控528个永续合约
- 🚨 最近24小时已触发26个警报
- 💥 CRITICAL级别警报：21个
- 🔥 HIGH级别警报：1个
- 🚨 MEDIUM级别警报：1个

### 警报触发条件
- 持仓量变化≥8% 且 价格变化≥2%
- 警报级别根据变化幅度自动判断

### 最严重的警报示例
- 交易对：NEIROETHUSDT
- OI变化：+43.67%
- 价格变化：-20.04%
- 级别：CRITICAL

## 如何配置真实Telegram推送

### 步骤1：创建Telegram Bot
1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 命令
3. 输入bot名称和用户名
4. 保存返回的Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 步骤2：获取Chat ID
1. 在Telegram中搜索你刚创建的bot
2. 发送任意消息给bot
3. 访问：`https://api.telegram.org/bot&lt;YOUR_BOT_TOKEN&gt;/getUpdates`
4. 找到返回数据中的`chat.id`

### 步骤3：配置环境变量
```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

### 步骤4：重启监控系统
```bash
pkill -TERM -f enhanced_monitor.py
python3 enhanced_monitor.py
```

## 警报消息格式

当警报触发时，系统会发送格式化的Telegram消息：

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

⏰ <b>检测时间:</b> 2025-09-14 01:11:41

⚠️  请注意风险控制！
```

## 警报级别说明

- **💥 CRITICAL**：OI变化≥15% 或 价格变化≥5%
- **🔥 HIGH**：OI变化≥12% 或 价格变化≥4%
- **🚨 MEDIUM**：OI变化≥10% 或 价格变化≥3%
- **⚠️ LOW**：OI变化≥8% 或 价格变化≥2%

## 当前监控状态

系统正在实时监控，每15分钟检查一次，当发现符合条件的异常波动时会立即发送Telegram警报。

**注意**：配置真实Token后，系统将自动开始发送警报消息到您指定的Telegram频道。