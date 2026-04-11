"""
OpenOps FastAPI Server
Provides REST API endpoints for the incident management environment
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
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

# Global environment instance
env_instance: Optional[MyEnvEnvironment] = None


# Request Models
class StepRequest(BaseModel):
    action_id: int
    task_id: Optional[int] = 1


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
async def reset(task_id: int = Query(default=1, ge=1, le=3)) -> Dict[str, Any]:
    """
    Reset the environment for a specific task.
    OpenEnv standard endpoint.
    
    Args:
        task_id: Task difficulty (1=easy, 2=medium, 3=hard)
    
    Returns:
        Initial observation after reset
    """
    global env_instance
    
    try:
        # Create new environment instance
        env_instance = MyEnvEnvironment()
        obs = env_instance.reset(task_id=task_id)
        
        # Return observation in OpenEnv format
        return obs.model_dump()
        
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
            task_id=request.task_id if request.task_id else env_instance.task_id
        )
        
        # Execute step
        obs = env_instance.step(action)
        
        # Return observation in OpenEnv format
        return obs.model_dump()
        
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


def main():
    """Entry point for uv run server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )


if __name__ == "__main__":
    main()