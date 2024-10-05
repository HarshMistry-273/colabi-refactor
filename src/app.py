from fastapi import FastAPI
from src.agents.apis import router as agents_router
from src.tools.apis import router as tools_router
from src.tasks.apis import router as tasks_router

app = FastAPI(title="Colabi")

app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tools_router, prefix="/api/v1/tools", tags=["tools"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
