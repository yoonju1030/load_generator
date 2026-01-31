import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.router import api_router

app = FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=3000, reload=True)
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    start_server()
