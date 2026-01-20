from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.journal_entry import JournalEntry, ExtractedMetric
from app.ai_pipeline.agents.extraction_agent import ExtractionAgent


class ExtractionService:
    """
    Service for extracting structured activities from journal entries
    and persisting them to the database.

    Uses ExtractionAgent (Claude + instructor) to identify and extract
    quantifiable activities from journal text.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize extraction service with database session.

        Args:
            db: SQLAlchemy async session for database operations
        """
        self.db = db

    async def extract_and_persist(self, entry: JournalEntry) -> list[ExtractedMetric]:
        """
        Extract activities from journal entry and persist to database.

        This method:
        1. Uses ExtractionAgent to extract structured activities from entry text
        2. Creates ExtractedMetric records for each activity
        3. Persists to database and returns the metrics

        Args:
            entry: JournalEntry to extract activities from

        Returns:
            List of ExtractedMetric records created
        """
        # Instantiate extraction agent
        agent = ExtractionAgent()

        # Extract activities from journal content
        result = agent.extract(entry.content_markdown)

        # Convert each extracted activity to ExtractedMetric
        metrics = []
        for activity in result.activities:
            metric = ExtractedMetric(
                entry_id=entry.id,
                category=activity.category,
                key=activity.key,
                value=activity.value,
                evidence=activity.evidence,
                confidence=activity.confidence,
            )
            self.db.add(metric)
            metrics.append(metric)

        # Commit all metrics at once
        await self.db.commit()

        # Refresh to get database-assigned IDs
        for metric in metrics:
            await self.db.refresh(metric)

        return metrics

    async def get_metrics_for_entry(self, entry_id: UUID) -> list[ExtractedMetric]:
        """
        Retrieve all extracted metrics for a specific journal entry.

        Args:
            entry_id: UUID of the journal entry

        Returns:
            List of ExtractedMetric records for the entry
        """
        result = await self.db.execute(
            select(ExtractedMetric).where(ExtractedMetric.entry_id == entry_id)
        )
        return list(result.scalars().all())

    async def clear_metrics_for_entry(self, entry_id: UUID) -> None:
        """
        Delete all extracted metrics for a specific journal entry.

        Useful for re-extraction when entry content is updated.

        Args:
            entry_id: UUID of the journal entry
        """
        await self.db.execute(
            delete(ExtractedMetric).where(ExtractedMetric.entry_id == entry_id)
        )
        await self.db.commit()
