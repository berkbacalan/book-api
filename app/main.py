from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Default Backend - 200"}
