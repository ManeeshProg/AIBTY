---
phase: 03
plan: 01
subsystem: ai-pipeline
tags: [extraction, instructor, claude, pydantic, persistence]
requires:
  - phase-02-plan-03  # Scoring foundation with LLM patterns
provides:
  - extraction-schemas  # ExtractedActivity and ExtractionResult
  - extraction-agent  # Claude-based agent with instructor
  - extraction-service  # Persistence to ExtractedMetric table
affects:
  - phase-04  # Historical trends will query ExtractedMetric
  - phase-05  # Verdict generation will use extracted signals
tech-stack:
  added:
    - instructor: ^1.14.0
  upgraded:
    - anthropic: ^0.15.0 → ^0.45.0
  patterns:
    - instructor-patched-client  # Structured LLM outputs with retries
    - pydantic-schemas-for-ai  # Type-safe AI responses
key-files:
  created:
    - backend/app/ai_pipeline/schemas/extraction.py
    - backend/app/ai_pipeline/agents/extraction_agent.py
    - backend/app/services/extraction_service.py
  modified:
    - backend/app/core/config.py  # Added extra="ignore" for env vars
    - backend/pyproject.toml  # Added instructor, upgraded anthropic
decisions:
  - decision: Use instructor library for structured outputs
    rationale: Automatic Pydantic parsing and retry logic eliminates manual JSON parsing
    impact: Cleaner code, better error handling, type safety
    date: 2026-01-21
  - decision: Claude Sonnet 4 for extraction
    rationale: Model excels at text analysis and nuance detection per research
    impact: More accurate activity extraction with context awareness
    date: 2026-01-21
  - decision: Temperature 0.2 for extraction
    rationale: Lower temperature for more consistent structured extraction
    impact: More deterministic results across similar inputs
    date: 2026-01-21
  - decision: Seven standard categories for activities
    rationale: Aligns with common personal goal types (productivity, fitness, learning, discipline, well-being, creativity, social)
    impact: Consistent categorization, easier goal mapping
    date: 2026-01-21
metrics:
  tasks: 3
  commits: 2
  files_created: 8
  dependencies_added: 1
  dependencies_upgraded: 1
  duration: ~15min
  completed: 2026-01-21
---

# Phase 03 Plan 01: Signal Extraction Pipeline Summary

**One-liner:** Claude-based extraction agent using instructor for structured activity extraction from journal entries with automatic Pydantic parsing and retry logic.

## What Was Built

Created the core signal extraction pipeline that analyzes journal entries and extracts structured, quantifiable activities using Claude Sonnet 4 and the instructor library.

### Components Created

1. **Extraction Schemas** (`backend/app/ai_pipeline/schemas/extraction.py`)
   - `ExtractedActivity`: Pydantic model for individual extracted activities
     - Fields: category, key, value, evidence, confidence
     - Confidence validation: 0.0-1.0 range
   - `ExtractionResult`: Container for extraction results
     - Fields: activities list, raw_text for debugging

2. **Extraction Agent** (`backend/app/ai_pipeline/agents/extraction_agent.py`)
   - Uses instructor-patched Anthropic client for structured outputs
   - Claude Sonnet 4 (claude-sonnet-4-20250514) model
   - Temperature 0.2 for consistent extraction
   - Comprehensive system prompt with extraction guidelines:
     - Extract ALL quantifiable activities
     - Convert time to minutes
     - Estimate implicit values with lower confidence
     - Provide evidence snippets
     - Categorize into 7 standard categories

3. **Extraction Service** (`backend/app/services/extraction_service.py`)
   - Follows existing async service pattern
   - `extract_and_persist()`: Extracts and saves to ExtractedMetric table
   - `get_metrics_for_entry()`: Retrieves metrics for a journal entry
   - `clear_metrics_for_entry()`: Enables re-extraction after updates

## Technical Decisions

### Instructor Library Integration

**Decision:** Use instructor library for structured LLM outputs instead of manual JSON parsing

**Why:**
- Automatic Pydantic model parsing from LLM responses
- Built-in retry logic on validation failures
- Type safety and IDE support
- Cleaner code without try/except JSON parsing

**Impact:**
- More robust extraction with automatic error handling
- Type-safe responses guaranteed to match Pydantic schema
- Better developer experience with autocomplete

### Seven Standard Categories

**Categories chosen:**
1. productivity (work, tasks, focus time)
2. fitness (exercise, workouts, steps)
3. learning (study, courses, books)
4. discipline (meditation, journaling, habits)
5. well-being (sleep, mood, stress management)
6. creativity (writing, art, music)
7. social (conversations, networking, relationships)

**Why:**
- Aligns with common personal development goal types
- Comprehensive coverage of life domains
- Consistent with research on goal categories

**Impact:**
- Easier goal mapping in future phases
- Consistent activity categorization
- User-friendly category names

### Extraction Confidence Scoring

**Decision:** Use 1.0 for explicit numbers, 0.7-0.9 for inferred values

**Why:**
- Explicit mentions ("45 minutes") are certain → 1.0
- Implied activities ("quick workout") require estimation → 0.7-0.9
- Enables filtering by confidence threshold in future phases

**Impact:**
- Transparent about extraction certainty
- Allows downstream systems to weight activities by confidence
- Better user trust through evidence tracking

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Config.py extra fields handling**

- **Found during:** Task 1 verification
- **Issue:** Settings class rejected extra .env fields (DB_HOST, DB_PORT, etc.) causing ValidationError
- **Fix:** Added `extra = "ignore"` to Settings.Config class
- **Files modified:** `backend/app/core/config.py`
- **Commit:** 6549298
- **Rationale:** Critical for config to load - blocks all imports. Standard Pydantic pattern for settings classes.

**2. [Rule 3 - Blocking] Installed missing dependencies**

- **Found during:** Task verification
- **Issue:** Missing python-jose, passlib, pydantic-settings modules blocked imports
- **Fix:** Installed via pip (python-jose[cryptography], passlib[bcrypt], pydantic-settings)
- **Files modified:** None (runtime environment only)
- **Rationale:** Required dependencies from pyproject.toml not installed, blocking task verification

**3. [Rule 1 - Bug] Task 3 already completed in Task 1**

- **Found during:** Task 3 execution
- **Issue:** Task 3 requested adding instructor dependency, but it was already added in Task 1
- **Action:** Verified instructor installed (1.14.4) and marked task complete
- **Rationale:** Natural consolidation - dependencies needed for Task 1 implementation

## Integration Points

### Upstream Dependencies
- **Phase 02-03:** Established instructor pattern with LLMScoreEnhancer
- **ExtractedMetric model:** Already exists in `backend/app/models/journal_entry.py`
- **ANTHROPIC_API_KEY:** Already in config.py from Phase 2

### Downstream Usage
- **Phase 04 (Historical Trends):** Will query ExtractedMetric for trend analysis
- **Phase 05 (Verdict Generation):** Will use extracted signals for verdict reasoning
- **Goal Mapping:** Future phase will map ExtractedMetric.category to UserGoal

## Next Phase Readiness

### Ready to Proceed
- Extraction pipeline complete and verified
- Service follows existing patterns for easy integration
- All dependencies installed and compatible

### No Blockers
- All success criteria met
- No authentication gates encountered
- No architectural decisions needed

### Context for Phase 04
- ExtractedMetric records now available for historical analysis
- Confidence scores enable quality filtering
- Evidence field enables explainability

## Verification Results

### All Success Criteria Met
1. ✅ ExtractionAgent exists and uses instructor + Claude for structured extraction
2. ✅ ExtractionService can be instantiated with an async session
3. ✅ Pydantic schemas define ExtractedActivity and ExtractionResult
4. ✅ instructor dependency installed (1.14.4)
5. ✅ All imports work without errors

### Test Output
```bash
# Import verification
All imports successful

# Schema validation
Created: {
  'activities': [{
    'category': 'fitness',
    'key': 'workout_duration',
    'value': 45.0,
    'evidence': 'worked out for 45 minutes',
    'confidence': 1.0
  }],
  'raw_text': 'test'
}
```

## Commits

| Commit | Message | Files |
|--------|---------|-------|
| 6549298 | feat(03-01): create extraction schemas and agent | extraction.py, extraction_agent.py, config.py, pyproject.toml, 4x __init__.py |
| 80eceff | feat(03-01): create ExtractionService with persistence | extraction_service.py |

## Learnings & Notes

### What Went Well
- Instructor integration was seamless
- Existing patterns made service creation straightforward
- Config fix was simple and standard practice

### What to Watch
- OpenAI version conflict warning (label-studio incompatibility) - doesn't affect our use case but worth noting
- Poetry not available, using pip directly - works but less ideal for lock file management

### Patterns Established
- **AI Pipeline structure:** `app/ai_pipeline/agents/` and `app/ai_pipeline/schemas/`
- **Instructor pattern:** Patch client once, use response_model parameter
- **Extraction prompt structure:** Comprehensive guidelines with examples and categories

### Future Improvements
- Consider caching extraction results to avoid re-processing identical text
- Add extraction quality metrics (extraction count, confidence distribution)
- Consider batch extraction for performance optimization
