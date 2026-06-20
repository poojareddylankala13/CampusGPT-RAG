import os
from collections.abc import Generator

import pytest
from fpdf import FPDF

from modules.document_parser import extract_document_metadata, extract_pdf_markdown, extract_pdf_text


@pytest.fixture
def temp_test_pdf() -> Generator[str, None, None]:
    """Fixture to dynamically generate a two-page PDF file for testing."""
    os.makedirs("tests", exist_ok=True)
    pdf_path = "tests/temp_test_doc.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Academic Syllabus CS-101", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 6, "This is page one of our university syllabus.\nAttendance minimum is 75% for classes.")

    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Evaluation Guidelines", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 6, "This is page two of our university syllabus.\nMid-semester exams start on October 12.")

    pdf.output(pdf_path)

    yield pdf_path

    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass


def test_extract_pdf_markdown(temp_test_pdf):
    # Test page-by-page extraction
    docs = extract_pdf_markdown(temp_test_pdf)

    assert len(docs) == 2
    assert docs[0].metadata["page"] == 0
    assert docs[1].metadata["page"] == 1
    assert docs[0].metadata["source"] == "temp_test_doc.pdf"

    # Check that text content contains clean markdown keywords
    assert "Academic Syllabus CS-101" in docs[0].page_content
    assert "Attendance minimum is 75%" in docs[0].page_content
    assert "Evaluation Guidelines" in docs[1].page_content
    assert "Mid-semester exams start on October 12" in docs[1].page_content


def test_extract_pdf_text(temp_test_pdf):
    # Test full text compilation
    full_text = extract_pdf_text(temp_test_pdf)
    assert "Academic Syllabus CS-101" in full_text
    assert "Evaluation Guidelines" in full_text
    assert len(full_text) > 50


def test_extract_document_metadata(temp_test_pdf):
    # Test metadata dictionary extraction
    meta = extract_document_metadata(temp_test_pdf)
    assert meta["file_name"] == "temp_test_doc.pdf"
    assert meta["page_count"] == 2
    assert meta["file_size"] > 0
    assert "upload_date" in meta
