#!/usr/bin/env python3
"""
配置文件 - 存储Telegram Bot配置和其他敏感信息
使用单独的Python文件来存储配置，便于管理和保护敏感信息
"""

import os
from typing import Optional

class Config:
    """配置管理类"""

    # Telegram Bot配置
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置"""
        cls.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        cls.TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    @classmethod
    def load_from_file(cls, config_file: str = 'telegram_config.py'):
        """从配置文件加载"""
        try:
            # 动态导入配置文件
            import importlib.util
            spec = importlib.util.spec_from_file_location("telegram_config", config_file)
            if spec and spec.loader:
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)

                if hasattr(config_module, 'TELEGRAM_BOT_TOKEN'):
                    cls.TELEGRAM_BOT_TOKEN = config_module.TELEGRAM_BOT_TOKEN
                if hasattr(config_module, 'TELEGRAM_CHAT_ID'):
                    cls.TELEGRAM_CHAT_ID = config_module.TELEGRAM_CHAT_ID

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    @classmethod
    def save_to_file(cls, bot_token: str, chat_id: str, config_file: str = 'telegram_config.py'):
        """保存配置到文件"""
        config_content = f'''# Telegram Bot配置文件
# 请妥善保管此文件，不要上传到版本控制系统

TELEGRAM_BOT_TOKEN = "{bot_token}"
TELEGRAM_CHAT_ID = "{chat_id}"
'''
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            # 设置文件权限为仅当前用户可读写
            os.chmod(config_file, 0o600)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    @classmethod
    def get_telegram_config(cls) -> tuple:
        """获取Telegram配置"""
        # 优先从环境变量加载
        cls.load_from_env()

        # 如果环境变量没有，尝试从配置文件加载
        if not cls.TELEGRAM_BOT_TOKEN or not cls.TELEGRAM_CHAT_ID:
            cls.load_from_file()

        return cls.TELEGRAM_BOT_TOKEN, cls.TELEGRAM_CHAT_ID

    @classmethod
    def is_telegram_configured(cls) -> bool:
        """检查Telegram是否已配置"""
        bot_token, chat_id = cls.get_telegram_config()
        return bool(bot_token and chat_id)

    @classmethod
    def get_config_info(cls) -> dict:
        """获取配置信息（不包含敏感信息）"""
        bot_token, chat_id = cls.get_telegram_config()
        return {
            'telegram_configured': cls.is_telegram_configured(),
            'bot_token_set': bool(bot_token),
            'chat_id_set': bool(chat_id),
            'config_source': '环境变量' if os.environ.get('TELEGRAM_BOT_TOKEN') else '配置文件'
        }

# 初始化配置
Config.load_from_env()
Config.load_from_file()