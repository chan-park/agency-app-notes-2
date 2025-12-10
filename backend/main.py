from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import SessionLocal, engine, Base
from models import Note, NoteCreate, NoteUpdate
import crud

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes API",
    description="A simple note-taking API with CRUD operations",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {"message": "Notes API", "version": "1.0.0"}

@app.get("/notes", response_model=List[Note])
async def get_notes(skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    """
    Retrieve all notes with optional search functionality
    
    - **skip**: Number of notes to skip (for pagination)
    - **limit**: Maximum number of notes to return
    - **search**: Optional search term to filter notes by title
    """
    notes = crud.get_notes(db, skip=skip, limit=limit, search=search)
    return notes

@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Get a specific note by ID
    
    - **note_id**: The ID of the note to retrieve
    """
    note = crud.get_note(db, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.post("/notes", response_model=Note, status_code=201)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """
    Create a new note
    
    - **title**: The title of the note
    - **body**: The content/body of the note
    """
    return crud.create_note(db=db, note=note)

@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """
    Update an existing note
    
    - **note_id**: The ID of the note to update
    - **title**: Updated title (optional)
    - **body**: Updated body content (optional)
    """
    db_note = crud.update_note(db, note_id=note_id, note=note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note by ID
    
    - **note_id**: The ID of the note to delete
    """
    success = crud.delete_note(db, note_id=note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)