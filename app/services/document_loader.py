"""
Service for loading and processing documents and questions.
"""
import json
import pypdf
from fastapi import UploadFile, HTTPException
from typing import Dict, List
import io


class DocumentLoader:
    """Handles loading of documents and questions from various file formats."""
    
    async def load_document(self, file: UploadFile) -> str:
        """
        Load document content from PDF or JSON file.
        
        Args:
            file: Uploaded file (PDF or JSON)
            
        Returns:
            Document content as string
        """
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self._load_pdf(content)
        elif file_extension == 'json':
            return self._load_json_document(content)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: PDF, JSON")
    
    def _load_pdf(self, content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
    
    async def load_pdf_with_metadata(self, file: UploadFile) -> List[Dict]:
        """
        Load PDF with page-level metadata for better chunking.
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            List of dictionaries with page text and metadata
        """
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension != 'pdf':
            raise ValueError("File must be a PDF")
        
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            pages_data = []
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text.strip():
                    pages_data.append({
                        "page_number": page_num,
                        "text": page_text,
                        "source": file.filename
                    })
            
            return pages_data
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
    
    def _load_json_document(self, content: bytes) -> str:
        """Extract text from JSON document."""
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON structures
            if isinstance(json_data, dict):
                # If it's a dict, try to extract text content
                if 'text' in json_data:
                    return json_data['text']
                elif 'content' in json_data:
                    return json_data['content']
                elif 'document' in json_data:
                    return json_data['document']
                else:
                    # Convert entire dict to string representation
                    return json.dumps(json_data, indent=2)
            elif isinstance(json_data, list):
                # If it's a list, join all items
                return "\n".join(str(item) for item in json_data)
            else:
                return str(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {str(e)}")
    
    async def load_questions(self, file: UploadFile) -> Dict:
        """
        Load questions from JSON file.
        
        Args:
            file: Uploaded JSON file containing questions
            
        Returns:
            Dictionary containing questions list
        """
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension != 'json':
            raise ValueError("Questions file must be a JSON file")
        
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON structures
            if isinstance(json_data, dict):
                if 'questions' in json_data:
                    return json_data
                elif 'question' in json_data:
                    return {"questions": [json_data["question"]]}
                else:
                    # Try to extract questions from any list in the dict
                    for key, value in json_data.items():
                        if isinstance(value, list):
                            return {"questions": value}
                    raise ValueError("No 'questions' field found in JSON")
            elif isinstance(json_data, list):
                # If it's a list, assume it's a list of questions
                return {"questions": json_data}
            else:
                raise ValueError("Invalid JSON structure for questions file")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing questions JSON file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading questions file: {str(e)}")

