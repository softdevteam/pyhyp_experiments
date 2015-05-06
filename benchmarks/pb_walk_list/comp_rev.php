<?php{
function make_chain($x) {
    $curr = "end";
    while ($x >= 0) {
        $curr = array($x, 2 * $x, $curr);
        $x -= 1;
    }
    return $curr;
}

function consume_chain($chain) {
    $res = 0;
    while($chain != "end") {
        $val1 = $chain[0];
        $val2 = $chain[1];
        $chain = $chain[2];
        $res += $val2 - $val1;
    }
    return $res;
}

embed_py_func_global("def outer(outer, inner):\n    import math\n    correct = math.floor(inner * (inner + 1) / 2)\n    \n    i = 0\n    while i < outer:\n        res = consume_chain(make_chain(inner))\n        assert res == correct\n        i += 1");

function run_iter($n) {
	outer($n, 10000);
}
}?>