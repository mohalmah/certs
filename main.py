import subprocess
import uvicorn
from asyncio import Semaphore
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

sem = Semaphore(value=1)

class Token(BaseModel):
    token: str

@app.get("/run/{token}")
async def run_script(token: str):
    async with sem:
        # Validate the token
        if token != "sec":
            return {"error": "Invalid token"}
        
        # Run the script and get the output
        output = subprocess.run(["python", "improvedcertmailer1.py"], capture_output=True)
        
        # Return the output to the client
        return {"output": output.stdout.decode()}
    
    # Reload the server after the script is done running
    uvicorn.reload()




"""

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import Query
from fastapi import status
from threading import Lock
import sys
import subprocess
app = FastAPI()

lock = Lock()

@app.middleware("http")
async def acquire_lock(request: Request, call_next):
    acquired = lock.acquire(blocking=False)
    if not acquired:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The server is currently busy. Please try again later.")
    response = await call_next(request)
    lock.release()
    return response

def run_program():
    s2_out = s2_out = subprocess.check_output([sys.executable, "improvedcertmailer1.py"])
    return s2_out

@app.get("/{token}")
def read_root(token: str):
    # Validate the token
    if token != "kshfuqwh323E34thisispasswordtosend":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    #try:
        # Run the script using subprocess
    subprocess.run(["python", "improvedcertmailer1.py"])
    #finally:
        # Release the lock
        #lock.release()
    
    return {"status": "success"}

"""



"""
import subprocess
import threading
from fastapi import FastAPI, HTTPException

app = FastAPI()
lock = threading.Lock()

@app.get("/run_script/{token}")
def run_script(token: str):
    # Check if the token is valid
    if token != "sec":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Acquire the lock to prevent multiple requests at the same time
    lock.acquire()
    try:
        # Run the script using subprocess
        subprocess.run(["python", "improvedcertmailer1.py"])
    finally:
        # Release the lock
        lock.release()
    
    return {"status": "success"}

"""









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