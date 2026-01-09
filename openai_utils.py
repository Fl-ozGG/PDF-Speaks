from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Chunk vacío, no se puede generar embedding")
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=1024
    )
    return response.data[0].embedding

def generate_answer(question: str, context: str) -> str:
    """Genera una respuesta usando GPT-4o basada en el contexto recuperado."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Puedes usar "gpt-3.5-turbo" si prefieres ahorrar
            messages=[
                {"role": "system", "content": (
                    "Eres un asistente experto. Responde a la pregunta del usuario utilizando "
                    "únicamente el contexto proporcionado a continuación. Si la respuesta no está "
                    "en el contexto, di que no tienes esa información."
                )},
                {"role": "user", "content": f"Contexto:\n{context}\n\nPregunta: {question}"}
            ],
            temperature=0.2  # Temperatura baja para respuestas más precisas
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"