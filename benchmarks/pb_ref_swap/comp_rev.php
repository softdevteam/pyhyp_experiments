<?php{

function f_swap(&$a, &$b) {
  $tmp = $a;
 	$a = $b;
 	$b = $tmp;
}

compile_py_func_global("def f_call(n):\n    ct = 0\n    i = 0\n    while i < n:\n        x1 = -i - n + 3\n        x2 = i + n\n        \n        x1_ref = PHPRef(x1)\n        x2_ref = PHPRef(x2)\n        f_swap(x1_ref, x2_ref)\n        x1 = x1_ref.deref()\n        x2 = x2_ref.deref()\n        \n        ct += x1 + x2\n        i += 1\n\n    # each loop iteration adds 3\n    expect = n * 3\n    assert ct == expect");

function run_iter($n) {
	f_call($n);
}
}?>