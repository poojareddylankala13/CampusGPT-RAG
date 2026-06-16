import logging
from modules.retriever import retrieve_relevant_chunks
from modules.database import add_search

logger = logging.getLogger("CampusGPT.semantic_search")

def perform_semantic_search(user_id, query, k=10):
    """Executes a semantic similarity search on the vector store and logs the search query.
    
    Args:
        user_id (int): ID of the searching user.
        query (str): The search query text.
        k (int): Number of top results to retrieve.
        
    Returns:
        list: List of matching chunks with similarity scores.
    """
    logger.info(f"User {user_id} executing semantic search: '{query}'")
    
    # Log search query to database for analytics
    add_search(user_id, query)
    
    # Fetch results from retriever
    results = retrieve_relevant_chunks(query, k=k)
    return results
