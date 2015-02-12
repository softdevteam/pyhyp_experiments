<?php{
// Same as pb_sum_meth, just using a attribute

class Sum {
	public $res = 0;


}
embed_py_meth("Sum", "def f_rcv(self, a1, a2, a3, a4, a5):\n    self.res = a1 + a2 + a3 + a4 + a5");

function f_call($n) {
	  $s = new Sum();

   $x = 31415;
   $expect = $x * 5 + 15;
	  for ($i = 0; $i < $n; $i++) {
		     $s->f_rcv($x + 1, $x + 2, $x + 3, $x + 4, $x + 5);
       assert($s->res == $expect);
	  }
}

function run_iter($n) {
	f_call($n);
}
}?>