# Telegram Bot配置文件模板
# 请复制此文件为 telegram_config.py 并填入你的实际配置
# 注意：telegram_config.py 已被添加到 .gitignore，不会被版本控制跟踪

# Telegram Bot Token - 从 @BotFather 获取
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Telegram Chat ID - 你的用户ID或群组ID
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

# 获取Chat ID的方法：
# 1. 给Bot发送一条消息
# 2. 访问：https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# 3. 在返回的JSON中找到 "chat" -> "id" 字段