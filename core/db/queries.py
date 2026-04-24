from sqlalchemy import func
from core.db import models

def get_dag_progress(db, dag_id: str):

    total = (
        db.query(func.count(models.Task.id))
        .filter(models.Task.dag_id == dag_id)
        .scalar()
    )

    if total == 0:
        return None

    status_counts = (
        db.query(models.Task.status, func.count(models.Task.id))
        .filter(models.Task.dag_id == dag_id)
        .group_by(models.Task.status)
        .all()
    )

    summary = {
        "total_tasks": total,
        "PENDING": 0,
        "RUNNING": 0,
        "SUCCESS": 0,
        "FAILED": 0,
    }

    for status, count in status_counts:
        summary[status] = count

    summary["completion_percentage"] = round(
        (summary["SUCCESS"] / total) * 100, 2
    )

    summary["is_completed"] = summary["SUCCESS"] == total

    return summary

def get_dag_details(db, dag_id: str):
    dag = db.query(models.DAG).filter(models.DAG.id == dag_id).first()

    if not dag:
        return None

    tasks = db.query(models.Task).filter(models.Task.dag_id == dag_id).all()

    return {
        "dag_id": dag.id,
        "tasks": [
            {
                "id": task.id,
                "status": task.status,
                "dependencies": task.dependencies,
                "command": task.command
            }
            for task in tasks
        ]
    }

def get_task_logs(db, task_id: str):
    logs = db.query(models.TaskLog).filter(models.TaskLog.task_id == task_id).all()

    return [
        {
            "log_content": log.log_content,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

