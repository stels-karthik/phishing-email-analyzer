from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import os

from ..models.schemas import EmailInput, AnalysisResult, HealthResponse
from ..agents.orchestrator import AnalysisOrchestrator
from ..utils.email_parser import EmailParser

router = APIRouter()

# Initialize orchestrator
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY environment variable not set")

orchestrator = AnalysisOrchestrator(groq_api_key)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        groq_configured=bool(os.getenv("GROQ_API_KEY"))
    )


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_email(email_input: EmailInput):
    """
    Analyze an email for phishing indicators.

    Accepts either:
    - raw_email: Complete raw email (RFC822 format)
    - OR individual fields: from_address, to_address, subject, body_text/body_html
    """
    try:
        # Parse email data
        if email_input.raw_email:
            # Parse raw email
            email_data = EmailParser.parse_raw_email(email_input.raw_email)
        else:
            # Use provided fields
            email_data = {
                "from": email_input.from_address or "",
                "to": email_input.to_address or "",
                "subject": email_input.subject or "",
                "body_text": email_input.body_text or "",
                "body_html": email_input.body_html or "",
                "headers": email_input.headers or {},
                "links": EmailParser.extract_links(email_input.body_html or email_input.body_text or ""),
                "attachments": [],
                "return_path": email_input.headers.get("Return-Path", "") if email_input.headers else "",
                "reply_to": email_input.headers.get("Reply-To", "") if email_input.headers else "",
            }

        # Run analysis
        result = await orchestrator.analyze_email(email_data)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/file")
async def analyze_email_file(file: UploadFile = File(...)):
    """
    Analyze an email file (.eml or .msg format).
    """
    try:
        # Read file content
        content = await file.read()
        raw_email = content.decode('utf-8')

        # Parse and analyze
        email_data = EmailParser.parse_raw_email(raw_email)
        result = await orchestrator.analyze_email(email_data)

        return result

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid email file encoding")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/stats")
async def get_stats():
    """Get analysis statistics (placeholder for future implementation)."""
    return {
        "total_analyses": 0,
        "threat_detections": 0,
        "message": "Statistics tracking not yet implemented"
    }
