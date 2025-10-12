import os
import json
from pathlib import Path
import sqlite3
from pydantic import Field, BaseModel
from datetime import datetime

DB_PATH = "database/notes.db"
NOTES_DIR = "Knowbases/base1/"
class Assetlocation(BaseModel):
    lecture_location : str = Field(description="lecture file location",default="")
    flashcards_location : str = Field(description="flashcards file location",default="")
    mindmap_location : str = Field(description="mindmap file location",default="")
class metadata(BaseModel):
    id : str  = Field(description="note id")
    parent_id : str = Field(description= "parent ID")
    title : str = Field(description="title of note")
    children : list[str] = Field(default_factory=list, description="sub notes")
    assets_location : Assetlocation = Field(description="assets location class")
    created_At : datetime  = Field(description="creation Date")
    update_At : datetime  = Field(description="edit Date")
    tags : list[str] = Field(default_factory=list, description="list of tags")

       
# Utility helpers
def ensure_dirs():
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs("database", exist_ok=True)

def now():
    return datetime.now().isoformat()


# =========================================================
# 1️⃣ Create Note
# =========================================================
def create_note(note_id,title:str, parent_id=None):
    """
    Make folder + files (note.html, assets/, meta.json)
    """
    path = os.path.join(NOTES_DIR, note_id)
    assets_path = os.path.join(path, "assets")

    os.makedirs(assets_path, exist_ok=True)
    # Write meta.json
    meta = metadata(
        id=note_id,parent_id=parent_id,children=[],title=title,
        assets_location=Assetlocation(flashcards_location="",lecture_location="",mindmap_location=""),
        created_At=datetime.now(),update_At=datetime.now(),tags=[])
   
    with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as f:
        f.write(meta.model_dump_json())



# =========================================================
# 3️⃣ Link Notes
# =========================================================
def link_notes(parent_id, child_id):
    """
    Update meta.json files to link parent/child
    """
    parent_meta = load_meta(parent_id)
    child_meta = load_meta(child_id)

    parent_meta.children.append(child_id)
    child_meta.parent_id = parent_id

    save_meta(parent_id, parent_meta)
    save_meta(child_id, child_meta)

def load_meta(note_id) ->metadata:
    path = os.path.join(NOTES_DIR, note_id, "meta.json")
    path = path.replace("\\", "/")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return metadata.model_validate_json(f.read())
    except FileNotFoundError:
        print(f"Meta file not found for note_id: {note_id}")

def save_meta(note_id,  meta : metadata):
    path = os.path.join(NOTES_DIR, note_id, "meta.json")
    path = path.replace("\\", "/")
    meta.update_At = now()
    with open(path, "w", encoding="utf-8") as f:
        f.write(meta.model_dump_json(indent= 2))


# =========================================================
# 4️⃣ Scan / Sync
# =========================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT,
            path TEXT,
            parent_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def sync_to_db():
    """
    Read all meta.json and update the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for root, dirs, files in os.walk(NOTES_DIR):
        if "meta.json" in files:
            meta_path = os.path.join(root, "meta.json")
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            c.execute("""
                INSERT OR REPLACE INTO notes
                (id, title, path, parent_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                meta["id"], meta["title"], root, meta["parent_id"],
                meta["created_at"], meta["updated_at"]
            ))

    conn.commit()
    conn.close()


# =========================================================
# 5️⃣ Browse / Search
# =========================================================
def list_notes():
    """
    Simple printout of all notes in DB.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in c.execute("SELECT id, title FROM notes ORDER BY created_at DESC"):
        print(f"{row[0]}  →  {row[1]}")
    conn.close()


# =========================================================
# 6️⃣ Edit / Update
# =========================================================
def edit_note_title(note_id, new_title):
    """
    Update title both in meta.json and DB.
    """
    meta = load_meta(note_id)
    meta["title"] = new_title
    save_meta(note_id, meta)
    sync_to_db()  # keep DB consistent


# =========================================================
# 7️⃣ (Optional) Sync Cloud
# =========================================================
def sync_cloud():
    """
    Placeholder for cloud upload/download logic.
    """


# =========================================================
# 8️⃣ (Optional) Add AI/Graph/History
# =========================================================
def build_graph():
    """
    Placeholder for note relationship graph or AI embeddings.
    """

import shutil

# =========================================================
# 9️⃣ Delete Note (with all children)
# =========================================================
def delete_note(note_id):
    """
    Delete a note and all its children recursively.
    Removes folders, meta.json and updates parent note.
    """
    meta = load_meta(note_id)
    try:
    # Recursively delete children first
        for child_id in meta.children:
            delete_note(child_id)
            # Delete from filesystem
        note_path = Path(NOTES_DIR) / note_id
        if os.path.exists(note_path):
            shutil.rmtree(note_path)

    # Update parent if exists
        parent_id = meta.parent_id
        if parent_id:
            parent_meta = load_meta(parent_id)
            parent_meta.children = [c for c in parent_meta.children if c != note_id]
            save_meta(parent_id, parent_meta)
    except Exception as e:
        print(f"Error deleting note '{note_id}': {e}")

    print(f"❌ Note '{note_id}' and all subnotes deleted.")
