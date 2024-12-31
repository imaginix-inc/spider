from src import execute
import asyncio
from asyncz.schedulers.asyncio import AsyncIOScheduler


async def main():
    async with AsyncIOScheduler() as scheduler:
        pass

if __name__ == '__main__':
    asyncio.run(main())
