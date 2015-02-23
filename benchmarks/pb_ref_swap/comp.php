<?php{

embed_py_func_global("@php_decor(refs=[0, 1])\ndef f_swap(a_ref, b_ref):\n    a, b = a_ref.deref(), b_ref.deref()\n    a_ref.store(b)\n    b_ref.store(a)");

function f_call($n) {
	 $ct = 0;
	 for ($i = 0; $i < $n; $i++) {
		  $x1 = -$i - $n + 3;
		  $x2 = $i + $n;
		  f_swap($x1, $x2);
		  $ct += $x1 + $x2;
	 }
	 // each loop iteration adds 3
	 $expect = $n * 3;
	 assert($ct == $expect);
}

function run_iter($n) {
 	f_call($n);
}
}?>