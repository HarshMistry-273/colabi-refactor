from fastapi import FastAPI, status
from src.crew_search_bot import CrewAgent

from src.agents.apis import router as agents_router
from src.tools.apis import router as tools_router
from src.tasks.apis import router as tasks_router

app = FastAPI(title="Colabi Web Search Agent (CrewAI)")

app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tools_router, prefix="/api/v1/tools", tags=["tools"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
