from app.embedder import Embedder
from app.vector_store import VectorStore
from app.chunker import Chunk

class Retriever:
    def __init__(self, vector_store, embedder, top_k=3):
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k
        self.min_score = 0.3

    def retrieve(self, question):
        print(f"\n[Retriever] Question: '{question[:60]}...'")
        query_vector = self.embedder.embed_query(question)
        raw_results = self.vector_store.search(
            query_vector,
            top_k=self.top_k
        )
        filtered = [r for r in raw_results if r["score"] >= self.min_score]
        if not filtered and raw_results:
            print("[Retriever] Nothing above min_score, using best match anyway")
            filtered = raw_results[:1]

        print(f"[Retriever] Found {len(filtered)} relevant chunks")
        for r in filtered:
            print(f"  → Rank {r['rank']} | Score: {r['score']:.3f} | "
                  f"{r['chunk'].source_file} p.{r['chunk'].page_number}")

        return filtered

    def format_context(self, results):
        if not results:
            return "No relevant documents found in the knowledge base."
        parts = []
        for r in results:
            chunk: Chunk = r["chunk"]
            header = (
                f"[Document {r['rank']} | "
                f"File: {chunk.source_file} | "
                f"Page: {chunk.page_number} | "
                f"Similarity: {r['score']:.2f}]"
            )
            parts.append(f"{header}\n{chunk.text}")

        return "\n\n---\n\n".join(parts)

