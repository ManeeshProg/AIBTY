import pytest
from app.ai_pipeline.scoring.deterministic import DeterministicScorer
from app.ai_pipeline.scoring.schemas import GoalScoreInput

class TestDeterministicScorer:
    """Tests for deterministic scoring engine."""

    @pytest.fixture
    def scorer(self):
        return DeterministicScorer()

    def test_no_engagement_returns_zero(self, scorer):
        """Entry with no goal-related content scores 0."""
        input = GoalScoreInput(
            goal_category="fitness",
            goal_description="Exercise 30 minutes daily",
            target_value=30,
            journal_content="Today I just watched TV and ordered pizza."
        )
        result = scorer.score_goal(input)

        assert result.base_score == 0.0
        assert result.showed_up is False
        assert result.effort_level == "none"

    def test_basic_engagement_scores_minimum(self, scorer):
        """Entry mentioning goal category gets base points."""
        input = GoalScoreInput(
            goal_category="fitness",
            goal_description="Exercise 30 minutes daily",
            target_value=30,
            journal_content="Went to the gym today."
        )
        result = scorer.score_goal(input)

        assert result.base_score >= 30.0  # Showed up points
        assert result.showed_up is True
        assert len(result.evidence) > 0

    def test_high_effort_scores_higher(self, scorer):
        """Entry with effort indicators scores higher."""
        input = GoalScoreInput(
            goal_category="fitness",
            goal_description="Exercise 30 minutes daily",
            target_value=30,
            journal_content="Crushed my workout today! Did 5 sets of hard squats and ran 3 miles. Pushed myself beyond my limits."
        )
        result = scorer.score_goal(input)

        assert result.base_score >= 70.0
        assert result.showed_up is True
        assert result.effort_level in ["substantial", "exceptional"]

    def test_quantifiers_add_points(self, scorer):
        """Numbers/quantifiers indicate specificity and add points."""
        input = GoalScoreInput(
            goal_category="learning",
            goal_description="Read 30 minutes daily",
            target_value=30,
            journal_content="Read 45 pages of my book today."
        )
        result = scorer.score_goal(input)

        # Should get quantifier bonus
        assert result.base_score >= 40.0

    def test_determinism(self, scorer):
        """Same input always produces same output."""
        input = GoalScoreInput(
            goal_category="productivity",
            goal_description="Complete 3 tasks daily",
            target_value=3,
            journal_content="Finished the report, sent emails, and reviewed the code."
        )

        results = [scorer.score_goal(input) for _ in range(5)]
        scores = [r.base_score for r in results]

        assert all(s == scores[0] for s in scores), "Scores should be identical"

    def test_evidence_extraction(self, scorer):
        """Evidence contains relevant sentences."""
        input = GoalScoreInput(
            goal_category="fitness",
            goal_description="Workout daily",
            target_value=1,
            journal_content="Morning was slow. Hit the gym at noon. Did my workout routine. Evening was relaxing."
        )
        result = scorer.score_goal(input)

        assert len(result.evidence) > 0
        assert any("gym" in e.lower() or "workout" in e.lower() for e in result.evidence)

    def test_reasoning_is_readable(self, scorer):
        """Reasoning provides human-readable explanation."""
        input = GoalScoreInput(
            goal_category="fitness",
            goal_description="Exercise daily",
            target_value=1,
            journal_content="Did my morning run today."
        )
        result = scorer.score_goal(input)

        assert "fitness" in result.reasoning.lower()
        assert len(result.reasoning) > 10

    def test_unknown_category_uses_fallback(self, scorer):
        """Unknown categories use category name as keyword."""
        input = GoalScoreInput(
            goal_category="gardening",
            goal_description="Water plants daily",
            target_value=1,
            journal_content="Spent time gardening and watering the plants."
        )
        result = scorer.score_goal(input)

        assert result.showed_up is True
        assert result.base_score > 0
