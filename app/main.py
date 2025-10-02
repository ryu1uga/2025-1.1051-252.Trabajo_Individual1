from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
import jwt
import redis.asyncio as redis
from datetime import datetime, timedelta

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"

# Fake DB
users_db = {"ryuichi": "password123"}

# Modelo para login con JSON
class LoginRequest(BaseModel):
    username: str
    password: str

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Token endpoint (JSON)
@app.post("/token")
def login(request: LoginRequest):
    username = request.username
    password = request.password
    if username in users_db and users_db[username] == password:
        exp = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode({"sub": username, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

# JWT dependency
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Protected endpoint with rate limiting
@app.get("/tasks", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def read_tasks(user: str = Depends(get_current_user)):
    return {"user": user, "tasks": ["Tarea 1", "Tarea 2"]}