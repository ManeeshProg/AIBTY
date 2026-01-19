import re
from typing import Sequence
from app.ai_pipeline.scoring.schemas import GoalScoreInput, GoalScoreOutput, ScoringResult
from app.models.goal import UserGoal

class DeterministicScorer:
    """
    Deterministic scoring engine for journal entries.

    Provides base scores using:
    - Keyword matching against goal categories
    - Activity/verb detection (did, completed, worked, exercised, etc.)
    - Quantifier detection (numbers, durations, frequencies)
    - Effort words (hard, easy, struggled, crushed, etc.)

    This handles ~70% of scoring logic. LLM enhancement adjusts within guardrails.
    """

    # Category-specific keywords (extend as needed)
    CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "fitness": ["workout", "exercise", "gym", "run", "running", "walk", "weights", "cardio",
                   "pushups", "squats", "yoga", "stretch", "miles", "steps", "active"],
        "productivity": ["work", "project", "task", "completed", "finished", "shipped", "meeting",
                        "code", "coding", "wrote", "built", "created", "delivered", "deadline"],
        "learning": ["read", "reading", "book", "studied", "study", "learned", "course", "class",
                    "tutorial", "practice", "skill", "chapter", "pages", "lesson"],
        "health": ["sleep", "slept", "water", "meal", "ate", "diet", "vitamin", "meditation",
                  "meditate", "rest", "recovery", "hydration", "nutrition"],
        "discipline": ["woke", "early", "routine", "habit", "consistent", "daily", "streak",
                      "morning", "schedule", "planned", "followed", "stuck"],
        "wellbeing": ["happy", "grateful", "mood", "feeling", "relaxed", "calm", "peace",
                     "joy", "content", "mindful", "present", "balanced"],
    }

    # Effort indicators (positive)
    EFFORT_POSITIVE = ["hard", "challenging", "pushed", "intense", "maximum", "best", "crushed",
                       "exceeded", "extra", "above", "beyond", "difficult"]

    # Effort indicators (negative/minimal)
    EFFORT_NEGATIVE = ["easy", "minimal", "quick", "brief", "short", "simple", "basic",
                       "half", "barely", "almost", "skipped", "missed"]

    # Activity verbs indicating engagement
    ACTIVITY_VERBS = ["did", "completed", "finished", "worked", "exercised", "practiced",
                      "wrote", "read", "studied", "built", "created", "made", "went", "ran"]

    def __init__(self):
        # Pre-compile regex patterns for efficiency
        self._number_pattern = re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|minutes?|mins?|pages?|miles?|km|reps?|sets?|times?)\b', re.IGNORECASE)
        self._activity_pattern = re.compile(r'\b(' + '|'.join(self.ACTIVITY_VERBS) + r')\b', re.IGNORECASE)

    def score_goal(self, input: GoalScoreInput) -> GoalScoreOutput:
        """Score a single goal against journal content."""
        content_lower = input.journal_content.lower()

        # 1. Check if goal category mentioned (keyword matching)
        keywords = self._get_keywords_for_category(input.goal_category)
        keyword_matches = [kw for kw in keywords if kw in content_lower]

        # 2. Extract evidence (sentences containing keywords)
        evidence = self._extract_evidence(input.journal_content, keyword_matches)

        # 3. Detect if user "showed up" (any engagement with category)
        showed_up = len(keyword_matches) > 0 or self._category_in_description(
            content_lower, input.goal_description
        )

        # 4. Detect effort level
        effort_level = self._assess_effort(content_lower, keyword_matches)

        # 5. Calculate base score
        base_score = self._calculate_base_score(
            showed_up=showed_up,
            keyword_count=len(keyword_matches),
            effort_level=effort_level,
            has_quantifiers=bool(self._number_pattern.search(content_lower)),
            evidence_count=len(evidence)
        )

        # 6. Generate reasoning
        reasoning = self._generate_reasoning(
            category=input.goal_category,
            showed_up=showed_up,
            keyword_matches=keyword_matches,
            effort_level=effort_level,
            base_score=base_score
        )

        return GoalScoreOutput(
            category=input.goal_category,
            base_score=base_score,
            showed_up=showed_up,
            effort_level=effort_level,
            evidence=evidence[:3],  # Limit to top 3 evidence pieces
            reasoning=reasoning
        )

    def score_entry(
        self,
        journal_content: str,
        goals: Sequence[UserGoal]
    ) -> ScoringResult:
        """Score a journal entry against all user goals."""
        goal_scores: list[GoalScoreOutput] = []

        for goal in goals:
            if not goal.is_active:
                continue

            input = GoalScoreInput(
                goal_category=goal.category,
                goal_description=goal.description,
                target_value=goal.target_value,
                journal_content=journal_content
            )
            score = self.score_goal(input)
            goal_scores.append(score)

        # Calculate overall engagement
        goals_addressed = sum(1 for gs in goal_scores if gs.showed_up)
        goals_total = len(goal_scores)

        if goals_total == 0:
            overall_engagement = 0.0
        else:
            # Weighted average of scores (weight=1 if showed_up, 0.5 otherwise)
            total_weighted = sum(
                gs.base_score * (1.0 if gs.showed_up else 0.5)
                for gs in goal_scores
            )
            overall_engagement = total_weighted / goals_total

        return ScoringResult(
            goal_scores=goal_scores,
            overall_engagement=min(100.0, overall_engagement),
            goals_addressed=goals_addressed,
            goals_total=goals_total
        )

    def _get_keywords_for_category(self, category: str) -> list[str]:
        """Get keywords for a category, with fallback to category name itself."""
        category_lower = category.lower()
        if category_lower in self.CATEGORY_KEYWORDS:
            return self.CATEGORY_KEYWORDS[category_lower]
        # Fallback: use the category name itself as a keyword
        return [category_lower]

    def _category_in_description(self, content: str, description: str) -> bool:
        """Check if goal description keywords appear in content."""
        # Extract significant words from description (>3 chars)
        desc_words = [w.lower() for w in description.split() if len(w) > 3]
        return any(word in content for word in desc_words)

    def _extract_evidence(self, content: str, keywords: list[str]) -> list[str]:
        """Extract sentences containing keywords as evidence."""
        if not keywords:
            return []

        sentences = re.split(r'[.!?]+', content)
        evidence = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in keywords):
                evidence.append(sentence)

        return evidence

    def _assess_effort(self, content: str, keyword_matches: list[str]) -> str:
        """Assess effort level based on language and quantifiers."""
        if not keyword_matches:
            return "none"

        # Check for positive effort indicators
        positive_count = sum(1 for word in self.EFFORT_POSITIVE if word in content)
        negative_count = sum(1 for word in self.EFFORT_NEGATIVE if word in content)

        # Check for quantifiers (numbers usually indicate more effort)
        has_numbers = bool(self._number_pattern.search(content))

        # Activity verb count
        activity_count = len(self._activity_pattern.findall(content))

        # Scoring logic
        effort_score = (
            positive_count * 2
            - negative_count
            + (2 if has_numbers else 0)
            + min(activity_count, 3)
        )

        if effort_score >= 6:
            return "exceptional"
        elif effort_score >= 4:
            return "substantial"
        elif effort_score >= 2:
            return "moderate"
        elif effort_score >= 1:
            return "minimal"
        else:
            return "none"

    def _calculate_base_score(
        self,
        showed_up: bool,
        keyword_count: int,
        effort_level: str,
        has_quantifiers: bool,
        evidence_count: int
    ) -> float:
        """Calculate deterministic base score (0-100)."""
        if not showed_up:
            return 0.0

        # Base: 30 points for showing up
        score = 30.0

        # Keyword relevance: up to 20 points
        score += min(keyword_count * 5, 20)

        # Effort level: up to 30 points
        effort_points = {
            "none": 0,
            "minimal": 5,
            "moderate": 15,
            "substantial": 25,
            "exceptional": 30
        }
        score += effort_points.get(effort_level, 0)

        # Quantifiers present: 10 points (indicates specificity)
        if has_quantifiers:
            score += 10

        # Evidence richness: up to 10 points
        score += min(evidence_count * 3, 10)

        return min(100.0, score)

    def _generate_reasoning(
        self,
        category: str,
        showed_up: bool,
        keyword_matches: list[str],
        effort_level: str,
        base_score: float
    ) -> str:
        """Generate human-readable reasoning for the score."""
        if not showed_up:
            return f"No evidence of engagement with {category} found in today's entry."

        parts = [f"Engaged with {category}"]

        if keyword_matches:
            parts.append(f"(keywords: {', '.join(keyword_matches[:3])})")

        parts.append(f"with {effort_level} effort")
        parts.append(f"-> base score {base_score:.0f}/100")

        return " ".join(parts)
