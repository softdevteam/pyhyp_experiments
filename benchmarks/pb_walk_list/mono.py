def make_chain(x):
    curr = None
    while x >= 0:
        curr = [x, 2 * x, curr]
        x -= 1
    return curr

def consume_chain(chain):
    res = 0
    while chain != None:
        val1, val2, chain = chain
        res += val2 - val1
    return res

def outer(outer, inner):
    correct = inner * (inner + 1) // 2
    i = 0
    while i < outer:
        res = consume_chain(make_chain(inner))
        assert res == correct
        i += 1

def run_iter(n):
    outer(n, 10000)
