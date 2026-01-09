from pinecone.grpc import PineconeGRPC as Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("PINECONE_API_KEY"))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")


def get_pinecone_index(api_key: str = PINECONE_API_KEY, index_host: str = PINECONE_INDEX_HOST):
    """
    Initialize Pinecone client and return the Index object.

    Args:
        api_key (str): Your Pinecone API key.
        index_host (str): Host URL for your Pinecone index.

    Returns:
        pinecone.grpc.Index: Pinecone Index object ready for upserts or queries.
    """
    pc = Pinecone(api_key=api_key)
    index = pc.Index(host=index_host)
    return index


# Example usage
if __name__ == "__main__":
    index = get_pinecone_index()
    print(os.getenv("PINECONE_API_KEY"))