# Requirements: Am I Better Than Yesterday?

**Defined:** 2026-01-19
**Core Value:** Consistency and momentum toward personal goals — the AI must accurately determine if today's effort maintained or exceeded yesterday's.

## v1 Requirements

Requirements for AI evaluation pipeline. Each maps to roadmap phases.

### Voice Input

- [ ] **VOICE-01**: User can record voice entry that gets transcribed to text
- [ ] **VOICE-02**: Transcription handles multiple entries per day (accumulates)

### Signal Extraction

- [ ] **EXTR-01**: System maps activities in entries to user's stated goals
- [ ] **EXTR-02**: System auto-suggests new goals from entry patterns

### Scoring

- [ ] **SCORE-01**: System scores each goal dimension daily (did you show up, how much effort)
- [ ] **SCORE-02**: System compares today's performance with yesterday
- [ ] **SCORE-03**: System tracks consecutive improvement streaks
- [ ] **SCORE-04**: Scoring uses deterministic rules + LLM reasoning hybrid

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
| Mobile app UI | Deferred to next milestone — backend first |
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
| VOICE-01 | TBD | Pending |
| VOICE-02 | TBD | Pending |
| EXTR-01 | TBD | Pending |
| EXTR-02 | TBD | Pending |
| SCORE-01 | TBD | Pending |
| SCORE-02 | TBD | Pending |
| SCORE-03 | TBD | Pending |
| SCORE-04 | TBD | Pending |
| HIST-01 | TBD | Pending |
| VERD-01 | TBD | Pending |
| VERD-02 | TBD | Pending |
| VERD-03 | TBD | Pending |
| ORCH-01 | TBD | Pending |
| ORCH-02 | TBD | Pending |
| NOTIF-01 | TBD | Pending |
| NOTIF-02 | TBD | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 0
- Unmapped: 16

---
*Requirements defined: 2026-01-19*
*Last updated: 2026-01-19 after initial definition*
