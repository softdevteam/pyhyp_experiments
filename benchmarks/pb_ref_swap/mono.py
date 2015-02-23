def f_swap(a_l, b_l):
    # python has no notion of references.
    # To get the desired effect, we must pass mutable args.
    tmp = a_l[0]
    a_l[0] = b_l[0]
    b_l[0] = tmp

def f_call(n):
    ct = 0;
    x1, x2 = [0], [0]

    for i in xrange(n):
        x1[0] = -i - n + 3
        x2[0] = i + n
        f_swap(x1, x2)
        ct += x1[0] + x2[0]

    # each loop iteration adds 3
    expect = n * 3
    assert ct == expect

def run_iter(n):
    f_call(n)
