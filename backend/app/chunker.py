import os
import PyPDF2
import tiktoken
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: int        
    text: str           
    page_number: int     
    source_file: str    
    token_count: int    

class PDFChunker:
    def __init__(self, chunk_size=300, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    def extract_text(self, pdf_path):
            pages = []
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    text = " ".join(text.split())
                    if text:
                        pages.append({
                            "page_number": i + 1,
                            "text": text
                        })
            return pages
    def split_into_chunks(self, text):
            tokens = self.tokenizer.encode(text)
            chunks = []
            start = 0
            while start < len(tokens):
                end = min(start + self.chunk_size, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                chunks.append(chunk_text)
                if end == len(tokens):
                    break
                start += self.chunk_size - self.chunk_overlap
            return chunks
    def process_pdf(self, pdf_path):
            filename = os.path.basename(pdf_path)
            pages = self.extract_text(pdf_path)

            all_chunks = []
            chunk_id = 0

            for page in pages:
                raw_chunks = self.split_into_chunks(page["text"])
                for text in raw_chunks:
                    token_count = len(self.tokenizer.encode(text))
                    all_chunks.append(Chunk(
                        chunk_id=chunk_id,
                        text=text,
                        page_number=page["page_number"],
                        source_file=filename,
                        token_count=token_count
                    ))
                    chunk_id += 1

            print(f"[Chunker] {filename} → {len(pages)} pages → {len(all_chunks)} chunks")
            return all_chunks


