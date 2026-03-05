import os
from app.chunker import PDFChunker
from app.embedder import Embedder
from app.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()


DATA_FOLDER = "data"              
VECTOR_STORE_DIR = "vector_store_data" 
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

chunker = PDFChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
embedder = Embedder()
vector_store = VectorStore(embedding_dim=3072)
def ingest_all_pdfs():
    pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"No PDFs found in '{DATA_FOLDER}' folder!")
        print(f"Please put your curriculum PDFs inside the '{DATA_FOLDER}' folder first.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to ingest:")
    for f in pdf_files:
        print(f"  → {f}")
    print()

    total_chunks = 0
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DATA_FOLDER, pdf_file)
        print(f"Processing: {pdf_file}")
        chunks = chunker.process_pdf(pdf_path)
        if not chunks:
            print(f"Could not read text from {pdf_file}, skipping..")
            continue

        embeddings = embedder.embed_chunks(chunks)
        vector_store.add(chunks, embeddings)
        total_chunks += len(chunks)
        print(f"Done! {len(chunks)} chunks added\n")

    vector_store.save(VECTOR_STORE_DIR)

    print("=" * 50)
    print(f"Ingestion complete!")
    print(f"PDFs processed : {len(pdf_files)}")
    print(f"Total chunks   : {total_chunks}")
    print(f"Saved to       : {VECTOR_STORE_DIR}/")
    print()
    print("Students can now ask questions about the curriculum!")


if __name__ == "__main__":
    ingest_all_pdfs()