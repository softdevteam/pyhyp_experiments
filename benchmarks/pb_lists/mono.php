<?php

function make_list($x) {
	$res = array();
	while ($x >= 0) {
		$res[] = $x;
		$x -= 1;
	}
	return $res;
}

function consume_list($l) {
	$res = 0;
	foreach($l as $i) {
		$res += $i;
	}

	return $res;
}

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


?>
