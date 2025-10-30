"""
Unit tests for ConversationManager.

Tests conversation state tracking, topic detection, and feed offer logic.
"""

import pytest
from datetime import datetime

from conversation_manager import ConversationManager, ConversationTurn
from models import AggregatedData


class TestConversationManager:
    """Test suite for ConversationManager class."""

    def test_initialization(self):
        """Test ConversationManager initializes correctly."""
        manager = ConversationManager()

        assert manager.conversation_history == []
        assert manager.feed_offered is False
        assert manager.feed_accepted is False
        assert manager.current_topic is None

    def test_add_turn(self):
        """Test adding conversation turns."""
        manager = ConversationManager()

        manager.add_turn(
            "When is Bayern's next game?",
            "Bayern München plays against Dortmund on Saturday."
        )

        assert len(manager.conversation_history) == 1
        assert manager.conversation_history[0].query == "When is Bayern's next game?"
        assert "Bayern Munich" in manager.conversation_history[0].detected_entities

    def test_extract_entities_teams(self):
        """Test entity extraction for team names."""
        manager = ConversationManager()

        # Test various team name formats
        entities = manager.extract_entities("When is Bayern Munich's next game?")
        assert "Bayern Munich" in entities

        entities = manager.extract_entities("How did Dortmund do last week?")
        assert "Borussia Dortmund" in entities

        entities = manager.extract_entities("Show me RB Leipzig stats")
        assert "RB Leipzig" in entities

        entities = manager.extract_entities("Gladbach vs Bayern")
        assert "Borussia Mönchengladbach" in entities
        assert "Bayern Munich" in entities

    def test_extract_entities_players(self):
        """Test entity extraction for player names."""
        manager = ConversationManager()

        entities = manager.extract_entities("How many goals does Harry Kane have?")
        assert "Harry Kane" in entities

        entities = manager.extract_entities("Musiala stats")
        assert "Jamal Musiala" in entities

        entities = manager.extract_entities("Did Wirtz score?")
        assert "Florian Wirtz" in entities

    def test_extract_entities_case_insensitive(self):
        """Test entity extraction is case-insensitive."""
        manager = ConversationManager()

        entities1 = manager.extract_entities("BAYERN MUNICH")
        entities2 = manager.extract_entities("bayern munich")
        entities3 = manager.extract_entities("Bayern Munich")

        assert entities1 == entities2 == entities3

    def test_detect_topic_pattern_insufficient_turns(self):
        """Test topic detection with < 2 turns."""
        manager = ConversationManager()

        # One turn - not enough
        manager.add_turn("When is Bayern's next game?", "Saturday")

        should_offer, topic = manager.should_offer_feed()

        assert should_offer is False
        assert topic is None

    def test_detect_topic_pattern_success(self):
        """Test topic detection with 2-3 related questions."""
        manager = ConversationManager()

        # Three Bayern questions
        manager.add_turn("When is Bayern's next game?", "Saturday")
        manager.add_turn("How did Bayern do last week?", "They won 3-1")
        manager.add_turn("Who scored for Bayern?", "Kane scored twice")

        should_offer, topic = manager.should_offer_feed()

        assert should_offer is True
        assert topic == "Bayern Munich"
        assert manager.feed_offered is True

    def test_detect_topic_pattern_mixed_topics(self):
        """Test topic detection with different topics."""
        manager = ConversationManager()

        # Different topics in each question
        manager.add_turn("When is Bayern's next game?", "Saturday")
        manager.add_turn("Show me Bundesliga standings", "Here are the standings")
        manager.add_turn("What are the latest odds?", "Here are the odds")

        should_offer, topic = manager.should_offer_feed()

        assert should_offer is False
        assert topic is None

    def test_detect_topic_pattern_two_mentions_minimum(self):
        """Test that 2 mentions are required for topic detection."""
        manager = ConversationManager()

        # Only 2 turns, but both mention Bayern
        manager.add_turn("When is Bayern's next game?", "Saturday")
        manager.add_turn("How did Bayern do last week?", "They won")

        should_offer, topic = manager.should_offer_feed()

        assert should_offer is True
        assert topic == "Bayern Munich"

    def test_feed_offer_not_repeated(self):
        """Test that feed offer is only made once."""
        manager = ConversationManager()

        # Create pattern
        manager.add_turn("Bayern game?", "Saturday")
        manager.add_turn("Bayern score?", "3-1")

        # First check - should offer
        should_offer1, topic1 = manager.should_offer_feed()
        assert should_offer1 is True

        # Second check - should NOT offer again
        should_offer2, topic2 = manager.should_offer_feed()
        assert should_offer2 is False

    def test_accept_feed_offer(self):
        """Test accepting feed offer."""
        manager = ConversationManager()

        manager.add_turn("Bayern game?", "Saturday")
        manager.add_turn("Bayern score?", "3-1")

        should_offer, topic = manager.should_offer_feed()
        assert should_offer is True

        manager.accept_feed_offer()
        assert manager.feed_accepted is True

    def test_reset_feed_state(self):
        """Test resetting feed state."""
        manager = ConversationManager()

        # Create state
        manager.add_turn("Bayern game?", "Saturday")
        manager.add_turn("Bayern score?", "3-1")
        manager.should_offer_feed()
        manager.accept_feed_offer()

        assert manager.feed_offered is True
        assert manager.feed_accepted is True
        assert manager.current_topic is not None

        # Reset
        manager.reset_feed_state()

        assert manager.feed_offered is False
        assert manager.feed_accepted is False
        assert manager.current_topic is None

    def test_get_conversation_state(self):
        """Test getting conversation state."""
        manager = ConversationManager()

        # Initial state
        state = manager.get_conversation_state()
        assert state["turn_count"] == 0
        assert state["detected_topic"] is None
        assert state["feed_offered"] is False

        # Add turns
        manager.add_turn("Bayern game?", "Saturday")
        manager.add_turn("Bayern score?", "3-1")
        manager.should_offer_feed()

        state = manager.get_conversation_state()
        assert state["turn_count"] == 2
        assert state["detected_topic"] == "Bayern Munich"
        assert state["feed_offered"] is True
        assert "Bayern Munich" in state["recent_entities"]

    def test_topic_detection_with_player_names(self):
        """Test topic detection with repeated player mentions."""
        manager = ConversationManager()

        # Three questions about Harry Kane
        manager.add_turn("How many goals does Kane have?", "15 goals")
        manager.add_turn("Did Kane score today?", "Yes, twice")

        should_offer, topic = manager.should_offer_feed()

        assert should_offer is True
        assert topic == "Harry Kane"

    def test_conversation_turn_dataclass(self):
        """Test ConversationTurn dataclass."""
        turn = ConversationTurn(
            query="Test query",
            response="Test response",
            detected_entities={"Bayern Munich"}
        )

        assert turn.query == "Test query"
        assert turn.response == "Test response"
        assert "Bayern Munich" in turn.detected_entities
        assert isinstance(turn.timestamp, datetime)

    def test_empty_query_no_entities(self):
        """Test that empty queries don't cause errors."""
        manager = ConversationManager()

        entities = manager.extract_entities("")
        assert entities == set()

        manager.add_turn("", "Response")
        assert len(manager.conversation_history) == 1
        assert manager.conversation_history[0].detected_entities == set()

    def test_special_characters_in_queries(self):
        """Test queries with special characters."""
        manager = ConversationManager()

        # German umlauts
        entities = manager.extract_entities("Wie geht's Bayern München?")
        assert "Bayern Munich" in entities

        # Punctuation
        entities = manager.extract_entities("Bayern vs. Dortmund - who wins?!")
        assert "Bayern Munich" in entities
        assert "Borussia Dortmund" in entities

    def test_multiple_teams_in_one_query(self):
        """Test extracting multiple teams from single query."""
        manager = ConversationManager()

        entities = manager.extract_entities(
            "Bayern plays Dortmund, while Leipzig faces Leverkusen"
        )

        assert "Bayern Munich" in entities
        assert "Borussia Dortmund" in entities
        assert "RB Leipzig" in entities
        assert "Bayer Leverkusen" in entities

    # Tests for Issue #10: Feed Generation

    def test_generate_feed_with_empty_data(self):
        """Test feed generation with no data."""
        manager = ConversationManager()
        data = AggregatedData()

        feed = manager.generate_feed("Bayern Munich", data, count=10)

        assert isinstance(feed, list)
        assert len(feed) == 0

    def test_generate_feed_with_news_articles(self):
        """Test feed generation with news articles."""
        from models import NewsArticle, DataSource
        from datetime import datetime

        manager = ConversationManager()

        # Create mock data with Bayern-related article
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Bayern Munich wins 3-1",
            content="Bayern Munich dominated the match with excellent performance.",
            url="https://kicker.de/test",
            timestamp=datetime.now()
        )

        data = AggregatedData(news_articles=[article])
        feed = manager.generate_feed("Bayern Munich", data, count=10)

        assert len(feed) >= 1
        assert feed[0]["type"] == "news"
        assert "Bayern Munich" in feed[0]["headline"]
        assert feed[0]["relevance"] > 0.3

    def test_generate_feed_filters_irrelevant_content(self):
        """Test that feed filters out irrelevant content."""
        from models import NewsArticle, DataSource
        from datetime import datetime

        manager = ConversationManager()

        # Create articles - one relevant, one not
        relevant = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Bayern Munich wins championship",
            content="Bayern secured the title with a convincing win.",
            timestamp=datetime.now()
        )

        irrelevant = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Dortmund signs new player",
            content="Dortmund announced a new signing from abroad.",
            timestamp=datetime.now()
        )

        data = AggregatedData(news_articles=[relevant, irrelevant])
        feed = manager.generate_feed("Bayern Munich", data, count=10)

        # Should only include Bayern article
        assert len(feed) == 1
        assert "Bayern" in feed[0]["headline"]

    def test_generate_feed_sorts_by_relevance(self):
        """Test that feed sorts items by relevance."""
        from models import NewsArticle, DataSource
        from datetime import datetime

        manager = ConversationManager()

        # Create articles with different relevance
        high_relevance = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Bayern Munich Bayern Munich Bayern Munich",
            content="Bayern Bayern Bayern" * 10,
            timestamp=datetime.now()
        )

        low_relevance = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="News about Bayern Munich",
            content="Some other content here.",
            timestamp=datetime.now()
        )

        data = AggregatedData(news_articles=[low_relevance, high_relevance])
        feed = manager.generate_feed("Bayern Munich", data, count=10)

        assert len(feed) == 2
        # Higher relevance should be first
        assert feed[0]["relevance"] > feed[1]["relevance"]

    def test_generate_feed_respects_count_limit(self):
        """Test that feed respects count parameter."""
        from models import NewsArticle, DataSource
        from datetime import datetime

        manager = ConversationManager()

        # Create 5 articles
        articles = [
            NewsArticle(
                source=DataSource.KICKER_RSS,
                title=f"Bayern Munich news {i}",
                content="Bayern Munich content.",
                timestamp=datetime.now()
            )
            for i in range(5)
        ]

        data = AggregatedData(news_articles=articles)

        # Request only 3
        feed = manager.generate_feed("Bayern Munich", data, count=3)

        assert len(feed) == 3

    def test_calculate_relevance(self):
        """Test relevance scoring."""
        manager = ConversationManager()

        # High relevance (multiple mentions)
        score1 = manager._calculate_relevance("Bayern Munich Bayern Munich Bayern Munich", "Bayern Munich")
        assert score1 > 0.5

        # Medium relevance (single mention in headline - gets boosted)
        score2 = manager._calculate_relevance("Bayern Munich and other news about the league", "Bayern Munich")
        assert score2 > 0.3  # Boosted by being in first 50 chars

        # Low relevance (mention not in headline)
        score3 = manager._calculate_relevance("Some other news and information about the league with Bayern Munich mentioned", "Bayern Munich")
        assert 0.0 < score3 <= 0.5

        # No relevance
        score4 = manager._calculate_relevance("Dortmund wins match", "Bayern Munich")
        assert score4 == 0.0

        # Empty text
        score5 = manager._calculate_relevance("", "Bayern Munich")
        assert score5 == 0.0

    def test_generate_feed_with_player_name(self):
        """Test feed generation for player names."""
        from models import PlayerStats, DataSource
        from datetime import datetime

        manager = ConversationManager()

        # Create mock player stat
        kane = PlayerStats(
            source=DataSource.SPORTS_API,
            player_name="Harry Kane",
            team="Bayern München",
            position="Forward",
            goals=15,
            assists=5,
            appearances=20,
            minutes_played=1800
        )

        data = AggregatedData(player_stats=[kane])
        feed = manager.generate_feed("Harry Kane", data, count=10)

        assert len(feed) >= 1
        assert feed[0]["type"] == "stats"
        assert "Harry Kane" in feed[0]["headline"]
        assert feed[0]["relevance"] == 1.0  # Direct name match

    def test_classify_article_news(self):
        """Test article classification as news."""
        manager = ConversationManager()

        category = manager._classify_article(
            "Bayern Munich wins 3-0",
            "Bayern secured a victory with dominant performance."
        )

        assert category == "news"

    def test_classify_article_analysis(self):
        """Test article classification as analysis."""
        manager = ConversationManager()

        category = manager._classify_article(
            "Tactical Analysis: Bayern Munich's formation",
            "How Bayern Munich's tactical flexibility and strategic system dominated"
        )

        assert category == "analysis"

    def test_persona_aware_feed_casual_fan(self):
        """Test persona-aware feed for casual fan."""
        from models import NewsArticle, SportsEvent, DataSource
        from datetime import datetime
        from user_config import Persona

        manager = ConversationManager()

        # Create mix of content
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Tactical Analysis: Bayern Munich formation",
            content="Bayern Munich's tactical system and strategic flexibility",
            timestamp=datetime.now()
        )

        event = SportsEvent(
            source=DataSource.SPORTS_API,
            event_type="match",
            title="Bayern Munich 3-0 Dortmund",
            content="Match result",
            timestamp=datetime.now(),
            home_team="Bayern Munich",
            away_team="Dortmund",
            score="3-0",
            league="Bundesliga"
        )

        data = AggregatedData(news_articles=[article], sports_events=[event])

        # Generate feed with casual fan persona
        feed = manager.generate_feed("Bayern Munich", data, count=10, persona=Persona.CASUAL_FAN)

        # Casual fan should boost match event and penalize analysis
        event_item = next((item for item in feed if item["type"] == "event"), None)
        analysis_item = next((item for item in feed if item.get("content_category") == "analysis"), None)

        assert event_item is not None
        assert event_item.get("persona_boost", 0) == 0.1  # Boosted

        if analysis_item:
            assert analysis_item.get("persona_boost", 0) == -0.1  # Penalized

    def test_persona_aware_feed_expert_analyst(self):
        """Test persona-aware feed for expert analyst."""
        from models import NewsArticle, DataSource
        from datetime import datetime
        from user_config import Persona

        manager = ConversationManager()

        # Create tactical analysis article
        article = NewsArticle(
            source=DataSource.KICKER_RSS,
            title="Tactical Analysis: Bayern Munich's formation changes",
            content="Bayern Munich's tactical flexibility and strategic positioning",
            timestamp=datetime.now()
        )

        data = AggregatedData(news_articles=[article])

        # Generate feed with expert analyst persona
        feed = manager.generate_feed("Bayern Munich", data, count=10, persona=Persona.EXPERT_ANALYST)

        # Expert analyst should boost analysis
        analysis_item = next((item for item in feed if item.get("content_category") == "analysis"), None)

        assert analysis_item is not None
        assert analysis_item.get("persona_boost", 0) == 0.2  # Strong boost

    def test_persona_aware_feed_fantasy_player(self):
        """Test persona-aware feed for fantasy player."""
        from models import PlayerStats, DataSource
        from user_config import Persona

        manager = ConversationManager()

        # Create player stats
        kane = PlayerStats(
            source=DataSource.SPORTS_API,
            player_name="Harry Kane",
            team="Bayern Munich",
            position="Forward",
            goals=36,
            assists=8,
            appearances=33,
            minutes_played=2970
        )

        data = AggregatedData(player_stats=[kane])

        # Generate feed with fantasy player persona
        feed = manager.generate_feed("Bayern Munich", data, count=10, persona=Persona.FANTASY_PLAYER)

        # Fantasy player should strongly boost player stats
        stats_item = next((item for item in feed if item["type"] == "stats"), None)

        assert stats_item is not None
        assert stats_item.get("persona_boost", 0) == 0.25  # Huge boost
