from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
import auth
import database

app = FastAPI()

database.init_db()

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
