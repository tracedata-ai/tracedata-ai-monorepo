"""
Database configuration and session management for TraceData AI Middleware.

This module sets up the SQLAlchemy ORM, including the engine, session factory,
and the declarative base for all entity models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database connection URL, defaulting to the docker-compose 'db' service
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/tracedata")

# Initialize the SQLAlchemy engine
# pool_pre_ping=True helps maintain connection reliability in containerized environments
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a thread-local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()

def get_db():
    """
    Dependency generator for database sessions.
    
    Yields:
        Session: A standard SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
