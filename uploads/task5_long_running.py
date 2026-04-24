import time

print("Long task starting...")

for i in range(1, 6):
    print(f"Processing step {i}/5")
    time.sleep(2)

print("Long task finished.")