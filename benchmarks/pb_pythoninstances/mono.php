<?php

class Terminator {
	function is_terminator() { return True; }
}

class Chain {
	function __construct($value, $next) {
		$this->value = $value;
		$this->next = $next;
	}

	function is_terminator() { return False; }
	function get_value() { return $this->value; }
	function get_next() { return $this->next; }
}

function make_instchain($x) {
	$cur = new Terminator();
	while($x >= 0) {
		$cur = new Chain($x, $cur);
		$x -= 1;
	}

	return $cur;
}

function consume_instchain($chain) {
	$res = 0;
	while(! ($chain->is_terminator())) {
		$res += $chain->get_value();
		$chain = $chain->get_next();
	}
	return $res;
}

function outer($outer, $inner) {
	$correct = floor($inner * ($inner + 1) / 2);
	for ($i = 0; $i < $outer; $i++) {
		$res = consume_instchain(make_instchain($inner));
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}

run_iter(1000);
?>
