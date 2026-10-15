# LinkupMates_backend

FastAPI + SQLite backend for the LinkupMates landing page.

## Run it
    python -m venv .venv
    .venv\Scripts\activate          (Windows)
    pip install -r requirements.txt
    uvicorn app:app --reload

Then open:
- http://127.0.0.1:8000/        landing page (static/index.html)
- http://127.0.0.1:8000/docs    interactive API docs, use this to test every route

## Folders
- app.py        creates the app and plugs in the routers
- database/     SQLite connection + table creation
- schemas/      Pydantic DTOs (what data comes in / goes out)
- routes/       one file per feature (pages, users, concepts, contact, collaborations, talents)
- utils/        password hashing
- static/       the HTML site

## Endpoints
| Verb  | URL                     | What it does                          |
|-------|-------------------------|---------------------------------------|
| GET   | /                       | landing page                          |
| GET   | /api/v1/concepts        | the 4 concept cards                   |
| GET   | /api/v1/concepts/{id}   | one concept                           |
| POST  | /api/v1/users           | register (Register button / sign up)  |
| POST  | /api/v1/users/login     | login                                 |
| GET   | /api/v1/users           | list users                            |
| GET   | /api/v1/users/{id}      | one user                              |
| PATCH | /api/v1/users/{id}      | update some fields of a user          |
| DELETE| /api/v1/users/{id}      | delete account (and its requests/talent) |
| POST  | /api/v1/collaborations  | Collaborate page: send a request      |
| GET   | /api/v1/inbox/{user_id} | Inbox button: requests sent to a user |
| PATCH | /api/v1/collaborations/{id} | accept / decline a request        |
| DELETE| /api/v1/collaborations/{id} | remove / cancel a request         |
| GET   | /api/v1/outbox/{user_id}| requests this user sent               |
| GET   | /api/v1/talents         | Find Talent (?category=Photography)   |
| GET   | /api/v1/talents/{id}    | one talent                            |
| POST  | /api/v1/talents         | Become Talent                         |
| DELETE| /api/v1/talents/{id}    | stop being listed                     |
| POST  | /api/v1/contact         | Contact Us form                       |
| GET   | /api/v1/contact         | read saved messages                   |
| DELETE| /api/v1/contact/{id}    | delete a saved message                |

## Status codes used
201 created, 204 deleted (no body), 400 nothing to update, 401 wrong login, 404 not found,
409 email already registered, 422 bad data (automatic from Pydantic).

See EXPLANATION.md for a walkthrough of how everything fits together.
If you ran an older version, delete linkupmates.db once so it is rebuilt (or just restart; the new table is added automatically).
