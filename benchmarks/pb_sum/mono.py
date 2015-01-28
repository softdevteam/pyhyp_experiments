def f_rcv(a1, a2, a3, a4, a5):
    return a1 + a2 + a3 + a4 + a5

def f_call(n):

    ct = 0
    for i in xrange(n):
        ct += f_rcv(n + 1, n + 2, n + 3, n + 4, n + 5)

    # each iteration adds 5n + 15
    expect = n * (5 * n + 15)
    assert ct == expect

def run_iter(n):
	f_call(n)

run_iter(900000000)
