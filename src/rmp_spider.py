from httpx_sse import aconnect_sse
import httpx
from tqdm.asyncio import tqdm


async def process_school(school_id: int, table_name: str, field_name: str):
    async with httpx.AsyncClient() as client:
        async with aconnect_sse(client, "GET", "http://localhost:8080/api/v1/spider/rateMyProfessor", params={
            'field': field_name,
            'tableName': table_name,
            'schoolId': school_id
        }) as event_source:
            async for event in event_source.aiter_sse():
                if event.event == 'done':
                    return
                if event.data.startswith("row size:"):
                    # get row size
                    row_size = int(event.data.split(":")[1].strip())
                # fetch 3 Edoardo Rubino
                # extract 3 from the text
                current_progress = int(event.data.split(" ")[1])

                if 'row_size' in locals():
                    progress_bar = tqdm(total=row_size)
                    progress_bar.update(current_progress)
