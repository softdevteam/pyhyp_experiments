<?php{

embed_py_func_global("@php_decor(refs=(0, 1, 2, 3, 4, 5, 6))\ndef inner_loop(re2_r, im2_r, color_r, re_r, im_r, imc_r, rec_r):\n    re2, im2, color, re, im, imc, rec = \\\n        re2_r.deref(), im2_r.deref(), color_r.deref(), re_r.deref(), im_r.deref(), imc_r.deref(), rec_r.deref()\n    while ((re2 + im2) < 1000000) and color > 0:\n        im = re * im  * 2 + imc;\n        re = re2 - im2 + rec\n        re2 = re * re\n        im2 = im * im\n        color = color - 1\n    re2_r.store(re)\n    im2_r.store(im2)\n    color_r.store(color)\n    re_r.store(re)\n    im_r.store(im)\n    imc_r.store(imc)\n    rec_r.store(rec)");

$H1 = 150;

function mandelPHP($n) {
  global $H1;

  $lines = array();

  $w1=$n;
  $h1=$H1;
  $recen=-0.45;
  $imcen=0.0;
  $r=0.7;
  $s=0;  $rec=0;  $imc=0;  $re=0;  $im=0;  $re2=0;  $im2=0;
  $x=0;  $y=0;  $w2=0;  $h2=0;  $color=0;
  $s=2*$r/$w1;
  $w2=40;
  $h2=12;
  for ($y=0 ; $y<=$w1; $y=$y+1) {
    $line = array();
    $imc=$s*($y-$h2)+$imcen;
    for ($x=0 ; $x<=$h1; $x=$x+1) {
      $rec=$s*($x-$w2)+$recen;
      $re=$rec;
      $im=$imc;
      $color=1000;
      $re2=$re*$re;
      $im2=$im*$im;

      inner_loop($re2, $im2, $color, $re, $im, $imc, $rec);

      if ( $color==0 ) {
        $line[] = "_";
      } else {
        $line[] = "#";
      }
    }
    $lines[] = join("", $line);
  }
  $out = join("\n", $lines) . "\n";
  return $out;
}

function run_iter($n){
    global $H1;
    $out = mandelPHP($n);
    echo $out;
    assert(strlen($out) == ($H1 + 2) * ($n + 1));
}
}?>