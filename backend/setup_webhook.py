#!/usr/bin/env python3
"""
Script to setup and verify Telegram webhook
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

def check_webhook_info():
    """Check current webhook info"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    data = make_request(url)

    if data and data.get("ok"):
        webhook_info = data.get("result", {})
        print("📋 Current webhook info:")
        print(f"   URL: {webhook_info.get('url', 'Not set')}")
        print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
        print(f"   Last error date: {webhook_info.get('last_error_date')}")
        print(f"   Last error message: {webhook_info.get('last_error_message')}")
    else:
        print("❌ Failed to get webhook info")

def delete_webhook():
    """Delete current webhook"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    data = make_request(url, method="POST")

    if data and data.get("ok"):
        print("✅ Webhook deleted successfully")
        return True
    else:
        print("❌ Failed to delete webhook")
        return False

def set_webhook():
    """Set new webhook"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment")
        return False

    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL not found in environment")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = {"url": WEBHOOK_URL}

    data = make_request(url, method="POST", data=params)

    if data and data.get("ok"):
        print("✅ Webhook set successfully")
        print(f"   URL: {WEBHOOK_URL}")
        return True
    else:
        print("❌ Failed to set webhook")
        return False

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL not found in environment")
        return False

    health_url = WEBHOOK_URL.replace('/webhook', '/health')

    try:
        req = urllib.request.Request(health_url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print("✅ Webhook endpoint is accessible")
                return True
            else:
                print(f"❌ Webhook endpoint returned status {response.status}")
                return False
    except Exception as e:
        print(f"❌ Cannot reach webhook endpoint: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 TELEGRAM WEBHOOK SETUP")
    print("=" * 40)

    print(f"Bot Token: {'✅ Set' if BOT_TOKEN else '❌ Not set'}")
    print(f"Webhook URL: {WEBHOOK_URL if WEBHOOK_URL else '❌ Not set'}")
    print()

    # Check current webhook
    print("1. Checking current webhook...")
    check_webhook_info()
    print()

    # Test endpoint accessibility
    print("2. Testing webhook endpoint accessibility...")
    endpoint_ok = test_webhook_endpoint()
    print()

    if not endpoint_ok:
        print("⚠️  Webhook endpoint is not accessible!")
        print("   Make sure:")
        print("   - ngrok tunnel is running")
        print("   - FastAPI application is running")
        print("   - URL is correct")
        return

    # Setup webhook
    print("3. Setting up webhook...")
    if delete_webhook():
        if set_webhook():
            print("\n✅ Webhook setup completed!")
            print("Now test your bot by sending /start command")
        else:
            print("\n❌ Failed to set webhook")
    else:
        print("\n❌ Failed to delete old webhook")

if __name__ == "__main__":
    main()
