"""Task endpoints."""
from fastapi import APIRouter, Depends
from api.api.deps import get_current_user
from api.models import User

router = APIRouter()


@router.get("/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),
):
    """List all tasks for current user."""
    return {"tasks": [], "message": "Task endpoints coming soon"}


@router.post("/tasks")
async def create_task(
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    return {"message": "Task creation coming soon"}
