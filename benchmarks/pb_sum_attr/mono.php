<?php

// Same as pb_sum_meth, just using a attribute

class Sum {
	public $ct = 0;

	function f_rcv($a1, $a2, $a3, $a4, $a5, $x) {
		$this->ct += $a1 + $a2 + $a3 + $a4 + $a5 + $x;
	}
}

function f_call($n) {
	$s = new Sum();

	for ($i = 0; $i < $n; $i++) {
		$s->f_rcv($n + 1, $n + 2, $n + 3, $n + 4, $n + 5, $i);
	}
	// each iteration adds 5n + 15 + $i.
	// the sum of all of the $i we add is (i/2)(i-1).
	$expect = (($i / 2) * ($i - 1)) + ($n * (5 * $n + 15));

	assert($s->ct == $expect);
}

function run_iter($n) {
	f_call($n);
}

run_iter(1000000000);

?>
