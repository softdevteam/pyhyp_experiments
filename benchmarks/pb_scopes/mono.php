<?php

function f_outer($n) {
	$inc = 0;

	$inner = function($x) use(&$inc) {
		return $x + $inc;
	};

	$tot = 0;
	for ($i = 0; $i < $n; $i++) {
		$inc = $i;
		$tot = $inner($tot);
	}

	// sum(0, 1, 2, ..., n - 1)
	$expect = ($n / 2) * ($n - 1);
	assert($tot == $expect);

}

function run_iter($n) {
	f_outer($n);
}

run_iter(500000000);

?>
