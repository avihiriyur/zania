# Question-Answering API

A production-ready backend API for a Question-Answering bot that leverages LangChain and OpenAI's GPT-4o-mini to answer questions based on document content. The API supports both PDF and JSON document formats.

## Features

- 📄 **Multi-format Support**: Process PDF and JSON documents
- 🤖 **LLM-powered**: Uses OpenAI's GPT-4o-mini for intelligent question answering
- 🔍 **Vector-based Retrieval**: Utilizes ChromaDB for efficient document retrieval
- 🚀 **FastAPI**: High-performance async API framework
- ✅ **Production-ready**: Includes error handling, validation, and tests

## Technology Stack

- **Python 3.x**
- **FastAPI** - Modern, fast web framework
- **LangChain** - Framework for LLM applications
- **OpenAI** (gpt-4o-mini) - Large language model
- **ChromaDB** - Vector database for embeddings
- **PyPDF** - PDF processing
- **Pydantic** - Data validation

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Setup

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd Zania
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Starting the Server

Run the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### API Endpoints

#### 1. Health Check
```
GET /
GET /health
```

#### 2. Question-Answering
```
POST /qa
```

**Request:**
- `document`: PDF or JSON file containing the document content
- `questions_file`: JSON file containing a list of questions

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/qa" \
  -F "document=@sample_document.pdf" \
  -F "questions_file=@questions.json"
```

**Example questions.json:**
```json
{
  "questions": [
    "What is the main topic of this document?",
    "What are the key points discussed?",
    "Who is the author?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    {
      "What is the main topic of this document?": "The document discusses..."
    },
    {
      "What are the key points discussed?": "The key points include..."
    },
    {
      "Who is the author?": "The author is..."
    }
  ]
}
```

### Supported File Formats

#### Document Files
- **PDF**: Standard PDF documents
- **JSON**: JSON files with text content. Supports various structures:
  - `{"text": "..."}`
  - `{"content": "..."}`
  - `{"document": "..."}`
  - Plain JSON objects (converted to string)

#### Questions File
- **JSON**: Must contain a `questions` array or be an array of questions:
  ```json
  {
    "questions": ["question1", "question2"]
  }
  ```
  or
  ```json
  ["question1", "question2"]
  ```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Project Structure

```
Zania/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── document_loader.py  # Document loading logic
│       └── qa_service.py       # QA chain implementation
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API endpoint tests
│   └── test_document_loader.py # Document loader tests
├── .env.example                 # Environment variables template
├── .gitignore
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## How It Works (RAG Pipeline)

The API uses **Retrieval Augmented Generation (RAG)** to answer questions:

1. **Document Processing**: 
   - Documents (PDF/JSON) are loaded and converted to text
   - For PDFs, page-level metadata is preserved (page numbers, source)
   - Text is split into chunks using an optimized chunking strategy

2. **Chunking Strategy**:
   - Uses `RecursiveCharacterTextSplitter` with intelligent separators
   - Chunk size: 1000 characters with 200 character overlap
   - Separators prioritize paragraph breaks (`\n\n\n`, `\n\n`) for better context preservation
   - PDF pages are chunked individually with metadata attached

3. **Vector Store Creation**:
   - Document chunks are embedded using OpenAI embeddings
   - Embeddings are stored in ChromaDB vector store (in-memory)
   - Each chunk retains metadata (page numbers, source file)

4. **RAG Retrieval**:
   - For each question, the system retrieves the top 5 most relevant chunks
   - Uses similarity search to find chunks most related to the question
   - Retrieved chunks provide context to the LLM

5. **Question Answering**:
   - Questions are processed through a RetrievalQA chain
   - Retrieved relevant chunks are sent to GPT-4o-mini as context
   - LLM generates accurate answers based solely on the retrieved context
   - Enhanced prompts ensure answers are grounded in the document

## Error Handling

The API includes comprehensive error handling:
- Invalid file formats
- Missing or malformed JSON
- Empty documents or questions
- API key validation
- LLM processing errors

## Production Considerations

For production deployment, consider:
- Adding authentication/authorization
- Implementing rate limiting
- Adding logging and monitoring
- Using persistent vector stores
- Setting up proper error tracking
- Adding request validation middleware
- Implementing caching for frequently asked questions

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

