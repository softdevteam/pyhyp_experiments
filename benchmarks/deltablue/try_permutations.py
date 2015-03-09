#
# dirty hack to try and isolate weirdness in deltablue composed.
#

import re
from collections import OrderedDict
import sys

def dot():
    sys.stdout.write(".")
    sys.stdout.flush()

PHP_FUNC_REGEX = r"// STARTFUNC.*?(function\s(.*?)\(.*?)// ENDFUNC"
def index_php_funcs(fh):
    php_src = fh.read()

    # Assume functions appear in the same order as in the python file
    php_funcs = OrderedDict()
    print("Finding PHP functions ")
    while True:
        match = re.search(PHP_FUNC_REGEX, php_src, re.DOTALL)
        if not match:
            break
        func_src, func_name = match.groups()
        php_funcs[func_name] = func_src

        # remove from the source
        php_src = re.sub(PHP_FUNC_REGEX, "\n", php_src, 1, re.DOTALL)

    return php_src, php_funcs

#PY_FUNC_REGEX = r".*(embed_py_(meth)\(\".*?\", \"def (.*?))\(.*"
PY_FUNC_REGEX = r".*(embed_py_(meth)\(\".*?\", \"def (.*?)\(.*|embed_py_(func_global)\(\"def (.*?)\(.*)"
def index_py_funcs(fh):
    py_src = fh.read()

    # Assume functions appear in the same order as in the python file
    py_funcs = OrderedDict()
    print("Finding Python functions ")
    for match in re.finditer(PY_FUNC_REGEX, py_src):
        src, meth_typ, meth_name, global_typ, global_name = match.groups()

        typ = meth_typ if meth_typ is not None else global_typ
        name = meth_name if meth_name is not None else global_name

        py_funcs[name] = (typ, src)
        print(name)

    return py_funcs

def main():
    with open("mono.php", "r") as fh:
        skeleton, php_funcs = index_php_funcs(fh)

    with open("comp.php", "r") as fh:
        py_funcs = index_py_funcs(fh)

    s1, s2 = set(php_funcs), set(py_funcs)

    print s1 - s2

if __name__ == "__main__":
    main()
