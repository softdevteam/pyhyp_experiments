<?php{
compile_py_func_global("def f_ret():\n    return 1");

function f_call($n) {

	$ct = 0;
	for ($i = 0; $i < $n; $i++) {
		$ct += f_ret();
	}
	assert($ct == $n);
}

function run_iter($n) {
	f_call($n);
}
}?>