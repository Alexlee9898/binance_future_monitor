#!/usr/bin/env python3
"""
Telegram Bot配置设置脚本
用于安全地设置和保存Telegram Bot配置
"""

import os
import sys
from config import Config

def setup_telegram_config():
    """交互式设置Telegram配置"""
    print("=== Telegram Bot配置设置 ===")
    print()
    print("请准备以下信息：")
    print("1. Telegram Bot Token - 从 @BotFather 获取")
    print("2. Telegram Chat ID - 你的用户ID或群组ID")
    print()

    # 检查现有配置
    current_config = Config.get_config_info()
    if current_config['telegram_configured']:
        print(f"⚠️  检测到已有配置（来源：{current_config['config_source']}）")
        response = input("是否重新配置？(y/N): ").strip().lower()
        if response != 'y':
            print("取消配置")
            return

    print()
    bot_token = input("请输入Telegram Bot Token: ").strip()
    if not bot_token:
        print("❌ Bot Token不能为空")
        return

    chat_id = input("请输入Telegram Chat ID: ").strip()
    if not chat_id:
        print("❌ Chat ID不能为空")
        return

    # 验证配置
    print("\n正在验证配置...")

    # 保存配置
    if Config.save_to_file(bot_token, chat_id):
        print("\n✅ 配置保存成功！")
        print(f"配置文件已创建：telegram_config.py")
        print("文件权限已设置为仅当前用户可读写")

        # 测试配置
        print("\n正在测试配置...")
        test_result = test_telegram_config(bot_token, chat_id)

        if test_result:
            print("\n🎉 Telegram配置完成并测试通过！")
            print("你现在可以运行监控程序，警报将通过Telegram推送")
        else:
            print("\n⚠️  配置已保存，但测试失败")
            print("请检查Bot Token和Chat ID是否正确")
            print("你可以稍后手动测试：python3 test_alert_push.py")
    else:
        print("\n❌ 配置保存失败")

def test_telegram_config(bot_token: str, chat_id: str) -> bool:
    """测试Telegram配置"""
    try:
        import requests

        message = "🧪 Telegram Bot配置测试\n\n如果收到此消息，说明配置正确！"
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, params=params, timeout=30)

        if response.json().get('ok'):
            print("✅ Telegram测试消息发送成功！")
            return True
        else:
            print(f"❌ Telegram测试失败：{response.json()}")
            return False

    except Exception as e:
        print(f"❌ Telegram测试异常：{e}")
        return False

def show_current_config():
    """显示当前配置信息（不包含敏感信息）"""
    print("=== 当前配置信息 ===")
    config_info = Config.get_config_info()

    print(f"Telegram配置状态: {'✅ 已配置' if config_info['telegram_configured'] else '❌ 未配置'}")
    print(f"Bot Token: {'✅ 已设置' if config_info['bot_token_set'] else '❌ 未设置'}")
    print(f"Chat ID: {'✅ 已设置' if config_info['chat_id_set'] else '❌ 未设置'}")
    print(f"配置来源: {config_info['config_source']}")
    print()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--show':
            show_current_config()
        elif sys.argv[1] == '--help':
            print("使用方法：")
            print("  python3 setup_telegram.py         # 交互式配置")
            print("  python3 setup_telegram.py --show  # 显示当前配置")
            print("  python3 setup_telegram.py --help  # 显示帮助")
        else:
            print("未知参数，使用 --help 查看帮助")
    else:
        setup_telegram_config()

if __name__ == '__main__':
    main()