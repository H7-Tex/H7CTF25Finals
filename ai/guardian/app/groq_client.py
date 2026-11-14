from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def get_ai_response(user_prompt):
    try:
        completion = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": Config.get_system_prompt()
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_OUTPUT_TOKENS,
            top_p=Config.TOP_P,
            presence_penalty=Config.PRESENCE_PENALTY,
            frequency_penalty=Config.FREQUENCY_PENALTY,
        )
        
        response = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens
        
        return response, tokens_used
        
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")
