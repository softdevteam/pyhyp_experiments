
def countdown(x):
    while x > 0:
        x -= 1

def outer(outer, inner):
    for i in xrange(outer):
        countdown(inner)

def run_iter(n):
	outer(n, 10000)
