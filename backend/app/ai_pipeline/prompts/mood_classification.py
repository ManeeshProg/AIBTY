"""Mood classification prompt for safety-first verdict generation."""

MOOD_CLASSIFICATION_PROMPT = """
You are analyzing a journal entry to classify the writer's emotional state.
This classification determines what type of feedback is appropriate.

CLASSIFICATION RULES:
- STRUGGLING: User shows signs of difficulty, low energy, disappointment, or frustration
  Examples: missed goals, expressing tiredness, mentioning setbacks, low motivation

- STABLE: User is neutral to positive, going through normal routines
  Examples: routine activities, moderate effort, neither great nor bad day

- THRIVING: User shows energy, accomplishment, momentum, enthusiasm
  Examples: achieved goals, excited about progress, multiple wins mentioned

CRISIS INDICATORS (set crisis_flag=true if ANY present):
- Mentions of self-harm or suicidal thoughts
- Expressions of hopelessness ("nothing matters", "what's the point")
- Extreme isolation language ("no one cares", "completely alone")
- References to harming self or others

When in doubt between levels, choose the MORE SUPPORTIVE option (struggling over stable).
It is safer to be too supportive than to deliver criticism to someone struggling.

Journal entry to analyze:
{journal_content}

Today's score context (if available):
{score_context}
"""

PROMPT_VERSION = "1.0.0"
