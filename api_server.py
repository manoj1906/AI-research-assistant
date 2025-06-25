#!/usr/bin/env python3
"""
FastAPI Server for AI Research Assistant
Provides REST API endpoints for paper analysis
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import sys
from pathlib import Path
import logging
import tempfile
import os
from typing import Optional, Dict, Any, List

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🔬 AI Research Assistant API",
    description="Intelligent analysis of academic papers and research documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize research assistant
assistant = ResearchAssistant()

# Pydantic models


class QuestionRequest(BaseModel):
    question: str
    paper_id: Optional[str] = None
    section: Optional[str] = None


class AnalysisRequest(BaseModel):
    paper_id: str
    analysis_type: str = "contribution"  # contribution, methodology, results


class ComparisonRequest(BaseModel):
    paper_ids: List[str]
    aspect: str = "methodology"  # methodology, results, approach


class SummaryRequest(BaseModel):
    paper_id: str
    section: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🔬 AI Research Assistant API",
        "version": "1.0.0",
        "description": "Intelligent analysis of academic papers and research documents",
        "endpoints": {
            "upload": "POST /upload - Upload a research paper",
            "ask": "POST /ask - Ask questions about papers",
            "analyze": "POST /analyze - Analyze paper contributions/methodology",
            "summarize": "POST /summarize - Generate paper summaries",
            "compare": "POST /compare - Compare multiple papers",
            "papers": "GET /papers - List uploaded papers",
            "paper": "GET /paper/{paper_id} - Get paper details"
        }
    }


@app.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    paper_id: Optional[str] = Form(None)
):
    """Upload and process a research paper."""

    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Process the paper
        processed_paper_id = assistant.upload_paper(tmp_file_path, paper_id)

        # Clean up temp file
        os.unlink(tmp_file_path)

        # Get paper info
        papers = assistant.list_papers()
        paper_info = next(
            (p for p in papers if p['id'] == processed_paper_id), None)

        return {
            "status": "success",
            "message": "Paper uploaded and processed successfully",
            "paper_id": processed_paper_id,
            "paper_info": paper_info
        }

    except Exception as e:
        logger.error(f"Error uploading paper: {e}")
        # Clean up temp file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        raise HTTPException(
            status_code=500, detail=f"Error processing paper: {str(e)}")


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about research papers."""

    try:
        answer = assistant.ask_question(
            question=request.question,
            paper_id=request.paper_id,
            section=request.section
        )

        return {
            "status": "success",
            "question": request.question,
            "answer": answer.answer,
            "confidence": answer.confidence,
            "evidence": answer.evidence,
            "section": answer.section,
            "page_numbers": answer.page_numbers
        }

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error answering question: {str(e)}")


@app.post("/analyze")
async def analyze_paper(request: AnalysisRequest):
    """Analyze paper contributions, methodology, or results."""

    try:
        if request.analysis_type == "contribution":
            analysis = assistant.analyze_contribution(request.paper_id)
        elif request.analysis_type == "methodology":
            analysis = assistant.analyze_methodology(request.paper_id)
        elif request.analysis_type == "results":
            analysis = assistant.analyze_results(request.paper_id)
        else:
            raise HTTPException(
                status_code=400, detail="Invalid analysis type")

        return {
            "status": "success",
            "analysis_type": request.analysis_type,
            "paper_id": request.paper_id,
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing paper: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error analyzing paper: {str(e)}")


@app.post("/summarize")
async def summarize_paper(request: SummaryRequest):
    """Generate a summary of a paper or specific section."""

    try:
        summary = assistant.summarize_paper(
            paper_id=request.paper_id,
            section=request.section
        )

        return {
            "status": "success",
            "paper_id": request.paper_id,
            "section": request.section,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error summarizing paper: {str(e)}")


@app.post("/compare")
async def compare_papers(request: ComparisonRequest):
    """Compare multiple research papers."""

    try:
        comparison = assistant.compare_papers(
            paper_ids=request.paper_ids,
            aspect=request.aspect
        )

        return {
            "status": "success",
            "paper_ids": request.paper_ids,
            "aspect": request.aspect,
            "comparison": comparison
        }

    except Exception as e:
        logger.error(f"Error comparing papers: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error comparing papers: {str(e)}")


@app.get("/papers")
async def list_papers():
    """List all uploaded papers."""

    try:
        papers = assistant.list_papers()
        return {
            "status": "success",
            "count": len(papers),
            "papers": papers
        }

    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error listing papers: {str(e)}")


@app.get("/paper/{paper_id}")
async def get_paper(paper_id: str):
    """Get details of a specific paper."""

    try:
        paper_details = assistant.get_paper_details(paper_id)
        return {
            "status": "success",
            "paper_id": paper_id,
            "details": paper_details
        }

    except Exception as e:
        logger.error(f"Error getting paper details: {e}")
        raise HTTPException(
            status_code=404, detail=f"Paper not found: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Research Assistant API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
