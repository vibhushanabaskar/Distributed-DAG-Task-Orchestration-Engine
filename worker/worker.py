import os
import redis
import subprocess
from core.db.database import SessionLocal
from core.db.models import Task, TaskLog

# Connect to Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)

print("✅ Worker started. Waiting for tasks...")

while True:
    # Wait for task
    _, task_id = redis_client.blpop("task_queue")
    print(f"📥 Received Task ID: {task_id}")

    db = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            print("⚠ Task not found")
            continue

        print(f"▶ Executing task {task_id}")
        task.status = "RUNNING"
        db.commit()
        
        # Decide execution command
        if task.file_path:
            execution_command = f"python {task.file_path}"
        else:
            execution_command = task.command
        print("EXECUTION COMMAND:", execution_command)
        process = subprocess.Popen(
            execution_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            process.kill()
            task.status = "TIMEOUT"
            db.commit()

            # Store timeout log
            log_entry = TaskLog(
                task_id=task_id,
                log_content="Task timed out."
            )
            db.add(log_entry)
            db.commit()

            print("⏱ Task timed out")
            continue

        output_text = stdout.decode()
        error_text = stderr.decode()

        print("OUTPUT:")
        print(output_text)

        if error_text:
            print("ERROR:")
            print(error_text)

        # Combine stdout + stderr
        full_log = output_text
        if error_text:
            full_log += "\nERROR:\n" + error_text

        if process.returncode == 0:
            task.status = "SUCCESS"
            print("✅ Task completed successfully")
        else:
            task.status = "FAILED"
            print("❌ Task failed")

        db.commit()

        # ✅ Store execution log
        log_entry = TaskLog(
            task_id=task_id,
            log_content=full_log
        )
        db.add(log_entry)
        db.commit()

    except Exception as e:
        print("🚨 Worker error:", e)

    finally:
        db.close()
