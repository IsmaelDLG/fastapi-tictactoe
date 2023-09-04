from fastapi import FastAPI, Request
import logging
import random, time
from .routers import games, moves, users, auth
from .logs import get_logger

logger = get_logger(__name__)
app = FastAPI()


# log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = f"{time.time():.3f}"
    auth = request.headers.get("authorization")
    logger.info(
        f"rid: {idem} method: {request.method} path: {request.url.path} auth-headers: {auth} start request "
    )
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"rid: {idem} completed_in: {formatted_process_time}ms status_code: {response.status_code}"
    )

    return response


@app.get("/")
def root():
    return {"message": "Hello World!"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(games.router)
app.include_router(moves.router)
