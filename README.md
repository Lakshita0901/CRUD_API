CRUD Task API — SQLite Edition
A simple Task Management REST API built with FastAPI and SQLModel, backed by a SQLite database. This is a continuation of the original in-memory CRUD API (Assignment 1) — the API surface is identical, but task data now persists in a real database instead of disappearing every time the server restarts.
---
Why SQLite
SQLite was chosen for this project because it's the simplest possible way to add real persistence to a small backend project:
No separate database server required — no install, no background service, no connection setup beyond a file path.
Single file storage — the entire database lives in one `.db` file, making it trivial to inspect, back up, or reset.
Zero configuration — the database and table are created automatically the first time the app runs.
Perfect for learning and small projects — it demonstrates exactly how an API talks to a database, without the overhead of running Postgres/MySQL locally.
For a project this size — a single-table task manager — SQLite gives full persistence with none of the operational overhead of a client-server database.
---
Where the database is stored
The database file is named `tasks.db`.
It lives in the project root directory (same folder as `main.py`).
It is created automatically the first time the application starts — there is no manual setup step.
Inside it, task data is stored in a table (SQLModel auto-generates the table name from the model class, so it is created as `task`).
On first run, if the table is empty, three example tasks are seeded automatically:
Buy milk
Walk the dog
Finish assignment (done)
This seeding logic only runs once — subsequent restarts detect existing data and skip re-inserting the seed tasks.
---
Tech Stack
Layer	Technology
API Framework	FastAPI
Data validation	Pydantic
ORM / DB layer	SQLModel
Database	SQLite
Server	Uvicorn
---
How to run this project
1. Clone the repository
```bash
git clone <https://github.com/Lakshita0901/CRUD_API>
cd CRUDapi
```
2. Create and activate a virtual environment
```bash
python -m venv env
env\Scripts\activate      # Windows (PowerShell)
# source env/bin/activate # macOS/Linux
```
3. Install dependencies
```bash
pip install fastapi uvicorn sqlmodel
```
4. Run the server
```bash
uvicorn main:app --reload
```
The server starts at `http://127.0.0.1:8000`. On this first run, `tasks.db` is created automatically along with the 3 seed tasks — no manual database setup needed.
5. Explore the API
Interactive API docs (Swagger UI) are available at:
```
http://127.0.0.1:8000/docs
```
---
API Endpoints
Method	Endpoint	Description
GET	`/`	API info
GET	`/health`	Health check
GET	`/tasks`	List all tasks (supports `?done=` and `?search=` filters)
GET	`/tasks/{id}`	Get a single task by ID
POST	`/tasks`	Create a new task
PUT	`/tasks/{id}`	Update an existing task
DELETE	`/tasks/{id}`	Delete a task
GET	`/stats`	Get task statistics (total / done / open)
POST	`/reset`	Reset the database back to the 3 seed tasks
All CRUD behavior — status codes, validation rules, and response shapes — is unchanged from the original in-memory version. Only the storage layer changed: data now lives in SQLite instead of a Python list, and survives server restarts.
---
Exploring the database directly
The database can be opened and inspected with DB Browser for SQLite:
Open DB Browser for SQLite.
File → Open Database → select `tasks.db` from the project folder.
Go to Browse Data to view rows visually, or Execute SQL to run raw queries.
Screenshot
![Database viewer showing the task table](./Screenshot.png)
Example SQL query executed
```sql
SELECT * FROM task WHERE done = 1;
```
This returns every task currently marked as completed — directly from the database file, independent of the running API.
One useful thing observed while testing: any change made directly in DB Browser (e.g. running `UPDATE task SET done = 1;` and clicking Write Changes) is immediately reflected by the API on the next request — no restart needed. This confirms the API and the database file are the same single source of truth.
---
Persistence check
To verify persistence:
Create a task via `POST /tasks`.
Stop the server (Ctrl+C).
Restart it with `uvicorn main:app --reload`.
Call `GET /tasks` again.
The task created before the restart is still present — proving data now survives restarts, unlike the original in-memory version.
---
Project Structure
```
CRUDapi/
├── main.py         # FastAPI app, database model, and all endpoints
├── tasks.db         # SQLite database file (auto-created on first run)
├── README.md        # This file
└── .gitignore
```