# Specification: Semantic Campus Search

---

## 1. Purpose
Allows users to perform raw semantic keyword queries against the FAISS vector database and view matching snippets sorted by similarity score.

---

## 2. Functional Requirements
*   **Vector Search**: Convert user query keywords into embedding vectors and retrieve matching document chunks.
*   **Cosine Similarity conversion**: Convert raw L2 distance scores returned by FAISS into readable percentages: `Cosine Similarity = 1 - (L2_dist^2)/2`.
*   **Result Displays**: Sort matches in descending order of similarity score. Render matched text previews alongside source document links and page numbers.

---

## 3. Inputs
*   `query` (string): User search keywords.
*   `threshold` (float): Minimum similarity score cutoff.
*   `top_k` (int): Maximum number of matches to retrieve.

---

## 4. Outputs
*   Renders formatted cards for each matching document chunk meeting the similarity score requirements.

---

## 5. Dependencies
*   FAISS vector store index.
*   `CachedLocalEmbeddings` wrapper.
*   Streamlit UI container elements.

---

## 6. Error Handling
*   If no matching chunks are found, display: `"No matches found meeting the minimum similarity threshold. Try lowering the threshold."`
*   If the index is missing, degrade to alert notifications.

---

## 7. Future Improvements
*   Add fuzzy search fallback if vector search fails.
*   Highlight query terms in the retrieved text snippets.
*   Support sorting search results by date uploaded or document source.
