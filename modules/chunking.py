import logging

# Fallback imports for LangChain compatibility
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore[no-redef]

logger = logging.getLogger("CampusGPT.chunking")


def split_documents(docs, chunk_size=1000, chunk_overlap=200):
    """Splits a list of LangChain Document objects into smaller chunks.

    Args:
        docs (list): List of Document objects.
        chunk_size (int): Size of each chunk in characters.
        chunk_overlap (int): Overlap size in characters.

    Returns:
        list: List of chunked Document objects.
    """
    logger.info(f"Splitting {len(docs)} documents (chunk_size={chunk_size}, overlap={chunk_overlap})")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(docs)
    logger.info(f"Successfully generated {len(chunks)} text chunks.")
    return chunks
