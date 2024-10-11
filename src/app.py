import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.agents.apis import router as agents_router
from src.tools.apis import router as tools_router
from src.tasks.apis import router as tasks_router

app = FastAPI(
    title="Colabi",
    # Disable OpenAPI docs in production to reduce startup time
    openapi_url=False,
    docs_url=False,
    redoc_url=False,
)

app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tools_router, prefix="/api/v1/tools", tags=["tools"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.mount("/static", StaticFiles(directory="static"), name="static")

if not os.path.exists("static"):
    os.mkdir("static")