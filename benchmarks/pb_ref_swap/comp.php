<?php{

embed_py_func_global("@php_decor(refs=[0, 1])\ndef f_swap(a_ref, b_ref):\n    # python has no notion of references.\n    # To get the desired effect, we must pass mutable args.\n    a, b = a_ref.deref(), b_ref.deref()\n    a_ref.store(b)\n    b_ref.store(a)");

function f_call($n) {

	$ct = 0;
	for ($i = 0; $i < $n; $i++) {
		$x1 = array(-$i - $n + 3);
		$x2 = array($i + $n);
		f_swap($x1, $x2);	
		$ct += $x1[0] + $x2[0];
	}
	// each loop iteration adds 3
	$expect = $n * 3;
	assert($ct == $expect);
}

function run_iter($n) {
	f_call($n);
}
}?>