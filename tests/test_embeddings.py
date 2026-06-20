from unittest.mock import MagicMock, patch

from langchain_core.embeddings import Embeddings

from modules.embedding_manager import CachedLocalEmbeddings, clear_embeddings_cache


# Fake embeddings stub
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[float(i)] * 384 for i in range(len(texts))]

    def embed_query(self, text):
        return [0.5] * 384


def test_cached_local_embeddings():
    # Clear cache database before test
    clear_embeddings_cache()

    # Mock get_cached_embedding_model to return MockEmbeddings
    with patch("modules.embedding_manager.get_cached_embedding_model") as mock_load:
        mock_load.return_value = MockEmbeddings()

        # Instantiate CachedLocalEmbeddings
        embeddings_wrapper = CachedLocalEmbeddings(model_key="bge-small")

        # Test document embedding (uncached first run)
        texts = ["hello university", "welcome syllabus"]
        vectors = embeddings_wrapper.embed_documents(texts)

        assert len(vectors) == 2
        assert len(vectors[0]) == 384
        assert vectors[0][0] == 0.0
        assert vectors[1][0] == 1.0

        # Verify that they were saved in the SQLite cache DB
        # Run second time - this time it should Hit the cache and not call underlying model!
        # We replace underling_embeddings with a MagicMock that raises an error if called
        embeddings_wrapper.underlying_embeddings.embed_documents = MagicMock(
            side_effect=AssertionError("Should not call embed_documents!")
        )

        cached_vectors = embeddings_wrapper.embed_documents(texts)
        assert len(cached_vectors) == 2
        assert cached_vectors[0][0] == 0.0
        assert cached_vectors[1][0] == 1.0

        # Test query embedding
        embeddings_wrapper.underlying_embeddings.embed_query = MagicMock(
            side_effect=AssertionError("Should not call embed_query!")
        )
        query_text = "hello university"  # already embedded, should hit cache
        query_vector = embeddings_wrapper.embed_query(query_text)
        assert len(query_vector) == 384
        assert query_vector[0] == 0.0

        # Clear cache and verify it was deleted
        clear_embeddings_cache()
