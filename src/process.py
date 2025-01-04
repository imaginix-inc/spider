from typing import List
from src.models import BaseDB
from openai import AsyncClient
from openai.types import CreateEmbeddingResponse
from sqlalchemy.sql import func
import asyncio
from snowflake import SnowflakeGenerator
from tqdm.asyncio import tqdm
generator = SnowflakeGenerator(1)
client = AsyncClient()

sem = asyncio.Semaphore(50)


async def embedd_text(text: str | None):
    async with sem:
        if text is None:
            return None
        resp = await client.embeddings.create(
            input=text, model='text-embedding-3-large')
        return resp.data[0].embedding


async def post_process(datas: List[BaseDB], embedding_texts: List[str], full_texts: List[str], showBar=True):
    # get embeddings of texts
    # TODO: cache
    tasks = [embedd_text(text) for text in embedding_texts]
    embeddings: List[CreateEmbeddingResponse]
    if showBar:
        embeddings = await tqdm.gather(*[task for task in tasks if task is not None], desc="Post Process")
    else:
        embeddings = await asyncio.gather(*[task for task in tasks if task is not None])
    # update datas
    for (data, embedding) in zip(datas, embeddings):
        data.name_vector = embedding
        data.id = next(generator)
    # create tsvector for full_texts
    for (data, full_text) in zip(datas, full_texts):
        data.search_vector = func.to_tsvector(full_text)
    return datas
