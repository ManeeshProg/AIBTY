---
phase: 03-signal-extraction
plan: 02
subsystem: ai-pipeline
tags: [goal-mapping, goal-suggestions, sqlalchemy, aggregation]

requires:
  - phase: 03-01
    provides: "ExtractionAgent and ExtractionService for activity extraction"
  - phase: 02-03
    provides: "Scoring foundation with database patterns"
provides:
  - GoalActivityLink model for extraction-to-goal mapping
  - map_metrics_to_goals() method in ExtractionService
  - suggest_goals() method for pattern-based goal suggestions
  - GoalSuggestion schema for surfacing new goal ideas
affects:
  - phase-04  # Historical trends may use goal mappings for context
  - phase-05  # Verdict generation may reference goal links
  - future-api  # GoalSuggestion endpoints will use this service

tech-stack:
  added: []
  patterns:
    - goal-mapping-via-category-and-keywords
    - pattern-based-goal-suggestions
    - sqlalchemy-aggregation-queries

key-files:
  created:
    - backend/alembic/versions/e16f5bf6a8aa_add_goal_activity_links_table.py
  modified:
    - backend/app/models/goal.py
    - backend/app/services/extraction_service.py
    - backend/app/ai_pipeline/schemas/extraction.py
    - backend/app/schemas/goal.py

key-decisions:
  - "Category exact match scores 1.0, keyword fuzzy match scores 0.7"
  - "Fuzzy matching uses significant words (>3 chars) from metric key"
  - "Goal suggestions require frequency >= 3 in lookback period"
  - "Category-specific description templates for goal suggestions"

patterns-established:
  - "Bidirectional relationships via backref for easy navigation"
  - "Match reason string explains why metric links to goal"
  - "Contribution score enables weighted goal progress tracking"

duration: 4min
completed: 2026-01-21
---

# Phase 03 Plan 02: Goal Mapping & Suggestions Summary

**Goal mapping links extracted activities to user goals, and surfaces pattern-based goal suggestions for unmatched recurring activities**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-20T19:19:14Z
- **Completed:** 2026-01-20T19:23:31Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- GoalActivityLink model connects ExtractedMetric to UserGoal with match reasoning
- map_metrics_to_goals() creates links using category and keyword matching
- suggest_goals() analyzes 30-day patterns to surface new goal ideas
- Goal suggestions filter out categories already covered by active goals

## Task Commits

Each task was committed atomically:

1. **Task 1: Create GoalActivityLink model and migration** - `14defcb` (feat)
2. **Task 2: Add goal mapping to ExtractionService** - `f39ad7c` (feat)
3. **Task 3: Add goal suggestion logic** - `c2785fa` (feat)

## Files Created/Modified

- `backend/app/models/goal.py` - Added GoalActivityLink model with bidirectional relationships
- `backend/alembic/versions/e16f5bf6a8aa_add_goal_activity_links_table.py` - Migration for goal_activity_links table
- `backend/app/services/extraction_service.py` - Added map_metrics_to_goals() and suggest_goals() methods
- `backend/app/ai_pipeline/schemas/extraction.py` - Added GoalSuggestion schema for pattern-based suggestions
- `backend/app/schemas/goal.py` - Added GoalSuggestionRead API response schema

## Technical Implementation

### GoalActivityLink Model

Created linking table with:
- `goal_id` and `metric_id` foreign keys (both indexed)
- `match_reason`: Explains why metric matches goal (e.g., "Category match: fitness")
- `contribution_score`: Weighted contribution (1.0 for exact category, 0.7 for fuzzy)
- Bidirectional relationships via backref for easy navigation

### Goal Mapping Logic

The `map_metrics_to_goals()` method implements two-tier matching:

**Primary match (score 1.0):** Category exact match
- `metric.category.lower() == goal.category.lower()`
- Example: fitness metric → fitness goal

**Secondary match (score 0.7):** Keyword fuzzy match
- Extracts significant words (>3 chars) from metric key
- Checks if any appear in goal description
- Example: "workout_duration" → goal containing "workout"

### Goal Suggestion Logic

The `suggest_goals()` method finds recurring patterns:

1. Queries ExtractedMetric for last 30 days (configurable)
2. Groups by (category, key) and counts frequency
3. Filters patterns with frequency >= 3
4. Excludes categories already covered by active goals
5. Generates human-readable descriptions via category templates
6. Scales confidence by frequency and avg metric confidence

**Category-specific templates:**
- productivity: "Track and improve {activity}"
- fitness: "Maintain consistent {activity}"
- learning: "Dedicate time to {activity}"
- discipline: "Build habit around {activity}"
- well-being: "Monitor and optimize {activity}"
- creativity: "Engage regularly in {activity}"
- social: "Prioritize {activity}"

## Decisions Made

**1. Two-tier matching strategy**
- Rationale: Category match is precise (1.0 score), keyword match catches variations (0.7 score)
- Impact: Enables weighted goal progress tracking via contribution_score

**2. Fuzzy matching via significant words**
- Rationale: Simple splitting by underscore and length filter (>3 chars) catches meaningful keywords
- Impact: Avoids false positives from common words like "the", "and", "of"

**3. Frequency threshold of 3 for suggestions**
- Rationale: Balances between catching patterns and avoiding noise from one-off mentions
- Impact: Suggestions reflect genuine recurring activities, not random occurrences

**4. Category-specific description templates**
- Rationale: Different goal types need different framing (track vs maintain vs build)
- Impact: More relevant and actionable goal suggestions

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all implementations completed without errors.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

### Ready to Proceed
- Goal mapping infrastructure complete
- Pattern analysis working with SQL aggregation
- All schemas and services verified

### No Blockers
- Migration applied successfully
- All imports working
- Database relationships functional

### Context for Phase 04
- GoalActivityLink records available for historical context
- Goal suggestions can inform trend analysis
- Contribution scores enable weighted progress tracking

---
*Phase: 03-signal-extraction*
*Completed: 2026-01-21*
