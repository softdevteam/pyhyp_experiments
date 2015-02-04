<?php{


embed_py_func_global("def Fannkuch_run(n):\n    check = 0\n    perm = [None for i in xrange(n)]\n    count = [None for i in xrange(n)]\n    maxPerm = [None for i in xrange(n)]\n    maxFlipsCount = 0\n    m = n - 1\n\n    perm1 = range(n)\n\n    r = n\n    while True:\n        while r != 1:\n            count[r-1] = r\n            r -= 1\n\n        if not (perm1[0] == 0 or perm1[m] == m):\n            for i in xrange(n):\n                perm[i] = perm1[i]\n\n            flipsCount = 0\n\n            while True:\n                k = perm[0]\n\n                if k == 0:\n                    break\n\n                k2 = (k + 1) >> 1\n\n                for i in xrange(k2):\n                    temp = perm[i]\n                    perm[i] = perm[k-i]\n                    perm[k - i] = temp\n                flipsCount += 1\n\n            if flipsCount > maxFlipsCount:\n                maxFlipsCount = flipsCount\n                for i in xrange(n):\n                    maxPerm[i] = perm1[i]\n\n        while True:\n            if r == n:\n                return maxFlipsCount\n\n            perm0 = perm1[0]\n            i = 0\n            while i < r:\n                j = i + 1\n                perm1[i] = perm1[j]\n                i = j\n            perm1[r] = perm0\n\n            count[r] = count[r] - 1\n            if count[r] > 0:\n                break\n\n            r += 1\n");
function run_iter($n) {
	$res = Fannkuch_run($n);
}

run_iter(10);
}?>