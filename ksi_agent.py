"""
KSI Agent - Powered by Claude Agent SDK

A sports intelligence agent that uses the Claude Agent SDK to provide
real-time sports data analysis through natural language interaction.
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Optional, Any

from claude_agent_sdk import Agent, AgentOptions
from dotenv import load_dotenv

from data_aggregator import DataAggregator


class KSISportsAgent:
    """
    Kicker Sports Intelligence Agent powered by Claude Agent SDK.

    Integrates real-time sports data with Claude's AI capabilities to answer
    questions about sports news, schedules, and results.
    """

    def __init__(self, refresh_interval: int = 300):
        """
        Initialize the KSI agent.

        Args:
            refresh_interval: Data refresh interval in seconds (default: 300 = 5 min)
        """
        load_dotenv()

        self.refresh_interval = refresh_interval
        self.aggregator = DataAggregator()

        # Data cache
        self.cached_data = None
        self.last_refresh: Optional[datetime] = None

        # Configure agent
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create and configure the Claude agent."""

        # Define system prompt for sports intelligence
        system_prompt = """You are KSI (Kicker Sports Intelligence), an expert sports analyst and assistant.

Your expertise includes:
- German football (Bundesliga, 2. Bundesliga)
- European football competitions (Champions League, Europa League)
- International sports news
- Match analysis and player statistics
- Upcoming fixtures and schedules

You have access to real-time sports data that is refreshed regularly. When answering questions:
1. Base your answers on the provided data context
2. Be specific with dates, scores, and player names
3. If information isn't in your data, clearly state that
4. Provide context and analysis, not just raw facts
5. Use a professional but friendly tone

The data you have access to includes:
- Latest news articles from Kicker.de
- Match results and scores
- Upcoming fixtures
- Player information

Always cite your sources when referencing specific matches or news."""

        # Configure agent options
        options = AgentOptions(
            system_prompt=system_prompt,
            # Allow all default tools for now
            permission_mode="allow_all",
            # Enable auto-compaction for context management
            auto_compact=True,
        )

        # Create agent
        agent = Agent(options=options)

        return agent

    def refresh_data(self, force: bool = False) -> str:
        """
        Refresh sports data if needed.

        Args:
            force: Force refresh even if cache is valid

        Returns:
            Context string for LLM
        """
        needs_refresh = force or self.cached_data is None

        if self.last_refresh:
            time_since_refresh = datetime.now() - self.last_refresh
            if time_since_refresh.total_seconds() > self.refresh_interval:
                needs_refresh = True

        if needs_refresh:
            print("\n[📡 Fetching latest sports data...]", flush=True)
            self.cached_data = self.aggregator.aggregate_all()
            self.last_refresh = datetime.now()
            print(f"[✓ Data refreshed: {len(self.cached_data.news_articles)} articles, "
                  f"{len(self.cached_data.sports_events)} events]\n", flush=True)

        return self.cached_data.to_context_string()

    async def chat_interactive(self):
        """Run interactive chat session with the agent."""

        print("\n" + "="*70)
        print("  🏆 KSI - Kicker Sports Intelligence")
        print("  Powered by Claude Agent SDK")
        print("="*70)
        print("\nAsk me anything about sports!")
        print("\nCommands:")
        print("  /refresh - Force data refresh")
        print("  /exit or /quit - Exit")
        print("="*70 + "\n")

        # Initial data load
        sports_context = self.refresh_data(force=True)

        while True:
            try:
                # Get user input
                user_input = input("\n🏆 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["/exit", "/quit"]:
                    print("\n👋 Thanks for using KSI! Goodbye.\n")
                    break

                if user_input.lower() == "/refresh":
                    sports_context = self.refresh_data(force=True)
                    continue

                # Refresh data if needed (automatic)
                sports_context = self.refresh_data()

                # Prepend sports data context to the message
                message_with_context = f"""Current Sports Data:
{sports_context}

---

User Question: {user_input}"""

                # Send to agent and stream response
                print("\n🤖 KSI: ", end="", flush=True)

                async for chunk in self.agent.stream(message_with_context):
                    if hasattr(chunk, 'text'):
                        print(chunk.text, end="", flush=True)
                    elif isinstance(chunk, str):
                        print(chunk, end="", flush=True)

                print()  # New line after response

            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using KSI! Goodbye.\n")
                break

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or use /exit to quit.\n")

    async def query_once(self, question: str) -> str:
        """
        Ask a single question and get a response.

        Args:
            question: The question to ask

        Returns:
            The agent's response
        """
        # Get latest data
        sports_context = self.refresh_data()

        # Build message with context
        message = f"""Current Sports Data:
{sports_context}

---

User Question: {question}"""

        # Get response
        response = await self.agent.run(message)

        return response


async def main():
    """Main entry point for KSI agent."""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("\nPlease:")
        print("1. Create a .env file (copy from .env.example)")
        print("2. Add your Anthropic API key")
        print("3. Or export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    try:
        # Create and run agent
        ksi = KSISportsAgent()
        await ksi.chat_interactive()

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
