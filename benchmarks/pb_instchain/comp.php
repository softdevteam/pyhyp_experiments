<?php{
class Terminator {

 
}
compile_py_meth("Terminator", "def is_terminator(self):\n    return True");

class Chain {
  
  

 
 
 
    
 

}
compile_py_meth("Chain", "def __construct(self, value, next):\n    self.value = value\n    self.next = next");
compile_py_meth("Chain", "def is_terminator(self):\n    return False");
compile_py_meth("Chain", "def get_value(self):\n    return self.value");
compile_py_meth("Chain", "def get_next(self):\n    return self.next");

compile_py_func_global("def make_instchain(x):\n    cur = Terminator()\n    while x >= 0:\n        cur = Chain(x, cur)\n        x -= 1\n    return cur");

compile_py_func_global("def consume_instchain(chain):\n    res = 0\n    while not chain.is_terminator():\n        res += chain.get_value()\n        chain = chain.get_next()\n    return res");

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