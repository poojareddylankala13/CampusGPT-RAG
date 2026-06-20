from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from modules.summarizer import generate_document_summary


def test_generate_document_summary_gemini():
    dummy_pages = [Document(page_content="This is the first page content.", metadata={"source": "doc.pdf", "page": 0})]

    with patch("modules.summarizer.validate_and_load_pdf") as mock_load:
        mock_load.return_value = dummy_pages

        with patch("modules.summarizer.get_llm") as mock_llm_loader:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "### 📋 Executive Summary\nThis is a mock summary."
            mock_llm.invoke.return_value = mock_response
            mock_llm_loader.return_value = mock_llm

            with patch("streamlit.session_state", {"ai_mode": "gemini"}):
                res = generate_document_summary("test_doc.pdf", "dummy_path.pdf")
                assert "Executive Summary" in res
                assert "mock summary" in res
                mock_load.assert_called_once_with("dummy_path.pdf")


def test_generate_document_summary_local():
    dummy_pages = [Document(page_content="This is the first page content.", metadata={"source": "doc.pdf", "page": 0})]

    with patch("modules.summarizer.validate_and_load_pdf") as mock_load:
        mock_load.return_value = dummy_pages

        # Mock generator stream for local response
        def mock_stream(*args, **kwargs):
            yield "### 📋 Executive Summary\n"
            yield "This is a mock offline summary."

        with patch("modules.llm_local.generate_local_response_stream", side_effect=mock_stream):
            with patch("modules.llm_local.is_llama_available", return_value=True):
                session_state = {
                    "ai_mode": "local",
                    "active_gguf_model": "qwen.gguf",
                }
                with patch("streamlit.session_state", session_state):
                    res = generate_document_summary("test_doc.pdf", "dummy_path.pdf")
                    assert "Executive Summary" in res
                    assert "mock offline summary" in res
