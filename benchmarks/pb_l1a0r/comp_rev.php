<?php{
function coutdown($x) {
    while($x > 0) {
        $x--;
    }
}

embed_py_func_global("def outer(outer, inner):\n    i = 0\n    while i < outer:\n        countdown(inner)\n        i += 1");

function run_iter($n) {
	outer($n, 10000);
}

run_iter(100);
}?>