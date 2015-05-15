<?php{

compile_py_func_global("def multiply_and_add(a, b, c):\n    return a + b * c");

function outer($outer, $inner_unused) {
	$iter_countdown = $outer * 10;
	$i = $iter_countdown;
	while($i > 0) {
		$i = multiply_and_add($i, 1, -1);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>