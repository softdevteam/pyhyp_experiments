<?php{
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


$__pyhyp__tree_size = embed_py_func("def __pyhyp__tree_size(i):\n    # Nodes used by a tree of a given size\n    return (1 << (i + 1)) - 1");
function tree_size($i){
    global $__pyhyp__tree_size;
    return $__pyhyp__tree_size( $i);
}


$__pyhyp__num_iters = embed_py_func("def __pyhyp__num_iters(i):\n    # Number of iterations to use for a given tree depth\n    return (2 * tree_size(kStretchTreeDepth) / tree_size(i))");
function num_iters($i){
    global $__pyhyp__num_iters;
    return $__pyhyp__num_iters( $i);
}


$__pyhyp__populate = embed_py_func("def __pyhyp__populate(depth, node):\n    # Build tree top down, assigning to older objects.\n    if depth <= 0:\n        return\n    depth -= 1\n    node.left = Node()\n    node.right = Node()\n    populate(depth, node.left)\n    populate(depth, node.right)");
function populate($depth, $node){
    global $__pyhyp__populate;
    return $__pyhyp__populate( $depth, $node);
}


$__pyhyp__make_tree = embed_py_func("def __pyhyp__make_tree(depth):\n    # build tree bottom-up\n    if depth <= 0:\n        return Node()\n    return Node(make_tree(depth-1), make_tree(depth-1))");
function make_tree($depth){
    global $__pyhyp__make_tree;
    return $__pyhyp__make_tree( $depth);
}


$__pyhyp__time_construction = embed_py_func("def __pyhyp__time_construction(depth, debug=False):\n    niters = num_iters(depth)\n    if debug:\n        print \"Creating %d trees of depth %d\\n\" % niters, depth\n    t_start = microtime(True)\n    for i in xrange(niters):\n        temp_tree = Node()\n        populate(depth, temp_tree)\n    t_finish = microtime(True)\n    if debug:\n        printf(\"\\tTop down construction took %f ms\\n\", ((t_finish - t_start)*1000))\n    t_start = microtime(True)\n    for i in xrange(niters):\n        temp_tree = make_tree(depth)\n    t_finish = microtime(True)\n    if debug:\n        printf(\"\\tBottom down construction took %f ms\\n\", ((t_finish - t_start)*1000))");
function time_construction($depth, $debug=False){
    global $__pyhyp__time_construction;
    return $__pyhyp__time_construction( $depth, $debug);
}

$DEFAULT_DEPTHS = array();
for ($i = kMinTreeDepth; $i < kMaxTreeDepth + 1; $i += 2) {
	$DEFAULT_DEPTHS[] = $i;
}


$__pyhyp__time_constructions = embed_py_func("def __pyhyp__time_constructions(depths, debug):\n    for d in depths.values():\n        time_construction(d, debug)");
function time_constructions($depths, $debug){
    global $__pyhyp__time_constructions;
    return $__pyhyp__time_constructions( $depths, $debug);
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
}?>