import math

def factorial(n):
    if n < 0:
        raise ValueError("n должно быть >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def circle_area(radius):
    if radius < 0:
        raise ValueError("radius должно быть >= 0")
    return math.pi * radius ** 2


def main():
    n = 5
    r = 3.0
    print(f"{n}! = {factorial(n)}")
    print(f"Площадь круга радиуса {r} = {circle_area(r):.2f}")


# def main():
#     print("Hello from mlops!")


if __name__ == "__main__":
    main()
