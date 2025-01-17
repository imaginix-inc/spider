from .spiders import spiders, Spider
from src.process import post_process
from .dataset import AsyncSessionLocal, async_engine, engine
from sqlalchemy import insert
import asyncio
from tqdm import tqdm
import time
import traceback


async def process_school(spider: Spider) -> float:
    print(f"Processing: {spider.school_name}")
    begin_time = time.time()
    datas = await spider.func()

    from sqlalchemy import inspect
    # inspector = inspect(engine)
    # if inspector.has_table(spider.scheme.__tablename__):
    #     spider.scheme.metadata.drop_all(engine)
    spider.scheme.metadata.create_all(engine)
    chunk_size = 100
    pbar = tqdm(total=len(datas) // chunk_size,
                desc=f"Uploading {spider.school_name}")
    for i in range(0, len(datas), chunk_size):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add_all(datas[i:i + chunk_size])
                await session.commit()
                pbar.update(1)
    with open('res.txt', 'a') as f:
        f.write(f"Insert {len(datas)} data to {spider.school_name} database\n")
    print(f"Insert {len(datas)} data to {spider.school_name} database")
    pbar.close()
    return time.time() - begin_time


async def execute():
    tasks = []
    for spider in spiders:
        tasks.append(process_school(spider))
    spend_time = await asyncio.gather(*tasks, return_exceptions=True)
    for (spider, time) in zip(spiders, spend_time):
        if isinstance(time, Exception):
            print(f"Error processing {spider.school_name}: {
                  time}, {traceback.format_exception(time)}")
        else:
            print(f"{spider.school_name} spend {time} seconds")
if __name__ == '__main__':
    asyncio.run(execute())
