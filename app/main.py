from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "App is alive!"}

@app.get("/env")
def read_env():
    return {
        "app_name": os.getenv("APP_NAME", "undefined"),
        "env": os.getenv("APP_ENV", "dev"),
        "host": os.getenv("APP_HOST", "0.0.0.0"),
        "port": os.getenv("APP_PORT", "8000"),
    }
