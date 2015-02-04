<?php{


$H1 = 150;

embed_py_func_global("def mandel_py(n):\n    lines = []\n\n    w1 = n\n    h1 = H1\n    recen = -0.45\n    imcen = 0.0\n    r = 0.7\n    s = 0\n    rec = 0\n    imc = 0\n    re = 0\n    im = 0\n    re2 = 0\n    im2 = 0\n    x = 0\n    y = 0\n    w2 = 0\n    h2 = 0\n    color = 0\n    s = 2 * r / w1\n    w2 = 40\n    h2 = 12\n\n    for y in xrange(w1 + 1):\n        line = []\n        imc = s * (y - h2) + imcen\n        for x in xrange(h1 + 1):\n            rec = s * (x - w2) + recen\n            re = rec\n            im = imc\n            color = 1000\n            re2 = re * re\n            im2 = im * im\n            while re2 + im2 < 1000000 and color > 0:\n                im = re * im * 2 + imc\n                re = re2 - im2 + rec\n                re2 = re * re\n                im2 = im * im\n                color = color - 1\n\n            if color == 0:\n                line.append(\"_\")\n            else:\n                line.append(\"#\")\n        lines.append(\"\".join(line))\n    out = \"\\n\".join(lines) + \"\\n\"\n    return out\n");
function run_iter($n){
    global $H1;
    $out = mandel_py($n);
    assert(strlen($out) == ($H1 + 2) * ($n + 1));
}
}?>