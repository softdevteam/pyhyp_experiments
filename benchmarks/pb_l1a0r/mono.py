
def countdown(x):
    while x > 0:
        x -= 1

def outer(outer, inner):
    i = 0
    while i < outer:
        countdown(inner)
        i += 1

def run_iter(n):
    outer(n, 10000)
