# routes/collaborations.py
# The "Collaborate" page sends a request, the "Inbox" button reads the requests.
from fastapi import APIRouter, HTTPException

from database.db import get_db
from schemas.collaboration import CreateCollabDTO, UpdateCollabDTO, InboxItemOut, OutboxItemOut

router = APIRouter(prefix="/api/v1", tags=["Collaborations"])


def user_exists(db, user_id: int) -> bool:
    return db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is not None


# Collaborate page: one user sends a request to another
@router.post("/collaborations", status_code=201)
def send_request(collab: CreateCollabDTO):
    if collab.sender_id == collab.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot collaborate with yourself")

    with get_db() as db:
        if not user_exists(db, collab.sender_id) or not user_exists(db, collab.receiver_id):
            raise HTTPException(status_code=404, detail="User not found")

        cursor = db.execute(
            "INSERT INTO collaborations (sender_id, receiver_id, message) VALUES (?, ?, ?)",
            (collab.sender_id, collab.receiver_id, collab.message),
        )
        new_id = cursor.lastrowid

    return {"message": "Request sent", "id": new_id}


# Inbox button: everything that was sent TO this user, newest first.
# JOIN pulls the sender's name out of the users table so the page can show "from Lerato".
@router.get("/inbox/{user_id}", response_model=list[InboxItemOut])
def get_inbox(user_id: int):
    with get_db() as db:
        if not user_exists(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")

        rows = db.execute(
            """
            SELECT c.id, c.sender_id, u.fullname AS sender_name,
                   c.message, c.status, c.created_at
            FROM collaborations c
            JOIN users u ON u.id = c.sender_id
            WHERE c.receiver_id = ?
            ORDER BY c.id DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


# Accept or decline a request from the inbox
@router.patch("/collaborations/{collab_id}")
def answer_request(collab_id: int, update: UpdateCollabDTO):
    with get_db() as db:
        cursor = db.execute(
            "UPDATE collaborations SET status = ? WHERE id = ?",
            (update.status, collab_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Request not found")
    return {"message": f"Request {update.status}"}


# Requests this user has SENT (so the Collaborate page can show "waiting for reply")
@router.get("/outbox/{user_id}", response_model=list[OutboxItemOut])
def get_outbox(user_id: int):
    with get_db() as db:
        if not user_exists(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")

        rows = db.execute(
            """
            SELECT c.id, c.receiver_id, u.fullname AS receiver_name,
                   c.message, c.status, c.created_at
            FROM collaborations c
            JOIN users u ON u.id = c.receiver_id
            WHERE c.sender_id = ?
            ORDER BY c.id DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


# remove a request (clear it from the inbox, or cancel one you sent)
@router.delete("/collaborations/{collab_id}", status_code=204)
def delete_request(collab_id: int):
    with get_db() as db:
        cursor = db.execute("DELETE FROM collaborations WHERE id = ?", (collab_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Request not found")
