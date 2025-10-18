from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE = os.environ["SUPABASE_SERVICE_ROLE"]
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

class TaskIn(BaseModel):
    title: str

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/tasks")
def list_tasks():
    data = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
    return data.data

@app.post("/tasks")
def create_task(task: TaskIn):
    data = supabase.table("tasks").insert({"title": task.title}).execute()
    if not data.data:
        raise HTTPException(500, "No se pudo crear")
    return data.data[0]

@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: str):
    row = supabase.table("tasks").select("is_done").eq("id", task_id).single().execute().data
    if not row:
        raise HTTPException(404, "No existe")
    new_val = not row["is_done"]
    data = supabase.table("tasks").update({"is_done": new_val}).eq("id", task_id).execute()
    return data.data[0]
