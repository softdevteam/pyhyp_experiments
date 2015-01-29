<?php

function sum_up_to_n($n) {
	$result = 0;
	while($n > 0) {
		$result += $n;
		$n -= 1;
	}
	return $result;
}

function outer($outer, $inner) {
	$correct = sum_up_to_n($inner);
	for ($i = 0; $i < $outer; $i++) {
		$res = sum_up_to_n($inner);
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}

run_iter(10000);

?>
