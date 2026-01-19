# Architecture Patterns: AI Evaluation Pipeline

**Domain:** Personal growth AI coaching with journal analysis
**Researched:** 2026-01-19
**Confidence:** HIGH (patterns verified against multiple authoritative sources)

## Executive Summary

The AI evaluation pipeline for "Am I Better Than Yesterday?" follows a **Sequential Pipeline Pattern** orchestrated by Celery, with each specialized agent processing data in order. This matches the domain requirement: journal entry flows through transcription, extraction, retrieval, scoring, and verdict generation in strict sequence.

The architecture leverages the existing FastAPI service layer pattern, treating AI agents as specialized services injected via FastAPI's dependency system. Celery chains provide durability and retry logic for the inherently unreliable LLM operations.

## Recommended Architecture

```
                                    EVENING TRIGGER (Celery Beat)
                                              |
                                              v
+-----------------------------------------------------------------------------------+
|                           ORCHESTRATOR (Celery Chain)                             |
|                                                                                   |
|  +-----------+    +------------+    +---------+    +---------+    +----------+   |
|  | Transcribe| -> | Extract    | -> | Retrieve| -> | Score   | -> | Verdict  |   |
|  | Agent     |    | Agent      |    | (RAG)   |    | Agent   |    | Agent    |   |
|  +-----------+    +------------+    +---------+    +---------+    +----------+   |
|       |                |                |              |               |          |
|       v                v                v              v               v          |
|   Whisper API    Claude (struct)   pgvector      Deterministic    Claude         |
|                                    + Claude      + Claude LLM     (coaching)     |
+-----------------------------------------------------------------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |  PostgreSQL                   |
                              |  - DailyScore                 |
                              |  - ScoreMetric                |
                              |  - ExtractedMetric            |
                              +-------------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |  Notification Service         |
                              |  (push notification trigger)  |
                              +-------------------------------+
```

## Component Boundaries

| Component | Responsibility | Input | Output | External Deps |
|-----------|---------------|-------|--------|---------------|
| **Orchestrator** | Coordinates agent sequence, handles errors, manages pipeline state | User ID, Date | DailyScore ID | Celery, Redis |
| **Transcription Agent** | Converts voice audio to text | Audio bytes/URL | Transcribed text | OpenAI Whisper API |
| **Extraction Agent** | Pulls structured signals from text | Journal text | ExtractedMetric[] | Claude API (Anthropic) |
| **RAG Retriever** | Fetches relevant historical context | Query text, User ID | Historical entries + embeddings | pgvector, OpenAI Embeddings |
| **Scoring Agent** | Computes deterministic + LLM scores | Today's metrics, Historical context | ScoreMetric[], composite score | Claude API (hybrid logic) |
| **Verdict Agent** | Generates emotional messaging | Scores, Historical context, User goals | Verdict, summary, advice | Claude API |
| **Notification Trigger** | Decides when/what to push | DailyScore, User preferences | Push payload | Push notification service |

## Data Flow

### Primary Flow: Journal Entry to Verdict

```
1. ENTRY CREATION (Sync - via API)
   Journal Entry → JournalService.create_or_update()
   └── If voice input: store audio URL (or bytes for immediate processing)
   └── Trigger: Queue evaluation task for evening

2. EVENING EVALUATION (Async - Celery Beat triggers at user's configured time)

   2a. Gather Day's Entries
       └── Query all JournalEntry for user + date
       └── If voice entries exist without transcription: transcribe first

   2b. Transcription (if needed)
       └── Input: Audio bytes or URL
       └── Output: Transcribed text appended to entry
       └── Model: OpenAI Whisper (whisper-1)
       └── Async pattern: Celery task with retry on API failure

   2c. Extraction
       └── Input: All entry content for the day (concatenated)
       └── Output: ExtractedMetric[] with category, key, value, evidence
       └── Model: Claude with structured output (Pydantic schema)
       └── Categories: productivity, fitness, learning, discipline, well-being

   2d. Embedding & RAG Retrieval
       └── Input: Today's entry text
       └── Create embedding: OpenAI text-embedding-3-small
       └── Store: EntryEmbedding in pgvector
       └── Retrieve: Top-k similar historical entries (cosine similarity)
       └── Retrieve: Yesterday's metrics + last 7 days scores

   2e. Scoring
       └── Input: Today's ExtractedMetric[], Historical context, User goals
       └── Process:
           - Deterministic rules: Compare metric values to yesterday
           - LLM reasoning: Claude judges effort, intensity, context
       └── Output: ScoreMetric[] per category, composite_score (0-100)

   2f. Verdict Generation
       └── Input: Scores, Historical trends, User goals, Personality prefs
       └── Output: verdict (better|same|worse), summary, actionable_advice
       └── Model: Claude with coaching personality
       └── Tone: Supportive but edgy - celebrates wins, pokes egos on slips

3. PERSISTENCE
   └── Save DailyScore with all ScoreMetric relationships
   └── Update user's streak counter

4. NOTIFICATION
   └── Evaluate notification trigger rules
   └── If triggered: Queue push notification with verdict preview
```

### Secondary Flow: Missing Entry Nudge

```
1. SCHEDULED CHECK (Celery Beat - mid-afternoon)
   └── Query users who haven't logged today
   └── For each: Generate provocative nudge based on yesterday's data
   └── Queue push notification

2. NUDGE GENERATION
   └── Input: Yesterday's score, streak, goals
   └── Output: Short, edgy message ("Yesterday you did 3 hard problems. Today... silence?")
   └── Model: Claude with specific nudge prompt template
```

## Agent Orchestration Pattern

**Recommendation: Celery Chain with Error Boundaries**

Based on research, the Sequential Pipeline Pattern via Celery chains is the best fit because:

1. **Strict ordering required**: Each agent depends on the previous agent's output
2. **Durability needed**: LLM API calls can fail; Celery provides retry logic
3. **Already in stack**: Celery + Redis already configured in requirements
4. **Simpler than LangGraph**: For a linear pipeline, Celery chains are simpler than graph-based orchestration

### Implementation Pattern

```python
# ai_pipeline/orchestrator.py

from celery import chain
from .tasks import (
    transcribe_entries_task,
    extract_signals_task,
    retrieve_context_task,
    compute_scores_task,
    generate_verdict_task,
    trigger_notification_task,
)

def run_evening_evaluation(user_id: str, date: str):
    """Execute the full evaluation pipeline as a Celery chain."""
    pipeline = chain(
        transcribe_entries_task.s(user_id, date),
        extract_signals_task.s(),     # receives transcription result
        retrieve_context_task.s(),    # receives extraction result
        compute_scores_task.s(),      # receives context result
        generate_verdict_task.s(),    # receives scores result
        trigger_notification_task.s() # receives verdict result
    )
    return pipeline.apply_async()
```

### Task Structure

```python
# ai_pipeline/tasks.py

from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def transcribe_entries_task(self, user_id: str, date: str):
    """Transcribe any voice entries for the user on this date."""
    try:
        # ... transcription logic
        return {"user_id": user_id, "date": date, "entries": entries}
    except OpenAIError as e:
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3)
def extract_signals_task(self, prev_result: dict):
    """Extract structured signals from entry text."""
    # ... extraction logic using Claude
    return {**prev_result, "metrics": extracted_metrics}
```

### Alternative Considered: LangGraph

LangGraph provides more sophisticated orchestration with cycles, conditional branching, and human-in-the-loop. However:

- **Overkill for linear pipeline**: This use case is strictly sequential
- **Added complexity**: LangGraph requires learning new abstractions
- **Celery already configured**: No need to add another dependency

**When to consider LangGraph**: If future requirements add conditional flows (e.g., "if score is very low, trigger intervention agent"), migrating to LangGraph would make sense.

## Agent Architecture: Service Pattern

**Recommendation: Agents as Injectable Services**

Each agent is a service class that can be injected via FastAPI's dependency system, matching the existing codebase pattern.

```python
# ai_pipeline/agents/base.py

from abc import ABC, abstractmethod
from anthropic import Anthropic
from openai import OpenAI

class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, anthropic_client: Anthropic, openai_client: OpenAI):
        self.anthropic = anthropic_client
        self.openai = openai_client

    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """Process input and return output."""
        pass
```

```python
# ai_pipeline/agents/extraction.py

from pydantic import BaseModel
from .base import BaseAgent

class ExtractedSignal(BaseModel):
    category: str
    key: str
    value: float
    evidence: str
    confidence: float

class ExtractionResult(BaseModel):
    signals: list[ExtractedSignal]

class ExtractionAgent(BaseAgent):
    """Extracts structured signals from journal entry text."""

    async def process(self, input_data: dict) -> ExtractionResult:
        entry_text = input_data["entry_text"]

        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": self._build_prompt(entry_text)}
            ],
            # Use tool_use for structured output
        )

        return self._parse_response(response)
```

## RAG Architecture

### Embedding Strategy

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Embedding model | OpenAI text-embedding-3-small | Already in stack, 1536 dims matches EntryEmbedding model |
| Chunking | Entry-level (no chunking) | Journal entries are short (<1000 words typically) |
| Storage | pgvector in PostgreSQL | Already configured, unified with relational data |

### Retrieval Strategy

```python
# ai_pipeline/rag/retriever.py

class HistoricalRetriever:
    """Retrieves relevant historical context for scoring."""

    async def retrieve(
        self,
        user_id: str,
        query_embedding: list[float],
        top_k: int = 10
    ) -> RetrievalResult:
        # 1. Semantic search: Similar entries via pgvector
        similar_entries = await self._semantic_search(user_id, query_embedding, top_k)

        # 2. Temporal context: Yesterday + last 7 days scores
        recent_scores = await self._get_recent_scores(user_id, days=7)
        yesterday_metrics = await self._get_yesterday_metrics(user_id)

        # 3. Goal context: User's active goals
        active_goals = await self._get_active_goals(user_id)

        return RetrievalResult(
            similar_entries=similar_entries,
            recent_scores=recent_scores,
            yesterday_metrics=yesterday_metrics,
            active_goals=active_goals,
        )
```

### pgvector Query Pattern

```sql
-- Semantic similarity search
SELECT
    je.id,
    je.entry_date,
    je.content_markdown,
    ee.chunk_text,
    1 - (ee.embedding <=> :query_embedding) as similarity
FROM entry_embeddings ee
JOIN journal_entries je ON ee.entry_id = je.id
WHERE je.user_id = :user_id
  AND je.entry_date < :today  -- Exclude today
ORDER BY ee.embedding <=> :query_embedding
LIMIT :top_k;
```

## Scoring Architecture

### Hybrid Scoring: Deterministic + LLM

Based on research, hybrid scoring (deterministic rules + LLM reasoning) provides the best balance of consistency and nuance.

```
SCORING FLOW
============

1. DETERMINISTIC SCORING (fast, consistent, explainable)
   └── Compare today's metrics to yesterday's:
       - hours_deep_work: today=4, yesterday=3 → +1 (better)
       - exercise_minutes: today=0, yesterday=30 → -1 (worse)
       - learning_items: today=2, yesterday=2 → 0 (same)
   └── Apply rules for streaks, consistency bonuses
   └── Output: raw_score per category

2. LLM SCORING (nuanced, contextual)
   └── Input: Raw scores + context (goals, historical trend, entry text)
   └── Prompt: "Given the user's goals and context, evaluate the significance..."
   └── Output: adjusted_score, reasoning
   └── Guards: Score must be within +-20% of deterministic score (prevents hallucination)

3. COMPOSITE SCORE
   └── Weighted average of category scores
   └── Weights based on user's goal priorities
   └── Output: 0-100 composite score

4. VERDICT DETERMINATION
   └── Compare composite to yesterday's:
       - >5 points higher → "better"
       - Within 5 points → "same"
       - >5 points lower → "worse"
```

### Score Guard Rails

```python
# ai_pipeline/agents/scoring.py

def validate_llm_score(deterministic_score: float, llm_score: float) -> float:
    """Ensure LLM doesn't hallucinate wildly different scores."""
    max_deviation = 0.2 * 10  # 20% of max score (10)

    if abs(llm_score - deterministic_score) > max_deviation:
        # Fall back to deterministic with small adjustment
        adjustment = 0.5 if llm_score > deterministic_score else -0.5
        return deterministic_score + adjustment

    return llm_score
```

## Suggested Build Order

Based on component dependencies, build in this sequence:

### Phase 1: Foundation (No LLM calls)
1. **Embedding Service** - Create embeddings, store in pgvector
2. **RAG Retriever** - Query similar entries, get recent scores
3. **Celery Setup** - Configure workers, beat scheduler

**Rationale**: These components can be tested with mock data before adding LLM complexity.

### Phase 2: Extraction Pipeline
4. **Extraction Agent** - Claude structured output for signal extraction
5. **Extraction Task** - Celery task wrapping the agent

**Rationale**: Extraction is the first LLM component and has clear input/output contract.

### Phase 3: Scoring Pipeline
6. **Deterministic Scorer** - Rule-based scoring (no LLM)
7. **Scoring Agent** - LLM-enhanced scoring with guard rails
8. **Scoring Task** - Celery task for full scoring flow

**Rationale**: Deterministic scorer provides baseline; LLM scorer adds nuance.

### Phase 4: Verdict Pipeline
9. **Verdict Agent** - Emotional messaging generation
10. **Verdict Task** - Celery task for verdict generation

**Rationale**: Verdict depends on scores being complete.

### Phase 5: Orchestration
11. **Evening Orchestrator** - Celery chain connecting all tasks
12. **Celery Beat Schedule** - Evening trigger per user timezone
13. **Transcription Agent** - Voice to text (can be added last since text input works)

**Rationale**: Orchestration ties everything together; transcription is optional path.

### Phase 6: Notifications
14. **Nudge Generator** - Missing entry detection and message generation
15. **Notification Trigger** - Push notification queue

**Rationale**: Notifications are downstream of core evaluation pipeline.

## Integration with Existing Backend

### Service Layer Integration

```python
# services/evaluation_service.py

from ai_pipeline.orchestrator import run_evening_evaluation

class EvaluationService:
    """Service for triggering and querying evaluations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def trigger_evaluation(self, user_id: str, date: date) -> str:
        """Trigger evening evaluation pipeline."""
        task = run_evening_evaluation.delay(str(user_id), date.isoformat())
        return task.id

    async def get_evaluation_status(self, task_id: str) -> dict:
        """Check status of evaluation pipeline."""
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        return {"status": result.status, "result": result.result}
```

### API Endpoint Integration

```python
# api/v1/evaluations.py

from fastapi import APIRouter, Depends
from app.deps import CurrentUser, get_db
from app.services.evaluation_service import EvaluationService

router = APIRouter()

@router.post("/trigger")
async def trigger_evaluation(
    user: CurrentUser,
    date: date = None,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger evaluation for testing."""
    service = EvaluationService(db)
    task_id = await service.trigger_evaluation(user.id, date or date.today())
    return {"task_id": task_id}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Check evaluation status."""
    service = EvaluationService(db)
    return await service.get_evaluation_status(task_id)
```

### Dependency Injection for AI Clients

```python
# deps.py (additions)

from anthropic import Anthropic
from openai import OpenAI
from app.core.config import settings

def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)

AnthropicClient = Annotated[Anthropic, Depends(get_anthropic_client)]
OpenAIClient = Annotated[OpenAI, Depends(get_openai_client)]
```

## Directory Structure

```
backend/app/ai_pipeline/
├── __init__.py
├── orchestrator.py          # Celery chain definitions
├── tasks.py                 # Celery task definitions
├── agents/
│   ├── __init__.py
│   ├── base.py              # BaseAgent abstract class
│   ├── transcription.py     # Whisper integration
│   ├── extraction.py        # Signal extraction with Claude
│   ├── scoring.py           # Hybrid scoring agent
│   └── verdict.py           # Coaching message generation
├── rag/
│   ├── __init__.py
│   ├── embedder.py          # OpenAI embedding creation
│   ├── retriever.py         # Historical context retrieval
│   └── queries.py           # pgvector query utilities
├── prompts/
│   ├── __init__.py
│   ├── extraction.py        # Extraction prompt templates
│   ├── scoring.py           # Scoring prompt templates
│   ├── verdict.py           # Verdict prompt templates
│   └── nudge.py             # Nudge message templates
└── schemas/
    ├── __init__.py
    ├── extraction.py        # Pydantic models for extraction
    ├── scoring.py           # Pydantic models for scoring
    └── pipeline.py          # Pipeline state models
```

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 100K users |
|---------|--------------|--------------|---------------|
| Evening evaluation | Single Celery worker | Multiple workers, staggered by timezone | Worker pool per timezone region |
| pgvector retrieval | Single query | Add HNSW index, tune ef_search | Consider dedicated vector DB |
| LLM API calls | Sequential | Batch where possible | Rate limiting, request queuing |
| Notification delivery | Direct push | Queue-based | Dedicated notification service |

## Anti-Patterns to Avoid

### Anti-Pattern 1: Synchronous LLM Calls in API Endpoints
**What:** Calling Claude/OpenAI directly in FastAPI route handlers
**Why bad:** LLM calls take 2-30 seconds; blocks request, causes timeouts
**Instead:** Queue to Celery, return task ID, poll for completion

### Anti-Pattern 2: Monolithic Evaluation Function
**What:** Single function doing transcription + extraction + scoring + verdict
**Why bad:** Can't retry individual steps, hard to debug, no partial progress
**Instead:** Celery chain with discrete tasks that can retry independently

### Anti-Pattern 3: Trusting LLM Scores Blindly
**What:** Using raw LLM-generated scores without validation
**Why bad:** LLMs can hallucinate numbers, inconsistent across calls
**Instead:** Hybrid scoring with deterministic baseline and guard rails

### Anti-Pattern 4: Embedding on Read
**What:** Creating embeddings during retrieval queries
**Why bad:** Slow, duplicates work, blocks retrieval
**Instead:** Embed on write (when entry is created), retrieve by vector

## Sources

**Multi-Agent Orchestration Patterns:**
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Google ADK Multi-Agent Patterns](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/)
- [LangGraph Multi-Agent Orchestration Guide](https://latenode.com/blog/ai-frameworks-technical-infrastructure/langgraph-multi-agent-orchestration/langgraph-multi-agent-orchestration-complete-framework-guide-architecture-analysis-2025)

**Celery Patterns:**
- [Celery Canvas Documentation](https://docs.celeryq.dev/en/stable/userguide/canvas.html)
- [Async LLM Tasks with Celery](https://medium.com/algomart/async-llm-tasks-with-celery-and-celery-beat-31c824837f35)
- [Productionize LLM RAG App with Celery](https://towardsdatascience.com/productionize-llm-rag-app-in-django-part-i-celery-26053b4acad6/)

**FastAPI Integration:**
- [FastAPI LangGraph Production Template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
- [Building Production-Ready AI Backends](https://dev.to/hamluk/building-production-ready-ai-backends-with-fastapi-4352)

**RAG Architecture:**
- [Vector Databases for RAG 2025](https://dev.to/klement_gunndu_e16216829c/vector-databases-guide-rag-applications-2025-55oj)
- [Advanced RAG Techniques](https://neo4j.com/blog/genai/advanced-rag-techniques/)

**Hybrid Scoring:**
- [LLM Evaluation Metrics Guide](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [Rulers: Deterministic LLM Evaluation](https://arxiv.org/html/2601.08654)

**Structured Extraction:**
- [LLM Structured Output Guide](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)
- [LlamaIndex Extraction Documentation](https://docs.llamaindex.ai/en/stable/use_cases/extraction/)

---

*Architecture research: 2026-01-19*
