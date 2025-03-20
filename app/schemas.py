"""
schemas.py (Pydantic Models for Validation & API Responses)

Defines Pydantic models for request validation and response formatting.
Ensures data correctness in API requests.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    passwd: str

class User(UserBase):
    id: int
    creation_dt: datetime

    # Allow the model to be initialized using objects (or ORM-like attributes) instead of just plain dictionaries.
    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# Video schemas
class VideoBase(BaseModel):
    title: str
    video_url: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    owner_id: int
    timestamp: datetime

class VideoWithStats(Video):
    likes_count: int
    shares_count: int
    owner_username: str

class VideoUpdate(BaseModel):
    title: str
    class Config:
        from_attributes = True


# Like schema
class Like(BaseModel):
    user_id: int
    post_id: int
    class Config:
        from_attributes = True


# Share schema
class Share(BaseModel):
    user_id: int
    post_id: int
    class Config:
        from_attributes = True