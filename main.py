from src import execute
import asyncio
from async_cron.job import CronJob
from async_cron.schedule import Scheduler


async def main():
    # Execute the task first
    await execute.execute()

    # Start the scheduler
    msh = Scheduler(locale="en_US")
    task = CronJob(name='spider').at('00:00').every(1).day.go(execute.execute)
    msh.add_job(task)
    await msh.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
