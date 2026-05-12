import uvicorn
from fastapi import FastAPI
from api import router as translation_router

app = FastAPI(
    title="AI Translation Service",
)

app.include_router(translation_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)