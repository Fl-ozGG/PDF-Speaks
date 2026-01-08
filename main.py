from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
import auth
import database
import shutil
from pathlib import Path
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
    return {"mensaje": f"Hola {current_user}, este es tu perfil privado."}


#----------------- PDF LOAD ENDPOINTS ---------------------------------------------------------------

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), current_user: str = Depends(auth.get_current_user)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "mensaje": "PDF recibido correctamente"}