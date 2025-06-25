#!/usr/bin/env python3
"""
FastAPI REST API for AI Research Assistant
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import sys
from pathlib import Path
import logging
import uvicorn

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Research Assistant API",
    description="REST API for analyzing academic papers and research documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the research assistant
assistant = ResearchAssistant()

# Pydantic models for API


class QuestionRequest(BaseModel):
    question: str
    paper_id: Optional[str] = None
    section: Optional[str] = None


class SummaryRequest(BaseModel):
    paper_id: str
    section: Optional[str] = None


class AnalysisRequest(BaseModel):
    paper_id: str


class SearchRequest(BaseModel):
    query: str
    paper_id: Optional[str] = None
    limit: int = 10


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Research Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /papers/upload",
            "ask": "POST /papers/ask",
            "summarize": "POST /papers/summarize",
            "analyze": "POST /papers/analyze",
            "list": "GET /papers",
            "search": "POST /papers/search"
        }
    }


@app.post("/papers/upload")
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    paper_id: Optional[str] = None
):
    """Upload and process a research paper"""

    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported")

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Process the paper
        result_paper_id = assistant.upload_paper(tmp_file_path, paper_id)

        # Clean up temp file in background
        background_tasks.add_task(lambda: Path(
            tmp_file_path).unlink(missing_ok=True))

        return {
            "message": "Paper uploaded successfully",
            "paper_id": result_paper_id,
            "filename": file.filename
        }

    except Exception as e:
        logger.error(f"Error uploading paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/papers/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about research papers"""

    try:
        answer = assistant.ask_question(
            request.question,
            request.paper_id,
            request.section
        )

        return {
            "question": request.question,
            "answer": answer.answer,
            "confidence": answer.confidence,
            "evidence": answer.evidence,
            "context": answer.context,
            "paper_id": request.paper_id,
            "section": request.section
        }

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/papers/summarize")
async def summarize_paper(request: SummaryRequest):
    """Generate a summary of a paper or section"""

    try:
        summary = assistant.summarize_paper(request.paper_id, request.section)

        return {
            "paper_id": request.paper_id,
            "section": request.section,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/papers/analyze")
async def analyze_paper(request: AnalysisRequest):
    """Analyze the contribution of a paper"""

    try:
        analysis = assistant.analyze_contribution(request.paper_id)

        return {
            "paper_id": request.paper_id,
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/papers")
async def list_papers():
    """List all uploaded papers"""

    try:
        papers = assistant.list_papers()

        return {
            "count": len(papers),
            "papers": papers
        }

    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/papers/search")
async def search_papers(request: SearchRequest):
    """Search across papers"""

    try:
        results = assistant.search_papers(
            request.query,
            request.paper_id,
            request.limit
        )

        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/papers/{paper_id}")
async def get_paper(paper_id: str):
    """Get details of a specific paper"""

    try:
        papers = assistant.list_papers()
        paper = next((p for p in papers if p['id'] == paper_id), None)

        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        return paper

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/papers/{paper_id}")
async def delete_paper(paper_id: str):
    """Delete a paper"""

    try:
        success = assistant.delete_paper(paper_id)

        if not success:
            raise HTTPException(status_code=404, detail="Paper not found")

        return {"message": "Paper deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Research Assistant API"}

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
