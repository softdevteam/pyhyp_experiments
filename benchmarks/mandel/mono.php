<?php
{

function inner_loop(&$re2, &$im2, &$color, &$re, &$im, $imc, $rec) {
      while( ((($re2+$im2)<1000000) && $color>0)) {
        $im=$re*$im*2+$imc;
        $re=$re2-$im2+$rec;
        $re2=$re*$re;
        $im2=$im*$im;
        $color=$color-1;
      }
}

# $n is the number of lines
function mandelPHP($n) {
  $H1 = 150; // keep in sync with H1 below

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
    $H1 = 150; // keep in sync with H1 above
    $out = mandelPHP($n);
    assert(strlen($out) == ($H1 + 2) * ($n + 1));
}

}
?>
