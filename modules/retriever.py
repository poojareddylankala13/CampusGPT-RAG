import logging

from modules.vector_store import load_vector_store

logger = logging.getLogger("CampusGPT.retriever")


def retrieve_relevant_chunks(query, k=5):
    """Retrieves the top k relevant chunks from FAISS along with normalized similarity scores.

    Args:
        query (str): The search query.
        k (int): Number of chunks to retrieve (default: 5).

    Returns:
        list: A list of dicts containing:
            - 'content': Text chunk content
            - 'metadata': Source metadata (source, page)
            - 'score': Normalized similarity score (0.0 to 1.0)
    """
    vector_store = load_vector_store()
    if not vector_store:
        logger.warning("No vector store loaded. Returning empty list.")
        return []

    try:
        # FAISS similarity search returns (document, L2 distance)
        docs_and_scores = vector_store.similarity_search_with_score(query, k=k)

        results = []
        for doc, l2_dist in docs_and_scores:
            # For normalized embeddings, the L2 distance ranges from 0 (exact match) to 2.
            # Cosine similarity = 1 - (L2_distance^2) / 2
            similarity = 1.0 - (l2_dist**2) / 2.0

            # Clamp to [0, 1] range to avoid floating-point edge issues
            similarity = max(0.0, min(1.0, similarity))

            results.append({"content": doc.page_content, "metadata": doc.metadata, "score": similarity})

        logger.info(f"Retrieved {len(results)} chunks for query: '{query}'")
        return results

    except Exception as e:
        logger.error(f"Error during retrieval: {str(e)}")
        return []
