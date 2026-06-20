from datetime import datetime

import streamlit as st
from fpdf import FPDF

from modules.auth import check_auth
from modules.database import list_documents
from modules.summarizer import generate_document_summary
from modules.ui import inject_custom_css, render_sidebar

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()


# Custom PDF generator for document summaries
class DocumentSummaryPDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 14)
        self.set_text_color(27, 54, 93)  # Navy
        self.cell(0, 10, "CampusGPT Document Summary Report", 0, 1, "C")
        self.set_draw_color(197, 160, 89)  # Gold
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def create_summary_pdf(doc_name, summary_text):
    pdf = DocumentSummaryPDF()
    pdf.add_page()

    # Metadata Block
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(197, 160, 89)  # Gold
    pdf.cell(0, 8, f"Document: {doc_name}", ln=True)
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Body text
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(51, 51, 51)

    lines = summary_text.split("\n")
    for line in lines:
        if line.startswith("###") or line.startswith("##"):
            cleaned_heading = line.replace("###", "").replace("##", "").strip()
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(27, 54, 93)  # Navy
            pdf.cell(0, 7, cleaned_heading, ln=True)
            pdf.ln(1)
        elif line.startswith("-") or line.startswith("*"):
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(51, 51, 51)
            # Indent bullet point
            pdf.multi_cell(0, 5, f"  {line}")
        elif line.strip():
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(51, 51, 51)
            pdf.multi_cell(0, 5, line)

    return bytes(pdf.output())


# Header layout
st.markdown("<h1 class='gradient-header'>📄 Document Summarization</h1>", unsafe_allow_html=True)
st.markdown(
    "Select an indexed university PDF and generate a structured executive summary, including important policies, deadlines, and key highlights."
)

# Load available documents
docs = list_documents()

if not docs:
    st.info("No documents are currently indexed. Please upload documents first on the Upload page.")
else:
    # Build dropdown select box options
    doc_options = {doc["name"]: doc for doc in docs}
    selected_doc_name = st.selectbox("Select document to summarize:", list(doc_options.keys()))

    # Initialize session state for cached summary values
    if "active_summary_name" not in st.session_state:
        st.session_state.active_summary_name = ""
    if "active_summary_content" not in st.session_state:
        st.session_state.active_summary_content = ""

    if st.button("🪄 Generate AI Summary", use_container_width=True):
        doc_details = doc_options[selected_doc_name]
        file_path = doc_details["file_path"]

        with st.spinner("Analyzing document text and drafting executive report..."):
            summary_markdown = generate_document_summary(selected_doc_name, file_path)

            # Save to session state to prevent reruns clearing the display
            st.session_state.active_summary_name = selected_doc_name
            st.session_state.active_summary_content = summary_markdown

    # Check if a summary exists for the currently selected document (either generated or restored)
    if st.session_state.active_summary_content and st.session_state.active_summary_name == selected_doc_name:
        st.markdown("---")
        st.markdown(f"### 📊 Report: {st.session_state.active_summary_name}")

        # Display the summary inside a styled container
        st.markdown(
            f"""
            <div style="background-color: #fcfdfe; padding: 25px; border: 1px solid rgba(27, 54, 93, 0.1); border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                {st.session_state.active_summary_content}
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Export panel
        st.markdown("#### 📥 Export Summary")
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            # Export TXT
            st.download_button(
                label="📥 Download TXT Summary",
                data=st.session_state.active_summary_content,
                file_name=f"{st.session_state.active_summary_name.replace('.pdf', '')}_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with exp_col2:
            # Export PDF
            try:
                pdf_bytes = create_summary_pdf(
                    st.session_state.active_summary_name, st.session_state.active_summary_content
                )
                st.download_button(
                    label="📥 Download PDF Summary Report",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.active_summary_name.replace('.pdf', '')}_summary_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error exporting PDF summary: {e}")
