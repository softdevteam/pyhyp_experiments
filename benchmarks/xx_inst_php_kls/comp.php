<?php

class A {
	function ret666() { return 666; }
}

$src = <<<EOD
def do():
	return A();
EOD;
$do = embed_py_func($src);

function run_iter($n) {
	global $do;

	for ($i = 0; $i < $n; $i++) {
		$r = $do();
		assert($r->ret666() == 666);
	}
}

run_iter(80000000);

?>
