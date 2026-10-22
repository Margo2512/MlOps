def is_prime(n):
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(n ** 0.5) + 1))


def main():
    n = 5
    print(f"{n} — простое число: {is_prime(n)}")