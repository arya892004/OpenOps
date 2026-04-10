"""
Pre-submission validation - Run this before deploying!
"""

import os
import sys
import subprocess


def check(condition, message):
    """Helper to check condition."""
    if condition:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False


def validate():
    """Run all validation checks."""
    print("="*60)
    print("OpenOps Pre-Submission Validation")
    print("="*60)
    print()
    
    checks = []
    
    # File existence
    print("📁 Checking required files...")
    checks.append(check(os.path.exists("models.py"), "models.py exists"))
    checks.append(check(os.path.exists("server/my_env_environment.py"), "server/my_env_environment.py exists"))
    checks.append(check(os.path.exists("graders.py"), "graders.py exists"))
    checks.append(check(os.path.exists("inference.py"), "inference.py exists"))
    checks.append(check(os.path.exists("openenv.yaml"), "openenv.yaml exists"))
    checks.append(check(os.path.exists("README.md"), "README.md exists"))
    checks.append(check(os.path.exists("server/Dockerfile"), "server/Dockerfile exists"))
    checks.append(check(os.path.exists("server/requirements.txt"), "server/requirements.txt exists"))
    checks.append(check(os.path.exists("server/app.py"), "server/app.py exists"))
    checks.append(check(os.path.exists("client.py"), "client.py exists"))
    print()
    
    # Import test
    print("🔧 Testing imports...")
    try:
        from models import IncidentAction, IncidentObservation, IncidentState
        from server.my_env_environment import MyEnvEnvironment
        from graders import get_grader
        checks.append(check(True, "All imports successful"))
    except Exception as e:
        checks.append(check(False, f"Import failed: {e}"))
    print()
    
    # Environment test
    print("🎮 Testing environment...")
    try:
        from server.my_env_environment import MyEnvEnvironment
        from models import IncidentAction
        
        env = MyEnvEnvironment()
        obs = env.reset(task_id=1)
        checks.append(check(obs is not None, "Environment resets"))
        
        action = IncidentAction(action_id=0, task_id=1)
        obs = env.step(action)
        checks.append(check(obs.reward is not None, "Environment steps"))
    except Exception as e:
        checks.append(check(False, f"Environment test failed: {e}"))
    print()
    
    # Grader test
    print("📊 Testing graders...")
    try:
        from graders import get_grader
        from server.my_env_environment import MyEnvEnvironment
        
        env = MyEnvEnvironment()
        env.reset(task_id=1)
        grader = get_grader(1)
        score = grader(env)
        checks.append(check(0.0 <= score <= 1.0, f"Grader works (score: {score:.2f})"))
    except Exception as e:
        checks.append(check(False, f"Grader test failed: {e}"))
    print()
    
    # Inference script test
    print("🤖 Testing inference script...")
    try:
        with open("inference.py", "r") as f:
            content = f.read()
        
        has_start = "[START]" in content
        has_step = "[STEP]" in content
        has_end = "[END]" in content
        
        checks.append(check(has_start and has_step and has_end, "Has required log format"))
        checks.append(check("from openai import OpenAI" in content or "OpenAI" in content, "Uses OpenAI-compatible client"))
    except Exception as e:
        checks.append(check(False, f"Inference validation failed: {e}"))
    print()
    
    # README check
    print("📖 Checking README...")
    try:
        with open("README.md", "r") as f:
            readme = f.read()
        
        checks.append(check(len(readme) > 500, "README has content (>500 chars)"))
        checks.append(check("OpenOps" in readme, "README mentions project name"))
        checks.append(check("Task 1" in readme or "Task 2" in readme, "README describes tasks"))
    except Exception as e:
        checks.append(check(False, f"README check failed: {e}"))
    print()
    
    # Summary
    print("="*60)
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ ALL CHECKS PASSED - READY TO SUBMIT! 🚀")
        return True
    else:
        print(f"\n⚠️  {total - passed} issues found - FIX BEFORE SUBMITTING!")
        return False


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)