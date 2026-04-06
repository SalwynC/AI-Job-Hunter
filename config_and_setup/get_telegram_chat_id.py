#!/usr/bin/env python3
"""
Get Your Telegram Chat ID
==========================

This script helps you get your Telegram Chat ID for the AI Job Hunter bot.

Steps:
1. Create a bot with @BotFather (get TOKEN)
2. Run this script with your bot token
3. Send a message to your bot
4. Script will display your Chat ID
"""

import sys
import time
from telegram import Bot


def get_chat_id(bot_token: str) -> str:
    """
    Get Telegram Chat ID by polling for messages.
    
    Args:
        bot_token: Your bot token from @BotFather
        
    Returns:
        Chat ID as string
    """
    print("\n" + "="*60)
    print("GETTING YOUR TELEGRAM CHAT ID")
    print("="*60)
    
    try:
        # Create bot
        bot = Bot(token=bot_token)
        
        # Verify bot token
        try:
            me = bot.get_me()
            print(f"\n✅ Bot verified: @{me.username}")
        except Exception as e:
            print(f"\n❌ Invalid bot token: {e}")
            return None
        
        # Instructions
        print(f"\n📱 INSTRUCTIONS:")
        print(f"1. Open Telegram")
        print(f"2. Search for: @{me.username}")
        print(f"3. Send any message (e.g., 'Hello', 'Test', or just '/start')")
        print(f"4. Once you've sent a message, press Enter here to continue...")
        
        input("\n⏳ Waiting for message... (Press Enter when done sending message to bot)")
        
        # Get updates
        print("\n⏳ Checking for messages...")
        time.sleep(2)  # Give Telegram time to register message
        
        updates = bot.get_updates()
        
        if not updates:
            print("❌ No messages found. Try:")
            print("   1. Make sure you sent a message to your bot")
            print("   2. Check your internet connection")
            print("   3. Try again")
            return None
        
        # Find chat ID
        for update in updates:
            if update.message:
                chat_id = update.message.chat_id
                user = update.message.from_user
                
                print(f"\n✅ Message found!")
                print(f"   Chat ID: {chat_id}")
                print(f"   From: {user.first_name} ({user.username or 'no username'})")
                print(f"   Message: {update.message.text}")
                
                return str(chat_id)
        
        print("❌ No chat ID found")
        return None
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"   - Check bot token is correct")
        print(f"   - Check you have internet connection")
        print(f"   - Check Telegram app is working")
        return None


def main():
    """Main function."""
    print("\n🤖 "*20)
    print("TELEGRAM CHAT ID RETRIEVER")
    print("🤖 "*20)
    
    # Get bot token
    bot_token = input("\nEnter your Telegram bot token (from @BotFather): ").strip()
    
    if not bot_token:
        print("❌ Bot token cannot be empty")
        return 1
    
    # Get chat ID
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        print(f"\n{'='*60}")
        print(f"YOUR CHAT ID: {chat_id}")
        print(f"{'='*60}")
        print(f"\nAdd this to your .env file:")
        print(f"   TELEGRAM_BOT_TOKEN={bot_token}")
        print(f"   TELEGRAM_CHAT_ID={chat_id}")
        print(f"\nFor group chats:")
        print(f"   1. Create a group/channel")
        print(f"   2. Add your bot to the group")
        print(f"   3. Send a message")
        print(f"   4. Run this script again to get the group chat ID")
        return 0
    else:
        print("\n❌ Could not retrieve chat ID")
        return 1


if __name__ == "__main__":
    sys.exit(main())
