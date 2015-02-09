<?php{

embed_py_func_global("def countdown(x):\n    while x > 0:\n        x -= 1");

function outer($outer, $inner) {
	for ($i = 0; $i < $outer; $i++) {
		countdown($inner);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>