#!/usr/bin/env python3
"""
Quick Model Connectivity Test
Tests all 15 models in ~30 seconds to see what works/what doesn't
"""

import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

# Simple German test prompt
TEST_PROMPT = "Sage 'Hallo' auf Deutsch."

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_status(model_name: str, status: str, message: str = "", time_ms: int = 0):
    """Print test result with color coding"""
    status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"

    # Pad model name for alignment
    padded_name = f"{model_name:<40}"

    if status == "success":
        print(f"{status_icon} {GREEN}{padded_name}{RESET} ({time_ms}ms)")
    elif status == "error":
        print(f"{status_icon} {RED}{padded_name}{RESET} {message}")
    else:
        print(f"{status_icon} {YELLOW}{padded_name}{RESET} {message}")

def test_anthropic_model(model_name: str) -> tuple[str, str, int]:
    """Test an Anthropic Claude model"""
    try:
        start = time.time()
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model=model_name,
            max_tokens=50,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        )

        elapsed_ms = int((time.time() - start) * 1000)
        return ("success", "", elapsed_ms)
    except Exception as e:
        error_msg = str(e)[:80]
        return ("error", error_msg, 0)

def test_openai_model(model_name: str) -> tuple[str, str, int]:
    """Test an OpenAI model"""
    try:
        start = time.time()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # gpt-5-pro uses Responses API (v1/responses endpoint)
        if model_name == "gpt-5-pro":
            response = client.responses.create(
                model=model_name,
                input=TEST_PROMPT,
                text={"max_output_tokens": 50}
            )
        # Other GPT-5 reasoning models use max_completion_tokens
        elif model_name.startswith("gpt-5"):
            response = client.chat.completions.create(
                model=model_name,
                max_completion_tokens=50,
                messages=[{"role": "user", "content": TEST_PROMPT}]
            )
        # GPT-4 and older use max_tokens
        else:
            response = client.chat.completions.create(
                model=model_name,
                max_tokens=50,
                messages=[{"role": "user", "content": TEST_PROMPT}]
            )

        elapsed_ms = int((time.time() - start) * 1000)
        return ("success", "", elapsed_ms)
    except Exception as e:
        error_msg = str(e)[:80]
        return ("error", error_msg, 0)

def test_mistral_model(model_name: str) -> tuple[str, str, int]:
    """Test a Mistral model via OpenAI-compatible API"""
    try:
        start = time.time()
        client = OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )

        response = client.chat.completions.create(
            model=model_name,
            max_tokens=50,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        )

        elapsed_ms = int((time.time() - start) * 1000)
        return ("success", "", elapsed_ms)
    except Exception as e:
        error_msg = str(e)[:80]
        return ("error", error_msg, 0)

def test_siliconflow_model(model_name: str) -> tuple[str, str, int]:
    """Test a SiliconFlow model via OpenAI-compatible API"""
    # Try both .cn and .com endpoints
    endpoints = ["https://api.siliconflow.cn/v1", "https://api.siliconflow.com/v1"]

    for base_url in endpoints:
        try:
            start = time.time()
            client = OpenAI(
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url=base_url
            )

            response = client.chat.completions.create(
                model=model_name,
                max_tokens=50,
                messages=[{"role": "user", "content": TEST_PROMPT}]
            )

            elapsed_ms = int((time.time() - start) * 1000)
            return ("success", "", elapsed_ms)
        except Exception as e:
            # If .cn failed, try .com
            if base_url == endpoints[0]:
                continue
            # If both failed, return error from .com attempt
            error_msg = str(e)[:80]
            return ("error", error_msg, 0)

    return ("error", "Both endpoints failed", 0)

def main():
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}  QUICK MODEL CONNECTIVITY TEST{RESET}")
    print(f"{BLUE}  Testing 15 models with: '{TEST_PROMPT}'{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    results = {
        "success": [],
        "error": []
    }

    # Test Anthropic models
    print(f"\n{BLUE}[ANTHROPIC]{RESET}")
    anthropic_models = [
        "claude-sonnet-4-5",           # Premium tier - SOTA reasoning
        "claude-haiku-4-5",            # Budget tier - Speed optimized
        # "claude-opus-4-1-20250805",  # REMOVED: Too expensive for benchmark
    ]

    for model in anthropic_models:
        status, msg, time_ms = test_anthropic_model(model)
        print_status(f"Anthropic: {model}", status, msg, time_ms)
        if status == "success":
            results["success"].append(f"anthropic:{model}")
        else:
            results["error"].append(f"anthropic:{model}")

    # Test OpenAI models
    print(f"\n{BLUE}[OPENAI]{RESET}")
    openai_models = [
        "gpt-5",                # Reasoning model - deep analysis
        "gpt-5-mini",          # Reasoning model - balanced
        "gpt-5-nano",          # Reasoning model - budget
        "gpt-5-chat-latest",   # Non-reasoning - conversational (ChatGPT model)
        # "gpt-5-pro",         # REMOVED: Too expensive + requires special access
    ]

    for model in openai_models:
        status, msg, time_ms = test_openai_model(model)
        print_status(f"OpenAI: {model}", status, msg, time_ms)
        if status == "success":
            results["success"].append(f"openai:{model}")
        else:
            results["error"].append(f"openai:{model}")

    # Test Mistral models
    print(f"\n{BLUE}[MISTRAL]{RESET}")
    mistral_models = [
        "mistral-large-latest",  # More stable than version numbers
        "mistral-medium-latest",
        "mistral-small-latest",
    ]

    for model in mistral_models:
        status, msg, time_ms = test_mistral_model(model)
        print_status(f"Mistral: {model}", status, msg, time_ms)
        if status == "success":
            results["success"].append(f"mistral:{model}")
        else:
            results["error"].append(f"mistral:{model}")

    # Test SiliconFlow models
    print(f"\n{BLUE}[SILICONFLOW]{RESET}")
    siliconflow_models = [
        "Qwen/Qwen2.5-72B-Instruct",           # Large Qwen model
        "Qwen/Qwen2.5-14B-Instruct",           # Medium Qwen model
        "meta-llama/Meta-Llama-3.1-8B-Instruct",  # Llama 3.1
    ]

    for model in siliconflow_models:
        status, msg, time_ms = test_siliconflow_model(model)
        print_status(f"SiliconFlow: {model}", status, msg, time_ms)
        if status == "success":
            results["success"].append(f"siliconflow:{model}")
        else:
            results["error"].append(f"siliconflow:{model}")

    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"\n{GREEN}✅ WORKING MODELS: {len(results['success'])}{RESET}")
    for model in results["success"]:
        print(f"   • {model}")

    print(f"\n{RED}❌ FAILED MODELS: {len(results['error'])}{RESET}")
    for model in results["error"]:
        print(f"   • {model}")

    print(f"\n{BLUE}{'='*80}{RESET}\n")

    if results["success"]:
        print(f"{GREEN}Ready to proceed with full benchmark on working models!{RESET}\n")
    else:
        print(f"{RED}No models working - check API keys and model names{RESET}\n")

if __name__ == "__main__":
    main()
