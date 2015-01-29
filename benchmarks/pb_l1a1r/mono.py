
def sum_up_to_n(n):
    result = 0
    while n > 0:
        result += n
        n -= 1
    return result

def outer(outer, inner):
    correct = sum_up_to_n(inner)
    for i in xrange(outer):
        res = sum_up_to_n(inner)
        assert(res == correct)

def run_iter(n):
    outer(n, 10000)
