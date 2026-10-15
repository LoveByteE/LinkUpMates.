# LinkupMates_backend: how it works

## 1. The big picture
The website (HTML) is what people see. The backend is a separate program that keeps the data.
They talk over HTTP:

    browser (HTML + fetch)  --request-->  FastAPI  --SQL-->  SQLite file (linkupmates.db)
    browser (HTML + fetch)  <--JSON------  FastAPI  <--rows--  SQLite file

- GET  = "give me data" (read)
- POST = "here is new data, save it" (create)
- PATCH = "change part of something that already exists" (update)
- DELETE = "remove this"

Data travels as JSON. FastAPI turns JSON into Python objects and back for us.

## 2. What each button on the site needs
| On the site                   | Request                              | Table              |
|-------------------------------|--------------------------------------|--------------------|
| Landing page                  | GET /                                | none (HTML file)   |
| Our Concepts cards            | GET /api/v1/concepts                 | concepts           |
| Register                      | POST /api/v1/users                   | users              |
| (logging in)                  | POST /api/v1/users/login             | users              |
| Collaborate                   | POST /api/v1/collaborations          | collaborations     |
| Inbox                         | GET /api/v1/inbox/{user_id}          | collaborations+users |
| Accept / decline in the inbox | PATCH /api/v1/collaborations/{id}    | collaborations     |
| Contact Us                    | POST /api/v1/contact                 | contact_messages   |
| Find Talent (nav)             | GET /api/v1/talents?category=...     | talents+users      |
| Become Talent (nav)           | POST /api/v1/talents                 | talents            |
| Stop being listed             | DELETE /api/v1/talents/{id}          | talents            |
| Sent requests (Collaborate)   | GET /api/v1/outbox/{user_id}         | collaborations+users |
| Clear / cancel a request      | DELETE /api/v1/collaborations/{id}   | collaborations     |
| Delete my account             | DELETE /api/v1/users/{id}            | users (+ related rows) |
| Admin: remove a message       | DELETE /api/v1/contact/{id}          | contact_messages   |

The concept pages (maximalism.html etc.) and the four art categories are plain pages, so they
need no routes of their own: the browser just loads the file from /static.

## 3. The files, one by one
**app.py**: starts everything.
- `FastAPI(...)` creates the app.
- `lifespan` runs `init_db()` once at startup so the tables always exist.
- `CORSMiddleware` lets the browser call the API even if the HTML was opened from another place.
- `include_router(...)` plugs in each routes file. `mount("/static", ...)` serves the HTML/CSS files.

**database/db.py**: all the SQLite code.
- `get_db()` opens the database, hands it to a route, then commits (saves) if all went well
  or rolls back (undoes) if something failed. It also turns foreign keys ON, because SQLite
  ignores them by default.
- `init_db()` creates 4 tables with `CREATE TABLE IF NOT EXISTS` and puts the 4 concepts in the
  concepts table the first time only.

Tables:
- users(id, fullname, email UNIQUE, password, location, age)
- concepts(id, title, tagline, image_url, page)
- contact_messages(id, name, email, message, created_at)
- collaborations(id, sender_id -> users.id, receiver_id -> users.id, message, status, created_at)
- talents(id, user_id -> users.id, category, bio, created_at), UNIQUE(user_id, category)

`sender_id` and `receiver_id` are foreign keys: they must match a real user, so the database
itself refuses a request from or to someone who doesn't exist.

**schemas/**: Pydantic classes that describe the JSON we accept and return.
If the JSON doesn't match (missing field, age is "abc"), FastAPI answers 422 before our code runs.
`UserOut` has no password field, so a password can never be sent back by accident.
`UpdateCollabDTO` uses `Literal["accepted","declined"]` so no other status is allowed.

**utils/security.py**: `hash_password` / `verify_password` with bcrypt. We store only the hash.
Even if someone reads the database, they cannot read the passwords.

**routes/**: the endpoints, one file per feature.
- pages.py: `GET /` returns static/index.html.
- users.py: create (hash password, 409 if email exists), list, get one, login, patch.
- concepts.py: list and get one.
- contact.py: save a message, read messages.
- collaborations.py: send a request, read inbox and outbox, accept/decline, delete.
- talents.py: Find Talent (list, filter by category, get one), Become Talent (post), remove (delete).

## 4. Walk through one request: Collaborate
1. The collab page sends `POST /api/v1/collaborations` with `{"sender_id":1,"receiver_id":2,"message":"Photo shoot?"}`.
2. FastAPI checks it against `CreateCollabDTO`.
3. `send_request` refuses if sender and receiver are the same (400) or if either user is missing (404).
4. It runs `INSERT INTO collaborations ...` using `?` placeholders (this stops SQL injection).
5. `get_db()` commits, and we answer 201 with the new id.
6. Later, user 2 clicks Inbox: `GET /api/v1/inbox/2` runs a `JOIN` between collaborations and users
   to attach the sender's name, newest first, and returns it as JSON.

## 4b. Why these extra routes (and why DELETE)
The nav bar has "Find Talent" and "Become Talent", and the landing page lists four art
categories (Photography, Sculpture, Graphic Design, Fine Art). That is data, so it needs a table:
`talents` links a user to a category. "Find Talent" is a GET that JOINs talents with users (and
never selects the password), "Become Talent" is a POST. The category is a `Literal` in the schema,
so a made-up category gets a 422.

DELETE is used where a user would reasonably want something gone:
- delete a collaboration request (clear the inbox, cancel one you sent)
- stop being listed as talent
- delete your account
- remove a contact message

Deleting a user is the interesting one. collaborations and talents point at users with foreign
keys, so SQLite refuses to delete a user who is still referenced. The route therefore deletes
that user's collaborations and talents first, then the user, all inside one `get_db()` block.
If any step fails, everything is rolled back, so we never end up half-deleted.
DELETE answers 204 (success, no body). It answers 404 if the row doesn't exist.

I did not add DELETE for concepts: they are fixed site content, not something visitors manage.

## 5. Status codes used
200 ok, 201 created, 204 deleted, 400 bad request (e.g. nothing to update), 401 wrong login,
404 not found, 409 conflict (email already used), 422 invalid data (automatic).

## 6. Questions you may be asked
- *Why SQLite?* One file, no server to install, fine for a course project. Only db.py would change for another database.
- *Why `?` in the SQL?* Values are sent separately from the query, so user input can't change the query.
- *Why hash passwords?* Never store the real password. bcrypt adds a random salt, so the same password gives different hashes.
- *Why separate schemas from tables?* The table has a password column; the response schema doesn't.
- *Why PATCH and not PUT?* PATCH changes only the fields sent; PUT replaces the whole thing.
- *Why does deleting a user remove other rows too?* Foreign keys: other tables reference the user, so those rows are removed first.
- *Why 204 for DELETE?* The thing is gone, so there is nothing to send back.

## 7. Connecting the HTML (fetch examples)
Register:
    fetch("http://127.0.0.1:8000/api/v1/users", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({fullname, email, password, age: Number(age), location})
    }).then(r => r.json()).then(console.log);

Collaborate:
    fetch("/api/v1/collaborations", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({sender_id: 1, receiver_id: 2, message: "Photo shoot?"})
    });

Inbox:
    fetch("/api/v1/inbox/2").then(r => r.json()).then(items => console.log(items));

Concept cards:
    fetch("/api/v1/concepts").then(r => r.json()).then(list => console.log(list));

(If the page is served by FastAPI itself, the short `/api/v1/...` form works.)

Find Talent:
    fetch("/api/v1/talents?category=Photography").then(r => r.json()).then(console.log);

Become Talent:
    fetch("/api/v1/talents", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({user_id: 1, category: "Photography", bio: "Portraits and street"})
    });

Delete (note: no body comes back, so don't call r.json()):
    fetch("/api/v1/collaborations/3", {method: "DELETE"}).then(r => console.log(r.status)); // 204
