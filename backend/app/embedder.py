import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from app.chunker import Chunk

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Embedder:
    def __init__(self):
        self.model = "models/gemini-embedding-001"

    def embed_text(self, text):
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        return np.array(result["embedding"], dtype=np.float32)

    def embed_query(self, text):
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return np.array(result["embedding"], dtype=np.float32)

    def embed_chunks(self, chunks):
        print(f"[Embedder] Embedding {len(chunks)} chunks...")
        all_vectors = []
        for i, chunk in enumerate(chunks):
            vector = self.embed_text(chunk.text)
            all_vectors.append(vector)
            if (i + 1) % 10 == 0:
                print(f"[Embedder] Done {i + 1}/{len(chunks)}")
        matrix = np.vstack(all_vectors)
        print(f"[Embedder] Created matrix of shape: {matrix.shape}")
        return matrix



