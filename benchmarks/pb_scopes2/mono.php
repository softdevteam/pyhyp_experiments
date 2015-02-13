<?php

function f_outer($n) {
	$inc = 2;

	$inner = function($x) use(&$inc) {
        $inner2 = function($x) use (&$inc) {
            return $x + $inc;
        };
        return $inner2($x);
	};

	$tot = 0;
	for ($i = 0; $i < $n; $i++) {
		$tot = $inner($tot);
	}

	$expect = 2 * $n;
	assert($tot == $expect);

}

function run_iter($n) {
	f_outer($n);
}

?>
