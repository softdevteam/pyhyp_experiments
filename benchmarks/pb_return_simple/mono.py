def f_ret():
    return 1

def f_call(n):
    ct = 0

    for i in xrange(n):
        ct += f_ret()

    assert(ct == n)


def run_iter(n):
    f_call(n)

run_iter(1000000000)
