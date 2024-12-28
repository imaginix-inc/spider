from .spiders import spiders, Spider
from src.process import post_process
from .dataset import AsyncSessionLocal, async_engine, engine
from sqlalchemy import insert
import asyncio
from tqdm import tqdm
import time
from src import rmp_spider


async def process_school(spider: Spider) -> float:
    begin_time = time.time()
    datas = await spider.func()
    pbar = tqdm(total=len(datas), desc=f"Processing {spider.school_name}")
    spider.scheme.metadata.drop_all(engine)
    spider.scheme.metadata.create_all(engine)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add_all(datas)
            await session.commit()

    pbar.close()
    return time.time() - begin_time


async def execute():
    tasks = []
    for spider in spiders:
        tasks.append(process_school(spider))
    spend_time = await asyncio.gather(*tasks)
    for (spider, time) in zip(spiders, spend_time):
        print(f"{spider.school_name} spend {time} seconds")
    # start to call java backend for rmp spider
    for spider in spiders:
        await rmp_spider.process_school(
            spider.school_id, spider.scheme.__tablename__, 'instructor_name')
if __name__ == '__main__':
    asyncio.run(execute())
