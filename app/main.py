from fastapi import FastAPI
from .routers import games

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World!"}

