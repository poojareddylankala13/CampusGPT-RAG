import logging
import os
from typing import Dict, Set

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from modules.retriever import retrieve_relevant_chunks

logger = logging.getLogger("CampusGPT.rag_chain")


def get_llm():
    """Initializes and returns the ChatGoogleGenerativeAI (Gemini) client.

    Checks environment variables first, and falls back to Streamlit session state if needed.
    """
    # Try getting key from environment first, then from Streamlit session state
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.session_state.get("gemini_api_key")

    if not api_key:
        raise ValueError(
            "Gemini API Key is not set. Please set the GEMINI_API_KEY environment variable "
            "in your .env file or enter it in the application sidebar/settings."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.1,  # Low temperature for precise factual retrieval
        max_tokens=2048,
    )


def generate_rag_answer(query):
    """Executes the complete RAG workflow: Retrieves contexts, queries Gemini, and returns answers with citations.

    Args:
        query (str): User's natural language question.

    Returns:
        dict: A dictionary containing:
            - 'answer': The generated string answer.
            - 'sources': A list of dicts with unique source documents and their page numbers.
            - 'retrieved_chunks': The raw list of retrieved chunks (for analytics/debugging).
    """
    # 1. Retrieve the top 5 chunks
    chunks = retrieve_relevant_chunks(query, k=5)

    if not chunks:
        return {
            "answer": "No university documents have been indexed yet. Please go to the Upload page to import PDFs.",
            "sources": [],
            "retrieved_chunks": [],
        }

    # 2. Format context for prompt
    context_blocks = []
    unique_sources: Dict[str, Set] = {}

    for i, chunk in enumerate(chunks):
        source_name = chunk["metadata"].get("source", "Unknown Document")
        page_num = chunk["metadata"].get("page", 0)

        # Save page numbers for citations (1-indexed)
        # Note: streamlit parses pages from 0, so convert to 1-indexed for citation readability
        display_page = page_num + 1 if isinstance(page_num, int) else page_num

        if source_name not in unique_sources:
            unique_sources[source_name] = set()
        unique_sources[source_name].add(display_page)

        context_blocks.append(f"--- Chunk {i+1} | Source: {source_name} (Page {display_page}) ---\n{chunk['content']}")

    context_text = "\n\n".join(context_blocks)

    # 3. Create System & Human Messages
    system_instruction = (
        "You are CampusGPT, an intelligent AI-powered University Knowledge Assistant.\n"
        "Your task is to answer the student or faculty member's question using ONLY the provided university document context below.\n\n"
        "Guidelines:\n"
        "1. Answer the question thoroughly, clearly, and professionally based strictly on the text provided.\n"
        "2. If the text does not contain the answer, reply exactly: "
        "\"I'm sorry, but I couldn't find the answer to your question in the uploaded university documents.\""
        "Do not try to make up an answer or use general knowledge.\n"
        "3. Rely only on factual context. Do not speculate or extrapolate.\n"
        "4. Avoid referencing 'Chunk 1' or 'as mentioned in the text'. Present the answer directly and naturally.\n"
    )

    human_prompt = f"University Document Context:\n{context_text}\n\nQuestion: {query}"

    # 4. Invoke LLM
    try:
        llm = get_llm()
        messages = [SystemMessage(content=system_instruction), HumanMessage(content=human_prompt)]

        logger.info("Sending RAG request to Gemini 2.5 Flash...")
        response = llm.invoke(messages)
        answer = response.content

        # 5. Format sources output list
        formatted_sources = []
        for src, pages in unique_sources.items():
            sorted_pages = sorted(list(pages))
            pages_str = ", ".join(str(p) for p in sorted_pages)
            formatted_sources.append({"document": src, "pages": pages_str})

        return {"answer": answer, "sources": formatted_sources, "retrieved_chunks": chunks}

    except ValueError as ve:
        return {"answer": f"⚠️ Configuration Error: {str(ve)}", "sources": [], "retrieved_chunks": []}
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        return {"answer": f"❌ Error generating response: {str(e)}", "sources": [], "retrieved_chunks": []}
