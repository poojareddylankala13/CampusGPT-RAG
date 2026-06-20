import logging
import os

from modules.document_parser import extract_pdf_markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusGPT.pdf_loader")


def validate_and_load_pdf(file_path: str):
    """Loads and extracts text from a PDF file using PyMuPDF4LLM.

    Performs basic validation on the file before reading.
    Returns:
        list: A list of Document objects if successful, else raises Exception.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    # Check file size (e.g., maximum 20MB limit for safety)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 20:
        raise ValueError(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed limit of 20 MB.")

    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    try:
        logger.info(f"Loading and parsing PDF using PyMuPDF4LLM: {file_path}")
        docs = extract_pdf_markdown(file_path)

        if not docs:
            raise ValueError("The PDF contains no readable text pages.")

        logger.info(f"Successfully loaded {len(docs)} pages from {os.path.basename(file_path)}")
        return docs

    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        raise e
