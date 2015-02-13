def f_outer(n):
    inc = 2

    def inner(x):
        def inner_2(x):
            return x + inc
        return inner_2(x)

    tot = 0
    for i in xrange(n):
        tot = inner(tot)

    expect = 2 * n
    assert tot == expect

def run_iter(n):
    f_outer(n)
