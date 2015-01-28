<?php{

$__pyhyp__f_swap = embed_py_func("def __pyhyp__f_swap(a_l, b_l):\n    # python has no notion of references.\n    # To get the desired effect, we must pass mutable args.\n    a, b = a_l[0], b_l[0]\n    a_l[0], b_l[0] = b, a");
function f_swap($a_l, $b_l){
    global $__pyhyp__f_swap;
    return $__pyhyp__f_swap( $a_l, $b_l);
}

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