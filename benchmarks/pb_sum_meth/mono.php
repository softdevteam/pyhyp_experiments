<?php

// Same as pb_sum, just using a method

class Sum {
	function f_rcv($a1, $a2, $a3, $a4, $a5) {
		return $a1 + $a2 + $a3 + $a4 + $a5;
	}
}

function f_call($n) {
	$s = new Sum();

	$x = 31415;
	$expect = $x * 5 + 15;
	for ($i = 0; $i < $n; $i++) {
		$res = $s->f_rcv($x + 1, $x + 2, $x + 3, $x + 4, $x + 5);
		assert($res == $expect);
	}
}

function run_iter($n) {
	f_call($n);
}

?>
