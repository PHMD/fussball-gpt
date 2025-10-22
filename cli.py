"""
CLI interface for KSI prototype.

Provides interactive command-line interface for querying sports data using LLM-powered RAG.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from data_aggregator import DataAggregator
from models import AggregatedData


class LLMClient:
    """Wrapper for LLM API clients (OpenAI or Anthropic)."""

    def __init__(self, provider: str = "openai"):
        """
        Initialize LLM client.

        Args:
            provider: Either "openai" or "anthropic"
        """
        self.provider = provider.lower()

        if self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-4-turbo-preview"
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                self.client = Anthropic(api_key=api_key)
                self.model = "claude-3-5-sonnet-20241022"
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'")

    def query(self, user_query: str, context_data: AggregatedData) -> str:
        """
        Send query to LLM with sports data context.

        Args:
            user_query: User's natural language question
            context_data: Aggregated sports data for context

        Returns:
            LLM's response as string
        """
        # Build system prompt with data context
        system_prompt = f"""You are a knowledgeable sports assistant with access to recent sports news and data.

Current sports data context:
{context_data.to_context_string()}

Use this data to answer questions accurately. If the answer isn't in the provided data, say so clearly."""

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )
                return response.choices[0].message.content

            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.7,
                )
                return response.content[0].text

        except Exception as e:
            return f"Error querying LLM: {str(e)}"


class KSI_CLI:
    """Interactive CLI for Kicker Sports Intelligence."""

    def __init__(self):
        """Initialize CLI with data aggregator and LLM client."""
        load_dotenv()

        # Get configuration from environment
        provider = os.getenv("LLM_PROVIDER", "openai")
        self.refresh_interval = int(os.getenv("DATA_REFRESH_INTERVAL", "300"))

        # Initialize components
        self.aggregator = DataAggregator()
        self.llm = LLMClient(provider=provider)

        # Data cache
        self.cached_data: Optional[AggregatedData] = None
        self.last_refresh: Optional[datetime] = None

        print(f"KSI initialized with {provider.upper()} provider")

    def refresh_data(self, force: bool = False) -> AggregatedData:
        """
        Refresh aggregated data if needed.

        Args:
            force: Force refresh even if cache is valid

        Returns:
            Fresh or cached AggregatedData
        """
        # Check if refresh needed
        needs_refresh = force or self.cached_data is None

        if self.last_refresh:
            time_since_refresh = datetime.now() - self.last_refresh
            if time_since_refresh.total_seconds() > self.refresh_interval:
                needs_refresh = True

        if needs_refresh:
            print("\n[Fetching latest sports data...]")
            self.cached_data = self.aggregator.aggregate_all()
            self.last_refresh = datetime.now()
            print(f"[Data refreshed: {len(self.cached_data.news_articles)} articles, "
                  f"{len(self.cached_data.sports_events)} events]")

        return self.cached_data

    def run(self):
        """Run the interactive CLI loop."""
        print("\n" + "="*60)
        print("  KICKER SPORTS INTELLIGENCE (KSI) - CLI Prototype")
        print("="*60)
        print("\nAsk questions about sports news and upcoming matches.")
        print("Commands:")
        print("  /refresh - Force data refresh")
        print("  /exit or /quit - Exit the program")
        print("="*60 + "\n")

        # Initial data load
        self.refresh_data(force=True)

        # Main loop
        while True:
            try:
                # Get user input
                user_input = input("\n🏆 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["/exit", "/quit"]:
                    print("\nGoodbye! Thanks for using KSI.")
                    break

                if user_input.lower() == "/refresh":
                    self.refresh_data(force=True)
                    continue

                # Refresh data if needed (automatic)
                data = self.refresh_data()

                # Query LLM
                print("\n🤖 KSI: ", end="", flush=True)
                response = self.llm.query(user_input, data)
                print(response)

            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for using KSI.")
                break

            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again or use /exit to quit.")


def main():
    """Entry point for CLI."""
    try:
        cli = KSI_CLI()
        cli.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your API keys (see .env.example)")
        print("2. Installed dependencies: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
