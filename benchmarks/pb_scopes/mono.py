def f_outer(n):
    inc = 2

    def inner(x):
        return x + inc

    tot = 0
    i = 0
    while i < n:
        tot = inner(tot)
        i += 1

    expect = 2 * n
    assert tot == expect

def run_iter(n):
    f_outer(n)
