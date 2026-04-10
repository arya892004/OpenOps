"""
OpenOps FastAPI Server
Provides REST API endpoints for the incident management environment
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from server.my_env_environment import MyEnvEnvironment
from models import IncidentAction, IncidentObservation


# FastAPI app
app = FastAPI(
    title="OpenOps API",
    description="Production Incident Management Environment API",
    version="1.0.0"
)

# Global environment instance (stateful for demo purposes)
env_instance: Optional[MyEnvEnvironment] = None


# Request/Response Models
class ResetRequest(BaseModel):
    task_id: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1
            }
        }


class StepRequest(BaseModel):
    action_id: int
    task_id: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_id": 0,
                "task_id": 1
            }
        }


class StateResponse(BaseModel):
    state: Dict[str, Any]


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OpenOps Incident Commander",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "reset": "/reset",
            "step": "/step",
            "state": "/state"
        }
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment_loaded": env_instance is not None,
        "current_task": env_instance.task_id if env_instance else None
    }


@app.post("/reset")
async def reset(request: ResetRequest) -> Dict[str, Any]:
    """
    Reset the environment for a specific task.
    
    Args:
        request: ResetRequest with task_id (1=easy, 2=medium, 3=hard)
    
    Returns:
        Initial observation after reset
    """
    global env_instance
    
    try:
        # Validate task_id
        if request.task_id not in [1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task_id: {request.task_id}. Must be 1, 2, or 3."
            )
        
        # Create new environment instance
        env_instance = MyEnvEnvironment()
        obs = env_instance.reset(task_id=request.task_id)
        
        # Return observation as dict
        return {
            "observation": obs.model_dump(),
            "task_id": request.task_id,
            "message": "Environment reset successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset environment: {str(e)}"
        )


@app.post("/step")
async def step(request: StepRequest) -> Dict[str, Any]:
    """
    Execute an action in the environment.
    
    Args:
        request: StepRequest with action_id and task_id
    
    Returns:
        Observation after taking the action
    """
    global env_instance
    
    try:
        # Check if environment is initialized
        if env_instance is None:
            raise HTTPException(
                status_code=400,
                detail="Environment not initialized. Call /reset first."
            )
        
        # Validate action_id
        if request.action_id < 0 or request.action_id > 20:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action_id: {request.action_id}. Must be 0-20."
            )
        
        # Create action
        action = IncidentAction(
            action_id=request.action_id,
            task_id=request.task_id
        )
        
        # Execute step
        obs = env_instance.step(action)
        
        # Get action name
        action_name = env_instance.ACTION_NAMES.get(request.action_id, "unknown")
        
        return {
            "observation": obs.model_dump(),
            "action_taken": {
                "action_id": request.action_id,
                "action_name": action_name
            },
            "reward": obs.reward,
            "done": obs.done,
            "total_reward": env_instance.total_reward,
            "incident_resolved": env_instance.incident_resolved
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute step: {str(e)}"
        )


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """
    Get current environment state.
    
    Returns:
        Current state of the environment
    """
    global env_instance
    
    try:
        if env_instance is None:
            raise HTTPException(
                status_code=400,
                detail="Environment not initialized. Call /reset first."
            )
        
        state = env_instance.state
        
        return {
            "state": state.model_dump() if hasattr(state, 'model_dump') else state,
            "task_id": env_instance.task_id,
            "total_reward": env_instance.total_reward,
            "incident_resolved": env_instance.incident_resolved,
            "time_elapsed": env_instance.time_elapsed
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get state: {str(e)}"
        )


@app.get("/actions")
async def get_actions() -> Dict[str, Any]:
    """
    Get list of available actions.
    
    Returns:
        Dictionary of action IDs and names
    """
    try:
        # Create temporary instance to get action names
        temp_env = MyEnvEnvironment()
        
        return {
            "actions": temp_env.ACTION_NAMES,
            "total_actions": len(temp_env.ACTION_NAMES)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get actions: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )