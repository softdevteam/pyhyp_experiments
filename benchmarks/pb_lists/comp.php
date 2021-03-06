<?php{
function make_list($x) {
	$res = array();
	while ($x >= 0) {
		$res[] = $x;
		$x -= 1;
	}
	return $res;
}
 
compile_py_func_global("def consume_list(l):\n    ll = l.as_list()\n    res = 0\n    for i in ll:\n        res += i\n    return res");

function outer($outer, $inner) {
	$correct = floor($inner * ($inner + 1) / 2);

	for ($i = 0; $i < $outer; $i++) {
		$res = consume_list(make_list($inner));
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>