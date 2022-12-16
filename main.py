import psutil
from fastapi import FastAPI, HTTPException
from fastapi import BackgroundTasks
import subprocess

app = FastAPI()

@app.get("/run_script/{token}")
def run_script(token: str, background_tasks: BackgroundTasks):
    if token != "sec":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check if the script is already running
    if "script.py" in [p.cmdline() for p in psutil.process_iter()]:
        raise HTTPException(status_code=400, detail="Script is already running")

    # Run the script in the background
    background_tasks.add_task(run_script_task)
    return {"message": "Script started"}

async def run_script_task():
    proc = subprocess.Popen(["python", "script.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stdout)
    print(stderr)










"""
from typing import Union
import sys
import subprocess
from fastapi import FastAPI

app = FastAPI()
def run_program():
    s2_out = s2_out = subprocess.check_output([sys.executable, "certmailer.py"])
    return s2_out

@app.get("/token/{item_id}")
async def read_root(item_id: int, q: Union[str, None] = None):
    return run_program() if q == "kshfuqwh323E34thisispasswordtosend" else {"not authorized"}
        #return run_program()

@app.get("/")
def read_root():
    return {"Hello": "Mohammed"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
"""