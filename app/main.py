from fastapi import FastAPI
from .routers import games, users, auth

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World!"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(games.router)
