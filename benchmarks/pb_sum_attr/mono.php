<?php

// Same as pb_sum_meth, just using a attribute

class Sum {
	public $res = 0;

	function f_rcv($a1, $a2, $a3, $a4, $a5) {
		$this->res = $a1 + $a2 + $a3 + $a4 + $a5;
	}
}

function f_call($n) {
	$s = new Sum();

	$x = 31415;
	$expect = 5 * $x + 15;
	for ($i = 0; $i < $n; $i++) {
		$s->f_rcv($x + 1, $x + 2, $x + 3, $x + 4, $x + 5);
		assert($s->res == $expect);
	}
}

function run_iter($n) {
	f_call($n);
}

?>
