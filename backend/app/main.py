from fastapi import FastAPI
import threading
from app.core.config import settings
from app.workers.indexer import run_indexer
from app.api.router import api_router

app = FastAPI(title="WEXARE MVP API")
app.include_router(api_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.on_event("startup")
def start_indexer_if_configured():
    if settings.rpc_url and settings.escrow_manager_address and settings.dispute_manager_address:
        t = threading.Thread(target=run_indexer, daemon=True)
        t.start()
