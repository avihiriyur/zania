"""
FastAPI application for Question-Answering bot using LangChain.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
import os
from dotenv import load_dotenv

from app.services.document_loader import DocumentLoader
from app.services.qa_service import QAService
from app.models.schemas import QARequest, QAResponse

load_dotenv()

app = FastAPI(
    title="Question-Answering API",
    description="API for answering questions based on document content using LangChain and OpenAI",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Question-Answering API is running"}


@app.post("/qa", response_model=QAResponse)
async def answer_questions(
    document: UploadFile = File(..., description="Document file (PDF or JSON)"),
    questions_file: UploadFile = File(..., description="JSON file containing list of questions")
):
    """
    Answer questions based on document content.
    
    Args:
        document: PDF or JSON file containing the document content
        questions_file: JSON file containing a list of questions
        
    Returns:
        JSON response with question-answer pairs
    """
    try:
        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not found in environment variables"
            )
        
        # Load and process document
        document_loader = DocumentLoader()
        
        # Load questions first
        questions_data = await document_loader.load_questions(questions_file)
        questions = questions_data.get("questions", [])
        
        if not questions:
            raise HTTPException(
                status_code=400,
                detail="No questions found in the questions file"
            )
        
        # For PDFs, try to load with metadata for better chunking
        document_metadata = None
        document_content = None
        
        if document.filename and document.filename.lower().endswith('.pdf'):
            # Read file content once
            file_content = await document.read()
            
            try:
                # Create a file wrapper for metadata loading
                class FileWrapper:
                    def __init__(self, content, filename):
                        self.content = content
                        self.filename = filename
                    
                    async def read(self):
                        return self.content
                
                file_wrapper = FileWrapper(file_content, document.filename)
                document_metadata = await document_loader.load_pdf_with_metadata(file_wrapper)
                
                # Also get the text content
                document_content = document_loader._load_pdf(file_content)
            except Exception:
                # Fall back to standard loading if metadata extraction fails
                document_content = document_loader._load_pdf(file_content)
                document_metadata = None
        else:
            # For non-PDF files, use standard loading
            document_content = await document_loader.load_document(document)
        
        # Initialize QA service
        qa_service = QAService()
        
        # Process questions and get answers using RAG
        qa_pairs = await qa_service.answer_questions(
            document_content=document_content,
            questions=questions,
            document_metadata=document_metadata
        )
        
        return QAResponse(answers=qa_pairs)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

