# routes/concepts.py
# The four "Our Concepts" cards on the landing page come from here.
from fastapi import APIRouter, HTTPException

from database.db import get_db
from schemas.concept import ConceptOut

router = APIRouter(prefix="/api/v1/concepts", tags=["Concepts"])


@router.get("", response_model=list[ConceptOut])
def get_concepts():
    with get_db() as db:
        rows = db.execute("SELECT * FROM concepts").fetchall()
    return [dict(row) for row in rows]


@router.get("/{concept_id}", response_model=ConceptOut)
def get_concept(concept_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return dict(row)
