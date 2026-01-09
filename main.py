from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
import auth
import pdf_processing
import database
import shutil
from pathlib import Path
import uuid
from db_pinecone import get_pinecone_index
from openai_utils import get_embedding
import os
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


#----------------- PDF LOAD ENDPOINTS ---------------------------------------------------------------

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)
def get_user_folder(user_id: str) -> Path:
    folder = UPLOAD_DIR / user_id
    folder.mkdir(exist_ok=True)
    return folder

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: str = Depends(auth.get_current_user)  # this should return user_id
):
    # 1️⃣ Check file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # 2️⃣ Save file in user-specific folder
    user_folder = UPLOAD_DIR / current_user
    user_folder.mkdir(exist_ok=True)

    document_id = str(uuid.uuid4())

    file_path = user_folder / f"{document_id}.pdf"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    processed_data = pdf_processing.process_pdf_for_user(current_user, str(file_path))

    print(processed_data["chunks"][0])

    records = [
        {
            "_id": f"{document_id}-chunk-{i}",
            "chunk_text": chunk,
            "source_pdf": file.filename,
            "user_id": current_user
        }
        for i, chunk in enumerate(processed_data["chunks"])
    ]

    index = get_pinecone_index("turbolauncher")
    batch_size = 96

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        vectors = [
            {
                "id": r["_id"],
                "values": get_embedding(r["chunk_text"]),  # implement this with OpenAI embeddings
                "metadata": {
                    "source_pdf": r["source_pdf"],
                    "user_id": r["user_id"]
                }
            }
            for r in batch
        ]
        index.upsert(vectors=vectors)

    return {
        "filename": file.filename,
        "document_id": document_id,
        "num_chunks": len(processed_data["chunks"]),
        "mensaje": "PDF recibido y procesado correctamente"
    }