import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def get_pinecone_index(index_name: str):
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY is not set in environment")
    
    # Initialize the modern client
    pc = Pinecone(api_key=api_key)
    # Return the index instance
    return pc.Index(index_name)

if __name__ == "__main__":
    index = get_pinecone_index()
    if index:
        print("Successfully connected to Pinecone!")