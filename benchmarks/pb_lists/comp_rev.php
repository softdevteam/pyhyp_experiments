<?php{
embed_py_func_global("def make_list(x):\n    res = []\n    while x >= 0:\n        res.append(x)\n        x -= 1\n    return res");

function consume_list($l) {
    $res = 0;
    foreach($l as $i) {
        $res += $i;
    }
    return $res;
}

embed_py_func_global("def outer(outer, inner):\n    correct = floor(inner * (inner + 1) / 2)\n    \n    i = 0\n    while i < outer:\n        res = consume_list(make_list(inner))\n        assert res == correct\n        i += 1");

function run_iter($n) {
	outer($n, 10000);
}

run_iter(100);
}?>