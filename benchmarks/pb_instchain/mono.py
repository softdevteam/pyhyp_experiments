class Terminator(object):

 def is_terminator(self):
    return True

class Chain(object):

    def __init__(self, value, next):
        self.value = value
        self.next = next

    def is_terminator(self):
        return False

    def get_value(self):
        return self.value

    def get_next(self):
        return self.next

def make_instchain(x):
    cur = Terminator()
    while x >= 0:
        cur = Chain(x, cur)
        x -= 1
    return cur

def consume_instchain(chain):
    res = 0
    while not chain.is_terminator():
        res += chain.get_value()
        chain = chain.get_next()
    return res

def outer(outer, inner):
    correct = inner * (inner + 1) // 2
    i = 0
    while i < outer:
        res = consume_instchain(make_instchain(inner))
        assert(res == correct)
        i += 1

def run_iter(n):
    outer(n, 10000)
