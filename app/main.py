from fastapi import FastAPI
from app.api import chat, documentos, erp

app = FastAPI(title="IDLED Backend")
app.include_router(erp.router)
app.include_router(chat.router)
app.include_router(documentos.router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
