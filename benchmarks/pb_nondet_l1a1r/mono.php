<?php

// This benchmark is not useful, since hippy doesn't support generators.
// In fact, only new PHP versions support generators.

function gen1($x) {
	while ($x >= 0) {
		yield 1;
		$x -= 1;
	}
}

function outer($outer, $inner) {
	for ($i = 0; $i < $outer; $i++) {
		$gen = gen1();
		foreach ($gen as $res) {
			assert($res == 1);
		}
	}
}

function run_iter($n) {
	outer($n, 10000);
}

run_iter(1000);

?>
