"""
Service for question-answering using LangChain and OpenAI.
"""
import os
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document


class QAService:
    """Handles question-answering using LangChain and vector store with RAG."""
    
    def __init__(self):
        """Initialize QA service with OpenAI and vector store."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        # Enhanced chunking strategy for better RAG retrieval
        # Larger chunk size preserves more context, helpful for complex questions
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # Increased from 1000 to preserve more context
            chunk_overlap=400,  # Increased overlap to maintain context continuity
            length_function=len,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],  # Better separators for PDFs
        )
    
    async def answer_questions(
        self, 
        document_content: str, 
        questions: List[str],
        document_metadata: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        Answer questions based on document content using RAG (Retrieval Augmented Generation).
        
        This method:
        1. Chunks the document using an optimized chunking strategy
        2. Creates embeddings and stores them in a vector database
        3. Retrieves relevant chunks for each question
        4. Sends retrieved context to LLM for answering
        
        Args:
            document_content: The document text to answer questions from
            questions: List of questions to answer
            document_metadata: Optional metadata about document pages (for PDFs)
            
        Returns:
            List of dictionaries with question-answer pairs
        """
        if not document_content or not document_content.strip():
            raise ValueError("Document content is empty")
        
        # Create document chunks with metadata if available
        if document_metadata:
            # Create documents with page metadata for better retrieval
            documents = []
            for page_data in document_metadata:
                page_text = page_data.get("text", "")
                if page_text.strip():
                    # Split each page into chunks and preserve metadata
                    page_chunks = self.text_splitter.create_documents([page_text])
                    for chunk in page_chunks:
                        chunk.metadata = {
                            "page_number": page_data.get("page_number", 0),
                            "source": page_data.get("source", "unknown")
                        }
                    documents.extend(page_chunks)
        else:
            # Standard chunking without metadata
            documents = self.text_splitter.create_documents([document_content])
        
        if not documents:
            raise ValueError("No document chunks created. Document may be empty or unreadable.")
        
        # Create vector store for RAG retrieval using FAISS
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        # Enhanced prompt for better RAG responses
        prompt_template = """You are a helpful assistant that answers questions based on the provided context from a document.

Use the following pieces of context to answer the question accurately and comprehensively.
- If the answer is not in the context, say "I don't know" based on the provided context.
- Do not make up information that is not in the context.
- Provide detailed and accurate answers based solely on the context provided.
- If multiple relevant pieces of context are provided, synthesize them into a comprehensive answer.

Context from document:
{context}

Question: {question}

Provide a clear, accurate answer based on the context above:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create RAG chain with optimized retrieval
        # Using similarity search with top-k retrieval
        # Increased k from 5 to 10 to retrieve more relevant chunks for comprehensive answers
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # Retrieve top 10 most relevant chunks for better context
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Stuff all retrieved chunks into prompt
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False
        )
        
        # Answer each question using RAG
        qa_dict = {}
        for question in questions:
            if not question or not question.strip():
                continue
            
            try:
                # Invoke RAG chain: retrieves relevant chunks and generates answer
                result = qa_chain.invoke({"query": question})
                answer = result.get("result", "I don't know the answer to this question based on the provided document.")
                qa_dict[question] = answer
            except Exception as e:
                # If there's an error answering a question, return error message
                qa_dict[question] = f"Error answering question: {str(e)}"
        
        # Convert to list of dicts format for API response
        return [qa_dict]

