def gcd(a, b):
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

def main():
    print(f"НОД(48, 18) = {gcd(48, 18)}")