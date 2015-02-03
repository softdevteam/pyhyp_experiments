def dbg_print_py(func, *args):
    return

    import sys
    sys.stdout.write("%s: " % func)
    for i in args:
        sys.stdout.write("%s " % i)
    sys.stdout.write("\n")

def Fannkuch_run(n):
    check = 0
    perm = [None for i in xrange(n)]
    count = [None for i in xrange(n)]
    maxPerm = [None for i in xrange(n)]
    maxFlipsCount = 0
    m = n - 1

    perm1 = range(n)

    r = n
    while True:
        dbg_print_py("Outer loop");

        while r != 1:
            dbg_print_py("Inner loop 1", r)
            count[r-1] = r
            r -= 1

        if not (perm1[0] == 0 or perm1[m] == m):
            dbg_print_py("Inner cond 1", perm1[0], perm1[m], m)
            for i in xrange(n):
                dbg_print_py("Inner loop 2", i, n)
                perm[i] = perm1[i]

            flipsCount = 0

            while True:
                k = perm[0]

                if k == 0:
                    break

                dbg_print_py("Inner loop 3", k, perm[0])

                k2 = (k + 1) >> 1

                for i in xrange(k2):
                    dbg_print_py("Inner loop 4", i, k2)
                    temp = perm[i]
                    perm[i] = perm[k-i]
                    perm[k - i] = temp
                flipsCount += 1

            if flipsCount > maxFlipsCount:
                dbg_print_py("Inner cond 2", flipsCount, maxFlipsCount)
                maxFlipsCount = flipsCount
                for i in xrange(n):
                    dbg_print_py("Inner loop 5", i, n)
                    maxPerm[i] = perm1[i]

        while True:
            dbg_print_py("Inner loop 6")
            if r == n:
                dbg_print_py("Inner cond 3", r, n)
                return maxFlipsCount

            perm0 = perm1[0]
            i = 0
            while i < r:
                dbg_print_py("Inner loop 7", i, r)
                j = i + 1
                perm1[i] = perm1[j]
                i = j
            perm1[r] = perm0

            count[r] = count[r] - 1
            if count[r] > 0:
                dbg_print_py("Inner cond 4", r)
                break

            r += 1

def run_iter(n):
    res = Fannkuch_run(n)
    dbg_print_py("run_iter", res)
