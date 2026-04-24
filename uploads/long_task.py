import time

print("Long task running...")

for i in range(1, 11):
    print(f"Step {i}/10")
    time.sleep(1)

print("Long task finished.")