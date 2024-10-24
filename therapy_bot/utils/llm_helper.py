from groq import Groq
from typing import Dict
from config.settings import GROQ_API_KEY

class LLMHelper:
    def __init__(self):
        self.groq_client = Groq(api_key=GROQ_API_KEY)

    async def get_response(self, prompt: str, user_context: Dict = None) -> str:
        language = user_context.get('language', 'english') if user_context else 'english'

        system_prompt = """You are a compassionate and supportive therapy chat bot. Your responses should be:
        1. Empathetic and understanding
        2. Encouraging but not dismissive of negative feelings
        3. Professional while maintaining a warm tone
        4. Keep to at most 2-3 sentences per response
        Never recommend medical advice or try to diagnose conditions. But give tips on how to overcome negative feelings. Answer in {language}."""
        
        context = ""
        if user_context:
            context = f"\nUser's previous mood rating: {user_context.get('mood_rating', 'Unknown')}\nLast message: {user_context.get('last_message', 'None')}"
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context}\n\nUser message: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return "Sorry the LLM ain't working right now. Please try again later."