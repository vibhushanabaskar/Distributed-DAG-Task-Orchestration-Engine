import random
import time

print("Generating random numbers...")
time.sleep(2)

numbers = [random.randint(1, 1000) for _ in range(100000)]
print("Generated", len(numbers), "numbers")