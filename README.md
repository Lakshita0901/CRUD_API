CRUD Task API — SQLite → PostgreSQL (Dockerized)

A Task Management REST API built with FastAPI and SQLModel. This project has evolved across three stages:

Assignment 1 — in-memory task list (no persistence)
Assignment 2 — SQLite database (local file-based persistence)
Assignment 3 (this update) — PostgreSQL running in Docker, with the whole stack (app + database) started via a single docker compose up command

At every stage, the API surface has never changed — same endpoints, same status codes, same response shapes. Only the storage layer underneath was swapped, proving that a well-layered API doesn't need to care what database sits behind it.

Why PostgreSQL + Docker (this stage)

SQLite was great for learning the basics of persistence, but it has real limitations: it doesn't run as a standalone server, doesn't handle concurrent writes well, and isn't how real production backends are typically deployed.

This stage moves to PostgreSQL, containerized with Docker, because:

Matches real-world backend setups — most production APIs talk to a client-server database like Postgres, not a single file.
Docker removes "works on my machine" problems — anyone cloning this repo gets the exact same database version and config, with zero manual Postgres installation.
docker compose up starts the entire stack — the API and the database boot together, wired to talk to each other automatically.
Data persists in a Docker volume, independent of the containers themselves — containers can be destroyed and recreated, and the data survives.
What changed vs. the SQLite version

Nothing changed in the service or route logic. Every endpoint — GET /tasks, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}, GET /stats, POST /reset — is byte-for-byte the same code as the SQLite version.

The only things that changed:

The connection string — create_engine("sqlite:///tasks.db") became create_engine(os.getenv("DATABASE_URL")), reading a Postgres URL from environment variables instead of a hardcoded SQLite path.
The database itself — now runs as a Postgres container instead of a local file.
Table creation — in addition to SQLModel's automatic create_all(), an explicit init.sql script was added so the table and seed data can also be created via raw SQL on first container startup (per the assignment requirement).

This is the proof the assignment asks for: swapping the entire storage backend was a one-line change to the connection string, not a rewrite of the application.

Tech Stack
Layer	Technology
API Framework	FastAPI
Data validation	Pydantic
ORM / DB layer	SQLModel
Database	PostgreSQL 16
Containerization	Docker + Docker Compose
Server	Uvicorn
Project Structure
CRUDapi/
├── main.py               # FastAPI app, database model, and all endpoints (unchanged logic)
├── init.sql               # SQL script that creates the `task` table and seeds 3 example tasks
├── Dockerfile              # Builds the FastAPI app into a container image
├── docker-compose.yml       # Defines and wires together the app + db services
├── requirements.txt         # Python dependencies
├── .env                    # Local environment variables (gitignored, holds DATABASE_URL)
├── .env.example             # Committed template showing required env vars
├── .dockerignore
├── .gitignore
└── README.md               # This file
How to run this project
1. Clone the repository
bash
git clone https://github.com/Lakshita0901/CRUD_API
cd CRUDapi
2. Set up environment variables

Copy the example file and adjust if needed (the defaults work out of the box for local development):

bash
cp .env.example .env

.env.example contains:

env
DATABASE_URL=postgresql://postgres:postgres@db:5432/tasksdb

Note: the host here is db, not localhost — this matches the service name defined in docker-compose.yml, which Docker's internal network uses to let the app container find the db container.

3. Start the whole stack

Make sure Docker Desktop is running, then:

bash
docker compose up

This single command:

Builds the FastAPI app image (if not already built)
Starts a PostgreSQL 16 container with a persistent volume (pgdata)
Waits for Postgres to report healthy before starting the app (via a healthcheck)
Runs init.sql automatically on first startup to create the task table and seed 3 example tasks
Starts the FastAPI app, connected to Postgres over Docker's internal network
4. Explore the API
http://127.0.0.1:8000/docs

(Note: use 127.0.0.1, not 0.0.0.0 — the latter only makes sense from inside the container.)

5. Stop the stack
bash
docker compose down

This stops and removes the containers, but not the pgdata volume — your data is preserved for next time. To wipe the data completely and start fully fresh (e.g. to re-test the SQL init script), use:

bash
docker compose down -v
API Endpoints
Method	Endpoint	Description
GET	/tasks	List all tasks (supports ?done= and ?search= filters)
GET	/tasks/{id}	Get a single task by ID
POST	/tasks	Create a new task
PUT	/tasks/{id}	Update an existing task
DELETE	/tasks/{id}	Delete a task
GET	/stats	Get task statistics (total / done / open)
POST	/reset	Reset the database back to the 3 seed tasks
GET	/health	Health check

Status codes are unchanged from earlier assignments: 201 on create, 204 on delete, 400 for invalid input, 404 for unknown ids.

Table creation — SQL init script

Instead of relying only on SQLModel's Python-based create_all(), the task table is also defined explicitly in init.sql:

sql
CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO task (title, done)
SELECT * FROM (VALUES
    ('Buy milk', FALSE),
    ('Walk the dog', FALSE),
    ('Finish assignment', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM task);

This file is mounted into Postgres's official auto-init folder (/docker-entrypoint-initdb.d/) via docker-compose.yml. Postgres runs any .sql file found there automatically, but only the first time it starts against a completely empty volume — on every subsequent startup, it detects existing data and skips re-running it. This was verified directly:

bash
docker compose logs db

showed the line:

running /docker-entrypoint-initdb.d/init.sql

on a fresh volume, and

PostgreSQL Database directory appears to contain a database; Skipping initialization

on a volume that already had data — confirming the script only seeds once.

Persistence check — how it was verified

This is the core requirement of the assignment: proving that data survives not just an app restart, but a full container restart.

Steps taken:

Started the stack with docker compose up.
Created a new task via POST /tasks:
json
   { "title": "final persistence check" }

Response confirmed 201 and id: 4. 3. Verified it existed via GET /tasks — 4 tasks total. 4. Fully stopped and removed both containers:

bash
   docker compose down
Restarted the stack from scratch:
bash
   docker compose up
Called GET /tasks again.

Result: all 4 tasks — including "final persistence check" — were still present, even though both the app and db containers had been completely destroyed and recreated in between. This confirms the data lives in the named Docker volume (pgdata), not in the containers themselves, satisfying the persistence requirement.

Honesty note on the "repository" requirement

The assignment asks for "a Postgres repository implementing the same interface as your in-memory one." This project does not have a formally separated repository class with an explicit interface — instead, SQLModel's Session object is used directly inside each route (the same pattern used in the SQLite version). What did stay constant, and what genuinely proves the architecture:

Every route function signature, validation rule, and response shape is unchanged from the SQLite version.
The only code that changed to move from SQLite → Postgres was the single line building engine from DATABASE_URL.

So while there isn't a dedicated repository abstraction layer, the practical outcome the assignment is testing for — that swapping storage backends requires touching only one line, not the routes — was fully demonstrated.

Previous stage: SQLite version

For reference, the earlier SQLite-based version of this project (Assignment 2) is preserved in git history / an earlier commit. It used:

tasks.db, a local SQLite file, auto-created on first run
The same endpoints and validation rules as this version
DB Browser for SQLite for manual inspection

That version's persistence was proven by restarting the local uvicorn server (not a container) and confirming tasks survived — the same principle applied here at the container level instead.