<?php{
function multiply_and_add($a, $b, $c) {
    return $a + $b * $c;
}


compile_py_func_global("def outer(outer, inner_unused):\n    iter_countdown = outer * 10\n    i = iter_countdown\n    while i > 0:\n        i = multiply_and_add(i, 1, -1)");

function run_iter($n) {
	outer($n, 10000);
}

}?>