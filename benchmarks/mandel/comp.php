<?php{

$__pyhyp__mandel = embed_py_func("def __pyhyp__mandel():\n    import sys\n    w1 = 50\n    h1=150\n    recen = -0.45\n    imcen = 0.0\n    r = 0.7\n    s = 0; rec = 0; imc = 0; re = 0; im = 0; re2 = 0; im2 = 0\n    x = 0; y = 0; w2 = 0; h2 = 0; color=0\n    s = 2*r/w1\n    w2 = 40\n    h2 = 12\n    for y in xrange(0, w1+1):\n        imc = s * (y-h2) + recen\n        for x in xrange(0, h1+1):\n            rec = s * (x-w2) + recen\n            re = rec\n            im = imc\n            color = 1000\n            re2 = re * re\n            im2 = im * im\n            while ((re2 + im2) < 1000000) and color > 0:\n                im = re * im*2 + imc\n                re = re2 - im2 + rec\n                re2 = re * re\n                im2 = im * im\n                color = color - 1\n            if color == 0:\n                sys.stdout.write(\"_\")\n            else:\n                sys.stdout.write(\"#\")\n        sys.stdout.write(\"\\n\")");
function mandel(){
    global $__pyhyp__mandel;
    return $__pyhyp__mandel();
}

function run_iter($n){
    mandel();
}
}?>