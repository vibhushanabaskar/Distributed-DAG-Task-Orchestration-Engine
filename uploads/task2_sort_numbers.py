import random
import time

print("Sorting numbers...")
time.sleep(3)

numbers = [random.randint(1, 1000) for _ in range(100000)]
numbers.sort()

print("Sorting complete.")