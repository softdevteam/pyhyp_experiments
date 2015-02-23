def f_ret():
    return 1

def f_call(n):
    ct = 0

    i = 0
    while i < n:
        ct += f_ret()
        i += 1

    assert(ct == n)


def run_iter(n):
    f_call(n)
