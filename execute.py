from spiders import spiders, Spider
from process import post_process
from dataset import AsyncSessionLocal, async_engine, engine
from sqlalchemy import insert
import asyncio
from tqdm import tqdm
import dotenv
dotenv.load_dotenv()


async def process_school(spider: Spider):
    datas = await spider.func()
    pbar = tqdm(total=len(datas), desc=f"Processing {spider.school_name}")
    spider.scheme.metadata.drop_all(engine)
    spider.scheme.metadata.create_all(engine)
    async with AsyncSessionLocal() as session:
        async with session.begin():

            chunk_size = 1000
            session.add_all(datas)
            await session.commit()

    pbar.close()


async def execute():
    tasks = []
    for spider in spiders:
        tasks.append(process_school(spider))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(execute())
