import os
import time
import json
import hashlib
import logging
from datetime import datetime
import streamlit as st

from modules.database import add_evaluation_log
from modules.embedding_manager import CachedLocalEmbeddings
from modules.vector_store import load_vector_store, get_index_path
from modules.llm_local import is_llama_available, generate_local_response_stream
from modules.rag_chain import generate_rag_answer

logger = logging.getLogger("CampusGPT.rag_pipeline")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERY_CACHE_DIR = os.path.join(BASE_DIR, 'cache', 'queries')
os.makedirs(QUERY_CACHE_DIR, exist_ok=True)

def clear_query_cache():
    """Removes all cached query JSON files from cache/queries/."""
    if not os.path.exists(QUERY_CACHE_DIR):
        return True
    try:
        count = 0
        for file in os.listdir(QUERY_CACHE_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(QUERY_CACHE_DIR, file))
                count += 1
        logger.info(f"Cleared {count} query cache entries.")
        return True
    except Exception as e:
        logger.error(f"Error clearing query cache: {e}")
        return False

def get_query_cache_key(query: str, settings: dict) -> str:
    """Generates an MD5 hash key for caching RAG query responses."""
    # Serialize settings fields that affect output
    inputs = {
        "query": query.strip().lower(),
        "ai_mode": settings.get("ai_mode", "gemini"),
        "embedding_model": settings.get("embedding_model", "bge-small"),
        "retrieval_method": settings.get("retrieval_method", "similarity"),
        "top_k": settings.get("top_k", 5),
        "threshold": settings.get("threshold", 0.6),
        "gguf_model": settings.get("active_gguf_model", "")
    }
    serialized = json.dumps(inputs, sort_keys=True)
    return hashlib.md5(serialized.encode('utf-8')).hexdigest()

def lookup_query_cache(cache_key: str):
    """Loads a cached query response if it exists."""
    cache_path = os.path.join(QUERY_CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                logger.info(f"Query Cache Hit: {cache_key}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read query cache file: {e}")
    return None

def write_query_cache(cache_key: str, response: dict):
    """Saves a query response to the cache directory."""
    cache_path = os.path.join(QUERY_CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        logger.info(f"Query Cache Written: {cache_key}")
    except Exception as e:
        logger.error(f"Failed to write query cache file: {e}")

# --- Unified Retrieval Logic ---

def execute_retrieval(query: str, settings: dict):
    """Retrieves document chunks based on active model settings.
    
    Supports Similarity Search, MMR (Max Marginal Relevance), and similarity score filtering.
    """
    model_key = settings.get("embedding_model", "bge-small")
    retrieval_method = settings.get("retrieval_method", "similarity")
    top_k = settings.get("top_k", 5)
    threshold = settings.get("threshold", 0.6)
    
    # 1. Load correct vector store for this embedding space
    # Override standard vector store load to pass active embeddings
    embeddings = CachedLocalEmbeddings(model_key=model_key)
    vector_store = load_vector_store()  # Fallback check
    
    # We dynamically load the FAISS store specific to the selected embedding model
    from langchain_community.vectorstores import FAISS
    from modules.vector_store import get_index_path
    
    index_path = get_index_path()
    # Check if this specific index exists
    # The get_index_path will be model-specific (e.g. data/faiss_index/bge-small or minilm)
    # We will modify get_index_path in vector_store.py to reflect this!
    if not os.path.exists(index_path) and not os.path.exists(f"{index_path}.faiss"):
        logger.warning(f"Vector store index not found at: {index_path}")
        return []
        
    try:
        vs = FAISS.load_local(
            folder_path=os.path.dirname(index_path),
            embeddings=embeddings,
            index_name=os.path.basename(index_path),
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        logger.error(f"Failed to load specific FAISS index: {e}")
        return []

    # 2. Query candidates with scores
    # FAISS distance is L2. Cosine similarity = 1 - (L2_dist^2)/2
    candidates_raw = vs.similarity_search_with_score(query, k=top_k * 2)
    candidates = []
    
    for doc, l2_dist in candidates_raw:
        similarity = 1.0 - (l2_dist ** 2) / 2.0
        similarity = max(0.0, min(1.0, similarity))
        candidates.append((doc, similarity))

    # 3. Retrieve documents based on method
    retrieved_docs = []
    
    if retrieval_method == 'mmr':
        # Perform MMR retrieval
        mmr_docs = vs.max_marginal_relevance_search(query, k=top_k)
        # Find scores for the MMR selected documents by matching against candidates
        for doc in mmr_docs:
            score = 0.5  # Fallback default
            for c_doc, c_score in candidates:
                if c_doc.page_content == doc.page_content:
                    score = c_score
                    break
            retrieved_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
    else:
        # Standard Similarity Search
        for doc, score in candidates[:top_k]:
            retrieved_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })

    # 4. Filter by threshold
    filtered_docs = [doc for doc in retrieved_docs if doc['score'] >= threshold]
    logger.info(f"Retrieved {len(filtered_docs)} chunks after applying threshold {threshold}")
    return filtered_docs

# --- Unified RAG Execution Pipeline ---

def execute_rag_pipeline(query: str, settings: dict):
    """Executes the complete RAG query pipeline.
    
    Args:
        query (str): The user's question.
        settings (dict): Current app config (ai_mode, embedding_model, retrieval_method, top_k, threshold).
        
    Returns:
        dict: The final response structured answer and metadata.
    """
    ai_mode = settings.get("ai_mode", "gemini")
    
    # 1. Check Query Cache
    cache_key = get_query_cache_key(query, settings)
    cached_res = lookup_query_cache(cache_key)
    if cached_res is not None:
        # Check if it was streaming or normal
        return cached_res

    # 2. Start performance profiling
    retrieval_start = time.time()
    chunks = execute_retrieval(query, settings)
    retrieval_time = time.time() - retrieval_start
    
    if not chunks:
        return {
            "answer": "I'm sorry, but I couldn't retrieve any relevant context from the uploaded university documents matching your query.",
            "sources": [],
            "retrieved_chunks": [],
            "retrieval_time": f"{retrieval_time:.3f}s",
            "generation_time": "0.000s"
        }

    # Format context and unique sources list
    context_blocks = []
    unique_sources = {}
    total_context_len = 0
    sum_similarity = 0.0
    
    for i, chunk in enumerate(chunks):
        src_name = chunk['metadata'].get('source', 'Unknown Document')
        page_num = chunk['metadata'].get('page', 0)
        display_page = page_num + 1 if isinstance(page_num, int) else page_num
        sum_similarity += chunk['score']
        
        if src_name not in unique_sources:
            unique_sources[src_name] = set()
        unique_sources[src_name].add(display_page)
        
        context_blocks.append(
            f"--- Context {i+1} | Source: {src_name} (Page {display_page}) ---\n{chunk['content']}"
        )
        total_context_len += len(chunk['content'])
        
    context_text = "\n\n".join(context_blocks)
    avg_similarity = sum_similarity / len(chunks) if chunks else 0.0
    
    formatted_sources = []
    for src, pages in unique_sources.items():
        sorted_pages = sorted(list(pages))
        pages_str = ", ".join(str(p) for p in sorted_pages)
        formatted_sources.append({
            "document": src,
            "pages": pages_str
        })

    generation_start = time.time()
    
    # 3. Model Inference Routing
    if ai_mode == 'gemini':
        # Route to Gemini API
        try:
            logger.info("Routing RAG request to Gemini API...")
            # We call the existing Gemini RAG logic, but construct prompt manually to match context
            from modules.rag_chain import get_llm
            from langchain_core.messages import SystemMessage, HumanMessage
            
            llm = get_llm()
            system_instruction = (
                "You are CampusGPT, an intelligent AI-powered University Knowledge Assistant.\n"
                "Your task is to answer the student or faculty member's question using ONLY the provided university document context below.\n\n"
                "Guidelines:\n"
                "1. Answer the question thoroughly, clearly, and professionally based strictly on the text provided.\n"
                "2. If the text does not contain the answer, reply exactly: "
                "\"I'm sorry, but I couldn't find the answer to your question in the uploaded university documents.\""
                "Do not try to make up an answer or use general knowledge.\n"
                "3. Rely only on factual context. Do not speculate or extrapolate.\n"
                "4. Avoid referencing 'Context 1' or 'as mentioned in the text'. Present the answer directly and naturally.\n"
            )
            human_prompt = f"University Document Context:\n{context_text}\n\nQuestion: {query}"
            
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=human_prompt)
            ]
            response = llm.invoke(messages)
            answer = response.content
            generation_time = time.time() - generation_start
            
        except Exception as e:
            logger.error(f"Gemini API execution error: {e}")
            answer = f"❌ Gemini API Error: {str(e)}"
            generation_time = 0.0
            
    else:
        # Route to Local Llama.cpp
        # Since local GGUF models are streaming, this function returns a static placeholder for caching,
        # but in Chat.py we will call `generate_local_response_stream` directly to stream!
        # For non-streaming pipelines (or query cache filling), we compile the stream.
        try:
            logger.info("Routing RAG request to Local GGUF model...")
            active_model = settings.get("active_gguf_model", "")
            
            if not active_model:
                answer = "⚠️ Local LLM Error: No GGUF model file selected in settings."
                generation_time = 0.0
            elif not is_llama_available():
                answer = "❌ Local LLM Error: llama-cpp-python is not installed on this system."
                generation_time = 0.0
            else:
                system_instruction = (
                    "You are CampusGPT, an intelligent AI-powered University Knowledge Assistant.\n"
                    "Your task is to answer the user's question using ONLY the provided university document context below.\n\n"
                    "Guidelines:\n"
                    "1. Answer the question thoroughly and factually based strictly on the context.\n"
                    "2. If the context does not contain the answer, reply exactly: "
                    "\"I'm sorry, but I couldn't find the answer to your question in the uploaded university documents.\"\n"
                    "3. Present the answer directly and naturally without referring to 'Context 1' or 'the context'."
                )
                prompt_text = f"University Document Context:\n{context_text}\n\nQuestion: {query}"
                
                # Fetch stream chunks and assemble
                stream = generate_local_response_stream(
                    prompt=prompt_text,
                    model_filename=active_model,
                    system_prompt=system_instruction,
                    context_len=settings.get("context_len", 2048)
                )
                
                assembled_chunks = []
                for chunk in stream:
                    assembled_chunks.append(chunk)
                answer = "".join(assembled_chunks)
                generation_time = time.time() - generation_start
        except Exception as e:
            logger.error(f"Local LLM execution error: {e}")
            answer = f"❌ Local LLM Error: {str(e)}"
            generation_time = 0.0

    # 4. Compile Response dictionary
    response_dict = {
        "answer": answer,
        "sources": formatted_sources,
        "retrieved_chunks": chunks,
        "retrieval_time": f"{retrieval_time:.3f}s",
        "generation_time": f"{generation_time:.3f}s"
    }

    # 5. Log metrics in SQLite rag_evaluations table
    add_evaluation_log(
        query=query,
        ai_mode=ai_mode if ai_mode == 'gemini' else f"local ({settings.get('active_gguf_model', 'gguf')})",
        retrieval_time=retrieval_time,
        generation_time=generation_time,
        chunk_count=len(chunks),
        avg_similarity=avg_similarity,
        context_length=total_context_len
    )

    # 6. Save in query cache (only cache valid non-error answers)
    if "❌" not in answer and "⚠️" not in answer:
        write_query_cache(cache_key, response_dict)

    return response_dict
