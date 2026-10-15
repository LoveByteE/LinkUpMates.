# routes/talents.py
# "Find Talent" (GET) and "Become Talent" (POST) in the nav bar.
import sqlite3
from fastapi import APIRouter, HTTPException

from database.db import get_db
from schemas.talent import CreateTalentDTO, TalentOut

router = APIRouter(prefix="/api/v1/talents", tags=["Talents"])

# we only select safe columns from users, never the password
BASE_QUERY = """
    SELECT t.id, t.user_id, u.fullname, u.location, t.category, t.bio
    FROM talents t
    JOIN users u ON u.id = t.user_id
"""


# Find Talent. Optional filter: /api/v1/talents?category=Photography
@router.get("", response_model=list[TalentOut])
def find_talent(category: str | None = None):
    with get_db() as db:
        if category:
            rows = db.execute(BASE_QUERY + " WHERE t.category = ? ORDER BY t.id DESC", (category,)).fetchall()
        else:
            rows = db.execute(BASE_QUERY + " ORDER BY t.id DESC").fetchall()
    return [dict(row) for row in rows]


@router.get("/{talent_id}", response_model=TalentOut)
def get_talent(talent_id: int):
    with get_db() as db:
        row = db.execute(BASE_QUERY + " WHERE t.id = ?", (talent_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    return dict(row)


# Become Talent
@router.post("", status_code=201)
def become_talent(talent: CreateTalentDTO):
    try:
        with get_db() as db:
            if db.execute("SELECT 1 FROM users WHERE id = ?", (talent.user_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail="User not found")
            cursor = db.execute(
                "INSERT INTO talents (user_id, category, bio) VALUES (?, ?, ?)",
                (talent.user_id, talent.category, talent.bio),
            )
            new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # UNIQUE(user_id, category) was broken
        raise HTTPException(status_code=409, detail="Already listed in this category")
    return {"message": "You are now listed as talent", "id": new_id}


# stop being listed
@router.delete("/{talent_id}", status_code=204)
def remove_talent(talent_id: int):
    with get_db() as db:
        cursor = db.execute("DELETE FROM talents WHERE id = ?", (talent_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Talent not found")
