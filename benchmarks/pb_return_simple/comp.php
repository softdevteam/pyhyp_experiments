<?php{

$__pyhyp__f_ret = embed_py_func("def __pyhyp__f_ret():\n    return 1");
function f_ret(){
    global $__pyhyp__f_ret;
    return $__pyhyp__f_ret();
}

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

run_iter(1000000000);

}?>