# Same as pb_sum_meth, just using a attribute

class Sum(object):

    def __init__(self):
        self.res = 0

    def f_rcv(self, a1, a2, a3, a4, a5):
        self.res = a1 + a2 + a3 + a4 + a5

def f_call(n):
    s = Sum()

    x = 31415;
    expect = x * 5 + 15
    for i in xrange(n):
        s.f_rcv(x + 1, x + 2, x + 3, x + 4, x + 5)
        assert s.res == expect

def run_iter(n):
    f_call(n)
