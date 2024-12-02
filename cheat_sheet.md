# fastapi sequental queue order

```python

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
```


# Complete Solution for Managing a `systemd` Service for Uvicorn

## Step 1: Create the Service File
Create a new service file `/etc/systemd/system/myapp.service` with the following content:

```ini
[Unit]
Description=My Uvicorn App Service
After=network.target

[Service]
# Specify the user and group that will run the service
User=administrator
Group=administrator

# Set the working directory where your application resides
WorkingDirectory=/home/administrator/app_models/main_model

# Command to start your application
ExecStart=/home/administrator/app_models/main_model/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 5001 --workers 2

# Restart policy to ensure service restarts if it crashes
Restart=always
RestartSec=5

# Log output
StandardOutput=file:/home/administrator/app_models/main_model/app_main.log
StandardError=file:/home/administrator/app_models/main_model/app_main.log

[Install]
WantedBy=multi-user.target
```

# Managing the `myapp` Service

## Stop the Service
To stop the service, run:

```bash
sudo systemctl stop myapp
```
Start the Service
```bash
sudo systemctl start myapp
```
Optional: Restart the Service
If you want to stop and start the service in a single command, you can use:

```bash
sudo systemctl restart myapp
```
Verify Status
After starting or restarting, confirm the service status:

```bash
sudo systemctl status myapp
```
