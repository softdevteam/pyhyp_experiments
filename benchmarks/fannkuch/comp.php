<?php{
embed_py_func_global("def dbg_print_py(func, *args):\n    return\n\n    import sys\n    sys.stdout.write(\"%s: \" % func)\n    for i in args:\n        sys.stdout.write(\"%s \" % i)\n    sys.stdout.write(\"\\n\")");

function dbg_print_php() {
    return;
    
    $ar = func_get_args();
    $len = func_num_args();
    
    echo "{$ar[0]}: ";
    for($i = 1; $i < $len; $i++) {
        echo "${ar[$i]} ";
    }
    echo "\n";
}
    

embed_py_func_global("def Fannkuch_run(n):\n    check = 0\n    perm = [None for i in xrange(n)]\n    count = [None for i in xrange(n)]\n    maxPerm = [None for i in xrange(n)]\n    maxFlipsCount = 0\n    m = n - 1\n\n    perm1 = range(n)\n\n    r = n\n    while True:\n        dbg_print_py(\"Outer loop\")\n        while r != 1:\n            dbg_print_py(\"Inner loop 1\", r)\n            count[r-1] = r\n            r -= 1\n\n        if not (perm1[0] == 0 or perm1[m] == m):\n            dbg_print_py(\"Inner cond 1\", perm1[0], perm1[m], m)\n            for i in xrange(n):\n                dbg_print_py(\"Inner loop 2\", i, n)\n                perm[i] = perm1[i]\n\n            flipsCount = 0\n\n            while True:\n                k = perm[0]\n\n                if k == 0:\n                    break\n                    \n                dbg_print_py(\"Inner loop 3\", k, perm[0])\n\n                k2 = (k + 1) >> 1\n\n                for i in xrange(k2):\n                    dbg_print_py(\"Inner loop 4\", i, k2)\n                    temp = perm[i]\n                    perm[i] = perm[k-i]\n                    perm[k - i] = temp\n                flipsCount += 1\n\n            if flipsCount > maxFlipsCount:\n                dbg_print_py(\"Inner cond 2\", flipsCount, maxFlipsCount)\n                maxFlipsCount = flipsCount\n                for i in xrange(n):\n                    dbg_print_py(\"Inner loop 5\", i, n)\n                    maxPerm[i] = perm1[i]\n\n        while True:\n            dbg_print_py(\"Inner loop 6\")\n            if r == n:\n                dbg_print_py(\"Inner cond 3\", r, n)\n                return maxFlipsCount\n\n            perm0 = perm1[0]\n            i = 0\n            while i < r:\n                dbg_print_py(\"Inner loop 7\", i, r)\n                j = i + 1\n                perm1[i] = perm1[j]\n                i = j\n            perm1[r] = perm0\n\n            count[r] = count[r] - 1\n            if count[r] > 0:\n                dbg_print_py(\"Inner cond 4\", r)\n                break\n\n            r += 1\n");
function run_iter($n) {
	$res = Fannkuch_run($n);
 dbg_print_php("run_iter", $res);
}
}?>