# Same as pb_sum_meth, just using a attribute

class Sum(object):

    def __init__(self):
        self.ct = 0

    def f_rcv(self, a1, a2, a3, a4, a5):
        self.ct += a1 + a2 + a3 + a4 + a5

def f_call(n):
    s = Sum()

    for i in xrange(n):
        s.f_rcv(n + 1, n + 2, n + 3, n + 4, n + 5)

    # each iteration adds 5n + 15
    expect = n * (5 * n + 15)

    assert s.ct == expect

def run_iter(n):
    f_call(n)
