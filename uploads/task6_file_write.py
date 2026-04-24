import time

print("Writing file...")
time.sleep(2)

with open("output.txt", "w") as f:
    f.write("Task completed successfully.")

print("File written.")