from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# This is where you could put your code for Indicateur 1
@app.post("/indicateur1")
async def root():
    return {"message": "Hello World"}