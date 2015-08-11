"""Generate different versions of the deltablue benchmark
Each version is a different mix of PHP and Python

NOTE, the mono PHP benchmark needs to be annotated with markers to
help this rudimentary script find the methods.

(If this were to be production code, you obviously wouldn't use
regex to parse source code.)
"""

import re
from collections import OrderedDict
import sys
import os

def dot():
    sys.stdout.write(".")
    sys.stdout.flush()

PHP_FUNC_REGEX = r"// STARTFUNC(.*?function\s(.*?)\(.*?)// ENDFUNC"
def index_php_funcs(fh):
    php_src = fh.read()
    ct = 0

    # Assume functions appear in the same order as in the python file
    php_funcs = []
    print("Finding PHP functions ")
    while True:
        match = re.search(PHP_FUNC_REGEX, php_src, re.DOTALL)
        if not match:
            break
        func_src, func_name = match.groups()
        php_funcs.append((func_name, func_src))

        # remove from the source
        php_src = re.sub(PHP_FUNC_REGEX, "// INSERTFUNC %03d\n" % ct, php_src, 1, re.DOTALL)
        ct += 1

    # add pyhyp delay parns
    php_src = php_src.replace("<?php", "<?php\n{\n")
    php_src = php_src.replace("?>", "}\n?>")

    return php_src, php_funcs

PY_FUNC_REGEX = r".*(compile_py_(meth)\(\".*?\", \".*?def (.*?)\(.*|compile_py_(func_global)\(\"def (.*?)\(.*)"
def index_py_funcs(fh):
    py_src = fh.read()

    # Assume functions appear in the same order as in the python file
    py_funcs = []
    print("Finding Python functions ")
    for match in re.finditer(PY_FUNC_REGEX, py_src):
        src, meth_typ, meth_name, global_typ, global_name = match.groups()

        typ = meth_typ if meth_typ is not None else global_typ
        name = meth_name if meth_name is not None else global_name

        py_funcs.append((name, typ, src))
        print(name)

    return py_funcs

def insert_py_func(src, func_idx, py_src):
    # find the nearest ENDCLASS XX marker and put a python method there

    # first find the INSERTFUNC marker
    idx = src.find("// INSERTFUNC %03d" % func_idx)
    remain_src = src[idx:]

    # find the next ENDCLASS marker
    match = re.search(r"(// ENDCLASS [0-9][0-9])", remain_src, re.DOTALL)
    assert match

    repl_marker = match.groups()[0]

    new_src = re.sub(repl_marker, "%s\n%s" % (repl_marker, py_src), src)
    return new_src

def mk_permutations(skeleton, php_funcs, py_funcs):
    assert len(php_funcs) == len(py_funcs)

    for permfile_idx in xrange(len(php_funcs)):
        src = skeleton[:]

        for func_idx in xrange(len(php_funcs)):
            if func_idx != permfile_idx:
                func_src = php_funcs[func_idx][1] # source of the php function
                new_src = re.sub(r"// INSERTFUNC %03d\n" % func_idx, func_src, src, 1, re.DOTALL)
            else:
                py_name, py_typ, py_src = py_funcs[func_idx]
                if py_typ == "func_global":
                    new_src = re.sub(r"// INSERTFUNC %03d\n" % func_idx, py_src, src, 1, re.DOTALL)
                else:
                    assert py_typ == "meth"
                    new_src = insert_py_func(src, func_idx, py_src)

            assert new_src != src
            src = new_src

        fn = os.path.join(OUT_DIR, "permutation_%03d.php" % permfile_idx)
        with open(fn, "w") as fh:
            fh.write(src)

BENCH_DIR = os.path.join(os.getcwd())
MONO_PHP = os.path.join(BENCH_DIR, "mono.php")
COMP_PHP = os.path.join(BENCH_DIR, "comp.php")
OUT_DIR = os.getcwd()

def main():
    with open(MONO_PHP, "r") as fh:
        skeleton, php_funcs = index_php_funcs(fh)

    with open(COMP_PHP, "r") as fh:
        py_funcs = index_py_funcs(fh)

    print "php funcs: %d" % len(php_funcs)
    print "py funcs: %d" % len(py_funcs)

    for i in range(len(py_funcs)):
        n, m = php_funcs[i], py_funcs[i]
        if n[0] != m[0]:
            print("error at index %d: %s vs %s" % (i, n[0], m[0]))
            sys.exit(1)

    mk_permutations(skeleton, php_funcs, py_funcs)

if __name__ == "__main__":
    main()
