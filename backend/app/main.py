from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pathlib import Path
from datetime import datetime
import uuid

from .config import settings

app = FastAPI(title="Gas Station MVP", version="0.1.0")

# CORS: for now allow localhost ports we might use
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (later)
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), tenant: str = "default"):
    # very basic content-type guard; we’ll refine later
    allowed = {
        "image/jpeg", "image/png", "application/pdf", "image/webp", "image/tiff"
    }
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported type: {file.content_type}")

    # path: data/{tenant}/{YYYY}/{MM}/{doc_id}/original.ext
    now = datetime.utcnow()
    doc_id = str(uuid.uuid4())
    ext = (Path(file.filename).suffix or "").lower()
    dest_dir = settings.DATA_DIR / tenant / f"{now:%Y}" / f"{now:%m}" / doc_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"original{ext if ext else ''}"

    # stream save
    logger.info(f"Saving upload -> {dest_file}")
    with dest_file.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)

    # return a tiny receipt; we’ll add DB + OCR later
    return {
        "doc_id": doc_id,
        "tenant": tenant,
        "filename": file.filename,
        "stored_path": str(dest_file),
        "mime": file.content_type,
        "upload_ts": now.isoformat() + "Z",
    }
