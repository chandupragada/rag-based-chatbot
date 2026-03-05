import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
class Generator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, question, context):
        print(f"\n[Generator] Sending to Groq (Llama 3)...")
        print(f"[Generator] Context length: {len(context)} characters")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful academic assistant.
You answer questions based ONLY on the context provided from the student's college curriculum.

STRICT RULES:
1. Only use information from the provided context
2. Always cite your source like this: (Source: filename, Page X)
3. If the answer is not in the context say:
   'I couldn't find this in your uploaded curriculum.'
4. Be clear and easy to understand
5. If multiple chunks are relevant, combine them into one clear answer"""
                },
                {
                    "role": "user",
                    "content": f"""Here are the relevant excerpts from the curriculum:

{context}

Based on the above, please answer this question:
{question}"""
                }
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content
        print(f"[Generator] Answer received!")
        return answer