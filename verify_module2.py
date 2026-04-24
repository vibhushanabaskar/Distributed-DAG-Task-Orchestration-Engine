import requests
import time
import sys
import uuid

API_URL = "http://localhost:8000"
POLL_INTERVAL = 2
TIMEOUT = 40  # seconds


def wait_for_condition(condition_fn, timeout, description):
    start = time.time()
    while time.time() - start < timeout:
        if condition_fn():
            return True
        time.sleep(POLL_INTERVAL)
    print(f"❌ Timeout waiting for: {description}")
    return False


def test_dag_execution():
    run_id = f"test_dag_{str(uuid.uuid4())[:8]}"
    print(f"\n🚀 Submitting DAG with ID: {run_id}")

    dag_payload = {
        "dag_id": run_id,
        "tasks": [
            {
                "id": f"A_{run_id}",
                "command": "echo 'Task A started'; sleep 10; echo 'Task A finished'",
                "dependencies": []
            },
            {
                "id": f"B_{run_id}",
                "command": "echo 'Task B running'",
                "dependencies": [f"A_{run_id}"]
            }
        ]
    }

    response = requests.post(f"{API_URL}/dags/", json=dag_payload)
    if response.status_code != 200:
        print(f"❌ DAG submission failed: {response.text}")
        sys.exit(1)

    print("✅ DAG submitted successfully")

    # Helper function to get progress
    def get_progress():
        res = requests.get(f"{API_URL}/dags/{run_id}/progress")
        if res.status_code != 200:
            return None
        return res.json()

    # ---- STEP 1: Confirm Task A starts first ----
    print("\n🔍 Verifying dependency enforcement...")

    def task_a_running():
        progress = get_progress()
        if not progress:
            return False
        return progress["RUNNING"] == 1 and progress["SUCCESS"] == 0

    if not wait_for_condition(task_a_running, 15, "Task A to start running"):
        sys.exit(1)

    print("✅ Task A is running")
    print("🛑 Verifying Task B has NOT started yet...")

    progress = get_progress()
    if progress["RUNNING"] > 1:
        print("❌ Dependency violation! Task B started too early.")
        sys.exit(1)

    print("✅ Task B correctly waiting (PENDING)")

    # ---- STEP 2: Confirm Task A completes ----
    print("\n⏳ Waiting for Task A to complete...")

    def task_a_completed():
        progress = get_progress()
        if not progress:
            return False
        return progress["SUCCESS"] >= 1

    if not wait_for_condition(task_a_completed, TIMEOUT, "Task A to complete"):
        sys.exit(1)

    print("✅ Task A completed successfully")

    # ---- STEP 3: Confirm Task B executes after A ----
    print("\n🔁 Waiting for Task B to execute...")

    def dag_completed():
        progress = get_progress()
        if not progress:
            return False
        return progress["SUCCESS"] == progress["total_tasks"]

    if not wait_for_condition(dag_completed, TIMEOUT, "DAG completion"):
        sys.exit(1)

    final_progress = get_progress()

    print("\n🎯 FINAL DAG PROGRESS:")
    print(final_progress)

    if final_progress["completion_percentage"] == 100.0:
        print("\n🎉 DAG EXECUTION VERIFIED SUCCESSFULLY!")
        # ---- STEP 4: Fetch Full DAG Details (For Dashboard Testing) ----
        print("\n📊 Fetching Full DAG Structure...")

    dag_details_response = requests.get(f"{API_URL}/dags/{run_id}")

    if dag_details_response.status_code == 200:
        dag_details = dag_details_response.json()
        print("\n🧩 FULL DAG DETAILS:")
        print(dag_details)
    else:
        print("❌ Failed to fetch full DAG details:", dag_details_response.text)
        sys.exit(1)



if __name__ == "__main__":
    test_dag_execution()
