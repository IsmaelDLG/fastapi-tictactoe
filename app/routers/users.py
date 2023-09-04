from typing import List
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import db, schemas, models, utils, logs

logger = logs.get_logger(__name__)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        logger.info(f"username: {user.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"username already exists",
        )
    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.debug("ok")
    return new_user


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse]
)
def get_all(db: Session = Depends(db.get_db), limit: int = 3):
    users = db.query(models.User).limit(limit).all()
    logger.debug("ok")
    return users


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse
)
def get_one(id: int, db: Session = Depends(db.get_db)):
    logger.debug(f"id: {id}")
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} was not found",
        )

    return user
