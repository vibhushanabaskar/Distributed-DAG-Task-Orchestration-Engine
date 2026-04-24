from fastapi import FastAPI, UploadFile, File
from core.db.database import Base, engine
# FIX 1: Import models so SQLAlchemy knows they exist
from core.db import models 
# FIX 2: Correct import path since file is in 'routes' folder
from routes.dag_routes import router as dag_router 
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI(title="DAG Orchestrator API")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Later you can restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create the tables in the database
Base.metadata.create_all(bind=engine)

# FIX 3: Register the endpoints
app.include_router(dag_router)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_path": file_location}

@app.get("/health")
def health():
    return {"status": "API running"}