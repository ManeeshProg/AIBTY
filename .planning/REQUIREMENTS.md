# Requirements: Am I Better Than Yesterday?

**Defined:** 2026-01-19
**Core Value:** Consistency and momentum toward personal goals - the AI must accurately determine if today's effort maintained or exceeded yesterday's.

## v1 Requirements

Requirements for AI evaluation pipeline. Each maps to roadmap phases.

### Voice Input

- [x] **VOICE-01**: User can record voice entry that gets transcribed to text
- [x] **VOICE-02**: Transcription handles multiple entries per day (accumulates)

### Signal Extraction

- [ ] **EXTR-01**: System maps activities in entries to user's stated goals
- [ ] **EXTR-02**: System auto-suggests new goals from entry patterns

### Scoring

- [x] **SCORE-01**: System scores each goal dimension daily (did you show up, how much effort)
- [x] **SCORE-02**: System compares today's performance with yesterday
- [x] **SCORE-03**: System tracks consecutive improvement streaks
- [x] **SCORE-04**: Scoring uses deterministic rules + LLM reasoning hybrid

### Historical Context

- [ ] **HIST-01**: System shows week-over-week trends per goal

### Verdict

- [ ] **VERD-01**: System delivers better/same/worse verdict daily
- [ ] **VERD-02**: Verdict includes emotional messaging (encouraging when better, ego-poking when worse)
- [ ] **VERD-03**: Verdict includes actionable guidance for tomorrow

### Orchestration

- [ ] **ORCH-01**: Evening analysis runs automatically at scheduled time
- [ ] **ORCH-02**: Analysis aggregates all entries from the day

### Notifications

- [ ] **NOTIF-01**: System detects users who haven't logged today
- [ ] **NOTIF-02**: System generates ego-poking reminder messages

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Historical Context

- **HIST-02**: Full RAG semantic search across all history ("best coding week since October")
- **HIST-03**: Personal baseline calibration (what's normal for this user)

### Verdict

- **VERD-04**: Score breakdown visualization per goal
- **VERD-05**: Trend graph visualization over days/weeks

### Notifications

- **NOTIF-03**: Fatigue-aware notification frequency (reduce if user ignores)

### Signal Extraction

- **EXTR-03**: Intensity/difficulty detection ("3 hard problems" vs "1 easy problem")

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mobile app UI | Deferred to next milestone - backend first |
| On-device RAG | Requires mobile-specific architecture, defer to mobile milestone |
| Real-time chat/coaching | Single daily verdict is the core UX |
| Social features | Personal growth is private |
| Gamification/badges | Conflicts with "honest assessment" philosophy |
| OAuth/social login | Email/password sufficient for v1 |
| Audio file storage | Transcribe immediately, don't persist audio |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| VOICE-01 | Phase 1 | Complete |
| VOICE-02 | Phase 1 | Complete |
| EXTR-01 | Phase 3 | Pending |
| EXTR-02 | Phase 3 | Pending |
| SCORE-01 | Phase 2 | Complete |
| SCORE-02 | Phase 2 | Complete |
| SCORE-03 | Phase 2 | Complete |
| SCORE-04 | Phase 2 | Complete |
| HIST-01 | Phase 4 | Pending |
| VERD-01 | Phase 5 | Pending |
| VERD-02 | Phase 5 | Pending |
| VERD-03 | Phase 5 | Pending |
| ORCH-01 | Phase 6 | Pending |
| ORCH-02 | Phase 6 | Pending |
| NOTIF-01 | Phase 7 | Pending |
| NOTIF-02 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-01-19*
*Last updated: 2026-01-21 after Phase 2 completion*
