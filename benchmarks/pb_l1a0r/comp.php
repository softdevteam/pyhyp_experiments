<?php{


$__pyhyp__countdown = embed_py_func("def __pyhyp__countdown(x):\n    while x > 0:\n        x -= 1");
function countdown($x){
    global $__pyhyp__countdown;
    return $__pyhyp__countdown( $x);
}

function outer($outer, $inner) {
	for ($i = 0; $i < $outer; $i++) {
		countdown($inner);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>