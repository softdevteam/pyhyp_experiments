<?php{
function f_outer($n) {
	$inc = 2;

 $inner = embed_py_func("def inner(x):\n    inner2 = embed_php_func(\"\"\"\nfunction inner2(\$x) {\n        return \$x + \$inc;\n    }\n\"\"\")\n    return inner2(x)");;

	$tot = 0;
	for ($i = 0; $i < $n; $i++) {
		$tot = $inner($tot);
	}

	$expect = 2 * $n;
	assert($tot == $expect);

}

function run_iter($n) {
	f_outer($n);
}
}?>