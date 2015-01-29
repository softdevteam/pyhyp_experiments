<?php{


$__pyhyp__sum_up_to_n = embed_py_func("def __pyhyp__sum_up_to_n(n):\n    result = 0\n    while n > 0:\n        result += n\n        n -= 1\n    return result");
function sum_up_to_n($n){
    global $__pyhyp__sum_up_to_n;
    return $__pyhyp__sum_up_to_n( $n);
}

function outer($outer, $inner) {
	$correct = sum_up_to_n($inner);
	for ($i = 0; $i < $outer; $i++) {
		$res = sum_up_to_n($inner);
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>