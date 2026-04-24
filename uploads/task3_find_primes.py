import time

print("Finding primes...")
time.sleep(2)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

primes = [i for i in range(5000) if is_prime(i)]
print("Found", len(primes), "primes")