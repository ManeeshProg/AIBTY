# Roadmap: Am I Better Than Yesterday?

**Created:** 2026-01-19
**Core Value:** Consistency and momentum toward personal goals - determining if today maintained or exceeded yesterday.
**Depth:** Standard

## Overview

This roadmap delivers the AI evaluation pipeline for daily journaling analysis. The structure follows research guidance: build deterministic scoring foundation first, then layer on extraction, historical context, and verdict generation. Voice input is placed early as an independent capability. Notifications are last since they depend on the complete evaluation system.

## Phases

### Phase 1: Voice Transcription

**Goal:** Users can submit voice entries that become text journal entries.

**Dependencies:** None (existing journal CRUD provides the foundation)

**Requirements:**
- VOICE-01: User can record voice entry that gets transcribed to text
- VOICE-02: Transcription handles multiple entries per day (accumulates)

**Success Criteria:**
1. User can upload audio file and receive transcribed text within 30 seconds
2. Multiple voice entries in one day accumulate into the journal (not replace)
3. Transcription accuracy is sufficient for downstream analysis (95%+ for clear speech)

**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md — Voice transcription endpoint with OpenAI Whisper API

---

### Phase 2: Scoring Foundation

**Goal:** System can score daily performance against goals using deterministic rules with LLM enhancement.

**Dependencies:** Phase 1 not required (works with text entries)

**Requirements:**
- SCORE-01: System scores each goal dimension daily (did you show up, how much effort)
- SCORE-02: System compares today's performance with yesterday
- SCORE-03: System tracks consecutive improvement streaks
- SCORE-04: Scoring uses deterministic rules + LLM reasoning hybrid

**Success Criteria:**
1. Each user goal receives a daily score (0-100) with explainable breakdown
2. System determines if today was better/same/worse than yesterday for each goal
3. Consecutive improvement days are tracked and visible per goal
4. Deterministic rules provide base score; LLM adjusts within guardrails (+/-20%)
5. Scoring is consistent (same input produces same output within 5% variance)

**Plans:** 3 plans

Plans:
- [ ] 02-01-PLAN.md — Deterministic scoring engine with keyword/effort analysis
- [ ] 02-02-PLAN.md — LLM score enhancement with Claude + instructor
- [ ] 02-03-PLAN.md — ScoringService orchestration, API endpoints, streak tracking

---

### Phase 3: Signal Extraction

**Goal:** System extracts structured signals from journal entries and maps them to goals.

**Dependencies:** Phase 2 (extraction feeds scoring)

**Requirements:**
- EXTR-01: System maps activities in entries to user's stated goals
- EXTR-02: System auto-suggests new goals from entry patterns

**Success Criteria:**
1. Activities mentioned in entries are automatically linked to relevant goals
2. User sees which entry content contributed to which goal's score
3. System surfaces patterns that suggest adding new goals ("You mention 'meditation' frequently - add as goal?")

**Plans:** 2 plans

Plans:
- [ ] 03-01-PLAN.md — ExtractionService with Claude + instructor for structured activity extraction
- [ ] 03-02-PLAN.md — Goal mapping (EXTR-01) and goal suggestions (EXTR-02)

---

### Phase 4: Historical Trends

**Goal:** Users can see week-over-week progress trends per goal.

**Dependencies:** Phase 2 (requires accumulated scores)

**Requirements:**
- HIST-01: System shows week-over-week trends per goal

**Success Criteria:**
1. User can view 7-day score trend for each goal
2. Week-over-week comparison shows improvement or decline percentage
3. Trend data is structured for mobile visualization consumption

**Plans:** 1 plan

Plans:
- [ ] 04-01-PLAN.md — TrendService, schemas, and API endpoint for goal trends

---

### Phase 5: Verdict Generation

**Goal:** System delivers daily verdicts with emotional messaging and actionable guidance.

**Dependencies:** Phase 2 (scoring), Phase 3 (extraction for specificity)

**Requirements:**
- VERD-01: System delivers better/same/worse verdict daily
- VERD-02: Verdict includes emotional messaging (encouraging when better, ego-poking when worse)
- VERD-03: Verdict includes actionable guidance for tomorrow

**Success Criteria:**
1. User receives single daily verdict: "better", "same", or "worse" than yesterday
2. Verdict messaging matches user's performance (celebrating wins, poking ego on slips)
3. Verdict references specific activities from today's entries (not generic)
4. Each verdict includes at least one concrete action for tomorrow
5. Mood classification prevents inappropriate criticism during detected low states

---

### Phase 6: Evening Orchestration

**Goal:** Analysis runs automatically at user's scheduled evening time.

**Dependencies:** Phase 2 (scoring), Phase 5 (verdict generation)

**Requirements:**
- ORCH-01: Evening analysis runs automatically at scheduled time
- ORCH-02: Analysis aggregates all entries from the day

**Success Criteria:**
1. User can configure their preferred analysis time (e.g., 9pm local)
2. System automatically triggers analysis at scheduled time without user action
3. All entries from the day are aggregated into single analysis
4. Failed analyses retry with exponential backoff

**Plans:** 3 plans

Plans:
- [ ] 06-01-PLAN.md — User analysis_time preference field and API endpoint
- [ ] 06-02-PLAN.md — Celery app configuration with Redis broker and beat scheduler
- [ ] 06-03-PLAN.md — Orchestrator task with entry aggregation and retry logic

---

### Phase 7: Smart Notifications

**Goal:** System detects non-loggers and sends ego-poking reminders.

**Dependencies:** Phase 6 (orchestration), Phase 5 (verdict generation for messaging style)

**Requirements:**
- NOTIF-01: System detects users who haven't logged today
- NOTIF-02: System generates ego-poking reminder messages

**Success Criteria:**
1. System identifies users with no entries by a configurable cutoff time
2. Reminder messages reference user's previous activity ("Yesterday you logged 3 workouts...")
3. Messages use the "supportive but with edge" tone
4. Users can disable notifications without affecting core functionality

**Plans:** 4 plans

Plans:
- [ ] 07-01-PLAN.md — Notification model, user preferences schema, database migration
- [ ] 07-02-PLAN.md — NotificationService with non-logger detection and message generation
- [ ] 07-03-PLAN.md — Notification API endpoints for mobile consumption
- [ ] 07-04-PLAN.md — Celery task for scheduled notification checks

---

## Progress

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Voice Transcription | VOICE-01, VOICE-02 | Complete |
| 2 | Scoring Foundation | SCORE-01, SCORE-02, SCORE-03, SCORE-04 | Planned |
| 3 | Signal Extraction | EXTR-01, EXTR-02 | Planned |
| 4 | Historical Trends | HIST-01 | Planned |
| 5 | Verdict Generation | VERD-01, VERD-02, VERD-03 | Not Started |
| 6 | Evening Orchestration | ORCH-01, ORCH-02 | Planned |
| 7 | Smart Notifications | NOTIF-01, NOTIF-02 | Planned |

## Coverage

**Total v1 Requirements:** 16
**Mapped:** 16
**Coverage:** 100%

| Requirement | Phase |
|-------------|-------|
| VOICE-01 | Phase 1 |
| VOICE-02 | Phase 1 |
| SCORE-01 | Phase 2 |
| SCORE-02 | Phase 2 |
| SCORE-03 | Phase 2 |
| SCORE-04 | Phase 2 |
| EXTR-01 | Phase 3 |
| EXTR-02 | Phase 3 |
| HIST-01 | Phase 4 |
| VERD-01 | Phase 5 |
| VERD-02 | Phase 5 |
| VERD-03 | Phase 5 |
| ORCH-01 | Phase 6 |
| ORCH-02 | Phase 6 |
| NOTIF-01 | Phase 7 |
| NOTIF-02 | Phase 7 |

---

*Roadmap created: 2026-01-19*
