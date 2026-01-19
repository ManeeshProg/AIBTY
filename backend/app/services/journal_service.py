from uuid import UUID
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.journal_entry import JournalEntry


class JournalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_date(self, user_id: UUID, entry_date: date) -> JournalEntry | None:
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.metrics))
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.entry_date == entry_date,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> list[JournalEntry]:
        query = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.metrics))
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.entry_date.desc())
        )

        if from_date:
            query = query.where(JournalEntry.entry_date >= from_date)
        if to_date:
            query = query.where(JournalEntry.entry_date <= to_date)

        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UUID,
        entry_date: date,
        content_markdown: str,
        input_source: str = "text",
        audio_file_url: str | None = None,
    ) -> JournalEntry:
        journal = JournalEntry(
            user_id=user_id,
            entry_date=entry_date,
            content_markdown=content_markdown,
            input_source=input_source,
            audio_file_url=audio_file_url,
        )
        self.db.add(journal)
        await self.db.commit()
        await self.db.refresh(journal)
        return journal

    async def append_content(
        self,
        user_id: UUID,
        entry_date: date,
        new_content: str,
        input_source: str = "voice",
    ) -> JournalEntry:
        """
        Append content to existing journal or create new one.

        Multiple voice entries accumulate into the journal, separated by newlines.
        """
        existing = await self.get_by_date(user_id, entry_date)
        if existing:
            # Append with separator (two newlines)
            existing.content_markdown = f"{existing.content_markdown}\n\n{new_content}"
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create(user_id, entry_date, new_content, input_source=input_source)

    async def create_or_update(
        self,
        user_id: UUID,
        entry_date: date,
        content_markdown: str,
    ) -> JournalEntry:
        existing = await self.get_by_date(user_id, entry_date)
        if existing:
            existing.content_markdown = content_markdown
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        return await self.create(user_id, entry_date, content_markdown)

    async def update(self, journal: JournalEntry, content_markdown: str) -> JournalEntry:
        journal.content_markdown = content_markdown
        await self.db.commit()
        await self.db.refresh(journal)
        return journal

    async def delete(self, journal: JournalEntry) -> None:
        await self.db.delete(journal)
        await self.db.commit()
