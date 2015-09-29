<?php{

compile_py_func_global("def f_rcv(ary):\n    ary = ary.as_list()\n    ct = 0\n    for i in ary:\n        ct += i\n    return ct");

function f_call($n) {

	$a = array();
	for ($i = 0; $i < 1000; $i++) {
		$a[] = $i;
	}

	$v = 0;
	for ($i = 0; $i < $n; $i++) {
		$v += f_rcv($a);
	}
	
	$expect = 499500 * $n;
	assert($v == $expect);
}

function run_iter($n) {
	f_call($n);
}
}?>