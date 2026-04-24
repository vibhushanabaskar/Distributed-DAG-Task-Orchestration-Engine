import time
import os
import redis
import datetime
from sqlalchemy.exc import OperationalError, ProgrammingError
from core.db.database import SessionLocal
from core.db.models import Task

# 1. Setup Redis Connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)

def check_parents_success(task, db):
    """
    Core Logic: Returns True ONLY if all parent tasks are 'SUCCESS'.
    """
    if not task.dependencies:
        return True
    
    parent_ids = task.dependencies
    parents = db.query(Task).filter(Task.id.in_(parent_ids)).all()
    
    if len(parents) != len(parent_ids):
        return False

    for parent in parents:
        if parent.status != "SUCCESS":
            return False 
            
    return True

def schedule_tasks():
    db = SessionLocal()
    try:
        # 1. Fetch only PENDING tasks
        pending_tasks = db.query(Task).filter(Task.status == "PENDING").all()
        
        for task in pending_tasks:
            # 2. The "Brain": Check if dependencies are met
            if check_parents_success(task, db):
                # Print timestamp to verify timing
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] [Scheduler] Task {task.id} is READY. Pushing to queue.", flush=True)
                
                # 3. Push to Redis (The Producer)
                redis_client.rpush("task_queue", task.id)
                
                # 4. Update DB State (The State Manager)
                task.status = "QUEUED"
                db.commit() # Save changes immediately
            else:
                pass
                
    except (OperationalError, ProgrammingError) as e:
        # Gracefully handle DB not ready or Tables missing
        # This explicitly catches the 'UndefinedTable' error during startup
        print(f"Database tables not ready yet (retrying in 5s)...", flush=True)
        db.rollback()
    except Exception as e:
        print(f"Error in scheduler loop: {e}", flush=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Scheduler Service Started...", flush=True)
    while True:
        schedule_tasks()
        time.sleep(5) # Polling Interval