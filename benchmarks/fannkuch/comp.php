<?php

$__pyhyp__Fannkuch_run = embed_py_func("def __pyhyp__Fannkuch_run(n):\n    maxFlipsCount = 0\n    permSign = True \n    checksum = 0 \n \n    perm1 = list(xrange(0,n))   \n    count = perm1[:] \n    rxrange = xrange(2, n - 1) \n    nm = n - 1 \n    while 1: \n        k = perm1[0] \n        if k: \n            perm = perm1[:] \n            flipsCount = 1 \n            kk = perm[k] \n            while kk: \n                perm[:k+1] = perm[k::-1] \n                flipsCount += 1 \n                k = kk \n                kk = perm[kk] \n            if maxFlipsCount < flipsCount: \n                maxFlipsCount = flipsCount \n            checksum += flipsCount if permSign else -flipsCount \n \n        # Use incremental change to generate another permutation \n        if permSign: \n            perm1[0],perm1[1] = perm1[1],perm1[0] \n            permSign = False \n        else: \n            perm1[1],perm1[2] = perm1[2],perm1[1] \n            permSign = True \n            for r in rxrange: \n                if count[r]: \n                    break \n                count[r] = r \n                perm0 = perm1[0] \n                perm1[:r+1] = perm1[1:r+2] \n                perm1[r+1] = perm0 \n            else: \n                r = nm \n                if not count[r]:\n                    return maxFlipsCount \n            count[r] -= 1 ");function Fannkuch_run($n){global $__pyhyp__Fannkuch_run; return $__pyhyp__Fannkuch_run( $n);}

function run_iter($n) {
	Fannkuch_run($n);
}
?>
