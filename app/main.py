import streamlit as st
from supabase import create_client
import os

# Lee secrets (en Streamlit Cloud usarás Settings -> Secrets)
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(page_title="Tasks Cloud", page_icon="✅", layout="centered")
st.title("Tasks Cloud (Streamlit + Supabase)")

# Crea tabla si no existe (opcional: puedes crearla en Supabase SQL Editor)
def ensure_table():
    try:
        # Si falla, ignora silencioso (ya existe)
        supabase.table("tasks").select("id").limit(1).execute()
    except Exception:
        st.error("Crea la tabla 'tasks' en Supabase:\n"
                 "id uuid pk default gen_random_uuid(), "
                 "title text not null, is_done boolean default false, created_at timestamptz default now()")

ensure_table()

# Form para crear tarea
with st.form("new_task", clear_on_submit=True):
    title = st.text_input("Nueva tarea", placeholder="Ej. Preparar demo Cloud ☁️")
    submitted = st.form_submit_button("Agregar")
    if submitted and title.strip():
        supabase.table("tasks").insert({"title": title.strip()}).execute()
        st.success("Tarea agregada ✅")

# Listado
res = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
tasks = res.data or []

for t in tasks:
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        toggled = st.checkbox("", value=t["is_done"], key=t["id"])
    with col2:
        st.write("~~" + t["title"] + "~~" if toggled else t["title"])

    # Si el user cambió el checkbox, actualiza
    if toggled != t["is_done"]:
        supabase.table("tasks").update({"is_done": toggled}).eq("id", t["id"]).execute()
        st.rerun()
