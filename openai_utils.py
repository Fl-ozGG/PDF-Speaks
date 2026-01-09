from openai import OpenAI

client = OpenAI(api_key="OPENAI_API_KEY")

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding
