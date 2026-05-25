import os
import tempfile
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from utils.env_loader import load_project_env
from services.summary_service import SummaryService
from utils.pdf_handler import extract_text_from_pdf
from utils.url_extractor import extract_text_from_url

# Load environment configuration
load_project_env()
PORT = int(os.getenv("PORT", "8000"))

app = FastAPI(title="AI Content Summarizer API")

# Initialize the SummaryService
try:
    service = SummaryService()
except Exception as exc:
    print(f"Failed to start SummaryService: {exc}")
    service = None

# Input schemas for JSON requests
class TextSummaryRequest(BaseModel):
    text: str
    summary_style: str
    document_style: str

class UrlSummaryRequest(BaseModel):
    url: str
    summary_style: str
    document_style: str

# Serve index.html at root
@app.get("/")
def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Static assets are being created. Please refresh in a moment."}

@app.post("/api/summarize/text")
def summarize_text_endpoint(payload: TextSummaryRequest):
    if not service:
        raise HTTPException(status_code=500, detail="Database/AI services are unavailable.")
    
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")
    
    try:
        record = service.create_summary(
            source_type="text",
            source_content=text,
            summary_style=payload.summary_style,
            document_style=payload.document_style,
            title="",
        )
        return record
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/summarize/url")
def summarize_url_endpoint(payload: UrlSummaryRequest):
    if not service:
        raise HTTPException(status_code=500, detail="Database/AI services are unavailable.")
    
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    
    try:
        title, article_text = extract_text_from_url(url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to extract URL content: {exc}")
    
    try:
        record = service.create_summary(
            source_type="url",
            source_content=article_text,
            summary_style=payload.summary_style,
            document_style=payload.document_style,
            title=title,
        )
        return record
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/summarize/pdf")
async def summarize_pdf_endpoint(
    file: UploadFile = File(...),
    summary_style: str = Form(...),
    document_style: str = Form(...)
):
    if not service:
        raise HTTPException(status_code=500, detail="Database/AI services are unavailable.")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Create a temp file to extract text from PyPDF2
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            extracted_text = extract_text_from_pdf(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF file: {exc}")
    
    try:
        record = service.create_summary(
            source_type="pdf",
            source_content=extracted_text,
            summary_style=summary_style,
            document_style=document_style,
            title=os.path.basename(file.filename),
        )
        return record
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/history")
def get_history_endpoint(limit: int = 20):
    if not service:
        raise HTTPException(status_code=500, detail="Database/AI services are unavailable.")
    try:
        history = service.get_history(limit=limit)
        return history
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Mount static folder (created dynamically)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)
