# Research Summary: AI Evaluation Pipeline

**Project:** Am I Better Than Yesterday? - AI Evaluation Pipeline
**Synthesized:** 2026-01-19
**Research Files:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md

---

## Executive Summary

Building an AI evaluation pipeline for personal growth journaling requires a **deterministic-first, LLM-enhanced architecture**. The critical insight from research is that pure LLM scoring exhibits ~40% inconsistency due to position and verbosity biases - unacceptable for a product whose core value proposition is answering "Am I better than yesterday?" The recommended approach: Celery-orchestrated sequential pipeline with hybrid scoring (deterministic rules provide 70% of score, Claude enhances the remaining 30% with contextual reasoning).

The existing FastAPI + PostgreSQL + Celery backend is well-positioned for this addition. Keep pgvector for RAG (0.8.0 delivers 9x performance improvement), use `instructor` for structured LLM outputs rather than heavy LangChain abstractions, and add Langfuse for observability. The stack recommendation is conservative - avoid framework churn (PydanticAI over LangGraph for this use case), prioritize operational simplicity, and invest in monitoring infrastructure from day one.

The biggest risks are **LLM scoring drift**, **embedding drift breaking historical comparisons**, and **emotional tone miscalibration**. All three require monitoring infrastructure, not just features. The product's "supportive but with edge" voice is particularly dangerous without mood classification guardrails - delivering criticism to a struggling user is a trust-destroying failure mode. Build mood detection before shipping verdicts with attitude.

---

## Key Findings

### From STACK.md: Technology Recommendations

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| **PydanticAI / Direct API** | Agent orchestration | LangGraph is overkill for linear pipeline; Celery chains provide sufficient orchestration |
| **instructor 1.14+** | Structured LLM outputs | 3M+ monthly downloads, patches existing clients, automatic retries on validation failure |
| **faster-whisper 1.2+** | Voice transcription | 4x faster than OpenAI Whisper, lower memory, no FFmpeg dependency |
| **pgvector 0.8+** | Vector storage | Already in stack; 9x query speedup with iterative scans; no need for Pinecone/Chroma migration |
| **text-embedding-3-small** | Embeddings | Best cost/quality ratio at $0.02/1M tokens |
| **Claude Sonnet 4** | Primary analysis | Excels at text analysis and emotional nuance; 100k+ context window |
| **Langfuse 3.12+** | Observability | Open source, framework-agnostic, 50k free events vs LangSmith's 5k |
| **deepeval 3.8+** | Evaluation metrics | G-Eval for LLM-as-judge with 0.514 Spearman correlation to human judgment |

**Critical version requirements:**
- Python 3.10+ (LangChain 1.x requirement)
- pgvector 0.8.0+ for iterative scan performance
- CUDA 12 + cuDNN 9 for GPU transcription

### From FEATURES.md: Feature Prioritization

**Table Stakes (Must Have):**
- Accurate transcription (95%+ expected)
- Basic mood/sentiment detection
- Streak tracking (with grace days to prevent abandonment)
- Daily/weekly summaries
- Progress visualization
- Goal tracking with progress indicators
- Privacy/encryption (55% cite privacy concerns)

**Core Differentiators (Your Brand):**
1. Daily verdict with emotional messaging - "Am I Better Than Yesterday?" is the value prop
2. Multi-signal extraction (productivity, fitness, learning, discipline, well-being from single entry)
3. Historical comparison via RAG ("30% more productive than last month")
4. Deterministic + LLM hybrid scoring (explainability builds trust)

**Defer to v2+:**
- Voice input (text works for MVP)
- Complex RAG (start with SQL lookups)
- Cognitive bias detection
- Adaptive difficulty mode

**Anti-Features (Deliberately Avoid):**
- Perfection-based streaks (48% abandonment from broken streaks)
- Generic AI responses ("Great job!" without specifics)
- Social features/leaderboards (conflicts with "better than YOUR yesterday")
- Black-box scoring (always explain why)
- AI that only validates (honest assessment required)

### From ARCHITECTURE.md: System Design

**Pattern:** Sequential Pipeline via Celery Chains

```
Entry -> Transcribe -> Extract -> RAG Retrieve -> Score -> Verdict -> Notify
```

**Component Boundaries:**
| Component | Responsibility | External Deps |
|-----------|---------------|---------------|
| Orchestrator | Celery chain coordination, error handling | Celery, Redis |
| Transcription Agent | Voice to text | OpenAI Whisper API |
| Extraction Agent | Structured signal extraction | Claude (instructor) |
| RAG Retriever | Historical context | pgvector, OpenAI Embeddings |
| Scoring Agent | Hybrid deterministic + LLM scoring | Claude |
| Verdict Agent | Emotional messaging generation | Claude |

**Key Design Decisions:**
- Agents as injectable FastAPI services (matches existing patterns)
- Entry-level embeddings (no chunking needed for short journal entries)
- Temporal decay weighting for RAG (recent entries matter more)
- Score guard rails: LLM scores constrained to +-20% of deterministic baseline

**Directory Structure:**
```
backend/app/ai_pipeline/
  orchestrator.py     # Celery chains
  tasks.py           # Celery task definitions
  agents/            # BaseAgent, extraction, scoring, verdict
  rag/               # embedder, retriever, queries
  prompts/           # Versioned prompt templates
  schemas/           # Pydantic models
```

### From PITFALLS.md: Risk Mitigation

**Critical (Prevent at All Costs):**

1. **LLM Scoring Inconsistency (40% variance)**
   - Prevention: Deterministic-first scoring, multi-evaluation averaging, score bucketing
   - Phase: Scoring Engine (Phase 1)

2. **Embedding Drift (Silent RAG Breaker)**
   - Prevention: Pin model versions, store version with embeddings, quarterly reindexing plan
   - Phase: RAG System (Phase 2)

3. **Emotional Tone Miscalibration**
   - Prevention: Mood classification before verdicts, hard guardrails on crisis language
   - Phase: Verdict Generation (Phase 3)

4. **Model Drift Without Detection**
   - Prevention: Daily golden-set evaluation, drift alerts at 10% deviation
   - Phase: All phases (monitoring infrastructure)

**Moderate (Plan For):**
- RAG retrieval noise: MMR diversity, hybrid search, temporal weighting
- Notification fatigue: Track fatigue metrics, adaptive frequency
- Prompt brittleness: MOF diversification, structured output enforcement, adversarial testing

---

## Implications for Roadmap

Based on combined research, the following phase structure is recommended:

### Phase 1: Scoring Foundation

**Rationale:** Scoring is the core of "Am I Better?" - must be reliable before adding complexity.

**Delivers:**
- Deterministic scoring rules for quantifiable metrics
- Basic LLM enhancement with guard rails
- Golden-set monitoring infrastructure (catches drift early)
- Prompt testing framework

**Features from FEATURES.md:**
- Goal-activity mapping
- Daily scoring (deterministic rules)
- Basic historical comparison (SQL, not RAG yet)

**Pitfalls to Avoid:**
- LLM inconsistency (deterministic-first design)
- Prompt brittleness (establish testing patterns)
- Model drift (monitoring from day one)

**Research Flag:** Standard patterns - well-documented.

---

### Phase 2: RAG Historical Context

**Rationale:** Historical comparison is core differentiator; RAG enables "better than last week/month."

**Delivers:**
- Embedding service with version tracking
- pgvector retrieval with HNSW indexing
- Hybrid search (semantic + keyword for goal names)
- Drift detection infrastructure

**Features from FEATURES.md:**
- Historical comparison via RAG ("30% more productive than last month")
- Pattern recognition ("your entries show you tend to...")

**Pitfalls to Avoid:**
- Embedding drift (version pinning, monitoring)
- Retrieval noise (MMR, temporal decay, hybrid search)
- Comparison without context (filter by comparable contexts)

**Research Flag:** Needs `/gsd:research-phase` - embedding drift mitigation strategies deserve deeper investigation.

---

### Phase 3: Verdict Generation

**Rationale:** Verdicts depend on reliable scoring and context; emotional messaging requires safety infrastructure.

**Delivers:**
- Mood classification (prerequisite for safe verdicts)
- Verdict agent with tone calibration
- Crisis detection and escalation paths
- User-configurable feedback intensity

**Features from FEATURES.md:**
- Daily verdict with emotional messaging (CORE DIFFERENTIATOR)
- Actionable guidance for tomorrow

**Pitfalls to Avoid:**
- Emotional tone miscalibration (mood classification first)
- Over-engineered emotional intelligence (stay in lane)
- Generic responses (always reference specific user data)

**Research Flag:** Needs `/gsd:research-phase` - emotional AI safety patterns and crisis detection warrant careful specification.

---

### Phase 4: Signal Extraction

**Rationale:** Extraction enables multi-signal scoring; can be developed in parallel with Phase 3.

**Delivers:**
- Claude-powered signal extraction with instructor
- Pydantic schemas for structured outputs
- Multi-category extraction (productivity, fitness, learning, discipline, well-being)

**Features from FEATURES.md:**
- Multi-signal extraction (differentiator)
- Basic mood/sentiment detection (table stakes)

**Pitfalls to Avoid:**
- Prompt brittleness (structured output enforcement)
- Gaming metrics (length-normalize, substance focus)

**Research Flag:** Standard patterns - instructor documentation sufficient.

---

### Phase 5: Voice & Transcription (Optional)

**Rationale:** Voice is enhancement, not core; text input delivers full value prop.

**Delivers:**
- faster-whisper integration
- Audio upload and storage
- Transcription queue with retry logic

**Features from FEATURES.md:**
- Voice journaling with smart transcription

**Pitfalls to Avoid:**
- GPU resource management
- Transcription latency expectations

**Research Flag:** Standard patterns - faster-whisper well-documented.

---

### Phase 6: Notifications & Nudges

**Rationale:** Notifications are downstream of core evaluation; require fatigue infrastructure.

**Delivers:**
- Missing entry detection
- Nudge generation with context
- Fatigue scoring per user
- Adaptive frequency controls

**Features from FEATURES.md:**
- Ego-poking smart notifications
- Streak maintenance nudges

**Pitfalls to Avoid:**
- Notification fatigue loop (measure fatigue, not just opens)
- Wrong timing (learn user engagement patterns)

**Research Flag:** Standard patterns - notification systems well-documented.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | PyPI versions verified 2026-01-19; instructor/faster-whisper/Langfuse mature |
| Features | MEDIUM-HIGH | Competitor analysis solid; some differentiators inferred from market gaps |
| Architecture | HIGH | Celery chains, service patterns well-documented; matches existing codebase |
| Pitfalls | HIGH | Cross-referenced academic sources and production reports |

### Gaps to Address During Planning

1. **Mood classification approach:** Research mentions need but doesn't specify implementation - sentiment analysis vs. keyword detection vs. LLM classification needs investigation
2. **Crisis escalation specifics:** What language triggers escalation? What resources to surface? Requires domain expertise
3. **Scoring rubric calibration:** Specific thresholds for "better/same/worse" need user research or iteration
4. **User preference for "edge" level:** How much attitude is welcomed? Needs A/B testing infrastructure
5. **Reindexing strategy:** When pgvector reindexing happens, what's the user experience? Needs operational planning

---

## Sources

### Stack Research (HIGH confidence)
- [LangGraph 1.0 Announcement](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Instructor Documentation](https://python.useinstructor.com/)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [pgvector 0.8.0 Performance](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)
- [Langfuse vs LangSmith](https://langfuse.com/faq/all/langsmith-alternative)

### Feature Research (MEDIUM-HIGH confidence)
- [Reflection.app](https://www.reflection.app/)
- [Mindsera](https://www.mindsera.com)
- [Rosebud](https://www.rosebud.app/)
- [Pattrn](https://pattrn.io/)
- [Straits Research - Habit Tracking Apps Market](https://straitsresearch.com/report/habit-tracking-apps-market)

### Architecture Research (HIGH confidence)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Celery Canvas Documentation](https://docs.celeryq.dev/en/stable/userguide/canvas.html)
- [Neo4j Advanced RAG Techniques](https://neo4j.com/blog/genai/advanced-rag-techniques/)
- [LLM Structured Output Guide](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)

### Pitfall Research (HIGH confidence)
- [Confident AI - LLM Evaluation Metrics](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [LLM-as-a-Judge Bias Research](https://llm-judge-bias.github.io/)
- [Embedding Drift - Drift-Adapter EMNLP 2025](https://aclanthology.org/2025.emnlp-main.805/)
- [TC Columbia Expert Warnings on Emotional AI](https://www.tc.columbia.edu/articles/2025/december/experts-caution-against-using-ai-chatbots-for-emotional-support/)
- [ZenML LLMOps Production Report](https://www.zenml.io/blog/what-1200-production-deployments-reveal-about-llmops-in-2025)

---

*Research synthesis complete. Ready for roadmap creation.*
