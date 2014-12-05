<?php
class Node {
	function __construct($l=NULL, $r=NULL) {
		$this->left = $l;
		$this->right = $r;
	}
}

define('kStretchTreeDepth', 19);
define('kLongLivedTreeDepth', 16);
define('kArraySize', 500001);
define('kMinTreeDepth', 4);
define('kMaxTreeDepth', 16);

function tree_size($i) {
    // Nodes used by a tree of a given size
    return (1 << ($i + 1)) - 1;
}

function num_iters($i) {
    // Number of iterations to use for a given tree depth
    return (2 * tree_size(kStretchTreeDepth) / tree_size($i));
}

function populate($depth, $node) {
    // Build tree top down, assigning to older objects.
    if ($depth <= 0) {
        return;
	}
	$depth--;
	$node->left = new Node();
	$node->right = new Node();
	populate($depth, $node->left);
	populate($depth, $node->right);
}

function make_tree($depth) {
    // Build tree bottom-up
    if ($depth <= 0) {
        return new Node();
	}
	return new Node(make_tree($depth-1), make_tree($depth-1));
}

function time_construction($depth, $debug=False) {
    $niters = num_iters($depth);
    if ($debug) {
        printf("Creating %d trees of depth %d\n", $niters, $depth);
	}
    $t_start = microtime(true);
	for ($i = 0; $i < $niters; $i++) {
		$temp_tree = new Node();
		populate($depth, $temp_tree);
	}
    $t_finish = microtime(true);
	if ($debug) {
        printf("\tTop down constrution took %f ms\n", (($t_finish-$t_start)*1000.0));
	}
    $t_start = microtime(true);
	for ($i = 0; $i < $niters; $i++) {
		$temp_tree = make_tree($depth);
	}
    $t_finish = microtime(true);
    if ($debug) {
        printf("\tBottom up constrution took %f ms\n", (($t_finish-$t_start)*1000.0));
	}
}

$DEFAULT_DEPTHS = array();
for ($i = kMinTreeDepth; $i < kMaxTreeDepth + 1; $i += 2) {
	$DEFAULT_DEPTHS[] = $i;
}

function time_constructions($depths, $debug) {
	foreach ($depths as $d) {
		time_construction($d, $debug);
	}
}

function run_iter($n) {
  for ($r = 0; $r < $n; $r++) {
	   global $DEFAULT_DEPTHS;

   	$temp_tree = make_tree(kStretchTreeDepth);
   	$long_lived_tree = new Node();
   	populate(kLongLivedTreeDepth, $long_lived_tree);

   	$long_lived_array = array(0.0);
   	for ($i = 1; $i < kArraySize; $i++) {
   		$long_lived_array[] = 1/$i;
    }
 
   	time_constructions($DEFAULT_DEPTHS, False);
  }
}
?>