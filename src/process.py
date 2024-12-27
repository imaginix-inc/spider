from typing import List
from src.models import BaseDB
from openai import AsyncClient
from openai.types import CreateEmbeddingResponse
from sqlalchemy.sql import func
import asyncio
from snowflake import SnowflakeGenerator
generator = SnowflakeGenerator(1)
client = AsyncClient()


async def post_process(datas: List[BaseDB], embedding_texts: List[str], full_texts: List[str]):
    # get embeddings of texts
    # TODO: cache
    tasks = [client.embeddings.create(
        input=text, model='text-embedding-3-large') if text is not None else None for text in embedding_texts]
    embeddings: List[CreateEmbeddingResponse] = await asyncio.gather(*[task for task in tasks if task is not None])
    embeddings = [
        embedding.data[0].embedding if embedding is not None else None for embedding in embeddings]
    # update datas
    for (data, embedding) in zip(datas, embeddings):
        data.name_vector = embedding
        data.id = next(generator)
    # create tsvector for full_texts
    for (data, full_text) in zip(datas, full_texts):
        data.search_vector = func.to_tsvector(full_text)
    return datas
