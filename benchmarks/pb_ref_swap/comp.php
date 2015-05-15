<?php{

compile_py_func_global("@php_decor(refs=[0, 1])\ndef f_swap(a_ref, b_ref):\n    tmp = a_ref.deref()\n    a_ref.store(b_ref.deref())\n    b_ref.store(tmp)");

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