"""
Grading functions for OpenOps tasks
Each grader returns a score between 0.0 and 1.0
"""

from typing import Callable
from server.my_env_environment import MyEnvEnvironment


def grade_task_1(env: MyEnvEnvironment) -> float:
    """
    Grade Task 1: Simple API Crash
    
    Scoring criteria:
    - Investigation (30%): Read alerts + inspected API logs
    - Mitigation (50%): Restarted API service
    - Resolution (20%): Incident resolved
    
    Args:
        env: Environment instance after task completion
        
    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0
    
    # Investigation (30%)
    if env.alerts_read:
        score += 0.15
    if "api" in env.logs_inspected:
        score += 0.15
    
    # Mitigation (50%)
    if "api" in env.services_restarted:
        score += 0.50
    
    # Resolution (20%)
    if env.incident_resolved:
        score += 0.20
    
    return min(1.0, score)


def grade_task_2(env: MyEnvEnvironment) -> float:
    """
    Grade Task 2: Bad Deployment
    
    Scoring criteria:
    - Investigation (25%): Read alerts + inspected database logs
    - Mitigation (45%): Rolled back database
    - Communication (15%): Notified team
    - Resolution (15%): Incident resolved
    
    Args:
        env: Environment instance after task completion
        
    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0
    
    # Investigation (25%)
    if env.alerts_read:
        score += 0.10
    if "database" in env.logs_inspected:
        score += 0.15
    
    # Mitigation (45%)
    if "database" in env.services_rolled_back:
        score += 0.45
    
    # Communication (15%)
    if env.teams_notified:
        score += 0.15
    
    # Resolution (15%)
    if env.incident_resolved:
        score += 0.15
    
    return min(1.0, score)


def grade_task_3(env: MyEnvEnvironment) -> float:
    """
    Grade Task 3: Cascading Failure
    
    Scoring criteria:
    - Investigation (20%): Read alerts + inspected both services
    - Mitigation (50%): Scaled database + restarted API
    - Communication (15%): Notified team + updated status
    - Resolution (15%): Incident resolved
    
    Args:
        env: Environment instance after task completion
        
    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0
    
    # Investigation (20%)
    if env.alerts_read:
        score += 0.05
    if "database" in env.logs_inspected:
        score += 0.075
    if "api" in env.logs_inspected:
        score += 0.075
    
    # Mitigation (50%)
    if "database" in env.services_scaled:
        score += 0.25
    if "api" in env.services_restarted:
        score += 0.25
    
    # Communication (15%)
    if env.teams_notified:
        score += 0.075
    if env.status_page_updated:
        score += 0.075
    
    # Resolution (15%)
    if env.incident_resolved:
        score += 0.15
    
    return min(1.0, score)


def get_grader(task_id: int) -> Callable[[MyEnvEnvironment], float]:
    """
    Get the appropriate grader function for a task.
    
    Args:
        task_id: Task ID (1, 2, or 3)
        
    Returns:
        Grader function
        
    Raises:
        ValueError: If task_id is invalid
    """
    graders = {
        1: grade_task_1,
        2: grade_task_2,
        3: grade_task_3
    }
    
    if task_id not in graders:
        raise ValueError(f"Invalid task_id: {task_id}. Must be 1, 2, or 3.")
    
    return graders[task_id]