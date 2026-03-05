import os
import pickle
import faiss
import numpy as np


class VectorStore:
    def __init__(self, embedding_dim=3072):
        self.embedding_dim = embedding_dim
        self.chunks = []       
        self.index = None      

    def build(self, chunks, embeddings):
        print(f"[VectorStore] Building index with {len(chunks)} chunks...")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / np.maximum(norms, 1e-10)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(normalized)
        self.chunks = chunks
        print(f"[VectorStore] Index built! Total vectors: {self.index.ntotal}")

    def add(self, new_chunks, new_embeddings):
        if self.index is None:
            self.build(new_chunks, new_embeddings)
            return
        norms = np.linalg.norm(new_embeddings, axis=1, keepdims=True)
        normalized = new_embeddings / np.maximum(norms, 1e-10)
        self.index.add(normalized)
        self.chunks.extend(new_chunks)
        print(f"[VectorStore] Added {len(new_chunks)} chunks. Total: {self.index.ntotal}")

    def search(self, query_vector, top_k=3):
        if self.index is None or self.index.ntotal == 0:
            return []
        query = query_vector.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(query)
        query = query / max(norm, 1e-10)
        scores, indices = self.index.search(query, min(top_k, self.index.ntotal))
        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx == -1:
                continue
            results.append({
                "chunk": self.chunks[idx],   
                "score": float(score),        
                "rank": rank + 1 
            })
        return results

    def save(self, directory="vector_store"):
        os.makedirs(directory, exist_ok=True)
        faiss.write_index(self.index, os.path.join(directory, "faiss.index"))
        with open(os.path.join(directory, "chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)
        print(f"[VectorStore] Saved to '{directory}' folder")

    def load(self, directory="vector_store"):
        index_path = os.path.join(directory, "faiss.index")
        chunks_path = os.path.join(directory, "chunks.pkl")
        if not os.path.exists(index_path):
            print("[VectorStore] No saved index found. Starting fresh.")
            return
        self.index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)
        print(f"[VectorStore] Loaded {self.index.ntotal} vectors from disk")

    @property
    def total_chunks(self):
        return len(self.chunks)


