<?php

function make_chain($x) {
	$curr = "end";
	while($x >= 0) {
		$curr = array($x, 2 * $x, $curr);
		$x -= 1;
	}

	return $curr;
}

function consume_chain($chain) {
	$res = 0;
	while($chain != "end") {
		list($val1, $val2, $chain) = $chain;
		$res += $val2 - $val1;
	}

	return $res;
}

function outer($outer, $inner) {
	$correct = $inner * ($inner + 1) / 2;

	for ($i = 0; $i < $outer; $i++) {
		$res = consume_chain(make_chain($inner));
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}

?>
