import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import json

from modules.auth import check_auth
from modules.ui import inject_custom_css, render_sidebar
from modules.rag_chain import generate_rag_answer
from modules.database import get_chat_history, add_chat_entry, clear_chat_history
from modules.feedback import submit_feedback

# 1. Auth Guard
check_auth()

# 2. Styling and Navigation
inject_custom_css()
render_sidebar()

# Custom PDF class for chat logs
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
        pdf.set_text_color(51, 51, 51)  # Dark Charcoal
        pdf.multi_cell(0, 5, f"CampusGPT: {entry['answer']}")
        pdf.ln(2)
        
        # Sources
        if entry.get('sources'):
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            src_str = ", ".join([f"{s['document']} (Page {s['pages']})" for s in entry['sources']])
            pdf.multi_cell(0, 5, f"Sources: {src_str}")
            
        pdf.ln(4)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        
    return bytes(pdf.output())

# Header layout
st.markdown("<h1 class='gradient-header'>💬 CampusGPT AI Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("Ask natural language questions about course requirements, handbooks, placement criteria, or calendars.")

user_id = st.session_state.user_id

# Retrieve existing chat history from SQLite
chat_history = get_chat_history(user_id)

# --- Chat history display ---
chat_container = st.container()

with chat_container:
    for chat in chat_history:
        # User message bubble
        st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-sender">You</div>
                <div class="chat-content">{chat['question']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Assistant message bubble
        sources_html = ""
        if chat.get('sources'):
            pills = "".join([f"<span class='source-pill'>📄 {s['document']} (p. {s['pages']})</span>" for s in chat['sources']])
            sources_html = f"<div class='source-pill-container'>{pills}</div>"
            
        st.markdown(f"""
            <div class="chat-message assistant">
                <div class="chat-sender">CampusGPT</div>
                <div class="chat-content">{chat['answer']}</div>
                {sources_html}
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
    
    with st.spinner("Analyzing university documents..."):
        # Run RAG
        result = generate_rag_answer(user_query)
        
        # Save to database
        chat_id = add_chat_entry(user_id, user_query, result['answer'], result['sources'])
        st.session_state.last_chat_id = chat_id
        
        # Rerun to render new history
        st.rerun()

# --- Feedback & Actions for Last Answer ---
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
        # Export PDF
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
        # Export CSV
        csv_data = []
        for chat in chat_history:
            srcs = ", ".join([f"{s['document']} (p. {s['pages']})" for s in chat['sources']]) if chat.get('sources') else ""
            csv_data.append({
                "Timestamp": chat['timestamp'],
                "User Question": chat['question'],
                "AI Response": chat['answer'],
                "Citations": srcs
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
