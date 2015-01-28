def f_rcv(a1, a2, a3, a4, a5, x):
    return a1 + a2 + a3 + a4 + a5 + x

def f_call(n):

    ct = 0
    for i in xrange(n):
        ct += f_rcv(n + 1, n + 2, n + 3, n + 4, n + 5, i)

    # each iteration adds 5n + 15 + i.
    # the sum of all of the i we add is (i/2)(i-1).
    expect = int(((float(i) / 2) * (i - 1))) + (n * (5 * n + 15))
    import pdb; pdb.set_trace()
    assert ct == expect

def run_iter(n):
	f_call(n)

run_iter(900000000)
