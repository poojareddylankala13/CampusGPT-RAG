import os
import fitz  # PyMuPDF
import pymupdf4llm
import logging
from datetime import datetime
from langchain_core.documents import Document

logger = logging.getLogger("CampusGPT.document_parser")

def extract_pdf_markdown(pdf_path: str):
    """Parses a PDF file page-by-page using PyMuPDF4LLM.
    
    Args:
        pdf_path (str): The absolute path to the PDF file.
        
    Returns:
        list: A list of LangChain Document objects with markdown content and page metadata.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found at: {pdf_path}")
        
    logger.info(f"Extracting markdown page-by-page from: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        documents = []
        
        for page_num in range(page_count):
            # Extract markdown from a specific page (0-indexed in pymupdf4llm)
            page_md = pymupdf4llm.to_markdown(pdf_path, pages=[page_num])
            
            # Create a LangChain document object
            doc_obj = Document(
                page_content=page_md,
                metadata={
                    "source": os.path.basename(pdf_path),
                    "page": page_num  # 0-indexed page index
                }
            )
            documents.append(doc_obj)
            
        logger.info(f"Successfully parsed {len(documents)} pages from {os.path.basename(pdf_path)} using PyMuPDF4LLM")
        return documents
        
    except Exception as e:
        logger.error(f"Error parsing PDF with PyMuPDF4LLM: {str(e)}")
        raise e

def extract_pdf_text(pdf_path: str) -> str:
    """Returns the full text of the PDF as a single markdown string.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: The full document content as markdown.
    """
    try:
        logger.info(f"Extracting full markdown text from: {pdf_path}")
        return pymupdf4llm.to_markdown(pdf_path)
    except Exception as e:
        logger.error(f"Error extracting full markdown text: {str(e)}")
        raise e

def extract_document_metadata(pdf_path: str) -> dict:
    """Extracts standard file metadata.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        dict: Metadata dictionary (file_name, page_count, upload_date, file_size).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found at: {pdf_path}")
        
    try:
        doc = fitz.open(pdf_path)
        file_name = os.path.basename(pdf_path)
        page_count = len(doc)
        file_size = os.path.getsize(pdf_path)
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            "file_name": file_name,
            "page_count": page_count,
            "file_size": file_size,
            "upload_date": upload_date
        }
    except Exception as e:
        logger.error(f"Error extracting metadata from {pdf_path}: {str(e)}")
        raise e
