import math

def closest_divisors(n: int) -> tuple[int, int]:
    for i in range(int(math.isqrt(n)), 0, -1):
        if n % i == 0:
            return (i, n // i)
    return (0, 0)
