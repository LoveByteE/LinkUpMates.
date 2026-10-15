# database/db.py
# Everything to do with the SQLite database lives in this file.
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# the database is just a file that sits next to app.py
DB_PATH = Path(__file__).resolve().parent.parent / "linkupmates.db"


@contextmanager
def get_db():
    """Open a connection, hand it to the route, then save and close it.

    Usage inside a route:
        with get_db() as db:
            db.execute(...)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name: row["email"]
    conn.execute("PRAGMA foreign_keys = ON")  # sqlite ignores foreign keys unless we ask
    try:
        yield conn
        conn.commit()      # save changes if nothing went wrong
    except Exception:
        conn.rollback()    # undo changes if something broke
        raise
    finally:
        conn.close()


def init_db():
    """Create the tables (if they don't exist yet) and add the starter concepts."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname  TEXT NOT NULL,
                email     TEXT NOT NULL UNIQUE,
                password  TEXT NOT NULL,      -- stored as a bcrypt hash, never plain text
                location  TEXT,
                age       INTEGER NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                tagline      TEXT NOT NULL,
                image_url    TEXT,
                page         TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                email       TEXT NOT NULL,
                message     TEXT NOT NULL,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # a collaboration request is one user asking another user to work together.
        # The receiver sees it in their inbox.
        db.execute("""
            CREATE TABLE IF NOT EXISTS collaborations (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id    INTEGER NOT NULL REFERENCES users(id),
                receiver_id  INTEGER NOT NULL REFERENCES users(id),
                message      TEXT NOT NULL,
                status       TEXT NOT NULL DEFAULT 'pending',   -- pending / accepted / declined
                created_at   TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # "Become Talent": a user lists themselves under one of the art categories.
        # UNIQUE(user_id, category) stops the same person joining the same category twice.
        db.execute("""
            CREATE TABLE IF NOT EXISTS talents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                category    TEXT NOT NULL,      -- Photography / Sculpture / Graphic Design / Fine Art
                bio         TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, category)
            )
        """)

        # only fill the concepts table the first time
        count = db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        if count == 0:
            db.executemany(
                "INSERT INTO concepts (title, tagline, image_url, page) VALUES (?, ?, ?, ?)",
                [
                    ("Maximalism", "Bold. Vibrant. Unapologetic.",
                     "https://i.pinimg.com/1200x/be/92/29/be9229d9d0cbd16198192308958b9a93.jpg", "maximalism.html"),
                    ("Dadaism", "Absurd. Rebellious. Unpredictable",
                     "https://i.pinimg.com/1200x/83/06/0d/83060d34fb4189e3c3c4fab03a2da4af.jpg", "dadaism.html"),
                    ("Abstract", "Expressive. Interpretive. Boundless.",
                     "https://i.pinimg.com/736x/e9/2e/3b/e92e3b7b336ec3db147665fd34e11169.jpg", "abstract.html"),
                    ("Expressionism", "Emotion. Intensity. Truth.",
                     "https://i.pinimg.com/736x/ad/7b/8a/ad7b8a8c82eb922e897d5a41a32ce67f.jpg", "expressionism.html"),
                ],
            )

        # a database created earlier has Expressionism with no page, so fill it in
        db.execute("UPDATE concepts SET page = 'expressionism.html' WHERE title = 'Expressionism' AND page IS NULL")
