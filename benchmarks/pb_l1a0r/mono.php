<?php

function countdown($x) {
	while($x > 0) {
		$x -= 1;
	}
}

function outer($outer, $inner) {
	for ($i = 0; $i < $outer; $i++) {
		countdown($inner);
	}
}

function run_iter($n) {
	outer($n, 10000);
}

run_iter(10000);

?>
