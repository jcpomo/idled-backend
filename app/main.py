import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import chat, documentos, erp
from app.documentos.deps import get_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the object-storage bucket exists before any upload is served.
    # Mirrors the worker ensuring the Qdrant collection at job time.
    await asyncio.to_thread(get_storage().ensure_bucket)
    yield


app = FastAPI(title="IDLED Backend", lifespan=lifespan)
app.include_router(erp.router)
app.include_router(chat.router)
app.include_router(documentos.router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
