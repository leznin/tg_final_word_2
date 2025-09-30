#!/usr/bin/env python3
"""
Fix webhook allowed_updates to include payment events
"""
import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

def make_request(url, method="GET", data=None):
    """Make HTTP request"""
    try:
        if data:
            data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
        else:
            req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def fix_webhook():
    """Fix webhook with proper allowed_updates"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return False

    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL not found")
        return False

    # Set webhook with proper allowed_updates
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = {
        "url": WEBHOOK_URL,
        "allowed_updates": json.dumps([
            "message", "edited_message", "callback_query",
            "pre_checkout_query", "successful_payment",
            "my_chat_member", "chat_member", "chat_join_request"
        ])
    }

    data = make_request(url, method="POST", data=params)

    if data and data.get("ok"):
        print("✅ Webhook fixed successfully!")
        print(f"   URL: {WEBHOOK_URL}")
        print("   Allowed updates: pre_checkout_query, successful_payment, etc.")
        return True
    else:
        print("❌ Failed to fix webhook")
        print(f"Response: {data}")
        return False

def check_webhook():
    """Check current webhook info"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    data = make_request(url)

    if data and data.get("ok"):
        webhook_info = data.get("result", {})
        print("📋 Current webhook info:")
        print(f"   URL: {webhook_info.get('url', 'Not set')}")
        print(f"   Allowed updates: {webhook_info.get('allowed_updates', [])}")
        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
    else:
        print("❌ Failed to get webhook info")

if __name__ == "__main__":
    print("🔧 FIXING WEBHOOK ALLOWED_UPDATES")
    print("=" * 40)

    print("1. Current webhook info:")
    check_webhook()
    print()

    print("2. Fixing webhook...")
    if fix_webhook():
        print()
        print("3. Verifying fix...")
        check_webhook()
        print("\n✅ Webhook fix completed! Now payment events should work.")
    else:
        print("\n❌ Failed to fix webhook")
