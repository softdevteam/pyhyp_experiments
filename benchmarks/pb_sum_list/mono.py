
def f_rcv(ary):
    ct = 0
    for i in ary:
        ct += i
    return ct

def f_call(n):

    a = range(1000)

    v = 0
    for i in xrange(n):
        v += f_rcv(a)

    expect = 499500 * n
    assert v == expect

def run_iter(n):
    f_call(n)

run_iter(900000)
