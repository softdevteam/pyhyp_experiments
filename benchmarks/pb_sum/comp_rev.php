<?php{
function f_rcv($a1, $a2, $a3, $a4, $a5) {
    return $a1 + $a2 + $a3 + $a4 + $a5;
}

compile_py_func_global("def f_call(n):\n    x = 31415\n    expect = x * 5 + 15\n    i = 0\n    while i < n:\n        rs = f_rcv(x+1, x+2, x+3, x+4, x+5)\n        assert rs == expect\n        i += 1");

function run_iter($n) {
	f_call($n);
}
}?>