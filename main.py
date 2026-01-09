from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
import os
import shutil
import uuid


import auth
import database
import pdf_processing
from db_pinecone import get_pinecone_index
from openai_utils import get_embedding, generate_answer


app = FastAPI()

database.init_db()


#----------------- AUTH ENDPOINTS ---------------------------------------------------------------

@app.post("/register", status_code=201)
async def register(username: str = Body(...), password: str = Body(...)):
    if not database.create_user(username, password):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return {"mensaje": f"Usuario {username} creado con éxito"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = database.get_user(form_data.username)
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):


        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = auth.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/perfil")
async def read_users_me(current_user: str = Depends(auth.get_current_user)):
    print(os.getenv("PINECONE_API_KEY"))
    return {"mensaje": f"Hola {current_user}, este es tu perfil privado."}



UPLOAD_DIR = Path("uploaded_pdfs")

UPLOAD_DIR.mkdir(exist_ok=True)

def get_user_folder(user_id: str) -> Path:
    folder = UPLOAD_DIR / user_id
    folder.mkdir(exist_ok=True)
    return folder

#----------------- PDF LOAD ENDPOINTS ---------------------------------------------------------------

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: str = Depends(auth.get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    user_folder = get_user_folder(current_user)
    user_folder.mkdir(exist_ok=True)
    document_id = str(uuid.uuid4())
    file_path = user_folder / f"{document_id}.pdf"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    processed_data = pdf_processing.process_pdf_for_user(current_user, str(file_path))
    chunks = processed_data.get("chunks", [])

    if not chunks:
        raise HTTPException(status_code=400, detail="El PDF no contiene texto procesable")

    # Call the updated helper with the index name
    index = get_pinecone_index("turbolauncher")
    
    batch_size = 96
    batch_vectors = []

    for chunk in chunks:
        try:
            embedding = get_embedding(chunk["text"])
            # Ensure embedding is a list of floats
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()
        except Exception as e:
            print(f"Error embedding chunk {chunk['chunk_id']}: {e}")
            continue

        batch_vectors.append({
            "id": chunk["chunk_id"],
            "values": embedding,
            "metadata": {
                "document_id": chunk["document_id"],
                "user_id": chunk["user_id"],
                "source_pdf": file.filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"] # Highly recommended to store text in metadata for RAG
            }
        })

        if len(batch_vectors) >= batch_size:
            index.upsert(vectors=batch_vectors)
            batch_vectors = []

    if batch_vectors:
        index.upsert(vectors=batch_vectors)

    return {
        "filename": file.filename,
        "document_id": document_id,
        "num_chunks": len(chunks),
        "mensaje": "PDF recibido y procesado correctamente"
    }
    
#----------------- ASK ENDPOINTS --------------------------------------------------------------------


@app.post("/ask")
async def ask_question(
    question: str = Body(..., embed=True),
    current_user: str = Depends(auth.get_current_user)
):
    # 1. Obtener el embedding de la pregunta
    query_vector = get_embedding(question)

    # 2. Buscar en Pinecone
    index = get_pinecone_index("turbolauncher")
    search_results = index.query(
        vector=query_vector,
        top_k=5, 
        include_metadata=True,
        filter={"user_id": {"$eq": current_user}}
    )

    matches = search_results.get("matches", [])
    if not matches:
        return {"respuesta": "No encontré información relevante."}

    # 3. Extraer contexto y formatear fuentes más descriptivas
    context_chunks = []
    fuentes_detalladas = []

    for m in matches:
        texto_chunk = m["metadata"].get("text", "Texto no disponible")
        context_chunks.append(texto_chunk)
        
        # Creamos un objeto de fuente más informativo
        fuentes_detalladas.append({
            "archivo": m["metadata"].get("source_pdf"),
            "pagina": m["metadata"].get("page"),
            "contenido_referenciado": texto_chunk[:200] + "..." # Mostramos un preview del texto
        })

    context_text = "\n\n---\n\n".join(context_chunks)

    # 4. Generar respuesta con OpenAI
    answer = generate_answer(question, context_text)

    return {
        "pregunta": question,
        "respuesta": answer,
        "fuentes": fuentes_detalladas
    }