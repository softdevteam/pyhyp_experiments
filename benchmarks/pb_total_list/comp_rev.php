<?php{
function f_rcv($ary) {
    $ct = 0;
    foreach($ary as $i) {
        $ct += $i;
    }
    return $ct;
}

embed_py_func_global("def f_call(n):\n    a = []\n    i = 0\n    while i < 1000:\n        a.append(i)\n        i += 1\n    \n    v = 0\n    i = 0\n    while i < n:\n        v += f_rcv(a)\n        i += 1\n    \n    expect = 499500 * n\n    assert v == expect");

function run_iter($n) {
	f_call($n);
}
}?>