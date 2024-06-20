from fastapi import FastAPI
from middleware.auth_middleware import AuthMiddleware

app = FastAPI()
app.add_middleware(AuthMiddleware, validation_service_url="http://127.0.0.1:8000/token-check", timeout=10)

@app.get("/")
async def root():
    return {"message": "Hello World"} 