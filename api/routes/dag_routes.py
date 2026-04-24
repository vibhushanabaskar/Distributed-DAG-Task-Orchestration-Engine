from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.db import models
from schemas.dag_schema import DAGSchema
from utils.cycle_detection import detect_cycle
from core.db.queries import get_dag_progress
from core.db.queries import get_dag_details,get_task_logs


router = APIRouter()

@router.post("/dags/")
def create_dag(dag: DAGSchema, db: Session = Depends(get_db)):

    tasks_data = [task.dict() for task in dag.tasks]

    if detect_cycle(tasks_data):
        raise HTTPException(status_code=400, detail="Cycle detected")

    task_ids = [task.id for task in dag.tasks]
    if len(task_ids) != len(set(task_ids)):
        raise HTTPException(status_code=400, detail="Duplicate task IDs")

    new_dag = models.DAG(id=dag.dag_id)
    db.add(new_dag)
    db.commit()

    for task in dag.tasks:
        db.add(models.Task(
            id=task.id,
            command=task.command,
            file_path=task.file_path,   # ADD THIS LINE
            dag_id=dag.dag_id,
            dependencies=task.dependencies
        ))

    db.commit()
    return {"message": "DAG created"}

@router.get("/dags/{dag_id}/progress")
def dag_progress(dag_id: str, db: Session = Depends(get_db)):

    result = get_dag_progress(db, dag_id)

    if not result:
        raise HTTPException(status_code=404, detail="DAG not found")

    return result

@router.get("/dags/{dag_id}")
def get_dag(dag_id: str, db: Session = Depends(get_db)):

    result = get_dag_details(db, dag_id)

    if not result:
        raise HTTPException(status_code=404, detail="DAG not found")

    return result

@router.get("/tasks/{task_id}/logs")
def get_logs(task_id: str, db: Session = Depends(get_db)):

    logs = get_task_logs(db, task_id)

    return {"task_id": task_id, "logs": logs}

@router.get("/dags")
def list_dags(db: Session = Depends(get_db)):
    dags = db.query(models.DAG).all()
    return [dag.id for dag in dags]
