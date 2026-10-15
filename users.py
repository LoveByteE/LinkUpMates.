# routes/users.py
# Everything to do with users: register, list, login, update.
import sqlite3
from fastapi import APIRouter, HTTPException

from database.db import get_db
from schemas.user import CreateUserDTO, UpdateUserDTO, LoginDTO, UserOut
from utils.security import hash_password, verify_password

# prefix means every route below starts with /api/v1/users
router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
def get_users():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, fullname, email, location, age FROM users"
        ).fetchall()
    return [dict(row) for row in rows]


# login is declared before "/{user_id}" so FastAPI never mistakes the word "login" for an id.
# It is a POST because we are sending a password in the body, not the URL.
@router.post("/login")
def login(credentials: LoginDTO):
    with get_db() as db:
        row = db.execute(
            "SELECT id, fullname, password FROM users WHERE email = ?",
            (credentials.email,),
        ).fetchone()

    # same error for "no such email" and "wrong password" so we don't leak which emails exist
    if row is None or not verify_password(credentials.password, row["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": row["id"], "fullname": row["fullname"]}


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with get_db() as db:
        row = db.execute(
            "SELECT id, fullname, email, location, age FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


@router.post("", status_code=201, response_model=UserOut)
def create_user(user: CreateUserDTO):
    try:
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO users (fullname, email, password, location, age) VALUES (?, ?, ?, ?, ?)",
                (user.fullname, user.email, hash_password(user.password), user.location, user.age),
            )
            new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # the email column is UNIQUE, so a duplicate email lands here
        raise HTTPException(status_code=409, detail="Email already registered")

    return {"id": new_id, "fullname": user.fullname, "email": user.email,
            "location": user.location, "age": user.age}


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UpdateUserDTO):
    # exclude_unset=True keeps only the fields the client actually sent
    changes = user.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Nothing to update")

    if "password" in changes:
        changes["password"] = hash_password(changes["password"])

    # build "fullname = ?, age = ?" from whatever fields were sent
    # (the column names come from our own schema, not from the user, so this is safe)
    set_part = ", ".join(f"{column} = ?" for column in changes)
    values = list(changes.values()) + [user_id]

    try:
        with get_db() as db:
            cursor = db.execute(f"UPDATE users SET {set_part} WHERE id = ?", values)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            row = db.execute(
                "SELECT id, fullname, email, location, age FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")

    return dict(row)


# Delete account.
# Other tables point at this user (foreign keys), so we delete those rows first,
# otherwise SQLite refuses to delete the user.
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    with get_db() as db:
        if db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="User not found")

        db.execute("DELETE FROM collaborations WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
        db.execute("DELETE FROM talents WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
