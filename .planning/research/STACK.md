# Technology Stack: AI Evaluation Pipeline

**Project:** Am I Better Than Yesterday - AI Evaluation Pipeline
**Researched:** 2026-01-19
**Focus:** AI orchestration, RAG, embeddings, scoring patterns for personal growth journaling app

## Executive Summary

This research covers the AI/ML stack needed to add an evaluation pipeline (voice transcription, signal extraction, RAG, scoring, verdict generation) to an existing FastAPI + PostgreSQL + Celery backend. The 2025/2026 landscape has matured significantly around multi-agent orchestration and structured LLM outputs.

**Key finding:** LangGraph 1.0 is the production standard for multi-agent orchestration, but for your specific use case (deterministic + LLM scoring pipeline), a simpler approach using `instructor` for structured outputs may be more appropriate. Reserve LangGraph for complex stateful agent workflows.

---

## Recommended Stack

### Multi-Agent Orchestration

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **LangGraph** | 1.0.6 | Stateful multi-agent workflows | HIGH |
| **PydanticAI** | 1.44.0 | Simpler agent patterns, type-safe | HIGH |
| **LangChain** | 1.2.6 | Integrations, chains (use sparingly) | HIGH |

**Recommendation:** Start with **PydanticAI** for the evaluation pipeline. LangGraph is overkill unless you need:
- Complex branching logic with state persistence
- Human-in-the-loop approval workflows
- Long-running agents that survive restarts

**Rationale:**
- LangGraph 1.0 reached GA in October 2025 with built-in persistence, time-travel debugging, and robust fault tolerance ([LangGraph 1.0 Announcement](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available))
- However, LangChain/LangGraph adds 15-25% latency overhead for simple scenarios and significant complexity ([Performance Analysis](https://fenilsonani.com/articles/langchain-vs-direct-api-performance-analysis))
- PydanticAI brings "FastAPI feeling" to agent development with full type safety and model-agnostic design
- For a scheduled evening analysis pipeline, direct API calls + Celery tasks are likely simpler and faster

**What NOT to use:**
- **AutoGen** - Microsoft's framework is powerful but complex; better suited for research/experimentation than production pipelines
- **CrewAI** - Good for multi-agent roleplay scenarios but adds abstraction layers you don't need
- **Raw LangChain LCEL** - API is unstable, "changes week to week" with breaking changes ([LangGraph Alternatives](https://www.zenml.io/blog/langgraph-alternatives))

---

### Structured LLM Outputs

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **instructor** | 1.14.4 | Structured extraction from LLMs | HIGH |
| **pydantic** | 2.x | Schema validation | HIGH |

**Recommendation:** Use **instructor** for all LLM-to-structured-data workflows.

**Rationale:**
- 3+ million monthly downloads, battle-tested in production (LSEG deployed it for financial surveillance in 2025) ([Instructor Docs](https://python.useinstructor.com/))
- Works with your existing Anthropic and OpenAI clients - just a patch, not a framework
- Automatic retries when validation fails, streaming support
- Built on Pydantic for full IDE autocomplete and type checking

**Example use cases in your pipeline:**
- Signal extraction: `JournalSignals` Pydantic model with emotion, goals, actions
- Scoring: `ScoreResult` model with numeric scores and reasoning
- Verdict: `Verdict` model with tone, message, and encouragement level

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel

client = instructor.from_anthropic(Anthropic())

class JournalSignals(BaseModel):
    primary_emotion: str
    emotion_intensity: float  # 0-1
    goals_mentioned: list[str]
    actions_taken: list[str]
    blockers_identified: list[str]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": journal_entry}],
    response_model=JournalSignals,
)
```

---

### Voice Transcription

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **faster-whisper** | 1.2.1 | Local transcription (4x faster than OpenAI Whisper) | HIGH |
| **openai-whisper** | (API) | Cloud fallback ($0.006/min) | HIGH |

**Recommendation:** Use **faster-whisper** for self-hosted transcription.

**Rationale:**
- 4x faster than original Whisper with same accuracy via CTranslate2 optimization ([faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper))
- Lower memory footprint, supports INT8/FP16 quantization
- No FFmpeg dependency (bundles via PyAV)
- Use `whisper-turbo` model for 8x speedup with near-large accuracy

**Configuration:**
```python
from faster_whisper import WhisperModel

# GPU: CUDA 12 + cuDNN 9 required
model = WhisperModel("turbo", device="cuda", compute_type="float16")

# CPU fallback with INT8 quantization
model = WhisperModel("turbo", device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)
```

**What NOT to use:**
- **Deepgram** - Fastest (20s/hour) but 3-5x more expensive, unnecessary for async batch processing
- **AssemblyAI** - Best for real-time streaming which you don't need
- **openai-whisper (local)** - Slower, higher memory, requires FFmpeg

**GPU Requirements:**
- Whisper turbo: ~6GB VRAM
- Whisper large-v3: ~10GB VRAM

---

### RAG & Embeddings

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **pgvector** | 0.8.0+ | Vector storage (you have this) | HIGH |
| **text-embedding-3-small** | - | Primary embedding model | HIGH |
| **langchain-text-splitters** | latest | Semantic chunking | MEDIUM |

**Recommendation:** Keep **pgvector** - no need to migrate to Chroma/Pinecone.

**Rationale:**
- pgvector 0.8.0 delivers 9x faster queries and 100x better relevance with iterative scans ([AWS pgvector Blog](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/))
- You already have PostgreSQL infrastructure; adding a separate vector DB adds operational complexity
- For a single-user journaling app, pgvector scales to millions of entries without issues

**Embedding Model Choice:**

| Model | Dimensions | Cost/1M tokens | Best For |
|-------|------------|----------------|----------|
| text-embedding-3-small | 1536 | $0.02 | **Recommended** - best cost/quality |
| text-embedding-3-large | 3072 | $0.13 | Only if quality issues arise |
| text-embedding-ada-002 | 1536 | $0.10 | Legacy, don't use |

**HNSW Index Tuning for Journal Entries:**
```sql
-- Create optimized index for journal chunks
CREATE INDEX ON journal_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Runtime query optimization
SET hnsw.ef_search = 100;  -- Higher = better recall
SET hnsw.iterative_scan = relaxed_order;  -- pgvector 0.8.0+
```

**Chunking Strategy for Journals:**
- Use **semantic chunking** or **sentence-based** for personal entries
- Chunk size: 256-512 tokens with 10-20% overlap
- Preserve date boundaries - each entry should be a natural chunk boundary
- Add metadata: date, mood, topics for hybrid search

---

### LLM Evaluation & Scoring

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **deepeval** | 3.8.0 | LLM evaluation framework | HIGH |
| **Custom G-Eval** | - | LLM-as-judge scoring | HIGH |

**Recommendation:** Use **DeepEval** for evaluation metrics, custom G-Eval for scoring.

**Rationale:**
- DeepEval provides 50+ research-backed metrics, supports custom LLM judges ([DeepEval Docs](https://deepeval.com/))
- G-Eval achieves 0.514 Spearman correlation with human judgments - best available ([G-Eval Paper](https://www.confident-ai.com/blog/g-eval-the-definitive-guide))
- Binary or 3-point scales more reliable than 10-point scales

**Scoring Pattern for "Am I Better":**

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase

# Custom metric for goal progress
goal_progress_metric = GEval(
    name="Goal Progress",
    criteria="Evaluate how much progress the user made toward their stated goals",
    evaluation_steps=[
        "Identify goals mentioned in the journal entry",
        "Compare actions taken against goals",
        "Assess momentum: moving forward, stagnant, or regressing",
        "Award 1 point for each goal with measurable progress",
    ],
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
)
```

**Recommended Scoring Dimensions:**
1. **Consistency** (binary): Did they journal today? Streak maintained?
2. **Goal Alignment** (3-point): Actions align with stated goals?
3. **Emotional Growth** (3-point): Processing emotions vs. ruminating?
4. **Action Density** (numeric): Concrete actions mentioned per entry
5. **Momentum** (binary): Better than yesterday baseline?

---

### LLM Provider Strategy

| Model | Use Case | Confidence |
|-------|----------|------------|
| **Claude Sonnet 4** | Signal extraction, verdict generation | HIGH |
| **Claude Haiku** | Quick scoring, classification | HIGH |
| **GPT-4o-mini** | Fallback, cost optimization | MEDIUM |

**Recommendation:** Use **Claude Sonnet** for primary analysis, **Haiku** for lightweight tasks.

**Rationale:**
- Claude excels at text analysis, human-like writing, and summarization ([Claude vs GPT Comparison](https://zapier.com/blog/claude-vs-chatgpt/))
- Claude Opus 4 outperforms GPT-4.1 on reasoning benchmarks (72.5% vs 54.6% on SWE-bench)
- 100k+ token context window handles full journal history
- Anthropic's structured outputs (beta) integrate with instructor

**What NOT to use for this use case:**
- **GPT-4** - More expensive, no clear advantage for text analysis
- **Gemini** - Good but less proven for nuanced emotional content
- **Local LLMs** - Quality gap still significant for evaluation tasks

---

### Observability & Tracing

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **Langfuse** | 3.12.0 | LLM observability, tracing | HIGH |
| **LangSmith** | - | Alternative if deep LangChain usage | MEDIUM |

**Recommendation:** Use **Langfuse** for observability.

**Rationale:**
- Open source, MIT licensed, free self-hosting ([Langfuse vs LangSmith](https://langfuse.com/faq/all/langsmith-alternative))
- Framework-agnostic - works with direct API calls, not just LangChain
- 50k free events/month on cloud vs LangSmith's 5k
- Built on OpenTelemetry for distributed tracing

**What NOT to use:**
- **LangSmith** - Only makes sense if you're all-in on LangChain; vendor lock-in concerns
- **No observability** - You'll regret this when debugging production LLM issues

---

### Task Queue (Existing)

| Technology | Version | Purpose | Confidence |
|------------|---------|---------|------------|
| **Celery** | (existing) | Background LLM tasks | HIGH |
| **Celery Beat** | (existing) | Scheduled evening analysis | HIGH |
| **Redis** | (existing) | Broker + backend | HIGH |

**Recommendation:** Keep your existing Celery + Redis setup.

**Best Practices for LLM Tasks:**

1. **Don't run async inside Celery tasks** - Celery workers aren't async; creates event loop issues ([Celery + FastAPI Guide](https://medium.com/@termtrix/using-celery-with-fastapi-the-async-inside-tasks-event-loop-problem-and-how-endpoints-save-79e33676ade9))

2. **Set time limits** for LLM tasks:
```python
@celery_app.task(time_limit=300, soft_time_limit=240)
def analyze_journal_entry(entry_id: int):
    # LLM call with 5-minute hard limit
    pass
```

3. **Design idempotent tasks** - Enable `task_acks_late` for robustness against worker restarts

4. **Generate IDs upfront** - Don't wait for Celery result to get identifiers:
```python
analysis_id = uuid4()
analyze_journal_entry.delay(entry_id, analysis_id)
return {"analysis_id": analysis_id, "status": "processing"}
```

5. **Use Celery Beat** for evening analysis:
```python
CELERY_BEAT_SCHEDULE = {
    'evening-analysis': {
        'task': 'tasks.run_daily_analysis',
        'schedule': crontab(hour=21, minute=0),
    },
}
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Orchestration | PydanticAI / Direct | LangGraph | Overkill for scheduled pipeline |
| Structured Output | instructor | LangChain output parsers | instructor is lighter, more reliable |
| Transcription | faster-whisper | Deepgram API | Cost, you control infra |
| Vector DB | pgvector | Pinecone/Chroma | Already have Postgres, no migration needed |
| Observability | Langfuse | LangSmith | Open source, framework-agnostic |
| Embeddings | text-embedding-3-small | Cohere/Voyage | Cost-effective, quality sufficient |

---

## Installation

### Core AI Pipeline
```bash
# Structured outputs
pip install instructor>=1.14.0

# Voice transcription
pip install faster-whisper>=1.2.0

# LLM evaluation
pip install deepeval>=3.8.0

# Observability
pip install langfuse>=3.12.0

# Optional: if you need complex agent workflows
pip install pydantic-ai>=1.44.0

# Optional: if you need stateful multi-agent
pip install langgraph>=1.0.6
```

### Updated LangChain Stack (if keeping)
```bash
# Update from your current versions
pip install langchain>=1.2.6  # was 0.1.20
pip install langchain-anthropic>=1.3.1
pip install langchain-openai>=latest
```

### GPU Support for Whisper
```bash
# Requires CUDA 12 + cuDNN 9
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

---

## Version Compatibility Matrix

| Package | Minimum | Recommended | Notes |
|---------|---------|-------------|-------|
| Python | 3.10 | 3.12 | LangChain 1.x requires 3.10+ |
| instructor | 1.14.0 | 1.14.4 | Anthropic structured outputs support |
| faster-whisper | 1.2.0 | 1.2.1 | CUDA 12 required for GPU |
| deepeval | 3.7.0 | 3.8.0 | G-Eval improvements |
| langfuse | 3.0.0 | 3.12.0 | v3 SDK rewrite, migration required from v2 |
| pydantic-ai | 1.40.0 | 1.44.0 | Mature, production-ready |
| langgraph | 1.0.0 | 1.0.6 | GA release October 2025 |
| pgvector | 0.7.0 | 0.8.0 | Iterative scans, major perf improvements |

---

## Confidence Assessment

| Area | Confidence | Rationale |
|------|------------|-----------|
| Multi-agent orchestration | HIGH | LangGraph 1.0 GA, PydanticAI mature, verified on PyPI |
| Structured outputs | HIGH | instructor widely adopted, Anthropic native support verified |
| Transcription | HIGH | faster-whisper benchmarked, version verified |
| RAG/Embeddings | HIGH | pgvector 0.8.0 released, OpenAI embeddings stable |
| LLM Scoring | MEDIUM | G-Eval patterns established, but custom tuning needed |
| Celery + LLM | HIGH | Production patterns documented, well-understood |
| Observability | HIGH | Langfuse 3.x verified, open source |

---

## Sources

### Official Documentation
- [LangGraph 1.0 Announcement](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Instructor Documentation](https://python.useinstructor.com/)
- [DeepEval Documentation](https://deepeval.com/)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Langfuse Documentation](https://langfuse.com/)

### Comparisons & Benchmarks
- [LangChain vs Direct API Performance](https://fenilsonani.com/articles/langchain-vs-direct-api-performance-analysis)
- [Choosing Whisper Variants](https://modal.com/blog/choosing-whisper-variants)
- [pgvector 0.8.0 Performance](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)
- [Langfuse vs LangSmith](https://langfuse.com/faq/all/langsmith-alternative)
- [LLM-as-Judge Best Practices](https://www.confident-ai.com/blog/g-eval-the-definitive-guide)

### Package Versions (PyPI, verified 2026-01-19)
- [langgraph 1.0.6](https://pypi.org/project/langgraph/)
- [instructor 1.14.4](https://pypi.org/project/instructor/)
- [faster-whisper 1.2.1](https://pypi.org/project/faster-whisper/)
- [deepeval 3.8.0](https://pypi.org/project/deepeval/)
- [langfuse 3.12.0](https://pypi.org/project/langfuse/)
- [pydantic-ai 1.44.0](https://pypi.org/project/pydantic-ai/)
