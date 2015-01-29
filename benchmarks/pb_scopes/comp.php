<?php{
function f_outer($n) {
	$inc = 2;

 $inner = embed_py_func("def inner(x): return x + inc");;

	$tot = 0;
	for ($i = 0; $i < $n; $i++) {
		$tot = $inner($tot);
	}

	$expect = 2 * n;
	assert($tot == $expect);

}

function run_iter($n) {
	f_outer($n);
}

}?>