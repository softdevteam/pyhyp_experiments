<?php{
define ('IM', 139968);
define ('IA', 3877);
define ('IC', 29573);

$LAST = 42;


$__pyhyp__gen_random = embed_py_func("def __pyhyp__gen_random(n):\n    global LAST\n    LAST = (LAST * IA + IC) % IM\n    return n * float(LAST) / IM");
function gen_random($n){
    global $__pyhyp__gen_random;
    return $__pyhyp__gen_random( $n);
}

/* Weighted selection from alphabet */

$__pyhyp__makeCumulative = embed_py_func("def __pyhyp__makeCumulative(genelist):\n    count = len(genelist)\n    for i in xrange(1, count):\n        genelist[i][1] += genelist[i-1][1]");
function makeCumulative($genelist){
    global $__pyhyp__makeCumulative;
    return $__pyhyp__makeCumulative( $genelist);
}


$__pyhyp__selectRandom = embed_py_func("def __pyhyp__selectRandom(a):\n    r = gen_random(1)\n    hi = len(a)\n    for i in xrange(0, hi):\n        if r < a[i][1]:\n            return a[i][0]\n    return a[hi-1][0]");
function selectRandom($a){
    global $__pyhyp__selectRandom;
    return $__pyhyp__selectRandom( $a);
}

/* Generate and write FASTA format */
define ('LINE_LENGTH', 60);


$__pyhyp__makeRandomFasta = embed_py_func("def __pyhyp__makeRandomFasta(id, desc, genelist, n):\n    for todo in xrange(n, 0, -LINE_LENGTH):\n        pick = \"\";\n        if todo < LINE_LENGTH:\n            m = todo\n        else:\n            m = LINE_LENGTH\n        for i in xrange(0, m):\n            pick += selectRandom(genelist)\n        pick += \"\\n\";\n        import sys; sys.stdout.write(pick)");
function makeRandomFasta($id, $desc, $genelist, $n){
    global $__pyhyp__makeRandomFasta;
    return $__pyhyp__makeRandomFasta( $id, $desc, $genelist, $n);
}


$__pyhyp__makeRepeatFasta = embed_py_func("def __pyhyp__makeRepeatFasta(id, desc, s, n):\n    import sys\n    i = 0\n    sLength = len(s)\n    lineLength = LINE_LENGTH\n    while n > 0:\n        if n < lineLength:\n            lineLength = n;\n        if i + lineLength < sLength:\n            sys.stdout.write(\"%s\\n\" % s[i:i + lineLength])\n            i += lineLength\n        else:\n            sys.stdout.write(s[i:])\n            i = lineLength - (sLength - i)\n            sys.stdout.write(\"%s\\n\" % s[0:i])\n        n -= lineLength");
function makeRepeatFasta($id, $desc, $s, $n){
    global $__pyhyp__makeRepeatFasta;
    return $__pyhyp__makeRepeatFasta( $id, $desc, $s, $n);
}

/* Main -- define alphabets, make 3 fragments */
function fasta($n) {
	$iub = array(
		array('a', 0.27),
		array('c', 0.12),
		array('g', 0.12),
		array('t', 0.27),

		array('B', 0.02),
		array('D', 0.02),
		array('H', 0.02),
		array('K', 0.02),
		array('M', 0.02),
		array('N', 0.02),
		array('R', 0.02),
		array('S', 0.02),
		array('V', 0.02),
		array('W', 0.02),
		array('Y', 0.02)
	);

	$homosapiens = array(
		array('a', 0.3029549426680),
		array('c', 0.1979883004921),
		array('g', 0.1975473066391),
		array('t', 0.3015094502008)
	);

	$alu =
		'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG' .
		'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA' .
		'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT' .
		'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA' .
		'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG' .
		'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC' .
		'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA';

	makeCumulative($iub);
	makeCumulative($homosapiens);
 
 //var_dump($iub);
 //var_dump($homosapiens);
 //exit(1);

	makeRepeatFasta('ONE', 'Homo sapiens alu', $alu, $n*2);
	makeRandomFasta('TWO', 'IUB ambiguity codes', $iub, $n*3);
	makeRandomFasta('THREE', 'Homo sapiens frequency', $homosapiens, $n*5);
}

function run_iter($n) {
	       fasta($n);
}

run_iter(1000);


}?>