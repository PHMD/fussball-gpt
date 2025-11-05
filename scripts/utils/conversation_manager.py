"""
Conversation management for KSI prototype.

Tracks conversation state, detects topic patterns, and triggers proactive feed offers.
Implements spec requirements from Section 4.1.2 (Proactive Feed Offer).
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from collections import Counter

from models import AggregatedData
from user_config import Persona


@dataclass
class ConversationTurn:
    """Single turn in conversation (user query + assistant response)."""
    query: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    detected_entities: set[str] = field(default_factory=set)


class ConversationManager:
    """
    Manages conversation state for proactive feed offers.

    Spec Requirements:
    - Track conversation history
    - Detect when 2-3 questions are about the same topic
    - Trigger proactive feed offer when pattern detected
    - Generate personalized feed for detected topic
    """

    # Bundesliga teams for entity extraction
    BUNDESLIGA_TEAMS = {
        "bayern", "munich", "bayern munich",
        "dortmund", "bvb", "borussia dortmund",
        "leipzig", "rb leipzig",
        "leverkusen", "bayer leverkusen",
        "frankfurt", "eintracht frankfurt",
        "union", "union berlin",
        "freiburg", "sc freiburg",
        "gladbach", "mönchengladbach", "borussia mönchengladbach",
        "bremen", "werder bremen",
        "wolfsburg", "vfl wolfsburg",
        "stuttgart", "vfb stuttgart",
        "hoffenheim", "tsg hoffenheim",
        "augsburg", "fc augsburg",
        "mainz", "mainz 05",
        "bochum", "vfl bochum",
        "heidenheim", "fc heidenheim",
        "st. pauli", "st pauli", "sankt pauli",
        "kiel", "holstein kiel",
    }

    # Popular Bundesliga players (expandable)
    POPULAR_PLAYERS = {
        "kane", "harry kane",
        "musiala", "jamal musiala",
        "wirtz", "florian wirtz",
        "füllkrug", "niclas füllkrug",
        "sané", "leroy sané",
        "kimmich", "joshua kimmich",
        "gündogan", "ilkay gündogan",
        "goretzka", "leon goretzka",
    }

    def __init__(self):
        """Initialize conversation manager."""
        self.conversation_history: list[ConversationTurn] = []
        self.feed_offered = False
        self.feed_accepted = False
        self.current_topic: Optional[str] = None

    def add_turn(self, user_query: str, assistant_response: str) -> None:
        """
        Add a conversation turn and analyze for topic patterns.

        Args:
            user_query: User's question
            assistant_response: Assistant's response
        """
        # Extract entities from query
        entities = self.extract_entities(user_query)

        # Create turn
        turn = ConversationTurn(
            query=user_query,
            response=assistant_response,
            timestamp=datetime.now(),
            detected_entities=entities
        )

        # Add to history
        self.conversation_history.append(turn)

        # Analyze for topic patterns
        self.detect_topic_patterns()

    def extract_entities(self, text: str) -> set[str]:
        """
        Extract team and player names from text.

        Simple keyword-based extraction for initial implementation.
        Can be upgraded to NER (Named Entity Recognition) later.

        Args:
            text: Text to analyze (query or response)

        Returns:
            Set of detected entities (team names, player names)
        """
        text_lower = text.lower()
        entities = set()

        # Check for team names
        for team in self.BUNDESLIGA_TEAMS:
            if team in text_lower:
                # Normalize to short form
                if "bayern" in team:
                    entities.add("Bayern Munich")
                elif "dortmund" in team:
                    entities.add("Borussia Dortmund")
                elif "leipzig" in team:
                    entities.add("RB Leipzig")
                elif "leverkusen" in team:
                    entities.add("Bayer Leverkusen")
                elif "frankfurt" in team:
                    entities.add("Eintracht Frankfurt")
                elif "union" in team:
                    entities.add("Union Berlin")
                elif "freiburg" in team:
                    entities.add("SC Freiburg")
                elif "gladbach" in team or "mönchengladbach" in team:
                    entities.add("Borussia Mönchengladbach")
                elif "bremen" in team:
                    entities.add("Werder Bremen")
                elif "wolfsburg" in team:
                    entities.add("VfL Wolfsburg")
                elif "stuttgart" in team:
                    entities.add("VfB Stuttgart")
                elif "hoffenheim" in team:
                    entities.add("TSG Hoffenheim")
                elif "augsburg" in team:
                    entities.add("FC Augsburg")
                elif "mainz" in team:
                    entities.add("Mainz 05")
                elif "bochum" in team:
                    entities.add("VfL Bochum")
                elif "heidenheim" in team:
                    entities.add("FC Heidenheim")
                elif "pauli" in team:
                    entities.add("St. Pauli")
                elif "kiel" in team:
                    entities.add("Holstein Kiel")

        # Check for player names
        for player in self.POPULAR_PLAYERS:
            if player in text_lower:
                # Normalize to full name
                if "kane" in player:
                    entities.add("Harry Kane")
                elif "musiala" in player:
                    entities.add("Jamal Musiala")
                elif "wirtz" in player:
                    entities.add("Florian Wirtz")
                elif "füllkrug" in player:
                    entities.add("Niclas Füllkrug")
                elif "sané" in player:
                    entities.add("Leroy Sané")
                elif "kimmich" in player:
                    entities.add("Joshua Kimmich")
                elif "gündogan" in player:
                    entities.add("İlkay Gündoğan")
                elif "goretzka" in player:
                    entities.add("Leon Goretzka")

        return entities

    def detect_topic_patterns(self) -> None:
        """
        Analyze recent conversation history for topic patterns.

        Spec Requirement: Detect when 2-3 questions are about the same topic.

        Updates self.current_topic if pattern detected.
        """
        # Need at least 2 turns to detect pattern
        if len(self.conversation_history) < 2:
            self.current_topic = None
            return

        # Look at last 3 turns (spec: 2-3 questions)
        window = min(3, len(self.conversation_history))
        recent_turns = self.conversation_history[-window:]

        # Collect all entities from recent turns
        all_entities = []
        for turn in recent_turns:
            all_entities.extend(turn.detected_entities)

        if not all_entities:
            self.current_topic = None
            return

        # Find most common entity
        entity_counts = Counter(all_entities)
        most_common = entity_counts.most_common(1)[0]
        entity, count = most_common

        # Spec: Need 2+ mentions to consider it a pattern
        if count >= 2:
            self.current_topic = entity
        else:
            self.current_topic = None

    def should_offer_feed(self) -> tuple[bool, Optional[str]]:
        """
        Check if we should offer personalized feed to user.

        Spec Requirement: After 2-3 related questions, offer feed.

        Returns:
            Tuple of (should_offer, topic)
            - should_offer: True if feed should be offered
            - topic: Detected topic (team/player name)
        """
        # Don't offer if already offered
        if self.feed_offered:
            return (False, None)

        # Don't offer if less than 2 turns
        if len(self.conversation_history) < 2:
            return (False, None)

        # Check if we have a detected topic
        if self.current_topic:
            # Mark as offered (prevent repeat offers)
            self.feed_offered = True
            return (True, self.current_topic)

        return (False, None)

    def accept_feed_offer(self) -> None:
        """Mark that user accepted the feed offer."""
        self.feed_accepted = True

    def reset_feed_state(self) -> None:
        """Reset feed offer state (for testing or new conversation)."""
        self.feed_offered = False
        self.feed_accepted = False
        self.current_topic = None

    def generate_feed(
        self,
        topic: str,
        aggregated_data: AggregatedData,
        count: int = 10,
        persona: Optional[Persona] = None
    ) -> list[dict]:
        """
        Generate personalized feed items for topic.

        Filters and ranks content by relevance to topic and persona preferences.

        Args:
            topic: Topic to filter by (team/player name)
            aggregated_data: All available sports data
            count: Number of items to return (default: 10)
            persona: User persona for customized filtering/ranking (optional)

        Returns:
            List of feed items with format:
            {
                "type": "news" | "event" | "stats",
                "headline": str,
                "summary": str,
                "url": Optional[str],
                "timestamp": datetime,
                "relevance": float,  # 0-1 score
                "content_category": "news" | "analysis" | "stats" | "odds"  # NEW
            }
        """
        feed_items = []

        # Filter news articles by topic
        for article in aggregated_data.news_articles:
            text = f"{article.title} {article.content}"
            relevance = self._calculate_relevance(text, topic)

            if relevance > 0.3:  # Threshold for relevance
                # Classify content (news vs analysis)
                content_category = self._classify_article(article.title, article.content)

                feed_items.append({
                    "type": "news",
                    "headline": article.title,
                    "summary": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                    "url": article.url,
                    "timestamp": article.timestamp,
                    "relevance": relevance,
                    "source": article.source.value,
                    "content_category": content_category
                })

        # Filter sports events by topic
        for event in aggregated_data.sports_events:
            # Check if topic matches team names or event content
            relevance = 0.0

            # Direct team name match (high relevance)
            if event.home_team and topic.lower() in event.home_team.lower():
                relevance = 1.0
            elif event.away_team and topic.lower() in event.away_team.lower():
                relevance = 1.0
            else:
                # Check title and content
                text = f"{event.title} {event.content}"
                relevance = self._calculate_relevance(text, topic)

            if relevance > 0.3:
                feed_items.append({
                    "type": "event",
                    "headline": event.title,
                    "summary": event.content,
                    "url": None,
                    "timestamp": event.timestamp,
                    "relevance": relevance,
                    "home_team": event.home_team,
                    "away_team": event.away_team,
                    "score": event.score,
                    "content_category": "news"  # Events are factual news
                })

        # Filter player stats by topic (player name OR team name)
        for player in aggregated_data.player_stats:
            if topic.lower() in player.player_name.lower() or topic.lower() in player.team.lower():
                feed_items.append({
                    "type": "stats",
                    "headline": f"{player.player_name} - {player.team}",
                    "summary": f"{player.goals} goals, {player.assists} assists in {player.appearances} appearances ({player.minutes_played} minutes)",
                    "url": None,
                    "timestamp": datetime.now(),  # Stats are current
                    "relevance": 1.0,  # Direct name match
                    "player_name": player.player_name,
                    "team": player.team,
                    "goals": player.goals,
                    "assists": player.assists,
                    "content_category": "stats"  # Player statistics
                })

        # Apply persona-specific filtering and ranking
        if persona:
            feed_items = self._apply_persona_preferences(feed_items, persona)

        # Sort by combined score: relevance (70%) + recency (30%)
        def score_item(item):
            # Recency score: newer items score higher
            now = datetime.now()
            age_hours = (now - item["timestamp"]).total_seconds() / 3600
            recency_score = 1.0 / (1.0 + age_hours / 24)  # Decay over days

            # Base score: relevance (70%) + recency (30%)
            base_score = (item["relevance"] * 0.7) + (recency_score * 0.3)

            # Persona boost (applied in _apply_persona_preferences via "persona_boost")
            persona_boost = item.get("persona_boost", 0.0)

            return base_score + persona_boost

        feed_items.sort(key=score_item, reverse=True)

        # ENGAGEMENT ENGINE: Graceful fallback if sparse results
        if len(feed_items) < 3:
            # Try broadening search with relaxed threshold
            fallback_items = self._generate_fallback_content(
                topic, aggregated_data, existing_items=feed_items, persona=persona
            )
            feed_items.extend(fallback_items)

        # Return top N items
        return feed_items[:count]

    def _calculate_relevance(self, text: str, topic: str) -> float:
        """
        Calculate relevance score (0-1) for text given topic.

        Uses keyword matching with normalized scoring.

        Args:
            text: Text to analyze
            topic: Topic to match against

        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not text or not topic:
            return 0.0

        text_lower = text.lower()
        topic_lower = topic.lower()

        # No mention = no relevance
        if topic_lower not in text_lower:
            return 0.0

        # Count mentions
        mention_count = text_lower.count(topic_lower)

        # Calculate density (mentions per 100 characters)
        text_length = len(text)
        density = (mention_count / text_length) * 100

        # Normalize to 0-1 scale
        # Assume 3+ mentions per 100 chars = 1.0 relevance
        score = min(density / 3.0, 1.0)

        # Boost score if topic is in first 50 characters (likely headline)
        if topic_lower in text_lower[:50]:
            score = min(score * 1.5, 1.0)

        return round(score, 2)

    def _classify_article(self, title: str, content: str) -> str:
        """
        Classify article as 'news' or 'analysis'.

        Uses keyword-based heuristics for German content.

        Args:
            title: Article title
            content: Article content

        Returns:
            "news" or "analysis"
        """
        text = f"{title} {content}".lower()

        # Analysis indicators (German and English)
        analysis_keywords = [
            "taktik", "tactic", "tactical",
            "analyse", "analysis",
            "strategie", "strategy",
            "formation",
            "spielsystem", "system",
            "schwächen", "weakness", "stärken", "strength",
            "warum", "why", "wie", "how"
        ]

        # Count analysis keywords
        analysis_count = sum(1 for keyword in analysis_keywords if keyword in text)

        # If 2+ analysis keywords, classify as analysis
        return "analysis" if analysis_count >= 2 else "news"

    def _generate_fallback_content(
        self,
        topic: str,
        aggregated_data: AggregatedData,
        existing_items: list[dict],
        persona: Optional[Persona] = None
    ) -> list[dict]:
        """
        Generate fallback content when primary search yields sparse results.

        ENGAGEMENT ENGINE STRATEGY:
        - Never show empty results
        - Broaden search with relaxed threshold
        - Suggest related content
        - Keep users engaged

        Args:
            topic: Original search topic
            aggregated_data: All available data
            existing_items: Items already found (to avoid duplicates)
            persona: User persona for ranking

        Returns:
            List of fallback feed items
        """
        fallback_items = []
        existing_urls = {item.get("url") for item in existing_items if item.get("url")}

        # Strategy 1: Lower threshold (0.3 → 0.15) for marginal matches
        for article in aggregated_data.news_articles:
            if article.url in existing_urls:
                continue

            text = f"{article.title} {article.content}"
            relevance = self._calculate_relevance(text, topic)

            # Lower threshold for fallback
            if 0.15 <= relevance < 0.3:
                category = self._classify_article(article.title, article.content)
                fallback_items.append({
                    "type": "news",
                    "headline": f"[Related] {article.title}",
                    "summary": article.content[:200] + "...",
                    "url": article.url,
                    "timestamp": article.timestamp,
                    "relevance": relevance,
                    "source": article.source.value,
                    "content_category": category,
                    "is_fallback": True
                })

        # Strategy 2: If topic is a team, broaden to Bundesliga content
        bundesliga_keywords = ["bundesliga", "liga", "tabelle", "standings"]
        if len(fallback_items) < 2:
            for article in aggregated_data.news_articles:
                if article.url in existing_urls:
                    continue

                text = f"{article.title} {article.content}".lower()
                if any(keyword in text for keyword in bundesliga_keywords):
                    category = self._classify_article(article.title, article.content)
                    fallback_items.append({
                        "type": "news",
                        "headline": f"[Bundesliga] {article.title}",
                        "summary": article.content[:200] + "...",
                        "url": article.url,
                        "timestamp": article.timestamp,
                        "relevance": 0.2,  # Lower than direct matches
                        "source": article.source.value,
                        "content_category": category,
                        "is_fallback": True
                    })

                    if len(fallback_items) >= 5:
                        break

        # Strategy 3: Show all available player stats if < 2 results
        if len(existing_items) + len(fallback_items) < 2:
            for player in aggregated_data.player_stats:
                fallback_items.append({
                    "type": "stats",
                    "headline": f"{player.player_name} - {player.team}",
                    "summary": f"{player.goals} goals, {player.assists} assists in {player.appearances} appearances",
                    "url": None,
                    "timestamp": datetime.now(),
                    "relevance": 0.15,  # Fallback relevance
                    "player_name": player.player_name,
                    "team": player.team,
                    "goals": player.goals,
                    "assists": player.assists,
                    "content_category": "stats",
                    "is_fallback": True
                })

                if len(fallback_items) >= 5:
                    break

        # Apply persona preferences to fallback items
        if persona:
            fallback_items = self._apply_persona_preferences(fallback_items, persona)

        return fallback_items[:5]  # Limit fallback items

    def _apply_persona_preferences(self, feed_items: list[dict], persona: Persona) -> list[dict]:
        """
        Apply persona-specific filtering and ranking boosts.

        Args:
            feed_items: List of feed items
            persona: User persona

        Returns:
            Modified feed items with persona_boost field added
        """
        for item in feed_items:
            boost = 0.0
            category = item.get("content_category", "news")

            if persona == Persona.CASUAL_FAN:
                # Casual fans prefer simple news over analysis
                if category == "news" and item["type"] == "event":
                    boost = 0.1  # Boost match results
                elif category == "analysis":
                    boost = -0.1  # Penalize analysis

            elif persona == Persona.EXPERT_ANALYST:
                # Expert analysts prioritize analysis and tactical content
                if category == "analysis":
                    boost = 0.2  # Strong boost for analysis
                elif category == "news" and item["type"] == "event":
                    boost = -0.05  # Slight penalty for basic match results

            elif persona == Persona.BETTING_ENTHUSIAST:
                # Betting enthusiasts want stats and factual data
                if category == "stats" or item["type"] == "stats":
                    boost = 0.15  # Boost player stats
                elif category == "analysis":
                    boost = -0.05  # Slight penalty for analysis

            elif persona == Persona.FANTASY_PLAYER:
                # Fantasy players prioritize player stats
                if item["type"] == "stats":
                    boost = 0.25  # Strong boost for player stats
                elif category == "news" and "goal" in item["headline"].lower():
                    boost = 0.1  # Boost goal-related news
                elif category == "analysis":
                    boost = -0.1  # Penalize analysis

            item["persona_boost"] = boost

        return feed_items

    def classify_content_type(self, item: dict) -> str:
        """
        DEPRECATED: Use _classify_article() instead.

        Classify feed item as 'news' or 'analysis'.

        Args:
            item: Feed item dict with headline and summary

        Returns:
            "news" or "analysis"
        """
        # For backward compatibility
        return self._classify_article(item.get("headline", ""), item.get("summary", ""))

    def adjust_feed_mix(
        self,
        feed_items: list[dict],
        mix_value: float
    ) -> list[dict]:
        """
        Adjust feed ranking based on content mix preference.

        Spec Requirement: Slider control (0=More News, 1=More Analysis)

        Args:
            feed_items: Original feed items
            mix_value: Mix preference (0.0 to 1.0)
                      0.0 = All news prioritized
                      1.0 = All analysis prioritized
                      0.5 = Balanced

        Returns:
            Re-ranked feed items
        """
        # TODO: Implement in Issue #11
        # For now, return unchanged (stub for Issue #9)
        return feed_items

    def get_conversation_state(self) -> dict:
        """
        Get current conversation state for API responses.

        Returns:
            Dict with conversation metadata
        """
        return {
            "turn_count": len(self.conversation_history),
            "detected_topic": self.current_topic,
            "feed_offered": self.feed_offered,
            "feed_accepted": self.feed_accepted,
            "recent_entities": list(self.conversation_history[-1].detected_entities)
                              if self.conversation_history else []
        }
