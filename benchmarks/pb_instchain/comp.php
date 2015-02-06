<?php{
class Terminator {

 
}
embed_py_meth("Terminator", "def is_terminator(self):\n    return True");

class Chain {
  
  

 
 
 
    
 

}
embed_py_meth("Chain", "def get_next(self):\n    return self.next");
embed_py_meth("Chain", "def get_value(self):\n    return self.value");
embed_py_meth("Chain", "def is_terminator(self):\n    return False");
embed_py_meth("Chain", "def __construct(self, value, next):\n    self.value = value\n    self.next = next");


$__pyhyp__make_instchain = embed_py_func("def __pyhyp__make_instchain(x):\n    cur = Terminator()\n    while x >= 0:\n        cur = Chain(x, cur)\n        x -= 1\n    return cur");
function make_instchain($x){
    global $__pyhyp__make_instchain;
    return $__pyhyp__make_instchain( $x);
}


$__pyhyp__consume_instchain = embed_py_func("def __pyhyp__consume_instchain(chain):\n    res = 0\n    while not chain.is_terminator():\n        res += chain.get_value()\n        chain = chain.get_next()\n    return res");
function consume_instchain($chain){
    global $__pyhyp__consume_instchain;
    return $__pyhyp__consume_instchain( $chain);
}

function outer($outer, $inner) {
	$correct = floor($inner * ($inner + 1) / 2);
	for ($i = 0; $i < $outer; $i++) {
		$res = consume_instchain(make_instchain($inner));
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>