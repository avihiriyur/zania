"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel
from typing import List, Dict


class QARequest(BaseModel):
    """Request model for QA endpoint."""
    questions: List[str]
    document_content: str


class QAResponse(BaseModel):
    """Response model for QA endpoint."""
    answers: List[Dict[str, str]]

