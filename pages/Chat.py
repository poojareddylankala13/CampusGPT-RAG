import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import time
import json

from modules.auth import check_auth
from modules.ui import inject_custom_css, render_sidebar
from modules.llm_local import is_llama_available, generate_local_response_stream
from modules.database import get_chat_history, add_chat_entry, clear_chat_history, add_evaluation_log
from modules.feedback import submit_feedback
from modules.rag_pipeline import execute_rag_pipeline, execute_retrieval, write_query_cache, get_query_cache_key

# 1. Auth Guard
check_auth()

# 2. Styling and Navigation
inject_custom_css()
render_sidebar()

# PDF generation helper
class ChatTranscriptPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(27, 54, 93)  # Navy
        self.cell(0, 10, 'CampusGPT University Chat Transcript', 0, 1, 'C')
        self.set_draw_color(197, 160, 89)  # Gold
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(8)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_transcript(history):
    pdf = ChatTranscriptPDF()
    pdf.add_page()
    
    for i, entry in enumerate(history):
        # Header
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(197, 160, 89)  # Gold
        pdf.cell(0, 6, f"Query #{i+1} - {entry['timestamp']}", ln=True)
        pdf.ln(1)
        
        # Question
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(27, 54, 93)  # Navy
        pdf.multi_cell(0, 6, f"User: {entry['question']}")
        pdf.ln(1)
        
        # Answer
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.multi_cell(0, 5, f"CampusGPT: {entry['answer']}")
        pdf.ln(2)
        
        # Sources
        if entry.get('sources'):
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            sources_txt = []
            for s in entry['sources']:
                pct_str = f" [Match: {s['score']*100:.1f}%]" if 'score' in s else ""
                sources_txt.append(f"{s['document']} (Page {s.get('page', s.get('pages', 'N/A'))}){pct_str}")
            pdf.multi_cell(0, 5, "Sources: " + ", ".join(sources_txt))
            
        pdf.ln(4)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        
    return bytes(pdf.output())

# Header layout
st.markdown("<h1 class='gradient-header'>💬 CampusGPT AI Chat Assistant</h1>", unsafe_allow_html=True)

# Active Mode Pill
active_mode = st.session_state.get('ai_mode', 'gemini')
active_emb = st.session_state.get('embedding_model', 'bge-small')
active_ret = st.session_state.get('retrieval_method', 'similarity')

mode_badge = "☁️ Gemini API Mode" if active_mode == "gemini" else f"⚙️ Local Model Mode ({st.session_state.get('active_gguf_model', 'GGUF')})"
st.markdown(
    f"<span style='background-color: #eef2f6; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600; color: #1b365d;'>"
    f"Active Framework: <b>{mode_badge}</b> | Embeddings: <b>{active_emb.upper()}</b> | Search: <b>{active_ret.upper()}</b>"
    f"</span>", 
    unsafe_allow_html=True
)
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

user_id = st.session_state.user_id

# Retrieve existing chat history from SQLite
chat_history = get_chat_history(user_id)

# --- Chat history display ---
chat_container = st.container()

with chat_container:
    for chat in chat_history:
        # User message
        st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-sender">You</div>
                <div class="chat-content">{chat['question']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Assistant message
        st.markdown(f"""
            <div class="chat-message assistant">
                <div class="chat-sender">CampusGPT</div>
                <div class="chat-content">{chat['answer']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Traceable Sources Expander
        if chat.get('sources'):
            with st.expander("🔍 Citations & Source Text Previews", expanded=False):
                for idx, src in enumerate(chat['sources']):
                    doc_name = src.get('document', 'Unknown')
                    page_num = src.get('page', src.get('pages', 'N/A'))
                    score_pct = src.get('score', 0.0) * 100
                    preview = src.get('preview', 'No preview available.')
                    
                    st.markdown(f"""
                        <div style="background-color: #fafafa; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #c5a059;">
                            <span style="font-weight: 600; font-size: 12px; color: #1b365d;">#{idx+1} {doc_name} (Page {page_num})</span>
                            <span style="float: right; font-size: 11px; font-weight: 700; color: #197269; background-color: rgba(46, 196, 182, 0.1); padding: 2px 6px; border-radius: 10px;">🎯 {score_pct:.1f}% Match</span>
                            <p style="font-size: 12px; line-height: 1.4; color: #555; margin-top: 5px; font-family: monospace; white-space: pre-wrap;">{preview}</p>
                        </div>
                    """, unsafe_allow_html=True)

# --- Chat inputs and generation ---
user_query = st.chat_input("Enter your question here...")

if user_query:
    # Render user query instantly
    st.markdown(f"""
        <div class="chat-message user">
            <div class="chat-sender">You</div>
            <div class="chat-content">{user_query}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Retrieve current active settings
    settings = {
        "ai_mode": active_mode,
        "embedding_model": active_emb,
        "retrieval_method": active_ret,
        "top_k": st.session_state.get('top_k', 5),
        "threshold": st.session_state.get('threshold', 0.6),
        "active_gguf_model": st.session_state.get('active_gguf_model', ''),
        "context_len": 2048 # local GGUF default context size
    }
    
    # Check if this exact query is cached
    from modules.rag_pipeline import get_query_cache_key, lookup_query_cache
    cache_key = get_query_cache_key(user_query, settings)
    cached_res = lookup_query_cache(cache_key)
    
    if cached_res:
        with st.chat_message("assistant"):
            st.markdown(cached_res['answer'])
        # Save to database history
        chat_id = add_chat_entry(user_id, user_query, cached_res['answer'], cached_res['sources'])
        st.session_state.last_chat_id = chat_id
        st.rerun()
        
    else:
        # Generate Fresh Response
        if active_mode == 'gemini':
            # Run cloud pipeline synchronously
            with st.spinner("Querying Gemini API and indexing contexts..."):
                res = execute_rag_pipeline(user_query, settings)
                
            # Render response
            st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="chat-sender">CampusGPT</div>
                    <div class="chat-content">{res['answer']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Format sources for database
            db_sources = []
            for chunk in res['retrieved_chunks']:
                db_sources.append({
                    "document": chunk['metadata'].get('source', 'Unknown'),
                    "page": chunk['metadata'].get('page', 0) + 1,
                    "score": chunk['score'],
                    "preview": chunk['content'][:300] + "..."
                })
                
            chat_id = add_chat_entry(user_id, user_query, res['answer'], db_sources)
            st.session_state.last_chat_id = chat_id
            st.rerun()
            
        else:
            # Local Llama Mode - Run streaming chunking
            retrieval_start = time.time()
            chunks = execute_retrieval(user_query, settings)
            retrieval_time = time.time() - retrieval_start
            
            if not chunks:
                ans = "I'm sorry, but I couldn't retrieve any relevant context from the uploaded university documents."
                st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="chat-sender">CampusGPT</div>
                        <div class="chat-content">{ans}</div>
                    </div>
                """, unsafe_allow_html=True)
                add_chat_entry(user_id, user_query, ans, [])
                st.rerun()
            else:
                context_blocks = []
                unique_sources = {}
                total_context_len = 0
                sum_similarity = 0.0
                db_sources = []
                
                for idx, chunk in enumerate(chunks):
                    src_name = chunk['metadata'].get('source', 'Unknown')
                    page_num = chunk['metadata'].get('page', 0)
                    display_page = page_num + 1 if isinstance(page_num, int) else page_num
                    sum_similarity += chunk['score']
                    
                    db_sources.append({
                        "document": src_name,
                        "page": display_page,
                        "score": chunk['score'],
                        "preview": chunk['content'][:300] + "..."
                    })
                    
                    context_blocks.append(f"--- Context {idx+1} | Source: {src_name} (Page {display_page}) ---\n{chunk['content']}")
                    total_context_len += len(chunk['content'])
                    
                context_text = "\n\n".join(context_blocks)
                avg_similarity = sum_similarity / len(chunks) if chunks else 0.0
                
                system_instruction = (
                    "You are CampusGPT, an intelligent AI-powered University Knowledge Assistant.\n"
                    "Your task is to answer the user's question using ONLY the provided university document context below.\n\n"
                    "Guidelines:\n"
                    "1. Answer the question thoroughly and factually based strictly on the context.\n"
                    "2. If the context does not contain the answer, reply exactly: "
                    "\"I'm sorry, but I couldn't find the answer to your question in the uploaded university documents.\"\n"
                    "3. Present the answer directly and naturally without referring to 'Context 1' or 'the context'."
                )
                prompt_text = f"University Document Context:\n{context_text}\n\nQuestion: {user_query}"
                
                # Check model configuration
                active_model = settings.get("active_gguf_model", "")
                if not active_model:
                    st.error("⚠️ No GGUF model is selected. Go to Settings/Models page first.")
                elif not is_llama_available():
                    st.error("❌ Llama.cpp binding package is not available.")
                else:
                    # Stream tokens in real-time inside the chat bubble
                    with st.chat_message("assistant"):
                        answer_placeholder = st.empty()
                        assembled_chunks = []
                        
                        generation_start = time.time()
                        stream = generate_local_response_stream(
                            prompt=prompt_text,
                            model_filename=active_model,
                            system_prompt=system_instruction,
                            context_len=settings.get("context_len", 2048)
                        )
                        for token in stream:
                            assembled_chunks.append(token)
                            # Render current typing effect
                            answer_placeholder.markdown("".join(assembled_chunks) + " ▌")
                        
                        generation_time = time.time() - generation_start
                        final_answer = "".join(assembled_chunks)
                        answer_placeholder.markdown(final_answer)
                        
                    # Save metrics and write to query cache
                    add_evaluation_log(
                        query=user_query,
                        ai_mode=f"local ({active_model})",
                        retrieval_time=retrieval_time,
                        generation_time=generation_time,
                        chunk_count=len(chunks),
                        avg_similarity=avg_similarity,
                        context_length=total_context_len
                    )
                    
                    response_dict = {
                        "answer": final_answer,
                        "sources": db_sources,
                        "retrieved_chunks": chunks,
                        "retrieval_time": f"{retrieval_time:.3f}s",
                        "generation_time": f"{generation_time:.3f}s"
                    }
                    if "❌" not in final_answer and "⚠️" not in final_answer:
                        write_query_cache(cache_key, response_dict)
                        
                    chat_id = add_chat_entry(user_id, user_query, final_answer, db_sources)
                    st.session_state.last_chat_id = chat_id
                    st.rerun()

# --- Feedback & Actions ---
if chat_history:
    last_chat = chat_history[-1]
    last_chat_id = last_chat['id']
    
    st.markdown("---")
    col_fb_lbl, col_fb_btn1, col_fb_btn2, col_clear = st.columns([4, 1, 1, 2])
    
    with col_fb_lbl:
        st.write("Rate the last AI response:")
        
    with col_fb_btn1:
        if st.button("👍 Helpful", key="btn_helpful", use_container_width=True):
            submit_feedback(last_chat_id, user_id, "helpful")
            st.toast("Thank you for your feedback!", icon="👍")
            
    with col_fb_btn2:
        if st.button("👎 Not Helpful", key="btn_unhelpful", use_container_width=True):
            submit_feedback(last_chat_id, user_id, "not_helpful")
            st.toast("Thank you for your feedback!", icon="👎")
            
    with col_clear:
        if st.button("🗑️ Clear History", key="btn_clear_chat", use_container_width=True):
            clear_chat_history(user_id)
            st.toast("Chat history cleared.")
            st.rerun()

    # --- Export Panel ---
    st.markdown("### 📤 Export Transcript")
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        try:
            pdf_bytes = generate_pdf_transcript(chat_history)
            st.download_button(
                label="📥 Download PDF Transcript",
                data=pdf_bytes,
                file_name="campusgpt_chat_transcript.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            
    with exp_col2:
        csv_data = []
        for chat in chat_history:
            srcs = []
            if chat.get('sources'):
                for s in chat['sources']:
                    pct_str = f" [Match: {s['score']*100:.1f}%]" if 'score' in s else ""
                    srcs.append(f"{s['document']} (p. {s.get('page', s.get('pages', 'N/A'))}){pct_str}")
            csv_data.append({
                "Timestamp": chat['timestamp'],
                "User Question": chat['question'],
                "AI Response": chat['answer'],
                "Citations": ", ".join(srcs)
            })
        df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download CSV Transcript",
            data=csv_buffer.getvalue(),
            file_name="campusgpt_chat_transcript.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("No active conversation logs. Type your first question below to begin.")
