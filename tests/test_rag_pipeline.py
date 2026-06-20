from unittest.mock import MagicMock, patch

from modules.database import get_evaluation_metrics_logs
from modules.rag_pipeline import clear_query_cache, execute_rag_pipeline


def test_rag_pipeline_execution_and_caching():
    # 1. Clear query cache
    clear_query_cache()

    # 2. Mock execute_retrieval results
    retrieved_chunks = [
        {
            "content": "Attendance condonation is 65% minimum on medical grounds.",
            "metadata": {"source": "Handbook.pdf", "page": 0},
            "score": 0.88,
        }
    ]

    # Setup mocks
    with patch("modules.rag_pipeline.execute_retrieval") as mock_ret:
        mock_ret.return_value = retrieved_chunks

        with patch("modules.rag_chain.get_llm") as mock_llm_loader:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "According to Handbook.pdf, attendance condonation requires a minimum of 65%."
            mock_llm.invoke.return_value = mock_response
            mock_llm_loader.return_value = mock_llm

            settings = {
                "ai_mode": "gemini",
                "embedding_model": "bge-small",
                "retrieval_method": "similarity",
                "top_k": 5,
                "threshold": 0.6,
            }

            # 3. Run Pipeline (first run, should execute retrieval + invoke LLM + save cache)
            res = execute_rag_pipeline("what is the condonation attendance limit?", settings)

            assert "65%" in res["answer"]
            assert len(res["sources"]) == 1
            assert res["sources"][0]["document"] == "Handbook.pdf"

            # 4. Verify RAG performance logs in SQLite
            logs = get_evaluation_metrics_logs(limit=5)
            assert len(logs) > 0
            assert logs[0]["query"] == "what is the condonation attendance limit?"
            assert logs[0]["ai_mode"] == "gemini"
            assert logs[0]["chunk_count"] == 1
            assert logs[0]["avg_similarity"] == 0.88

            # 5. Verify Query Cache Hit (second run, should return cached results instantly)
            # Replace invoke with AssertionError to check that LLM is not called!
            mock_llm.invoke = MagicMock(side_effect=AssertionError("Should hit query cache and not call LLM!"))

            res_cached = execute_rag_pipeline("what is the condonation attendance limit?", settings)
            assert "65%" in res_cached["answer"]

            # Clean up query cache
            clear_query_cache()
