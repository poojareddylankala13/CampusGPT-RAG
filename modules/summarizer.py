import logging

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

from modules.pdf_loader import validate_and_load_pdf
from modules.rag_chain import get_llm

logger = logging.getLogger("CampusGPT.summarizer")


def generate_document_summary(doc_name, file_path):
    """Loads a PDF document and generates a structured summary.

    Routes execution to either cloud Gemini or local Llama.cpp depending on active Settings.

    The structured summary contains:
    - Executive Summary
    - Key Highlights
    - Important Dates
    - Important Policies
    - Action Items

    Args:
        doc_name (str): The name of the document.
        file_path (str): Path to the PDF file.

    Returns:
        str: Markdown formatted summary of the document.
    """
    logger.info(f"Generating summary for {doc_name}...")
    ai_mode = st.session_state.get("ai_mode", "gemini")

    try:
        # 1. Load PDF pages
        pages = validate_and_load_pdf(file_path)

        # 2. Extract full text
        full_text = ""
        for i, page in enumerate(pages):
            full_text += f"\n--- Page {i + 1} ---\n{page.page_content}\n"

        if not full_text.strip():
            return "❌ Could not extract text from the document. The PDF may be scanned or empty."

        # 3. Create prompts for structured summaries
        system_instruction = (
            "You are an expert academic administrator and summarizer. Your goal is to analyze the provided "
            "university document and generate a professional, structured executive summary.\n"
            "You must format the response in clean, beautiful Markdown with the following exact headings:\n\n"
            "### 📋 Executive Summary\n"
            "(Provide a concise 3-4 sentence overview of what this document is about, its target audience, and its core purpose.)\n\n"
            "### ✨ Key Highlights\n"
            "(Bullet points summarizing the 5-7 most important takeaways or rules.)\n\n"
            "### 📅 Important Dates & Deadlines\n"
            "(A list or timeline of any dates, deadlines, schedules, or timeframes mentioned in the document. If none are mentioned, state 'No dates or deadlines mentioned.')\n\n"
            "### ⚖️ Important Policies & Guidelines\n"
            "(Highlight critical rules, regulations, penalties, or compliance policies students or staff need to adhere to.)\n\n"
            "### 🎯 Action Items\n"
            "(Actionable next steps for the reader, e.g., things they must submit, registers, check, or sign.)\n"
        )

        # 4. Invoke LLM based on mode
        if ai_mode == "gemini":
            human_prompt = f"Document Name: {doc_name}\n\nDocument Text:\n{full_text}"
            llm = get_llm()
            messages = [SystemMessage(content=system_instruction), HumanMessage(content=human_prompt)]

            logger.info("Invoking Gemini for document summarization...")
            response = llm.invoke(messages)
            return response.content

        else:
            # Local Llama Mode
            # GGUF models have limited context windows. Prune text safely to ~5000 characters for safety.
            max_chars = 5000
            pruned_text = full_text[:max_chars]
            if len(full_text) > max_chars:
                pruned_text += "\n... [Text truncated for local execution context limit] ..."

            active_model = st.session_state.get("active_gguf_model", "")
            if not active_model:
                return "⚠️ Summarization Error: No local GGUF model is selected. Go to Models page to configure."

            from modules.llm_local import generate_local_response_stream, is_llama_available

            if not is_llama_available():
                return "❌ Summarization Error: Llama.cpp binding is not available in the current environment."

            logger.info(
                f"Invoking local model {active_model} for offline summarization (pruned to {len(pruned_text)} chars)..."
            )
            prompt_text = f"Document Name: {doc_name}\n\nDocument Text:\n{pruned_text}"

            stream = generate_local_response_stream(
                prompt=prompt_text,
                model_filename=active_model,
                system_prompt=system_instruction,
                context_len=4096,  # Set context window slightly larger for summarization task
            )

            assembled_chunks = []
            for chunk in stream:
                assembled_chunks.append(chunk)
            return "".join(assembled_chunks)

    except ValueError as ve:
        return f"⚠️ Configuration Error: {str(ve)}"
    except Exception as e:
        logger.error(f"Error generating summary for {doc_name}: {str(e)}")
        return f"❌ Error generating summary: {str(e)}"
