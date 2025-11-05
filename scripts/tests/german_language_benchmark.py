#!/usr/bin/env python3
"""
German Language Model Benchmark
Tests 12 LLMs on German sports intelligence tasks
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
from data_aggregator import DataAggregator

load_dotenv()

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Test categories and prompts
TEST_CATEGORIES = {
    "short_form_qa": {
        "name": "Short-Form Q&A (German Fluency Baseline)",
        "prompt": "Wer hat das letzte Bundesliga-Spiel zwischen Bayer Leverkusen und Bayern München gewonnen? Gib eine kurze, präzise Antwort.",
        "expected_length": "1-2 sentences"
    },
    "long_form_editorial": {
        "name": "Long-Form Editorial Synthesis",
        "prompt": "Erstelle einen vollständigen Spielbericht über die aktuelle Bundesliga-Woche. Analysiere die wichtigsten Spiele, Transfers und Entwicklungen. Der Bericht sollte im Stil eines professionellen Sportjournalisten geschrieben sein und mindestens 3-4 Absätze umfassen.",
        "expected_length": "3-4 paragraphs"
    },
    "multi_turn_conversation": {
        "name": "Multi-Turn Agent Conversation",
        "turns": [
            "Welche Spiele stehen diese Woche in der Bundesliga an?",
            "Welches dieser Spiele ist am wichtigsten für den Titelkampf?",
            "Erstelle eine kurze Vorschau für dieses Spiel mit Formanalyse beider Teams."
        ],
        "expected_length": "Multi-turn coherence"
    },
    "rag_data_grounding": {
        "name": "Real-Time Data Grounding (RAG Test)",
        "prompt": "Basierend auf den aktuellen Daten: Welche Mannschaft hat die beste Form in den letzten 5 Spielen? Nenne konkrete Beispiele aus den bereitgestellten Daten.",
        "expected_length": "Data-grounded analysis"
    }
}


class GermanBenchmark:
    def __init__(self):
        self.aggregator = DataAggregator()
        self.results = []

        # Initialize clients
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mistral_client = OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        # SiliconFlow - will try both .cn and .com endpoints
        self.siliconflow_endpoints = [
            "https://api.siliconflow.cn/v1",
            "https://api.siliconflow.com/v1"
        ]
        self.siliconflow_client = None  # Initialize on first use

        # Model configurations
        self.models = {
            "anthropic": [
                {"name": "claude-sonnet-4-5", "display": "Claude Sonnet 4.5"},
                {"name": "claude-haiku-4-5", "display": "Claude Haiku 4.5"},
            ],
            "openai": [
                {"name": "gpt-5", "display": "GPT-5"},
                {"name": "gpt-5-mini", "display": "GPT-5 Mini"},
                {"name": "gpt-5-nano", "display": "GPT-5 Nano"},
                {"name": "gpt-5-chat-latest", "display": "GPT-5 Chat"},
            ],
            "mistral": [
                {"name": "mistral-large-latest", "display": "Mistral Large"},
                {"name": "mistral-medium-latest", "display": "Mistral Medium"},
                {"name": "mistral-small-latest", "display": "Mistral Small"},
            ],
            "siliconflow": [
                {"name": "Qwen/Qwen2.5-72B-Instruct", "display": "Qwen 2.5 72B"},
                {"name": "Qwen/Qwen2.5-14B-Instruct", "display": "Qwen 2.5 14B"},
                {"name": "meta-llama/Meta-Llama-3.1-8B-Instruct", "display": "Llama 3.1 8B"},
            ]
        }

    def fetch_context_data(self) -> str:
        """Fetch real sports data for context"""
        print(f"{CYAN}📊 Fetching fresh sports data...{RESET}")
        data = self.aggregator.aggregate_all()
        return data.to_context_string()

    def test_anthropic_model(self, model_name: str, prompt: str, context: str = "") -> Dict:
        """Test Anthropic model"""
        start = time.time()

        system_prompt = f"""Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent.

Aktuelle Sportdaten:
{context}

Antworte auf Deutsch in professionellem, journalistischem Stil."""

        try:
            response = self.anthropic_client.messages.create(
                model=model_name,
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            elapsed = time.time() - start
            text = response.content[0].text

            return {
                "success": True,
                "response": text,
                "time_ms": int(elapsed * 1000),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "time_ms": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }

    def test_openai_model(self, model_name: str, prompt: str, context: str = "") -> Dict:
        """Test OpenAI model"""
        start = time.time()

        system_prompt = f"""Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent.

Aktuelle Sportdaten:
{context}

Antworte auf Deutsch in professionellem, journalistischem Stil."""

        try:
            # GPT-5 reasoning models use max_completion_tokens
            if model_name.startswith("gpt-5") and model_name != "gpt-5-chat-latest":
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    max_completion_tokens=1000,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    max_tokens=1000,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )

            elapsed = time.time() - start
            text = response.choices[0].message.content

            return {
                "success": True,
                "response": text,
                "time_ms": int(elapsed * 1000),
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "time_ms": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }

    def test_mistral_model(self, model_name: str, prompt: str, context: str = "") -> Dict:
        """Test Mistral model"""
        start = time.time()

        system_prompt = f"""Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent.

Aktuelle Sportdaten:
{context}

Antworte auf Deutsch in professionellem, journalistischem Stil."""

        try:
            response = self.mistral_client.chat.completions.create(
                model=model_name,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            elapsed = time.time() - start
            text = response.choices[0].message.content

            return {
                "success": True,
                "response": text,
                "time_ms": int(elapsed * 1000),
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "time_ms": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }

    def test_siliconflow_model(self, model_name: str, prompt: str, context: str = "") -> Dict:
        """Test SiliconFlow model - tries both .cn and .com endpoints"""
        system_prompt = f"""Du bist KSI (Kicker Sports Intelligence), ein deutscher Sportjournalismus-Assistent.

Aktuelle Sportdaten:
{context}

Antworte auf Deutsch in professionellem, journalistischem Stil."""

        # Try both endpoints
        for base_url in self.siliconflow_endpoints:
            try:
                start = time.time()
                client = OpenAI(
                    api_key=os.getenv("SILICONFLOW_API_KEY"),
                    base_url=base_url
                )

                response = client.chat.completions.create(
                    model=model_name,
                    max_tokens=1000,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )

                elapsed = time.time() - start
                text = response.choices[0].message.content

                return {
                    "success": True,
                    "response": text,
                    "time_ms": int(elapsed * 1000),
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "error": None
                }
            except Exception as e:
                # If .cn failed, try .com
                if base_url == self.siliconflow_endpoints[0]:
                    continue
                # If both failed, return error from .com attempt
                return {
                    "success": False,
                    "response": "",
                    "time_ms": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "error": str(e)
                }

        return {
            "success": False,
            "response": "",
            "time_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "error": "Both .cn and .com endpoints failed"
        }

    def run_single_test(self, provider: str, model_config: Dict, category: str,
                       category_config: Dict, context: str) -> Dict:
        """Run a single test case"""
        model_name = model_config["name"]
        display_name = model_config["display"]

        print(f"{YELLOW}  Testing: {display_name} on {category_config['name']}...{RESET}", end=" ", flush=True)

        # Get prompt
        if category == "multi_turn_conversation":
            # For multi-turn, use first question for now (simplified)
            prompt = category_config["turns"][0]
        else:
            prompt = category_config["prompt"]

        # Route to correct client
        if provider == "anthropic":
            result = self.test_anthropic_model(model_name, prompt, context)
        elif provider == "openai":
            result = self.test_openai_model(model_name, prompt, context)
        elif provider == "mistral":
            result = self.test_mistral_model(model_name, prompt, context)
        elif provider == "siliconflow":
            result = self.test_siliconflow_model(model_name, prompt, context)
        else:
            result = {"success": False, "error": "Unknown provider"}

        if result["success"]:
            print(f"{GREEN}✅ {result['time_ms']}ms{RESET}")
        else:
            print(f"{RED}❌ {result['error'][:50]}{RESET}")

        # Add metadata
        result.update({
            "provider": provider,
            "model": model_name,
            "display_name": display_name,
            "category": category,
            "category_name": category_config["name"],
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def run_full_benchmark(self):
        """Run complete benchmark across all models and categories"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}  GERMAN LANGUAGE MODEL BENCHMARK{RESET}")
        print(f"{BLUE}  Testing 12 models × 4 categories = 48 test cases{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")

        # Fetch context once
        context = self.fetch_context_data()
        print(f"{GREEN}✅ Sports data loaded{RESET}\n")

        total_tests = sum(len(models) for models in self.models.values()) * len(TEST_CATEGORIES)
        current_test = 0

        # Run tests
        for category, category_config in TEST_CATEGORIES.items():
            print(f"\n{MAGENTA}{'='*80}{RESET}")
            print(f"{MAGENTA}📝 Category: {category_config['name']}{RESET}")
            print(f"{MAGENTA}{'='*80}{RESET}\n")

            for provider, model_list in self.models.items():
                print(f"{CYAN}[{provider.upper()}]{RESET}")

                for model_config in model_list:
                    current_test += 1
                    print(f"  [{current_test}/{total_tests}] ", end="")

                    result = self.run_single_test(
                        provider, model_config, category, category_config, context
                    )
                    self.results.append(result)

                    # Small delay to avoid rate limits
                    time.sleep(0.5)

                print()  # Empty line between providers

        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}✅ Benchmark complete! {len(self.results)} tests run{RESET}")
        print(f"{GREEN}{'='*80}{RESET}\n")

    def save_results(self, filepath: str = "results/benchmark_results.json"):
        """Save detailed results to JSON"""
        os.makedirs("results", exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"{GREEN}💾 Results saved to: {filepath}{RESET}")

    def generate_summary_report(self):
        """Generate human-readable summary report"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}  BENCHMARK SUMMARY{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")

        # Success rate
        successful = [r for r in self.results if r["success"]]
        success_rate = len(successful) / len(self.results) * 100

        print(f"{GREEN}Success Rate: {success_rate:.1f}% ({len(successful)}/{len(self.results)}){RESET}\n")

        # Average latency by model
        print(f"{CYAN}Average Response Time by Model:{RESET}")
        model_times = {}
        for result in successful:
            display = result["display_name"]
            if display not in model_times:
                model_times[display] = []
            model_times[display].append(result["time_ms"])

        for model, times in sorted(model_times.items(), key=lambda x: sum(x[1])/len(x[1])):
            avg = sum(times) / len(times)
            print(f"  {model:<25} {avg:>6.0f}ms")

        # Total cost estimate
        print(f"\n{YELLOW}Token Usage & Cost Estimate:{RESET}")
        total_input = sum(r.get("input_tokens", 0) for r in successful)
        total_output = sum(r.get("output_tokens", 0) for r in successful)

        print(f"  Total Input Tokens:  {total_input:,}")
        print(f"  Total Output Tokens: {total_output:,}")
        print(f"  Estimated Cost:      ~${(total_input * 0.000001 * 1.5 + total_output * 0.000001 * 8):.2f}")

        print(f"\n{BLUE}{'='*80}{RESET}\n")


def main():
    benchmark = GermanBenchmark()
    benchmark.run_full_benchmark()
    benchmark.save_results()
    benchmark.generate_summary_report()

    print(f"{GREEN}✅ Full results saved to: results/benchmark_results.json{RESET}")
    print(f"{CYAN}Next: Review responses and generate quality analysis{RESET}\n")


if __name__ == "__main__":
    main()
