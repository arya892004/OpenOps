---
title: OpenOps Incident Commander
emoji: 🚨
colorFrom: red
colorTo: orange
sdk: docker
pinned: false
---
# OpenOps: AI Incident Commander Environment

Production incident management environment where AI agents learn to handle real-world outages.

## Overview

OpenOps simulates production incidents requiring an AI Incident Commander to:
- Investigate alerts and logs
- Identify root causes  
- Execute mitigation actions (restart/rollback/scale)
- Communicate with teams and users
- Resolve incidents quickly to minimize revenue loss

## Environment Specification

### Observation Space
```python
{
    "active_alerts": List[str],
    "service_status": Dict[str, str],
    "recent_logs": Dict[str, List[str]],
    "metrics_summary": Dict[str, float],
    "customer_complaints": int,
    "time_elapsed": int,
    "revenue_loss": float,
    "teams_notified": bool,
    "status_page_updated": bool,
    "user_communication_sent": bool
}
```

### Action Space (21 actions)
- 0: read_alerts
- 1-4: inspect_logs_{service}
- 5-8: check_metrics_{service}
- 9-12: restart_{service}
- 13-14: rollback_{service}
- 15-16: scale_{service}
- 17-19: Communication actions
- 20: resolve_incident

### Three Tasks

**Task 1 (Easy): Simple API Crash**
- API service down due to OOM
- Solution: Inspect logs → Restart API

**Task 2 (Medium): Bad Deployment**
- Database deployment broke queries
- Solution: Inspect logs → Rollback deployment → Notify team

**Task 3 (Hard): Cascading Failure**
- Database overload → API timeouts → Customer impact
- Solution: Inspect both services → Scale database → Restart API → Communicate

## Installation
```bash
pip install -r server/requirements.txt
```

## Usage

### Run Locally
```bash
cd server
uvicorn app:app --reload
```

### Run Inference
```bash
export OPENAI_API_KEY="your-key"
python inference.py
```

## Grading

Each task scored 0.0-1.0 based on:
- Investigation quality
- Correct mitigation actions
- Communication
- Successful resolution

## Deployment

Deploy to HuggingFace Spaces:
```bash
openenv push
```

## 📊 Sample Output
