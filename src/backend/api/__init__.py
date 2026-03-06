from fastapi import APIRouter
from src.backend.api.manager_agent import router as manager_agent_router

router = APIRouter(prefix="/api") 
router.include_router(manager_agent_router)

__all__ = ["router"]
