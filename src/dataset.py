from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
import os
from src.settings import settings
async_engine = create_async_engine(
    settings.dataset_url.replace('postgresql', 'postgresql+asyncpg'))
engine = create_engine(settings.dataset_url
                       )
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    future=True,
    expire_on_commit=False
)
