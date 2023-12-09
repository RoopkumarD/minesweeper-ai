def factorial(n):
    total = 1
    for i in range(1, n + 1):
        total = total * i

    return total


def nCr(n, r):
    num = factorial(n)
    deno = factorial(n - r) * factorial(r)

    return num / deno
