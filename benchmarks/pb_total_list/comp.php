<?php{


$__pyhyp__f_rcv = embed_py_func("def __pyhyp__f_rcv(ary):\n    ct = 0\n    for i in ary:\n        ct += i\n    return ct");
function f_rcv($ary){
    global $__pyhyp__f_rcv;
    return $__pyhyp__f_rcv( $ary);
}

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