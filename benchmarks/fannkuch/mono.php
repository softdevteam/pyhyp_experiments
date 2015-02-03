<?php
{

// used to check that different variants execute the same program statements.
function dbg_print_php() {
	return;

	$ar = func_get_args();
	$len = func_num_args();

	echo "{$ar[0]}: ";
	for($i = 1; $i < $len; $i++) {
		echo "{$ar[$i]} ";
	}
	echo "\n";
}

function Fannkuch_run($n){
	$check = 0;
	$perm = array();
	$perm1 = array();
	$count = array();
	$maxPerm = array();
	$maxFlipsCount = 0;
	$m = $n - 1;

	for ($i=0; $i<$n; $i++) $perm1[$i] = $i;
	$r = $n;
	while (TRUE) {
		dbg_print_php("Outer loop");
		while ($r != 1) {
			dbg_print_php("Inner loop 1", $r);
			$count[$r-1] = $r; $r--;
		}
		if (! ($perm1[0]==0 || $perm1[$m] == $m)){
			dbg_print_php("Inner cond 1", $perm1[0], $perm1[$m], $m);
			for($i=0; $i<$n; $i++) {
				dbg_print_php("Inner loop 2", $i, $n);
				$perm[$i] = $perm1[$i];
			}
			$flipsCount = 0;

			while ( !(($k=$perm[0]) == 0) ) {
				dbg_print_php("Inner loop 3", $k, $perm[0]);
				$k2 = ($k+1) >> 1;
				for($i=0; $i<$k2; $i++) {
					dbg_print_php("Inner loop 4", $i, $k2);
					$temp = $perm[$i];
					$perm[$i] = $perm[$k-$i];
					$perm[$k-$i] = $temp;
				}
				$flipsCount++;
			}

			if ($flipsCount > $maxFlipsCount) {
				dbg_print_php("Inner cond 2",
					$flipsCount, $maxFlipsCount);
				$maxFlipsCount = $flipsCount;
				for($i=0; $i<$n; $i++) {
					dbg_print_php("Inner loop 5", $i, $n);
					$maxPerm[$i] = $perm1[$i];
				}
			}
		}

		while (TRUE) {
			dbg_print_php("Inner loop 6");
			if ($r == $n) {
				dbg_print_php("Inner cond 3", $r, $n);
				return $maxFlipsCount;
			}
			$perm0 = $perm1[0];
			$i = 0;
			while ($i < $r) {
				dbg_print_php("Inner loop 7", $i, $r);
				$j = $i + 1;
				$perm1[$i] = $perm1[$j];
				$i = $j;
			}
			$perm1[$r] = $perm0;

			$count[$r] = $count[$r] - 1;
			if ($count[$r] > 0) {
				dbg_print_php("Inner cond 4", $r);
				break;
			}
			$r++;
		}
	}
}

function run_iter($n) {
	$res = Fannkuch_run($n);
	dbg_print_php("run_iter", $res);

}

}
?>
