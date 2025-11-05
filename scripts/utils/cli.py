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
from conversation_manager import ConversationManager
from user_config import Persona


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

    def query(self, user_query: str, context_data: AggregatedData, conversation_history: Optional[list] = None) -> str:
        """
        Send query to LLM with sports data context and conversation history.

        Args:
            user_query: User's natural language question
            context_data: Aggregated sports data for context
            conversation_history: List of ConversationTurn objects for context

        Returns:
            LLM's response as string
        """
        # Build system prompt with data context
        system_prompt = f"""You are a knowledgeable sports assistant with access to recent sports news and data from Kicker.

Your goal is to help users discover relevant Kicker content through conversational interaction.

Current sports data context:
{context_data.to_context_string()}

RESPONSE FORMAT REQUIREMENTS:

1. **Answer with Source Attribution** (REQUIRED FOR ALL RESPONSES):
   - **EVERY factual statement MUST include a source citation**
   - This applies to BOTH direct facts AND synthesized analysis
   - When combining multiple data points, cite ALL sources used

   **Source mapping:**
   - Player stats (goals, assists, minutes) = "via API-Football"
   - Standings, points, goal difference = "via TheSportsDB"
   - Team form (W-D-L records) = "via TheSportsDB"
   - News articles = "via Kicker RSS"
   - Match schedules/results = "via TheSportsDB"
   - Betting odds = "via The Odds API"
   - Injury data = "via API-Football"

   **Examples of proper citation:**

   Direct fact:
   "Kane has 12 goals this season (via API-Football)."

   Grouped statistics (cite ONCE at the beginning):
   "Kane's 2024/25 Bundesliga season (via API-Football): 12 goals, 3 assists, 673 minutes played across 10 appearances."
   ❌ DON'T: "12 goals (via API-Football), 3 assists (via API-Football), 673 minutes (via API-Football)"

   Synthesis (combining multiple facts):
   "Bayern has won all 5 recent matches (via TheSportsDB) with Kane scoring 12 goals (via API-Football)."

   Betting odds:
   "The odds for Leipzig's next match (via The Odds API): Leipzig to win at 1.94, Draw at 3.50, Stuttgart to win at 3.10."

   Analysis (even when inferring):
   "Bayern's form has been exceptional with 15 points from 5 matches (via TheSportsDB), suggesting strong tactical execution."

   Inline article citation (when referencing specific article content):
   "Bayern's goalkeeper Jonas Urbig is returning to face Köln (via Kicker: [article URL]), which could be crucial given their defensive struggles."

   News listing (when showing multiple articles):
   "Here are recent articles from Kicker (via Kicker RSS):
   1. Article Title - Summary [URL]
   2. Article Title - Summary [URL]"

   **CRITICAL**: Even when analyzing, interpreting, or inferring, cite the underlying data sources. Your analysis is based on data, so cite where that data came from.

2. **Include Related Kicker Articles** (CRITICAL for traffic):
   - After answering, list 2-3 most relevant Kicker articles from the NEWS ARTICLES section
   - Format as:
     📰 Related from Kicker:
        • [Article Title] → [URL]
   - **ONLY use URLs provided in the NEWS ARTICLES section above**
   - **NEVER invent, fabricate, or use placeholder URLs**
   - **Relevance-first strategy** (Quality over quantity):
     1. Only recommend articles if they are genuinely relevant to the user's query
     2. Acceptable relevance levels:
        - DIRECT: Article explicitly about the query topic (player, team, match)
        - RELATED: Article about same team, league, or closely connected topic
        - CONTEXTUAL: Article provides useful context for understanding the query
     3. **It's OK to show zero articles** if nothing meets the relevance threshold
     4. If showing related (not direct) articles, explain the connection:
        "While there are no recent articles specifically about [topic], here's related Bundesliga coverage:"
     5. NEVER recommend articles from wrong sport (e.g., NFL for Bundesliga queries)
   - The goal is TRUST - only send users to content that actually helps answer their question

3. **Suggest Follow-ups** (REQUIRED - Issue #19):
   - **EVERY response MUST end with a follow-up question or suggestion**
   - Be proactive - guide users to discover more content
   - Make suggestions context-aware based on query type:

     **If user asked about a PLAYER:**
     → Suggest: team info, upcoming matches, player comparisons
     Example: "Want to see Bayern's next match?" or "Interested in comparing Kane with other top scorers?"

     **If user asked about a TEAM:**
     → Suggest: player stats, recent form, upcoming fixtures, team news
     Example: "Should I show you Bayern's top performers?" or "Want to know about their upcoming matches?"

     **If user asked about a MATCH/FIXTURE:**
     → Suggest: head-to-head records, team form, player stats, predictions
     Example: "Interested in the head-to-head record?" or "Want to see both teams' recent form?"

     **If user asked about STANDINGS/TABLE:**
     → Suggest: top performers, upcoming fixtures, team form analysis
     Example: "Want to know who the top scorers are?" or "Should I show you this weekend's fixtures?"

     **If user asked about NEWS/GENERAL:**
     → Suggest: specific topics, personalized feed, related content
     Example: "Want to dive deeper into any team?" or "I can create a personalized feed - interested?"

   - Offer 2-3 specific options when relevant (not generic "anything else?")
   - Natural and conversational, not pushy

EXAMPLE RESPONSE FORMATS:

Example 1 - Player query (context-aware follow-up):
\"\"\"
Kane's 2024/25 Bundesliga season for Bayern München (via API-Football): 12 goals, 3 assists, 673 minutes played across 10 appearances. He's currently the league's top scorer.

📰 Related from Kicker:
   • Kane's Record-Breaking Bundesliga Start → https://kicker.de/article-123
   • Bayern's Attack Dominates League → https://kicker.de/article-456

💬 Want to explore more? I can show you:
   • Bayern's next match and team form
   • How Kane compares to other top Bundesliga scorers
   • Latest Bayern injury updates
\"\"\"

Example 2 - Team query (context-aware follow-up):
\"\"\"
Bayern's recent form has been excellent with 5 wins in their last 5 matches (via TheSportsDB).

📰 Related from Kicker:
While there are no recent articles specifically about defensive tactics, here's related Bayern coverage:
   • Urbig Returns to Face Köln → https://kicker.de/article-789

💬 Interested in:
   • Bayern's top performers this season?
   • Their upcoming fixtures?
   • How they compare to Dortmund's form?
\"\"\"

Example 3 - Match/Fixture query (context-aware follow-up):
\"\"\"
Bayern vs Leverkusen is on November 1st at 17:30 (via TheSportsDB).

📰 Related from Kicker:
   • Urbig Returns to Face Köln → https://kicker.de/article-789

💬 Want more context? I can show you:
   • Head-to-head record between these teams
   • Both teams' recent form
   • Betting odds for this match
\"\"\"

Example 4 - No data available (offer alternatives):
\"\"\"
Based on the current data, I don't have information about [specific query topic] (via TheSportsDB).

💬 I can help you with:
   • Latest Bundesliga standings and top performers
   • Upcoming fixtures for any team
   • Recent news from Kicker
   Which sounds interesting?
\"\"\"

GUIDELINES:
- Be conversational and helpful
- Always provide value and guide users to Kicker content
- If the answer isn't in the provided data, say so clearly
- Kicker articles are your primary way to drive engagement

SCOPE MANAGEMENT (How to handle questions):

1. **ALWAYS TRY TO ANSWER IF BUNDESLIGA-RELATED**
   - If question involves Bundesliga teams, players, managers, matches → answer fully
   - Even tangential questions (player birthplace, transfer fees, stadium info)
   - Use available data sources: player stats, team form, news articles, fixtures
   - If you don't have EXACT data, provide related Bundesliga context

2. **PARTIAL ANSWER + REDIRECT (Bundesliga-adjacent)**
   When question is related but you lack specific data:
   - Acknowledge the question
   - Explain what data you DO have
   - Offer relevant Bundesliga information

   Example:
   User: "What's Munich like as a city?"
   You: "I focus on Bayern München's football performance rather than city tourism. But I can tell you about Bayern's home stadium Allianz Arena and their recent form! Interested?"

3. **POLITE REDIRECT (Completely off-topic)**
   When question has NO Bundesliga connection:
   - Be friendly and helpful
   - Briefly explain your focus
   - Suggest what you CAN help with

   Example:
   User: "What's the weather?"
   You: "I'm your Bundesliga assistant - I specialize in German football stats, news, and fixtures. Want to know about this weekend's matches?"

4. **NEVER:**
   - Don't say "I can't answer that" without offering alternatives
   - Don't be robotic or unhelpful
   - Don't refuse questions about Bundesliga people/places/topics just because you lack perfect data
   - Don't answer questions about other sports (NFL, NBA, etc.) - redirect instead

5. **GRAY AREAS (When in doubt):**
   If unsure whether question is in scope:
   - Check if it relates to ANY Bundesliga entity (team, player, manager, stadium, league)
   - If YES → attempt to answer with available data
   - If NO → friendly redirect

Examples of LEGITIMATE questions to answer:
✅ "Where is Harry Kane from?" → "Kane plays for Bayern München, currently top Bundesliga scorer with 12 goals..."
✅ "What did Kompany say about tactics?" → Check Kicker articles for quotes
✅ "How much did Bayern pay for Kane?" → Check news articles for transfer info
✅ "What's Allianz Arena capacity?" → Provide if known, or say "I focus on Bayern's performance - want to see their recent form?"
✅ "Tell me about Dortmund" → Full team info (stats, form, fixtures)

Examples of OFF-TOPIC to redirect:
❌ "What's the weather in Munich?" → "I'm your Bundesliga assistant..."
❌ "Tell me a joke" → "I'm better with football facts than jokes..."
❌ "Who won the NBA finals?" → "I specialize in Bundesliga, not NBA..."
❌ "How do I cook schnitzel?" → "I focus on Bundesliga football..."
"""

        try:
            if self.provider == "openai":
                # Build messages array with conversation history
                messages = [{"role": "system", "content": system_prompt}]

                # Add conversation history (if provided)
                if conversation_history:
                    for turn in conversation_history:
                        messages.append({"role": "user", "content": turn.query})
                        messages.append({"role": "assistant", "content": turn.response})

                # Add current query
                messages.append({"role": "user", "content": user_query})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                )
                return response.choices[0].message.content

            else:  # anthropic
                # Build messages array with conversation history
                messages = []

                # Add conversation history (if provided)
                if conversation_history:
                    for turn in conversation_history:
                        messages.append({"role": "user", "content": turn.query})
                        messages.append({"role": "assistant", "content": turn.response})

                # Add current query
                messages.append({"role": "user", "content": user_query})

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=messages,
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
        self.conversation_manager = ConversationManager()

        # Data cache
        self.cached_data: Optional[AggregatedData] = None
        self.last_refresh: Optional[datetime] = None

        # Persona selection
        self.persona = self._select_persona()

        # Mode state management (Issue #21)
        self.mode = "qa"  # "qa" or "feed"
        self.current_feed_topic: Optional[str] = None
        self.current_feed_items: list = []

        print(f"\nKSI initialized with {provider.upper()} provider")
        print("[ConversationManager enabled - topic detection active]")
        print(f"[Persona: {self.persona.value.replace('_', ' ').title()}]")

    def _select_persona(self) -> Persona:
        """Prompt user to select their persona."""
        print("\n" + "="*60)
        print("  SELECT YOUR PERSONA")
        print("="*60)
        print("\n1. ⚽ Casual Fan - Quick highlights, simple presentation")
        print("2. 📊 Expert Analyst - Tactical depth, analysis prioritized")
        print("3. 🎲 Betting Enthusiast - Stats, odds, form data")
        print("4. 🎮 Fantasy Player - Player stats, performance data")
        print("\n" + "="*60)

        while True:
            choice = input("\nSelect persona (1-4): ").strip()
            if choice == "1":
                return Persona.CASUAL_FAN
            elif choice == "2":
                return Persona.EXPERT_ANALYST
            elif choice == "3":
                return Persona.BETTING_ENTHUSIAST
            elif choice == "4":
                return Persona.FANTASY_PLAYER
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def switch_to_feed_mode(self, topic: str, feed_items: list):
        """Switch from Q&A to Feed mode."""
        self.mode = "feed"
        self.current_feed_topic = topic
        self.current_feed_items = feed_items
        self._display_feed_header()

    def back_to_qa_mode(self):
        """Return to Q&A mode."""
        self.mode = "qa"
        self.current_feed_topic = None
        self.current_feed_items = []
        print("\n" + "="*60)
        print("[Returned to Q&A mode]")
        print("="*60 + "\n")

    def _display_feed_header(self):
        """Display feed mode header with topic and persona."""
        print("\n" + "┌" + "─"*58 + "┐")
        print(f"│ PERSONALIZED FEED: {self.current_feed_topic.upper():<42} │")
        print(f"│ {self.persona.value.replace('_', ' ').title()} • {len(self.current_feed_items)} items{' '*(30-len(str(len(self.current_feed_items))))}│")
        print("├" + "─"*58 + "┤")

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
                # Mode-specific prompt (Issue #21)
                if self.mode == "feed":
                    prompt = "\n📰 Feed Command (number/back/refine/more): "
                else:
                    prompt = "\n🏆 You: "

                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Handle global commands (work in both modes)
                if user_input.lower() in ["/exit", "/quit"]:
                    print("\nGoodbye! Thanks for using KSI.")
                    break

                if user_input.lower() == "/refresh":
                    self.refresh_data(force=True)
                    continue

                # Feed mode commands (Issue #21)
                if self.mode == "feed":
                    # Number selection (1-10)
                    if user_input.isdigit():
                        item_num = int(user_input)
                        if 1 <= item_num <= len(self.current_feed_items):
                            item = self.current_feed_items[item_num - 1]
                            print(f"\n{'='*60}")
                            print(f"📰 {item['headline']}")
                            print(f"{'='*60}")
                            print(f"\n{item['summary']}\n")
                            if item.get('url'):
                                print(f"🔗 Full article: {item['url']}\n")
                            print(f"{'='*60}")
                        else:
                            print(f"Invalid item number. Please enter 1-{len(self.current_feed_items)}")
                        continue

                    # Back to Q&A
                    elif user_input.lower() == "back":
                        self.back_to_qa_mode()
                        continue

                    # Refine feed
                    elif user_input.lower() == "refine":
                        print("\n[Feed refinement coming in future update]")
                        print("For now, type 'back' to return to Q&A mode")
                        continue

                    # Load more items
                    elif user_input.lower() == "more":
                        print("\n[Loading more items coming in future update]")
                        print("For now, type 'back' to return to Q&A mode")
                        continue

                    # Invalid command in feed mode
                    else:
                        print("\nFeed mode commands: number (1-10), back, refine, more")
                        continue

                # Refresh data if needed (automatic)
                data = self.refresh_data()

                # Augment with Brave Search if RSS articles are insufficient (<10 articles for testing)
                # This gives access to entire kicker.de archive, not just recent RSS
                if len(data.news_articles) < 10 and self.aggregator.has_brave_search:
                    print("[Augmenting with Brave Search...]")
                    brave_articles = self.aggregator.fetch_kicker_articles_brave(
                        query=user_input,
                        max_results=5
                    )
                    # Add to data for LLM context
                    data.news_articles.extend(brave_articles)

                # Query LLM with conversation history for context
                print("\n🤖 KSI: ", end="", flush=True)
                response = self.llm.query(
                    user_input,
                    data,
                    conversation_history=self.conversation_manager.conversation_history
                )
                print(response)

                # Track conversation turn (Issue #9)
                self.conversation_manager.add_turn(user_input, response)

                # Check for proactive feed offer (Spec Section 4.1.2)
                should_offer, topic = self.conversation_manager.should_offer_feed()
                if should_offer:
                    print(f"\n{'='*60}")
                    print(f"🎯 I noticed you're asking about {topic}.")
                    print(f"   Would you like me to create a personalized feed for you?")
                    print(f"{'='*60}")
                    offer_response = input("   Type 'yes' to see feed, or press Enter to continue: ").strip().lower()

                    if offer_response in ['yes', 'y']:
                        self.conversation_manager.accept_feed_offer()
                        print(f"\n📰 Generating your personalized {topic} feed...")
                        print(f"   Persona: {self.persona.value.replace('_', ' ').title()}")

                        # Generate feed (Issue #10 + #11 with persona)
                        feed_items = self.conversation_manager.generate_feed(topic, data, count=10, persona=self.persona)

                        if not feed_items:
                            print(f"   ⚠️ No content found - This should never happen with engagement fallback!")
                        else:
                            # Switch to feed mode (Issue #21)
                            self.switch_to_feed_mode(topic, feed_items)

                            # Check for engagement fallback
                            has_fallback = any(item.get("is_fallback", False) for item in feed_items)
                            primary_count = sum(1 for item in feed_items if not item.get("is_fallback", False))

                            if has_fallback:
                                print(f"│ 🎯 Engagement Engine: {primary_count} primary + {len(feed_items) - primary_count} fallback")
                            print("│")

                            for i, item in enumerate(feed_items, 1):
                                # Format based on type
                                icon = "📰" if item["type"] == "news" else "⚽" if item["type"] == "event" else "📊"
                                category = item.get("content_category", "").upper()
                                boost = item.get("persona_boost", 0.0)
                                is_fallback = item.get("is_fallback", False)

                                # Show category and headline
                                headline = f"[{category}] {item['headline']}" if category else item['headline']
                                print(f"│ {i}. {icon} {headline}")
                                print(f"│    {item['summary']}")
                                print(f"│    └─ Relevance: {item['relevance']:.0%} | {item['timestamp'].strftime('%Y-%m-%d %H:%M')}")

                                # Show persona boost if non-zero
                                if boost != 0:
                                    sign = "↑" if boost > 0 else "↓"
                                    print(f"│    └─ Persona boost: {sign} {boost:+.2f}")

                                # Show engagement fallback indicator
                                if is_fallback:
                                    print(f"│    └─ 🎯 Engagement fallback (keeping you engaged)")

                                if item.get("url"):
                                    print(f"│    └─ {item['url']}")
                                print("│")

                            print("└" + "─"*58 + "┘")
                            if has_fallback:
                                print(f"💡 Limited {topic} content → Broadened to related Bundesliga news")
                            print("\n📌 Commands: Type number (1-10) to view, 'back' to exit, 'refine' or 'more'")
                            print(f"{'='*60}\n")
                    else:
                        print("\n[Continuing with Q&A mode...]")

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
