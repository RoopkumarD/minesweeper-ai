def factorial(n):
    total = 1
    for i in range(1, n + 1):
        total = total * i

    return total


def nCr(n, r):
    if r < 0 or r > n:
        raise Exception("r < 0 or r > n")

    num = factorial(n)
    deno = factorial(n - r) * factorial(r)

    return num / deno
