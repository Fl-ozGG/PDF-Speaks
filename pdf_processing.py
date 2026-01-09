from pypdf import PdfReader
from tqdm import tqdm
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import uuid


def extract_text_from_pdf(pdf_path: str) -> list[str]:

    reader = PdfReader(pdf_path)
    pages = []

    for page in tqdm(reader.pages, desc="Extracting pages"):
        text = page.extract_text()
        if text:
            pages.append(text)
    return pages

def clean_text(text: str) -> str:

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)          # multiple spaces → 1
    text = re.sub(r"-\s+", "", text)          # remove hyphen breaks
    text = text.strip()
    return text

def chunk_texts(texts: List[str], chunk_size=500, chunk_overlap=100) -> List[str]:
    """
    Split large text into chunks for vectorization.
    Uses overlap to preserve context between chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    all_chunks = []
    for text in texts:
        cleaned = clean_text(text)
        chunks = splitter.split_text(cleaned)
        all_chunks.extend(chunks)
    return all_chunks

def process_pdf_for_user(user_id: str, pdf_path: str) -> dict:

    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_texts(pages)
    processed_chunks = []
    document_id = str(uuid.uuid4())

    for idx, chunk in enumerate(chunks):
        processed_chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "document_id": document_id,
            "user_id": user_id,
            "text": chunk,
            "page": idx // (len(chunks)//len(pages) + 1),
            "chunk_index": idx
        })

    return {
        "document_id": document_id,
        "chunks": processed_chunks
    }