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

        while r != 1:
            count[r-1] = r
            r -= 1

        if not (perm1[0] == 0 or perm1[m] == m):
            i = 0
            while i < n:
                perm[i] = perm1[i]
                i += 1

            flipsCount = 0

            while True:
                k = perm[0]

                if k == 0:
                    break


                k2 = (k + 1) >> 1

                i = 0
                while i < k2:
                    temp = perm[i]
                    perm[i] = perm[k-i]
                    perm[k - i] = temp
                    i += 1
                flipsCount += 1

            if flipsCount > maxFlipsCount:
                maxFlipsCount = flipsCount
                i = 0
                while i < n:
                    maxPerm[i] = perm1[i]
                    i += 1

        while True:
            if r == n:
                return maxFlipsCount

            perm0 = perm1[0]
            i = 0
            while i < r:
                j = i + 1
                perm1[i] = perm1[j]
                i = j
            perm1[r] = perm0

            count[r] = count[r] - 1
            if count[r] > 0:
                break

            r += 1

def run_iter(n):
    res = Fannkuch_run(n)

