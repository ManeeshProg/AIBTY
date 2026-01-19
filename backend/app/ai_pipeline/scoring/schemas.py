from pydantic import BaseModel, Field
from typing import Literal

class GoalScoreInput(BaseModel):
    """Input for scoring a single goal against journal content."""
    goal_category: str
    goal_description: str
    target_value: float
    journal_content: str

class GoalScoreOutput(BaseModel):
    """Output for a single goal's score."""
    category: str
    base_score: float = Field(ge=0, le=100, description="Deterministic base score 0-100")
    showed_up: bool = Field(description="Did user engage with this goal at all?")
    effort_level: Literal["none", "minimal", "moderate", "substantial", "exceptional"]
    evidence: list[str] = Field(default_factory=list, description="Quotes/phrases from journal supporting score")
    reasoning: str = Field(description="Human-readable explanation of score")

class ScoringResult(BaseModel):
    """Complete scoring result for all goals."""
    goal_scores: list[GoalScoreOutput]
    overall_engagement: float = Field(ge=0, le=100, description="How engaged was user overall")
    goals_addressed: int = Field(description="Number of goals with evidence in journal")
    goals_total: int = Field(description="Total number of active goals")
