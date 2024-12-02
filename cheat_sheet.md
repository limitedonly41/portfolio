# fastapi sequental queue order

from task import manager

import asyncio
from asyncio import Lock
task_lock = Lock()

app = FastAPI()
logger = setup_logging()
task_queue = asyncio.Queue()  # A queue to store incoming tasks

@app.post("/process_add")
async def process_add(task_request: TaskRequest, request: Request):
    ...
    logger.info(f"Task created with ID: {task_id}")
            async with task_lock:
                manager.do_task.delay(task_id, data)
            return {"status": "successful", "id": task_id}
