<?php

// compile this once
$pysrc = <<<EOD
def g():
    php_src = "function h() { return 666; }"
    h = embed_php_func(php_src)
    return h()
EOD;

function run_iter($n) {

	global $pysrc;
	embed_py_func_global($pysrc);

	for ($i = 0; $i < $n; $i++) {
		$r = g();
		assert($r == 666);
	}
}

?>
