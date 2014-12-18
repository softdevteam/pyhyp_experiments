<?php{
define ('IM', 139968);
define ('IA', 3877);
define ('IC', 29573);
$LAST = 42.0;

function gen_random($n) {
  global $LAST;
  return( ($n * ($LAST = ($LAST * IA + IC) % IM)) / IM );
}


$__pyhyp__heapsort_r = embed_py_func("def __pyhyp__heapsort_r(n, ra):\n    l = (n >> 1) + 1\n    ir = n\n    \n    while True:\n\n        if l > 1:\n            l -= 1\n            rra = ra[l]\n        else:\n            rra = ra[ir]\n            ra[ir] = ra[1]\n            ir -= 1\n            if ir == 1:\n                ra[1] = rra\n                return\n        i = l\n        j = l << 1\n        while j <= ir:\n            if j < ir and ra[j] < ra[j+1]:\n                j += 1\n            if rra < ra[j]:\n                ra[i] = ra[j]\n                i = j\n                j += i\n            else:\n                j = ir + 1\n        ra[i] = rra");
function heapsort_r($n, $ra){
    global $__pyhyp__heapsort_r;
    return $__pyhyp__heapsort_r( $n, $ra);
}

function heapsort($N = 20000) {
  global $LAST;

  $ary = array(0);
  for ($i=1; $i<=$N; $i++) {
    $ary[$i] = gen_random(1.0);
  }
  heapsort_r($N, $ary);
  echo $ary[$N];
  //printf("%.10f\n", $ary[$N]);
}

function run_iter($n):
    heapsort($n);
}
}?>
