#MSCS Academic RAG Chatbot

An intelligent academic chatbot for Rowan University MSCS students that answers questions based on uploaded curriculum documents with exact page citations.Built using a **Retrieval-Augmented Generation (RAG)** pipeline.

##What It Does

- Students ask questions about their MSCS curriculum
- Chatbot finds the most relevant sections from uploaded PDFs
- Answers are grounded **only** in the curriculum — no hallucination
- Every answer shows **exactly which page** the information came from
- Falls back to general CS knowledge when topic isn't in the curriculum
- Handles greetings and casual conversation naturally

## How It Works (RAG Pipeline)
Student Question
      ↓
Convert question to vectors (Gemini Embeddings)
      ↓
Search FAISS vector store for relevant chunks
      ↓
Retrieve top 3 most relevant curriculum sections
      ↓
Send question + retrieved chunks to Groq (Llama 3)
      ↓
Answer grounded in YOUR curriculum + page citations


## Tech Stack
Backend:FastAPI + Python
Vector Search:FAISS
Embeddings:Google Gemini (text-embedding)
LLM:Groq(Llama 3.3 70B)
PDF Processing:PyPDF2+tiktoken
Frontend:HTML+CSS+Vanilla JavaScript

## Setup & Run

### 1. Clone the repository
git clone https://github.com/chandupragada/rag-based-chatbot.git
cd rag-based-chatbot/backend

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up API keys
Create a `.env` file inside `backend/` folder:
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
> Get Gemini key free at: https://aistudio.google.com
> Get Groq key free at: https://console.groq.com

### 5. Add your curriculum PDFs
Put your PDF files inside backend/data/ folder

### 6. Ingest PDFs into knowledge base
python ingest.py

### 7. Start the backend server
python main.py

### 8. Open the chatbot
Open frontend/index.html in your browser
Make sure backend server is running first!

## Cost
This project runs on **free tier APIs only** no credit card needed!
