from typing import List
from models import BaseDB
from openai import AsyncClient
from openai.types import CreateEmbeddingResponse
from sqlalchemy.sql import func
import asyncio
client = AsyncClient()


async def post_process(datas: List[BaseDB], embedding_texts: List[str], full_texts: List[str]):
    # get embeddings of texts
    # TODO: cache
    tasks = [client.embeddings.create(
        text=text, model='text-embedding-3-large') for text in embedding_texts]
    embeddings: List[CreateEmbeddingResponse] = await asyncio.gather(*tasks)
    embeddings = [embedding.data[0].embedding for embedding in embeddings]
    # update datas
    for (data, embedding) in zip(datas, embeddings):
        data.name_vector = embedding
    # create tsvector for full_texts
    for (data, full_text) in zip(datas, full_texts):
        data.search_vector = func.to_tsvector(full_text)
    return datas
