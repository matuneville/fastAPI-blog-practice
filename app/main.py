"""
main.py

Entry point for the FastAPI application.
Initializes the FastAPI app, database, and registers API routes.
"""
from fastapi import FastAPI
from app.db import Base, engine
from app.routes import auth, posts, users

# Create db
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
