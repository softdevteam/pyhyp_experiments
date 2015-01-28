def f_outer(n):
    inc = 0

    def inner(x):
        return x + inc

    tot = 0
    for i in xrange(n):
        inc = i
        tot = inner(tot)

    # sum(0, 1, 2, ..., n - 1)
    expect = (float(n) / 2) * (n - 1)
    assert tot == expect

def run_iter(n):
	f_outer(n)

run_iter(500000000)

