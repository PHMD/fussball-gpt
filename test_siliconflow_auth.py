#!/usr/bin/env python3
"""
Silicon Flow API Authentication Test Script

Helps diagnose the "401 Api key is invalid" error by testing different
API endpoints and authentication methods.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SILICONFLOW_API_KEY")

print("=" * 80)
print("🔑 SILICON FLOW API AUTHENTICATION TEST")
print("=" * 80)
print()

if not API_KEY:
    print("❌ ERROR: SILICONFLOW_API_KEY not found in .env file")
    print("Please add your API key to .env:")
    print("SILICONFLOW_API_KEY=your_key_here")
    exit(1)

print(f"✅ API Key found: {API_KEY[:10]}...{API_KEY[-10:]}")
print()

# Test different endpoints and auth methods
endpoints_to_test = [
    {
        "name": "Silicon Flow Official Endpoint",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "auth_method": "Bearer"
    },
    {
        "name": "Alternative Endpoint (siliconflow.com)",
        "url": "https://api.siliconflow.com/v1/chat/completions",
        "auth_method": "Bearer"
    },
    {
        "name": "Alternative Endpoint (.ai TLD)",
        "url": "https://api.siliconflow.ai/v1/chat/completions",
        "auth_method": "Bearer"
    }
]

test_payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello' in German."}
    ],
    "max_tokens": 50,
    "temperature": 0.7
}

for i, endpoint_config in enumerate(endpoints_to_test, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}/{len(endpoints_to_test)}: {endpoint_config['name']}")
    print(f"URL: {endpoint_config['url']}")
    print("=" * 80)

    headers = {
        "Authorization": f"{endpoint_config['auth_method']} {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print("📤 Sending request...")
        response = requests.post(
            endpoint_config['url'],
            headers=headers,
            json=test_payload,
            timeout=30
        )

        print(f"📥 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS! API is working")
            data = response.json()
            print(f"Response: {data['choices'][0]['message']['content']}")
            print(f"\n🎉 Use this endpoint: {endpoint_config['url']}")
            break
        elif response.status_code == 401:
            print("❌ Authentication failed (401)")
            print(f"Error: {response.text}")
        elif response.status_code == 404:
            print("❌ Endpoint not found (404)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except requests.exceptions.Timeout:
        print("⏱️  Request timed out (30 seconds)")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - endpoint may not exist")
    except Exception as e:
        print(f"❌ Error: {e}")

# Additional diagnostics
print("\n" + "=" * 80)
print("💡 TROUBLESHOOTING TIPS")
print("=" * 80)
print("""
If all tests failed:

1. **Verify API Key Activation:**
   → Visit https://www.siliconflow.com
   → Check if your API key is active
   → Look for "API Keys" or "Developer" section

2. **Check Account Credits:**
   → Silicon Flow may require pre-paid credits
   → Verify you have available balance

3. **Confirm API Access:**
   → Some platforms require email verification
   → Check for any pending account setup steps

4. **Try Alternative Models:**
   → Instead of "Qwen/Qwen2.5-14B-Instruct", try:
     - "Qwen/Qwen2-7B-Instruct"
     - "meta-llama/Llama-2-7b-chat-hf"

5. **Check API Documentation:**
   → Visit https://docs.siliconflow.com
   → Look for authentication examples
   → Verify correct model names

6. **Contact Silicon Flow Support:**
   → If authentication continues to fail
   → They may need to activate your account manually

Alternative: Use Hugging Face Inference API
→ Many of the same models available at https://huggingface.co/inference-api
→ May have easier authentication setup
""")

print("\n" + "=" * 80)
print("📧 Need Help?")
print("=" * 80)
print("Visit Silicon Flow documentation: https://docs.siliconflow.com")
print("Or check model availability: https://www.siliconflow.com/models")
