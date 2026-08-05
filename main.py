from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine, select

app = FastAPI()
# database setup 
class Task(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    title:str
    done:bool=False

engine=create_engine("sqlite:///tasks.db")

def get_session():
    with Session(engine)as session:
        yield session


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if not existing:
            session.add_all([
                Task(title="Buy milk", done=False),
                Task(title="Walk the dog", done=False),
                Task(title="Finish assignment", done=True),
            ])
            session.commit()

# INITIAL_TASKS = [
#     {"id": 1, "title": "Buy milk", "done": False},
#     {"id": 2, "title": "Walk the dog", "done": False},
#     {"id": 3, "title": "Finish assignment", "done": True},
# ]

# tasks = [t.copy() for t in INITIAL_TASKS]

class TaskCreate(BaseModel):
    title: str
class TaskUpdate(BaseModel):
    title: str = ""
    done: bool = False

@app.get("/tasks", summary="List all tasks")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(Task)

    if done is not None:
        query = query.where(Task.done == done)

    if search:
        query = query.where(Task.title.contains(search))

    return session.exec(query).all()

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    new_task = Task(title=task.title, done=False)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if not update.title.strip():
                raise HTTPException(status_code=400, detail="Title cannot be empty")
            task["title"] = update.title
            task["done"] = update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.get("/stats", summary="Get task statistics")
def get_stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }
@app.post("/reset", summary="Reset tasks to initial seed data")
def reset_tasks():
    global tasks
    tasks = [t.copy() for t in INITIAL_TASKS]
    return {"message": "Tasks reset to initial data", "tasks": tasks}