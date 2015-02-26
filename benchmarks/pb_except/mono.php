<?php

function g($i) {
    throw new RuntimeException("Except $i");
}

function f($n) {
    $i = 0;
    while($i < $n) {
        try {
            g($i);
            assert(False);
        } catch(RuntimeException $e) {
            assert($e->getMessage() == "Except $i");
        }
        $i ++;
    }
}

function run_iter($n) {
    f($n);
}

?>
