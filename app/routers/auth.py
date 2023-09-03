from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from .. import db, schemas, models, utils, oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.LoginData, db: Session = Depends(db.get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == credentials.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    if not utils.verify(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return schemas.TokenResponse(token=access_token, type="Bearer")
