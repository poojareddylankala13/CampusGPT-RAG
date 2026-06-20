import os
import shutil
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from modules.vector_store import add_chunks_to_store, get_index_dir, load_vector_store


# Mock Embeddings stub
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, text):
        return [0.1] * 384


def test_faiss_vector_store():
    # Setup test index folder path
    test_index_dir = get_index_dir()
    if os.path.exists(test_index_dir):
        try:
            shutil.rmtree(test_index_dir)
        except Exception:
            pass

    with patch("modules.vector_store.get_active_embeddings") as mock_emb:
        mock_emb.return_value = MockEmbeddings()

        # 1. Verify index doesn't load when empty
        store_empty = load_vector_store()
        assert store_empty is None

        # 2. Add chunks to vector store
        chunks = [
            Document(
                page_content="Policy 1: Condonation requirement is 65% attendance.",
                metadata={"source": "DocA.pdf", "page": 0},
            ),
            Document(
                page_content="Policy 2: Semester exams start on Dec 10.", metadata={"source": "DocA.pdf", "page": 1}
            ),
        ]

        success = add_chunks_to_store(chunks)
        assert success is True

        # 3. Load vector store and verify chunks
        store = load_vector_store()
        assert store is not None

        # 4. Search verification
        docs_and_scores = store.similarity_search_with_score("attendance condonation", k=1)
        assert len(docs_and_scores) == 1
        assert docs_and_scores[0][0].metadata["source"] == "DocA.pdf"
        assert "Policy 1" in docs_and_scores[0][0].page_content

        # Clean up files created
        if os.path.exists(test_index_dir):
            try:
                shutil.rmtree(test_index_dir)
            except Exception:
                pass
