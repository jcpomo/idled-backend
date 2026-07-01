import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, documentos, erp, projects, tasks
from app.documentos.deps import get_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the object-storage bucket exists before any upload is served.
    # Mirrors the worker ensuring the Qdrant collection at job time.
    await asyncio.to_thread(get_storage().ensure_bucket)
    yield


app = FastAPI(title="IDLED Backend", lifespan=lifespan)

# Allow the frontend dev server (and any explicitly configured origins) to call
# the API from the browser. Comma-separated origins via CORS_ORIGINS override the
# localhost defaults.
_cors_origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(erp.router)
app.include_router(chat.router)
app.include_router(documentos.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
