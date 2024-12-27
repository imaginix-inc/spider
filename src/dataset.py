from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
import os
async_engine = create_async_engine(
    os.environ['DATASET_URL'].replace('postgresql', 'postgresql+asyncpg'))
engine = create_engine(os.environ['DATASET_URL']
                       )
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    future=True,
    expire_on_commit=False
)
