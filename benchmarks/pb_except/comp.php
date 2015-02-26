<?php{
embed_py_func_global("def g(i):\n    raise RuntimeError(\"Except %s\" % i)");

function f($n) {
    $i = 0;
    while($i < $n) {
        try {
            g($i);
            assert(False);
        } catch(PyException $e) {
            assert($e->getMessage() == "Except $i");
        }
        $i ++;
    }
}

function run_iter($n) {
    f($n);
}
}?>