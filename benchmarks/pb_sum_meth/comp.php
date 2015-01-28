<?php{
// Same as pb_sum, just using a method

class Sum {
 

}
embed_py_meth("Sum", "def f_rcv(self, a1, a2, a3, a4, a5):\n    return a1 + a2 + a3 + a4 + a5");

function f_call($n) {
	$s = new Sum();

	$ct = 0;
	for ($i = 0; $i < $n; $i++) {
		$ct += $s->f_rcv($n + 1, $n + 2, $n + 3, $n + 4, $n + 5);
	}
	// each iteration adds 5n + 15
	$expect = ($n * (5 * $n + 15));
	assert($ct == $expect);
}

function run_iter($n) {
	f_call($n);
}
}?>