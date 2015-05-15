<?php{
function f_ret() {
    return 1;
}

compile_py_func_global("def f_call(n):\n    ct = 0\n    i = 0\n    while i < n:\n        ct += f_ret()\n        i += 1\n    assert ct == n");

function run_iter($n) {
	f_call($n);
}
}?>