<?php

$src = <<<EOD
def f(a=1, b=2, c=3, d=4):
    return "%s%s%s%s" % (a, b, c, d)
EOD;
embed_py_func_global($src);

function run_iter($n) {

	$posargs = array("za");
	$kwargs = array("d" => "xd", "c" => "xc");

	for ($i = 0; $i < $n; $i++) {
		$res = call_py_func("f", $posargs, $kwargs);
		assert($res == "za2xcxd");
	}
}

run_iter(10000000);


?>
