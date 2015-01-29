
def multiply_and_add(a, b, c):
    return a + b * c

def outer(outer, inner_unused):
    iter_countdown = outer * 10
    i = iter_countdown
    while i > 0:
        i = multiply_and_add(i, 1, -1)

def run_iter(n):
    outer(n, 10000)
