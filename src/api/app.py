from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .run import router as run_router
from .initiate_simulation import router as initiate_router
from .results import router as results_router

app = FastAPI(title="SimOrch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)
app.include_router(initiate_router)
app.include_router(results_router)

app.get("/health")(lambda: {"status": "ok"})


