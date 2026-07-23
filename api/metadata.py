from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from db import get_session
from models import AnimeMetadata

router = APIRouter(
    prefix="/api/metadata",
    tags=["metadata"],
)


@router.post("/", response_model=AnimeMetadata)
def create_metadata(
    item: AnimeMetadata,
    session: Session = Depends(get_session),
):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/search", response_model=List[AnimeMetadata])
def search_metadata(
    q: str = Query(...),
    limit: int = 10,
    session: Session = Depends(get_session),
):
    statement = (
        select(AnimeMetadata)
        .where(AnimeMetadata.title.ilike(f"%{q}%"))
        .limit(limit)
    )

    results = session.exec(statement).all()

    return results


@router.get("/{meta_id}", response_model=AnimeMetadata)
def get_metadata(
    meta_id: int,
    session: Session = Depends(get_session),
):
    item = session.get(AnimeMetadata, meta_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Metadata not found",
        )

    return item