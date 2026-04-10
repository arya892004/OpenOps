"""
Grading functions for OpenOps tasks.
Each task has a grader that scores performance from 0.0 to 1.0.
"""

from server.my_env_environment import MyEnvEnvironment


def grade_task_1(env: MyEnvEnvironment) -> float:
    """
    Grade Task 1: Simple API Crash
    
    Scoring:
    - Investigation (30%): Inspected API logs?
    - Mitigation (50%): Restarted API?
    - Resolution (20%): Incident resolved?
    """
    score = 0.0
    
    if "inspect_logs_api" in env.investigations:
        score += 0.3
    
    if "restart_api" in env.mitigations:
        score += 0.5
    
    if env.incident_resolved and env.services["api"]["status"] == "healthy":
        score += 0.2
    
    return min(1.0, score)


def grade_task_2(env: MyEnvEnvironment) -> float:
    """
    Grade Task 2: Bad Deployment
    
    Scoring:
    - Investigation (20%): Inspected database logs?
    - Correct mitigation (50%): Rollback (not restart!)
    - Communication (15%): Notified team?
    - Resolution (15%): Incident resolved?
    """
    score = 0.0
    
    if "inspect_logs_database" in env.investigations:
        score += 0.2
    
    if "rollback_database" in env.mitigations:
        score += 0.5
    elif "restart_database" in env.mitigations:
        score -= 0.2  # Wrong action penalty
    
    if env.teams_notified:
        score += 0.15
    
    if env.incident_resolved and env.services["database"]["status"] == "healthy":
        score += 0.15
    
    return max(0.0, min(1.0, score))


def grade_task_3(env: MyEnvEnvironment) -> float:
    """
    Grade Task 3: Cascading Failure
    
    Scoring:
    - Multi-service investigation (20%)
    - Correct mitigations (40%)
    - Communication (20%)
    - Resolution (20%)
    """
    score = 0.0
    
    # Investigation
    if "inspect_logs_database" in env.investigations:
        score += 0.1
    if "inspect_logs_api" in env.investigations:
        score += 0.1
    
    # Mitigation
    if "scale_database" in env.mitigations:
        score += 0.2
    if "restart_api" in env.mitigations:
        score += 0.2
    
    # Communication
    if env.teams_notified:
        score += 0.1
    if env.status_page_updated:
        score += 0.1
    
    # Resolution
    if env.incident_resolved:
        if env.services["database"]["load"] < 0.7 and env.services["api"]["status"] == "healthy":
            score += 0.2
    
    return min(1.0, score)


def get_grader(task_id: int):
    """Factory function to get the appropriate grader."""
    graders = {
        1: grade_task_1,
        2: grade_task_2,
        3: grade_task_3
    }
    return graders.get(task_id, grade_task_1)