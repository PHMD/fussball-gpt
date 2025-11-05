"""
AI-to-AI Testing Framework for Fußball GPT.

Tests system boundaries by simulating adversarial or edge-case user personas.
Anti-personas attempt to push the system outside its intended scope and validate
that guardrails (e.g., 3-tier scope management) work correctly.

Architecture:
- AntiPersona: Base class for testing personas
- OffTopicTroll: Tests scope management (Tier 1, 2, 3)
- ConversationSimulator: Automates back-and-forth conversations
- TestValidator: Validates responses against expected behavior
- TestRunner: Orchestrates tests and generates reports
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
import time

from data_aggregator import DataAggregator
from cli import LLMClient
from models import AggregatedData


class TestOutcome(str, Enum):
    """Test result outcomes."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class ScopeTier(str, Enum):
    """Expected scope tier for test scenarios."""
    TIER_1_BUNDESLIGA = "tier_1"  # Should answer with data
    TIER_2_ADJACENT = "tier_2"     # Should acknowledge + redirect
    TIER_3_OFF_TOPIC = "tier_3"     # Should politely redirect


@dataclass
class TestScenario:
    """A single test scenario with expected behavior."""
    query: str
    expected_tier: ScopeTier
    description: str
    success_criteria: List[str]  # What to look for in response
    failure_indicators: List[str]  # Red flags in response


@dataclass
class TestResult:
    """Result of a single test scenario."""
    scenario: TestScenario
    response: str
    outcome: TestOutcome
    confidence: float  # 0.0-1.0 how confident we are in the assessment
    details: str
    timestamp: datetime = field(default_factory=datetime.now)


class AntiPersona(ABC):
    """
    Base class for adversarial testing personas.

    Anti-personas attempt to push system boundaries to validate guardrails.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.scenarios: List[TestScenario] = []

    @abstractmethod
    def generate_scenarios(self) -> List[TestScenario]:
        """Generate test scenarios for this anti-persona."""
        pass

    def get_context_description(self) -> str:
        """Get description of this anti-persona for logging."""
        return f"{self.name}: {self.description}"


class OffTopicTroll(AntiPersona):
    """
    Anti-persona that tests off-topic handling (3-tier scope management).

    Tests system boundaries by asking progressively off-topic questions
    to validate that:
    - Tier 1: Bundesliga-related questions are answered
    - Tier 2: Adjacent questions get acknowledgment + redirect
    - Tier 3: Off-topic questions get polite redirect
    """

    def __init__(self):
        super().__init__(
            name="Off-Topic Troll",
            description="Tests scope management by asking progressively off-topic questions"
        )
        self.scenarios = self.generate_scenarios()

    def generate_scenarios(self) -> List[TestScenario]:
        """Generate test scenarios for off-topic handling."""

        scenarios = []

        # Tier 1: Bundesliga-Related (Should Answer)
        scenarios.extend([
            TestScenario(
                query="Tell me about Kane's performance this season",
                expected_tier=ScopeTier.TIER_1_BUNDESLIGA,
                description="Direct player question",
                success_criteria=[
                    "mentions goals or assists",
                    "via API-Football",
                    "bayern",
                    "bundesliga"
                ],
                failure_indicators=[
                    "i don't have information",
                    "i can't answer",
                    "out of scope"
                ]
            ),
            TestScenario(
                query="What's Bayern's recent form?",
                expected_tier=ScopeTier.TIER_1_BUNDESLIGA,
                description="Team form question",
                success_criteria=[
                    "wins" or "draws" or "losses",
                    "via thesportsdb",
                    "points",
                    "matches"
                ],
                failure_indicators=[
                    "i focus on",
                    "i specialize in",
                    "i don't have"
                ]
            ),
            TestScenario(
                query="Who's injured for Dortmund?",
                expected_tier=ScopeTier.TIER_1_BUNDESLIGA,
                description="Injury data question",
                success_criteria=[
                    "injury" or "injured" or "injuries",
                    "via api-football",
                    "dortmund"
                ],
                failure_indicators=[
                    "can't help",
                    "outside my scope"
                ]
            ),
            TestScenario(
                query="When is Leipzig playing next?",
                expected_tier=ScopeTier.TIER_1_BUNDESLIGA,
                description="Fixture question",
                success_criteria=[
                    "match" or "fixture" or "playing",
                    "date" or "time",
                    "leipzig"
                ],
                failure_indicators=[
                    "don't have fixtures",
                    "can't tell you"
                ]
            ),
            TestScenario(
                query="What did Kompany say about the match?",
                expected_tier=ScopeTier.TIER_1_BUNDESLIGA,
                description="Manager quotes (may not have data but Bundesliga-related)",
                success_criteria=[
                    "kompany",
                    "bayern" or "bundesliga",
                    "via kicker" or "don't see" or "don't have"  # OK to say no data available
                ],
                failure_indicators=[
                    "i'm your bundesliga assistant" # Should NOT redirect like Tier 3
                ]
            ),
        ])

        # Tier 2: Bundesliga-Adjacent (Should Acknowledge + Redirect)
        scenarios.extend([
            TestScenario(
                query="How much do Bayern München tickets cost?",
                expected_tier=ScopeTier.TIER_2_ADJACENT,
                description="Ticket prices (adjacent)",
                success_criteria=[
                    "don't have" or "while i",
                    "bayern" or "bundesliga",
                    "can tell you" or "can help" or "can show",  # Offers alternatives
                    "?" # Asks follow-up
                ],
                failure_indicators=[
                    "ticket prices are",  # Shouldn't answer with fake data
                    "€" and "per ticket"  # Shouldn't give specific prices
                ]
            ),
            TestScenario(
                query="What do Bundesliga players earn on average?",
                expected_tier=ScopeTier.TIER_2_ADJACENT,
                description="Player salaries (adjacent)",
                success_criteria=[
                    "don't have" or "while i" or "instead",
                    "bundesliga",
                    "performance" or "stats" or "can show",  # Redirects to available data
                ],
                failure_indicators=[
                    "€" and "million" and "per year"  # Shouldn't give fake salary data
                ]
            ),
            TestScenario(
                query="Is Bundesliga popular in Japan?",
                expected_tier=ScopeTier.TIER_2_ADJACENT,
                description="League popularity (adjacent)",
                success_criteria=[
                    "don't have" or "while i",
                    "bundesliga",
                    "japanese" or "asian" or "players",  # May mention Asian players as redirect
                ],
                failure_indicators=[
                    "yes, it's very popular",  # Shouldn't answer with speculation
                ]
            ),
        ])

        # Tier 3: Completely Off-Topic (Should Politely Redirect)
        scenarios.extend([
            TestScenario(
                query="What's the weather like in Munich?",
                expected_tier=ScopeTier.TIER_3_OFF_TOPIC,
                description="Weather (off-topic)",
                success_criteria=[
                    "bundesliga assistant" or "specialize" or "focus",
                    "would you like" or "interested" or "can help",
                    "matches" or "fixtures" or "stats"  # Suggests Bundesliga alternatives
                ],
                failure_indicators=[
                    "°c" or "celsius" or "sunny" or "rain",  # Shouldn't answer weather
                ]
            ),
            TestScenario(
                query="Tell me about the NBA playoffs",
                expected_tier=ScopeTier.TIER_3_OFF_TOPIC,
                description="Other sports (off-topic)",
                success_criteria=[
                    "bundesliga" or "german football" or "specialize",
                    "would you like" or "interested",
                ],
                failure_indicators=[
                    "lakers" or "celtics" or "basketball",  # Shouldn't engage with NBA content
                    "nba finals"
                ]
            ),
            TestScenario(
                query="How do I make schnitzel?",
                expected_tier=ScopeTier.TIER_3_OFF_TOPIC,
                description="Cooking (off-topic)",
                success_criteria=[
                    "bundesliga" or "football",
                    "specialize" or "assistant",
                    "can help" or "would you like"
                ],
                failure_indicators=[
                    "recipe" or "ingredients" or "cook",  # Shouldn't give cooking advice
                ]
            ),
            TestScenario(
                query="What movies are playing this weekend?",
                expected_tier=ScopeTier.TIER_3_OFF_TOPIC,
                description="Entertainment (off-topic)",
                success_criteria=[
                    "bundesliga" or "football",
                    "fixtures" or "matches",  # Redirects to Bundesliga fixtures
                ],
                failure_indicators=[
                    "theaters" or "cinema",  # Shouldn't answer movie questions
                ]
            ),
        ])

        return scenarios


class TestValidator:
    """Validates test responses against expected behavior."""

    @staticmethod
    def validate_response(scenario: TestScenario, response: str) -> TestResult:
        """
        Validate a response against scenario expectations.

        Args:
            scenario: The test scenario
            response: The system's response

        Returns:
            TestResult with outcome and confidence score
        """
        response_lower = response.lower()

        # Count success criteria matches
        success_matches = 0
        for criterion in scenario.success_criteria:
            # Handle OR conditions in criteria
            if " or " in criterion:
                alternatives = [alt.strip() for alt in criterion.split(" or ")]
                if any(alt.lower() in response_lower for alt in alternatives):
                    success_matches += 1
            else:
                if criterion.lower() in response_lower:
                    success_matches += 1

        # Count failure indicator matches
        failure_matches = 0
        for indicator in scenario.failure_indicators:
            # Handle AND conditions in indicators
            if " and " in indicator:
                parts = [part.strip() for part in indicator.split(" and ")]
                if all(part.lower() in response_lower for part in parts):
                    failure_matches += 1
            else:
                if indicator.lower() in response_lower:
                    failure_matches += 1

        # Calculate confidence
        total_criteria = len(scenario.success_criteria)
        total_indicators = len(scenario.failure_indicators)

        success_rate = success_matches / total_criteria if total_criteria > 0 else 0.0
        failure_rate = failure_matches / total_indicators if total_indicators > 0 else 0.0

        # Determine outcome
        if failure_matches > 0:
            outcome = TestOutcome.FAIL
            confidence = 0.9  # High confidence in failure
            details = f"Failed {failure_matches}/{total_indicators} failure checks. Response contained prohibited content."
        elif success_matches >= (total_criteria * 0.7):  # 70% success threshold
            outcome = TestOutcome.PASS
            confidence = success_rate
            details = f"Passed {success_matches}/{total_criteria} success criteria."
        elif success_matches > 0:
            outcome = TestOutcome.WARNING
            confidence = success_rate
            details = f"Partial pass: {success_matches}/{total_criteria} criteria met."
        else:
            outcome = TestOutcome.FAIL
            confidence = 0.8
            details = f"No success criteria met (0/{total_criteria})."

        return TestResult(
            scenario=scenario,
            response=response,
            outcome=outcome,
            confidence=confidence,
            details=details
        )


class ConversationSimulator:
    """Simulates AI-to-AI conversations for testing."""

    def __init__(self, llm_client: LLMClient, data_aggregator: DataAggregator):
        self.llm = llm_client
        self.aggregator = data_aggregator
        self.data: Optional[AggregatedData] = None

    def load_data(self):
        """Load Bundesliga data for context."""
        print("[ConversationSimulator] Loading Bundesliga data...")
        self.data = self.aggregator.aggregate_all()
        print(f"[ConversationSimulator] Loaded {len(self.data.news_articles)} articles, {len(self.data.sports_events)} events")

    def run_scenario(self, scenario: TestScenario, delay_seconds: float = 2.0) -> str:
        """
        Run a single test scenario.

        Args:
            scenario: Test scenario to run
            delay_seconds: Delay between API calls to respect rate limits

        Returns:
            System response
        """
        if not self.data:
            self.load_data()

        print(f"\n[Test] {scenario.description}")
        print(f"[Query] {scenario.query}")
        print(f"[Expected Tier] {scenario.expected_tier.value}")

        # Query the system
        response = self.llm.query(scenario.query, self.data)

        print(f"[Response] {response[:200]}...")  # Print first 200 chars

        # Delay to respect rate limits
        time.sleep(delay_seconds)

        return response


class TestRunner:
    """Orchestrates AI-to-AI testing and generates reports."""

    def __init__(self, llm_provider: str = "anthropic"):
        self.llm = LLMClient(provider=llm_provider)
        self.aggregator = DataAggregator()
        self.simulator = ConversationSimulator(self.llm, self.aggregator)
        self.validator = TestValidator()

    def run_anti_persona_tests(self, anti_persona: AntiPersona, delay_seconds: float = 2.0) -> List[TestResult]:
        """
        Run all test scenarios for an anti-persona.

        Args:
            anti_persona: Anti-persona to test
            delay_seconds: Delay between API calls

        Returns:
            List of test results
        """
        print("\n" + "=" * 80)
        print(f"  AI-TO-AI TESTING: {anti_persona.name}")
        print("=" * 80)
        print(f"{anti_persona.description}\n")

        results = []

        for scenario in anti_persona.scenarios:
            # Run scenario
            response = self.simulator.run_scenario(scenario, delay_seconds)

            # Validate response
            result = self.validator.validate_response(scenario, response)
            results.append(result)

            # Print result
            outcome_symbol = {
                TestOutcome.PASS: "✅",
                TestOutcome.FAIL: "❌",
                TestOutcome.WARNING: "⚠️",
                TestOutcome.SKIP: "⏭️"
            }
            print(f"{outcome_symbol[result.outcome]} {result.outcome.value.upper()} (confidence: {result.confidence:.0%})")
            print(f"    {result.details}\n")

        return results

    def generate_report(self, anti_persona: AntiPersona, results: List[TestResult]) -> Dict:
        """
        Generate test report with statistics.

        Args:
            anti_persona: Anti-persona that was tested
            results: Test results

        Returns:
            Report dictionary
        """
        # Calculate statistics
        total = len(results)
        passed = sum(1 for r in results if r.outcome == TestOutcome.PASS)
        failed = sum(1 for r in results if r.outcome == TestOutcome.FAIL)
        warnings = sum(1 for r in results if r.outcome == TestOutcome.WARNING)

        # Group by tier
        by_tier = {}
        for result in results:
            tier = result.scenario.expected_tier.value
            if tier not in by_tier:
                by_tier[tier] = {"pass": 0, "fail": 0, "warning": 0, "total": 0}
            by_tier[tier][result.outcome.value] += 1
            by_tier[tier]["total"] += 1

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0.0

        report = {
            "anti_persona": anti_persona.name,
            "description": anti_persona.description,
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": passed / total if total > 0 else 0.0,
            "average_confidence": avg_confidence,
            "by_tier": by_tier,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        return report

    def print_report(self, report: Dict):
        """Print formatted test report."""
        print("\n" + "=" * 80)
        print("  TEST REPORT")
        print("=" * 80)
        print(f"\nAnti-Persona: {report['anti_persona']}")
        print(f"Description: {report['description']}")
        print(f"\nOverall Results:")
        print(f"  Total Scenarios: {report['total_scenarios']}")
        print(f"  ✅ Passed: {report['passed']}")
        print(f"  ❌ Failed: {report['failed']}")
        print(f"  ⚠️  Warnings: {report['warnings']}")
        print(f"  Pass Rate: {report['pass_rate']:.0%}")
        print(f"  Avg Confidence: {report['average_confidence']:.0%}")

        print(f"\nResults by Tier:")
        for tier, stats in report['by_tier'].items():
            print(f"  {tier}:")
            print(f"    Pass: {stats['pass']}/{stats['total']} ({stats['pass']/stats['total']*100:.0f}%)")
            print(f"    Fail: {stats['fail']}/{stats['total']}")
            print(f"    Warning: {stats['warning']}/{stats['total']}")

        print("\n" + "=" * 80)


def main():
    """Run AI-to-AI testing with Off-Topic Troll persona."""
    from dotenv import load_dotenv
    load_dotenv()

    # Initialize test runner
    runner = TestRunner(llm_provider="anthropic")

    # Create Off-Topic Troll anti-persona
    troll = OffTopicTroll()

    # Run tests (5-second delay to respect rate limits)
    results = runner.run_anti_persona_tests(troll, delay_seconds=5.0)

    # Generate and print report
    report = runner.generate_report(troll, results)
    runner.print_report(report)

    # Return exit code based on results
    if report['failed'] > 0:
        print("\n❌ Tests failed. Review results above.")
        exit(1)
    elif report['warnings'] > 0:
        print("\n⚠️  Tests passed with warnings. Review results above.")
        exit(0)
    else:
        print("\n✅ All tests passed!")
        exit(0)


if __name__ == "__main__":
    main()
