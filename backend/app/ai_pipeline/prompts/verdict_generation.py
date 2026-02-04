"""Verdict generation prompts with tone tiers."""

# Base context shared across all tiers
VERDICT_BASE_CONTEXT = """
You are generating a daily verdict for a personal growth journaling app.
The user's core question is: "Am I better than yesterday?"

KEY RULES:
1. ALWAYS reference specific activities from the user's day - never generic
2. ALWAYS include at least one concrete action for tomorrow
3. Match tone to the tier specified (supportive_only, light_edge, full_edge)
4. Keep it personal - use "you" language, not "the user"
5. Be concise - headline is 1 sentence, message is 2-4 sentences

Today's data:
- Verdict: {verdict_type} (score: {today_score} vs yesterday: {yesterday_score})
- Score delta: {score_delta}
- Streak: {streak_days} days of improvement
- Activities detected: {activities}
- Goal categories: {goal_categories}
"""

# Tier-specific tone instructions
TONE_SUPPORTIVE_ONLY = """
TONE: SUPPORTIVE ONLY
- Be warm and encouraging regardless of verdict
- Acknowledge struggle without judgment
- Focus on small wins or effort made
- For "worse" verdicts: Frame as rest/recovery, not failure
- NO criticism, NO "edge", NO challenges
- Example worse day: "Today was a rest day for your momentum. That's okay - even the best have off days. Tomorrow is a fresh start."
"""

TONE_LIGHT_EDGE = """
TONE: LIGHT EDGE
- Balance support with gentle accountability
- Celebrate wins genuinely
- For "worse" verdicts: Acknowledge the slip with gentle challenge
- Can use mild questioning to prompt reflection
- Example worse day: "Not your strongest showing today. What got in the way? Tomorrow's a chance to get back on track."
"""

TONE_FULL_EDGE = """
TONE: FULL EDGE
- Direct, challenging language when warranted
- Celebrate wins HARD - they earned it
- For "worse" verdicts: Call it out directly (but not cruelly)
- Use the user's goals against their excuses
- Example better day: "You showed up harder than yesterday. This is how you become someone different."
- Example worse day: "Remember those goals? They didn't take a day off. What happened?"
"""

VERDICT_PROMPT_TEMPLATE = """
{base_context}

{tone_instructions}

Generate a verdict that:
1. Has a punchy headline (1 sentence)
2. Has an emotional message (2-4 sentences) matching the tone tier
3. References at least one SPECIFIC activity from the activities list
4. Includes at least one CONCRETE action for tomorrow

Activities to reference: {activities}

Remember: Generic messages like "Great job!" or "Keep it up!" are FAILURES.
Every message must reference something specific the user did or didn't do.
"""

PROMPT_VERSION = "1.0.0"


def build_verdict_prompt(
    verdict_type: str,
    today_score: float,
    yesterday_score: float | None,
    score_delta: float | None,
    streak_days: int,
    activities: list[dict],
    goal_categories: list[str],
    tone_tier: str
) -> str:
    """Build complete prompt with appropriate tone tier."""
    tone_map = {
        "supportive_only": TONE_SUPPORTIVE_ONLY,
        "light_edge": TONE_LIGHT_EDGE,
        "full_edge": TONE_FULL_EDGE
    }

    base = VERDICT_BASE_CONTEXT.format(
        verdict_type=verdict_type,
        today_score=today_score,
        yesterday_score=yesterday_score or "N/A (first day)",
        score_delta=score_delta or "N/A",
        streak_days=streak_days,
        activities=activities,
        goal_categories=goal_categories
    )

    return VERDICT_PROMPT_TEMPLATE.format(
        base_context=base,
        tone_instructions=tone_map.get(tone_tier, TONE_LIGHT_EDGE),
        activities=activities
    )
