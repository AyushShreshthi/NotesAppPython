# Notes Application Backend

FastAPI + PostgreSQL backend with JWT authentication and soft-deletable notes.

## Project Structure

```
app/
├── main.py              # App entrypoint, router registration, global error handling
├── database.py          # Engine, SessionLocal, Base, get_db dependency
├── dependencies.py      # get_current_user (JWT -> DB user)
├── core/
│   ├── config.py        # Settings loaded from .env
│   └── security.py      # Password hashing + JWT encode/decode
├── models/               # SQLAlchemy ORM models (tables)
│   ├── user.py
│   └── note.py
├── schemas/              # Pydantic request/response models
│   ├── user.py
│   └── note.py
├── services/              # Business logic, separate from route handlers
│   ├── auth_service.py
│   └── note_service.py
└── routes/                # Thin controllers: validate input, call service, return response
    ├── auth.py
    ├── users.py
    └── notes.py
```

**Why split like this?** Routes stay thin (HTTP concerns only). Services hold business
logic and can be reused or unit-tested without spinning up FastAPI. Models define the
database shape; schemas define the API contract — keeping them separate means you can
change your DB structure without automatically exposing it over the API.

## Setup

1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE notes_db;
   ```

2. Copy `.env.example` to `.env` and fill in real values:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/notes_db
   SECRET_KEY=<generate with: openssl rand -hex 32>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app (tables auto-create on startup via `Base.metadata.create_all`):
   ```
   uvicorn app.main:app --reload
   ```

5. Open interactive docs at `http://localhost:8000/docs`.

> For production, replace `create_all` with proper Alembic migrations:
> `alembic init alembic`, configure `alembic/env.py` to import `Base` and `settings.DATABASE_URL`,
> then `alembic revision --autogenerate -m "init"` and `alembic upgrade head`.

## API Flow

1. **POST /auth/signup** — user registers with name/email/password. Password is hashed
   with bcrypt before storage; the plain password is never saved.
2. **POST /auth/login** — credentials are verified against the stored hash. On success,
   a JWT is issued containing the user's id (`sub` claim) and an expiry.
3. **GET /users/me** — protected route. The client sends `Authorization: Bearer <token>`.
   `get_current_user` decodes the JWT, loads the user from the DB, and injects it into
   the route — if the token is missing, invalid, or expired, a 401 is returned automatically.
4. **Notes CRUD** — all notes routes require the same JWT dependency, and every query
   filters by `owner_id`, so users can only see/edit/delete their own notes.
   - **Create**: inserts a row.
   - **List**: paginated via `page` and `page_size` query params, excludes rows where
     `deleted_at IS NOT NULL`.
   - **Get by id / Update**: 404 if not found, not owned by the caller, or soft-deleted.
   - **Delete**: sets `deleted_at = now()` instead of removing the row (soft delete) and
     returns `204 No Content`.

## Testing with Postman

Import `postman_collection.json`. It defines collection variables `base_url` and
`auth_token`. Run requests in order:

`Signup -> Login -> Get Profile -> Create Note -> Get Notes -> Get Note By ID -> Update Note -> Delete Note`

The **Login** request has a test script that automatically captures `access_token` from
the response into the `auth_token` variable, and **Create Note** captures the new note's
id into `note_id` — so every subsequent request is pre-wired with no manual copy/paste.
