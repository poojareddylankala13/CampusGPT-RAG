import logging
from modules.pdf_loader import validate_and_load_pdf
from modules.rag_chain import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger("CampusGPT.summarizer")

def generate_document_summary(doc_name, file_path):
    """Loads a PDF document and generates a structured summary using Gemini.
    
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
    
    try:
        # 1. Load PDF pages
        pages = validate_and_load_pdf(file_path)
        
        # 2. Extract full text
        full_text = ""
        for i, page in enumerate(pages):
            full_text += f"\n--- Page {i+1} ---\n{page.page_content}\n"
            
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
        
        human_prompt = f"Document Name: {doc_name}\n\nDocument Text:\n{full_text}"
        
        # 4. Invoke Gemini
        llm = get_llm()
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=human_prompt)
        ]
        
        logger.info(f"Invoking LLM for summarization on {doc_name}...")
        response = llm.invoke(messages)
        summary_markdown = response.content
        
        return summary_markdown
        
    except ValueError as ve:
        return f"⚠️ Configuration Error: {str(ve)}"
    except Exception as e:
        logger.error(f"Error generating summary for {doc_name}: {str(e)}")
        return f"❌ Error generating summary: {str(e)}"
