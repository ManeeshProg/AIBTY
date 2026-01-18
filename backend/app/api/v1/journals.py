from datetime import date
from fastapi import APIRouter, HTTPException, status, Query

from app.deps import DbSession, CurrentUser
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.journal_service import JournalService

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("/", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
async def create_or_update_journal(
    journal_in: JournalCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create or update a journal entry for a specific date."""
    service = JournalService(db)
    journal = await service.create_or_update(
        user_id=current_user.id,
        entry_date=journal_in.entry_date,
        content_markdown=journal_in.content_markdown,
    )
    return journal


@router.get("/", response_model=list[JournalRead])
async def list_journals(
    db: DbSession,
    current_user: CurrentUser,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """List journal entries with optional date filtering and pagination."""
    service = JournalService(db)
    journals = await service.list(
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit,
    )
    return journals


@router.get("/{entry_date}", response_model=JournalRead)
async def get_journal(
    entry_date: date,
    db: DbSession,
    current_user: CurrentUser,
):
    """Get a specific journal entry by date."""
    service = JournalService(db)
    journal = await service.get_by_date(current_user.id, entry_date)

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )
    return journal


@router.put("/{entry_date}", response_model=JournalRead)
async def update_journal(
    entry_date: date,
    journal_in: JournalUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update an existing journal entry."""
    service = JournalService(db)
    journal = await service.get_by_date(current_user.id, entry_date)

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    updated = await service.update(journal, journal_in.content_markdown)
    return updated


@router.delete("/{entry_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal(
    entry_date: date,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a journal entry."""
    service = JournalService(db)
    journal = await service.get_by_date(current_user.id, entry_date)

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    await service.delete(journal)
