from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Annotated
from datetime import timedelta, datetime, timezone

from app import models, schemas, auth
from app.db import get_db
from app.exceptions import *

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

db_dependency = Annotated[Session, Depends(get_db)]

# Get posts endpoint
@router.get("/", response_model=List[schemas.Post])
def read_posts(
        db: db_dependency,
        skip: int = 0,
        limit: int = 5
):
    # Get posts from [skip, limit] range, in date descending order (newest - oldest)
    posts = db.query(models.Post).order_by(models.Post.timestamp.desc()).offset(skip).limit(limit).all()
    return posts


# Create new post endpoint
@router.post("/", response_model=schemas.Post)
def create_new_post(
        post_request: schemas.PostCreate,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    # Create new table row with post info
    db_post = models.Post(text = post_request.text, owner_id = current_user.id)

    # Add post to sqlalchemy session
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# Delete post endpoint
@router.delete("/{post_id}", status_code=204)
def delete_existing_post(
        post_id: int,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    # Get post from db to delete (first occurrence of id)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None or post.owner_id != current_user.id:
        raise_not_found_except('Error: Post not found or not owner of post')
    db.delete(post)
    db.commit()
    return

# Update post endpoint
@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
        post_id: int,
        post_update: schemas.PostUpdate,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    # Get post from db to update
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if post is None:
        raise_not_found_except('Error: Post not found')
    if post.owner_id != current_user.id:
        raise_forbidden_except('Error: You can only edit posts of your own account')

    # Check post datetime (only editable within 1 hour since its creation)
    post_timestamp = post.timestamp.replace(tzinfo=timezone.utc)
    time_since_creation = datetime.now(timezone.utc) - post_timestamp
    if time_since_creation > timedelta(minutes=60):
        raise_not_found_except("Error: You can only edit a post within 1 hour since its creation")

    post.content = post_update.content
    db.add(post)
    db.commit()
    return post


# Like post endpoint
@router.post("/{post_id}/like", status_code=204)
def like_post(
        post_id: int,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    # Query post
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise_not_found_except('Error: Post not found')
    # Query like
    like = db.query(models.Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        raise_not_found_except("Already liked")
    # add new like row to db
    new_like = models.Like(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    db.commit()
    return


# Unlike post endpoint
@router.post("/{post_id}/unlike", status_code=204)
def unlike_post(
        post_id: int,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise_not_found_except('Error: Post not found')
    like = db.query(models.Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not like:
        raise_not_found_except("Error: Post not liked yet")
    db.delete(like)
    db.commit()
    return


# Share post endpoint
@router.post("/{post_id}/share", status_code=204)
def share_post(
        post_id: int,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise_not_found_except('Error: Post not found')
    share = db.query(models.Share).filter_by(user_id=current_user.id, post_id=post_id).first()
    if share:
        raise_not_found_except("Error: Already shared")
    # Add new share row to db
    new_share = models.Share(user_id=current_user.id, post_id=post_id)
    db.add(new_share)
    db.commit()
    return


# Unshare post endpoint
@router.post("/{post_id}/unshare", status_code=204)
def unshare_post(
        post_id: int,
        db: db_dependency,
        current_user: models.User = Depends(auth.get_current_user)
):
    share = db.query(models.Share).filter_by(user_id=current_user.id, post_id=post_id).first()
    if not share:
        raise_not_found_except("Error: Not shared yet")
    db.delete(share)
    db.commit()
    return


# Get posts with stats Endpoint
@router.get("/with_stats/", response_model=List[schemas.PostWithStats])
def read_posts_with_stats(
        db: db_dependency
):
    # subquery to count likes of each post
    likes_subquery = (
        db.query(models.Like.post_id, func.count(models.Like.user_id).label('likes_count'))
        .group_by(models.Like.post_id)
        .subquery()
    )

    # subquery to count likes of each post
    shares_subquery = (
        db.query(
            models.Share.post_id,
            func.count(models.Share.user_id).label('shares_count')
        )
        .group_by(models.Share.post_id)
        .subquery()
    )

    # Fetch posts along with their like/shares counts and owner username
    posts = (
        db.query(
            models.Post,  # Select the post data
            models.User.username.label('owner_username'),  # Include owner's username
            func.coalesce(likes_subquery.c.likes_count, 0).label('likes_count'),  # Join with likes count
            func.coalesce(shares_subquery.c.shares_count, 0).label('shares_count')  # Join with shares count
        )
        .join(models.User, models.Post.owner_id == models.User.id)  # Join Post with User table to get username
        .outerjoin(likes_subquery, models.Post.id == likes_subquery.c.post_id)  # Join posts with likes count subquery
        .outerjoin(shares_subquery, models.Post.id == shares_subquery.c.post_id)  # Join posts with shares count subquery
        .order_by(models.Post.timestamp.desc())  # Order by post creation timestamp
        .all()  # Execute the query
    )

    # Construct the response with posts, counts, and owner username
    response_posts = []
    for post, owner_username, likes_count, shares_count in posts:
        # Append each post along with its counts and owner's username to the response list
        response_posts.append(schemas.PostWithStats(
            id=post.id,
            text=post.text,
            timestamp=post.timestamp,
            owner_id=post.owner_id,
            owner_username=owner_username,  # Include owner's username in the response
            likes_count=likes_count,
            shares_count=shares_count
        ))

    return response_posts