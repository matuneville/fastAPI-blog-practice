"""
models.py (Defines Database Models - SQLAlchemy)

Defines ORM models that map Python classes to database tables.
Each class represents a database table.
"""

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime, timezone


# 'Follow' join table for the User class for the follow functionality (N:N, many users can follow many others)
Follow = Table(
    "follows",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followee_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    # Define columns for users db
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(15), index=True, unique=True, nullable=False)
    email = Column(String(127), index=True, unique=True, nullable=False)
    hashed_passwd = Column(String(255), nullable=False)

    creation_dt = Column(DateTime, default=datetime.now(timezone.utc))

    # Define relationships
    posts = relationship(
        "Post",
        back_populates="owner" # Post has a corresponding owner attr to refer back to the User
        )

    followers = relationship(
        "User",
        secondary=Follow,
        primaryjoin= id == Follow.c.followee_id,
        secondaryjoin= id == Follow.c.follower_id,
        backref="following" # create reverse relationship
        )
    

class Post(Base):
    __tablename__ = "posts"

    # Define columns for posts db
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(127), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Define relationships
    owner = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")
    shares = relationship("Share", back_populates="post")


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)

    user = relationship("User")
    post = relationship("Post", back_populates="likes")


class Share(Base):
    __tablename__ = "shares"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User")
    post = relationship("Post", back_populates="shares")