<?php

function multiply_and_add($a, $b, $c) {
	return $a + $b * $c;
}

function outer($outer, $inner) {
	$iter_countdown = $outer * 10;
	$i = $iter_countdown;
	while($i > 0) {
		$i = multiply_and_add($i, 1, -1);
	}
}

function run_iter($n) {
	outer($n, 10000);
}

run_iter(10000000);

?>
