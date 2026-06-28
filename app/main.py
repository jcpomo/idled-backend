from fastapi import FastAPI

app = FastAPI(title="IDLED Backend")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
