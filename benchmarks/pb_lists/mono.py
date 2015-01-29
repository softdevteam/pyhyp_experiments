def make_list(x):
    res = []
    while x >= 0:
        res.append(x)
        x -= 1
    return res

def consume_list(l):
    res = 0
    for i in l:
        res += i
    return res

def outer(outer, inner):
    correct = inner * (inner + 1) // 2

    for i in xrange(outer):
        res = consume_list(make_list(inner))
        assert res == correct

def run_iter(n):
    outer(n, 10000)
