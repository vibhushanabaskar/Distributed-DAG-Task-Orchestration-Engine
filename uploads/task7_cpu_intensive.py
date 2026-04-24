import time

print("Starting CPU intensive loop...")
time.sleep(1)

total = 0
for i in range(1, 2000):
    total += i

print("Total:", total)