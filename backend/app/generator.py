import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
class Generator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, question, context, no_context=False):
        if not no_context:
            system_prompt = """You are a helpful academic assistant for Rowan University MSCS students.

You have been given relevant excerpts from the student's curriculum documents.

RULES:
1. Answer primarily using the provided context
2. Always cite your source like this: (Source: filename, Page X)
3. If the context partially answers the question, use it AND
   supplement with your general knowledge — clearly saying:
   "Based on your curriculum... Additionally from general knowledge..."
4. Only if context has NOTHING relevant, answer from general
   knowledge and say: "This wasn't in your uploaded curriculum,
   but generally speaking..."
5. Be clear, helpful and easy to understand
6. Keep answers focused on MSCS / Computer Science topics"""

            prompt = f"""Here are relevant excerpts from the student's curriculum:

{context}

Based on the above (and your general knowledge if needed), answer:
{question}"""
        else:
            system_prompt = """You are a helpful academic assistant for Rowan University MSCS students.

No relevant documents were found in the curriculum for this question.

RULES:
1. Answer from your general knowledge about CS / MSCS topics
2. Start your answer with:
   "This wasn't found in your uploaded curriculum, but here's what I know:"
3. Be helpful and accurate
4. If question is completely unrelated to academics/CS, politely
   say: "I'm designed to help with MSCS academic topics. Could you
   ask something related to your coursework?"
5. Never make up specific Rowan University policies — only speak
   to general CS/academic knowledge"""

            prompt = question

        print(f"\n[Generator] Sending to Groq...")
        print(f"[Generator] Mode: {'RAG + fallback' if not no_context else 'General knowledge'}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content
        print(f"[Generator] Answer received!")
        return answer