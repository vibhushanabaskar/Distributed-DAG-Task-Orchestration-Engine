import random
import time

print("Multiplying matrices...")
time.sleep(3)

size = 150
A = [[random.randint(1, 5) for _ in range(size)] for _ in range(size)]
B = [[random.randint(1, 5) for _ in range(size)] for _ in range(size)]

result = [[sum(A[i][k]*B[k][j] for k in range(size)) for j in range(size)] for i in range(size)]

print("Matrix multiplication done.")