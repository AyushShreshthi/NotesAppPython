import math
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def create_note(db: Session, owner_id: int, note_in: NoteCreate) -> Note:
    note = Note(title=note_in.title, content=note_in.content, owner_id=owner_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes_paginated(db: Session, owner_id: int, page: int, page_size: int):
    query = db.query(Note).filter(
        Note.owner_id == owner_id,
        Note.deleted_at.is_(None),  # exclude soft-deleted notes
    ).order_by(Note.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total else 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items,
    }


def _get_active_note_or_404(db: Session, note_id: int, owner_id: int) -> Note:
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id == owner_id,
        Note.deleted_at.is_(None),
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return note


def get_note_by_id(db: Session, note_id: int, owner_id: int) -> Note:
    return _get_active_note_or_404(db, note_id, owner_id)


def update_note(db: Session, note_id: int, owner_id: int, note_in: NoteUpdate) -> Note:
    note = _get_active_note_or_404(db, note_id, owner_id)

    if note_in.title is not None:
        note.title = note_in.title
    if note_in.content is not None:
        note.content = note_in.content

    db.commit()
    db.refresh(note)
    return note


def soft_delete_note(db: Session, note_id: int, owner_id: int) -> None:
    note = _get_active_note_or_404(db, note_id, owner_id)
    note.deleted_at = datetime.now(timezone.utc)
    db.commit()
