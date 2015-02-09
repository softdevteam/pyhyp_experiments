<?php{

embed_py_func_global("def make_chain(x):\n    curr = \"end\"\n    while x >= 0:\n        curr = [x, 2 * x, curr]\n        x -= 1\n    return curr");


embed_py_func_global("def consume_chain(chain):\n    chain = chain.as_list()\n    res = 0\n    while chain != \"end\":\n        val1, val2, chain = chain\n        res += val2 - val1\n    return res");

function outer($outer, $inner) {
	$correct = floor($inner * ($inner + 1) / 2);

	for ($i = 0; $i < $outer; $i++) {
		$res = consume_chain(make_chain($inner));
		assert($res == $correct);
	}
}

function run_iter($n) {
	outer($n, 10000);
}
}?>