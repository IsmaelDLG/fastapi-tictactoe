from fastapi import FastAPI
from .routers import games, users

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World!"}


app.include_router(games.router)
app.include_router(users.router)
