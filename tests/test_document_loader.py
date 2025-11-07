"""
Tests for document loader service.
"""
import pytest
import json
from io import BytesIO
from fastapi import UploadFile
from app.services.document_loader import DocumentLoader


@pytest.fixture
def document_loader():
    """Create a DocumentLoader instance."""
    return DocumentLoader()


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content (minimal valid PDF)."""
    # This is a minimal valid PDF structure
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Size 1 /Root 1 0 R >>\nstartxref\n9\n%%EOF"


@pytest.fixture
def sample_json_content():
    """Sample JSON document content."""
    return json.dumps({
        "text": "This is a sample document text for testing purposes.",
        "title": "Test Document"
    }).encode('utf-8')


@pytest.fixture
def sample_questions_json():
    """Sample questions JSON content."""
    return json.dumps({
        "questions": [
            "What is the main topic?",
            "What is the document about?"
        ]
    }).encode('utf-8')


@pytest.mark.asyncio
async def test_load_json_document(document_loader, sample_json_content):
    """Test loading JSON document."""
    file = UploadFile(
        filename="test.json",
        file=BytesIO(sample_json_content)
    )
    content = await document_loader.load_document(file)
    assert isinstance(content, str)
    assert len(content) > 0


@pytest.mark.asyncio
async def test_load_questions(document_loader, sample_questions_json):
    """Test loading questions from JSON."""
    file = UploadFile(
        filename="questions.json",
        file=BytesIO(sample_questions_json)
    )
    result = await document_loader.load_questions(file)
    assert "questions" in result
    assert isinstance(result["questions"], list)
    assert len(result["questions"]) == 2


@pytest.mark.asyncio
async def test_load_questions_invalid_format(document_loader):
    """Test loading questions with invalid format."""
    invalid_content = b"not a json"
    file = UploadFile(
        filename="invalid.json",
        file=BytesIO(invalid_content)
    )
    with pytest.raises(ValueError):
        await document_loader.load_questions(file)


@pytest.mark.asyncio
async def test_load_document_unsupported_format(document_loader):
    """Test loading document with unsupported format."""
    content = b"some content"
    file = UploadFile(
        filename="test.txt",
        file=BytesIO(content)
    )
    with pytest.raises(ValueError):
        await document_loader.load_document(file)

