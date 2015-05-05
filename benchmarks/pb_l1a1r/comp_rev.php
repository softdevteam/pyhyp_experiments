<?php{
function sum_up_to_n($n) {
    $result = 0;
    while ($n > 0) {
        $result += $n;
        $n--;
    }
    return $result;
}

embed_py_func_global("def outer(outer, inner):\n    correct = sum_up_to_n(inner)\n    i = 0\n    while i < outer:\n        \$res = sum_up_to_n(inner)\n        assert res == correct");

function run_iter($n) {
	outer($n, 10000);
}

run_iter(100);
}?>