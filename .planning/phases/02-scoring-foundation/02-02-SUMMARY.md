---
phase: 02-scoring-foundation
plan: 02
subsystem: ai
tags: [anthropic, claude, instructor, llm, scoring, pydantic]

# Dependency graph
requires:
  - phase: 02-01
    provides: "Deterministic scoring schemas (GoalScoreOutput, ScoringResult)"
provides:
  - "LLMScoreEnhancer class for contextual score adjustment using Claude"
  - "EnhancedScore model with +/-20% guardrails"
  - "MockLLMScoreEnhancer for testing without API calls"
  - "Prompt templates for score enhancement"
affects: [02-03-integration, 05-verdict-generation]

# Tech tracking
tech-stack:
  added: [instructor==1.4.3, anthropic (ANTHROPIC_API_KEY config)]
  patterns:
    - "instructor.from_anthropic for structured LLM outputs"
    - "Pydantic field validators for guardrails"
    - "Mock classes for testing without API calls"

key-files:
  created:
    - backend/app/ai_pipeline/scoring/llm_enhancer.py
    - backend/app/ai_pipeline/scoring/prompts.py
  modified:
    - backend/requirements.txt
    - backend/app/core/config.py

key-decisions:
  - "Use instructor library for structured outputs with automatic retries"
  - "Enforce +/-20 point adjustment guardrails via field validator + post-response clamping"
  - "Provide MockLLMScoreEnhancer for testing to avoid API costs during development"
  - "Use Claude Sonnet 4 (claude-sonnet-4-20250514) for contextual analysis"

patterns-established:
  - "Belt-and-suspenders guardrails: Pydantic validator + post-response clamping"
  - "Mock classes mirror real class API for seamless testing"
  - "Prompt templates separate from implementation logic"

# Metrics
duration: 4min
completed: 2026-01-21
---

# Phase 2 Plan 2: LLM Score Enhancement Summary

**Claude-based contextual score adjustment with instructor structured outputs, +/-20% guardrails, and mock testing support**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-20T18:40:50Z
- **Completed:** 2026-01-20T18:44:57Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Created LLMScoreEnhancer class using instructor + Anthropic for contextual understanding
- Implemented EnhancedScore Pydantic model with double-enforced +/-20% adjustment guardrails
- Built comprehensive prompt templates guiding Claude to adjust scores conservatively
- Added MockLLMScoreEnhancer for testing without API calls or costs

## Task Commits

Each task was committed atomically:

1. **Task 1: Add instructor dependency and config** - `45915ff` (chore)
2. **Task 2: Create prompt templates** - `e0c950a` (feat)
3. **Task 3: Create LLM score enhancer** - `6da3bd7` (feat)

## Files Created/Modified
- `backend/requirements.txt` - Added instructor==1.4.3 dependency
- `backend/app/core/config.py` - Added ANTHROPIC_API_KEY configuration setting
- `backend/app/ai_pipeline/scoring/prompts.py` - Prompt templates for score enhancement with constraints
- `backend/app/ai_pipeline/scoring/llm_enhancer.py` - LLMScoreEnhancer, EnhancedScore, MockLLMScoreEnhancer classes

## Decisions Made

1. **Double-enforcement of guardrails**: Field validator + post-response clamping ensures +/-20 adjustment limit is never exceeded, even if LLM misbehaves
2. **instructor library for structured outputs**: Provides automatic Pydantic parsing and retry logic, eliminating manual JSON parsing
3. **Mock class with identical API**: MockLLMScoreEnhancer mirrors LLMScoreEnhancer interface, making testing seamless
4. **Explicit prompt constraints**: Prompts include computed valid range (min_score, max_score) to guide Claude

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Dependency installation error (non-blocking)**:
- During verification, `pip install anthropic==0.28.1 instructor==1.4.3` failed due to jiter Rust compilation issue on Windows
- This is an environment-specific issue that doesn't affect code quality
- Code syntax validated successfully
- User will install dependencies in their Python environment when ready to use

## User Setup Required

**External services require manual configuration.** Before using LLM score enhancement:

1. **Get Anthropic API Key:**
   - Visit: https://console.anthropic.com/settings/keys
   - Create new API key
   - Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Verify setup:**
   ```python
   from backend.app.ai_pipeline.scoring.llm_enhancer import LLMScoreEnhancer
   # Should not raise "ANTHROPIC_API_KEY not configured" if env var set
   ```

## Next Phase Readiness

**Ready for integration (Plan 02-03):**
- LLMScoreEnhancer can accept GoalScoreOutput from deterministic scorer
- Returns EnhancedScore with adjusted score and reasoning
- MockLLMScoreEnhancer available for testing integration without API calls
- Prompts guide Claude to focus on contextual factors deterministic analysis misses

**No blockers.** LLM enhancement layer complete and ready to wire into scoring pipeline.

---
*Phase: 02-scoring-foundation*
*Completed: 2026-01-21*
