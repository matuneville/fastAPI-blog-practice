from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app import models, schemas, auth
from app.db import get_db
from app.exceptions import *

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

db_dependency = Annotated[Session, Depends(get_db)]

# Registration Endpoint
@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: db_dependency):
    # Check if user is registered
    users_db = db.query(models.User).filter(models.User.username == user.username).first()
    if users_db:
        raise_conflict_except("Error: Username already exists")

    hashed_passwd = auth.get_hashed_passwd(user.password)
    new_user = models.User(username=user.username,
                           email=user.email,
                           hashed_passwd=hashed_passwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Follow Endpoint
@router.post("/{user_id}/follow", status_code=204)
def follow_user(user_id: int, db: db_dependency, current_user: models.User = Depends(auth.get_current_user)):
    followee = db.query(models.User).filter(models.User.id == user_id).first()

    if not followee:
        raise_not_found_except("Error: Username not found")
    if followee == current_user:
        raise_bad_request_except("Error: Cannot follow yourself")
    if followee in current_user.following:
        raise_bad_request_except("Error: Already following user")

    current_user.following.append(followee)
    db.commit()
    return

# Unfollow Endpoint
@router.post("/{user_id}/unfollow", status_code=204)
def unfollow_user(user_id: int, db: db_dependency, current_user: models.User = Depends(auth.get_current_user)):
    unfollowee = db.query(models.User).filter(models.User.id == user_id).first()
    if not unfollowee:
        raise_not_found_except("Error: Username not found")
    if unfollowee == current_user:
        raise_bad_request_except("Error: Cannot unfollow yourself")
    if unfollowee not in current_user.following:
        raise_bad_request_except("Error: You can only unfollow users which already follow")

    current_user.following.remove(unfollowee)
    db.commit()
    return