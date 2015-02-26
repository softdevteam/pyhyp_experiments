def g(i):
    raise RuntimeError("Except %s" % i)

def f(n):
    i = 0
    while i < n:
        try:
            g(i)
            assert False
        except RuntimeError as e:
            assert e.args[0] == "Except %s" % i
        i += 1

def run_iter(n):
    f(n)
