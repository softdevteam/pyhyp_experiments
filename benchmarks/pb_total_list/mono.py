def f_rcv(ary):
    ct = 0
    for i in ary:
        ct += i
    return ct

def f_call(n):
    a = range(1000)

    v = 0
    i = 0
    while i < n:
        v += f_rcv(a)
        i += 1

    expect = 499500 * n
    assert v == expect

def run_iter(n):
    f_call(n)
