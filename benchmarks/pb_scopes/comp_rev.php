<?php{
embed_py_func_global("def f_outer(n):\n    inc = 2\n    \n    inner = embed_php_func(\"\"\"\nfunction inner(\$x) { return \$x + \$inc; }\n\"\"\")\n    \n    tot = 0\n    i = 0\n    while i < n:\n        tot = inner(tot)\n        i += 1\n    \n    expect = 2 * n\n    assert tot == expect");

function run_iter($n) {
	f_outer($n);
}

run_iter(100);
}?>