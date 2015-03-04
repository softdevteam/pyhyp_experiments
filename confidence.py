#! work/virtualenv/pypy/bin/pypy
# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math
import prettytable
import os
import collections

from pykalibera.data import Data
from util import should_skip

CONF_SIZE = "0.99"  # intentionally str
ITERATIONS = 10000

def tex_escape_underscope(s):
    return s.replace("_", "\\_")

def avg(seq):
    return math.fsum(seq) / len(seq)

def error(data):
    # lower, median, upper
    a, b, c = data.bootstrap_confidence_interval(
        ITERATIONS,
        confidence=CONF_SIZE)

    return avg([b - a, c - b])

def rel(data, other):
    a, b, c = data.bootstrap_quotient(
        other, iterations=ITERATIONS, confidence=CONF_SIZE)
    self_avg = data.mean()
    other_avg = other.mean()

    if other_avg == 0:
        ratio = float("inf")
    else:
        ratio = self_avg / other_avg

    return ratio, avg([b - a, c - b])

def get_rowspan(row_data, bench, vm=None):
    ct = 0
    for key in row_data.keys():
        t_bench, t_vm, t_variant = key.split(":")

        if bench != t_bench:
            continue

        if vm is not None and vm != t_vm:
            continue

        ct += 1
    return ct

def make_kalibera_data(exp_data, warmup):
    data_arg = {}
    total_execs = len(exp_data)
    ok = False
    for exec_n in range(total_execs):
        exec_nowarmup = exp_data[exec_n][warmup - 1:]
        if not exec_nowarmup:
            return None
        data_arg[(exec_n, )] = exec_nowarmup

    return Data(data_arg, [total_execs, len(data_arg[(0, )])])

def make_tables(config, data_file, latex_table_file):

    with open(data_file, "r") as data_fh:
        results = json.load(data_fh)["data"]

    # convert to this tree-like dict, makes formatting tables easier
    # bench -> vm -> variant ->
    #    val * abs_err * rel_pypy * rel_pypy_err * rel_hip * rel_hip_err * warmup
    row_data = {}

    for bench_key, bench_param in config.BENCHMARKS.iteritems():
        if not row_data.has_key(bench_key):
            row_data[bench_key] = {}
        bench_data = row_data[bench_key]

        for vm_key, vm_info in config.VMS.iteritems():

            if not bench_data.has_key(vm_key):
                bench_data[vm_key] = {}
            variant_data = bench_data[vm_key]

            for variant_key in vm_info["variants"]:
                exp_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)

                sys.stdout.write(".")
                sys.stdout.flush()

                try:
                    exp_data = results[exp_key]
                except KeyError:
                    if should_skip(config, exp_key):
                        # XXX tidy up, make a "add dummy result" function
                        mean = None
                        err = None
                        rel_pypy = None
                        rel_pypy_err = None
                        rel_hippy = None
                        rel_hippy_err = None
                        row_data[bench_key][vm_key][variant_key] = \
                            mean, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup
                        continue
                    else:
                        print("Error, missing non-skipped data: %s" % exp_key)
                        sys.exit(1)

                warmup = vm_info["warm_upon_iter"]
                variant_info = config.VARIANTS[variant_key]

                kdata = make_kalibera_data(exp_data, warmup)
                if kdata is None: # not enough data or no data
                    print("missing data for %s" % exp_key)
                    mean = None
                    err = None
                    rel_pypy = None
                    rel_pypy_err = None
                    rel_hippy = None
                    rel_hippy_err = None

                    row_data[bench_key][vm_key][variant_key] = \
                        mean, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup
                    continue
                else:
                    mean = kdata.mean()
                    err = error(kdata)

                    # relative to pypy
                    pypy_key = "%s:PyPy:mono-python" % bench_key
                    has_pypy = True
                    try:
                        pypy_data = results[pypy_key]
                    except KeyError:
                        has_pypy = False

                    if has_pypy:
                        pypy_warmup = config.VMS["PyPy"]["warm_upon_iter"]
                        pypy_kdata = make_kalibera_data(pypy_data, pypy_warmup)
                        rel_pypy, rel_pypy_err = rel(kdata, pypy_kdata)
                    else:
                        rel_pypy, rel_pypy_err = None, None

                    # relative to hippyvm
                    hippy_key = "%s:HippyVM:mono-php" % bench_key
                    has_hippy = True
                    try:
                        hippy_data = results[hippy_key]
                    except KeyError:
                        has_hippy = False
                    if has_hippy:
                        hippy_warmup = config.VMS["HippyVM"]["warm_upon_iter"]
                        hippy_kdata = make_kalibera_data(hippy_data, hippy_warmup)
                        rel_hippy, rel_hippy_err = rel(kdata, hippy_kdata)
                    else:
                        rel_hippy, rel_hippy_err = None, None

                    row_data[bench_key][vm_key][variant_key] = \
                        mean, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup

    make_ascii_table(row_data)
    make_latex_table(row_data, latex_table_file)

def make_latex_table(row_data, latex_table_file):
    with open(latex_table_file, "w") as of:

        w = of.write

        # header
        w("""\\documentclass{article}
        \\usepackage{longtable}
        \\usepackage{booktabs}
        \\usepackage{multicol}
        \\usepackage{multirow}
        \\usepackage{xspace}
        \\usepackage{amsmath}
        \\begin{document}\small\n""")

        # absolute times
        w("\\begin{longtable}{cccrl}\n")
        w("\\toprule\n")
        w("Benchmark&   VM& Variant&    \multicolumn{2}{c}{Time (secs)}\\\\\n")

        last_bench_key, last_vm_key = None, None
        for bench_key, bench_data in row_data.iteritems():
            for vm_key, vm_data in bench_data.iteritems():

                for variant_key, variant_data in vm_data.iteritems():
                    val, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup = variant_data

                    vm_cline = True
                    if last_bench_key != bench_key:
                        w("\\midrule\n")
                        vm_cline = False
                        bench_rowspan = len(bench_data)
                        bench_cell = "\\multirow{%d}{*}{%s}" % (bench_rowspan, bench_key)
                        last_bench_key = bench_key
                    else:
                        bench_cell = ""

                    if last_vm_key != vm_key:
                        if vm_cline:
                            w("\\cline{2-5}\n")

                        vm_rowspan = len(vm_data)
                        vm_cell = "\\multirow{%d}{*}{%s}" % (vm_rowspan, vm_key)
                        last_vm_key = vm_key
                    else:
                        vm_cell = ""

                    if val is None: # no result for that combo
                        val_s = "n/a"
                        err_s = "n/a"
                    else:
                        val_s = "%.4f" % val
                        err_s = "%.4f" % err

                    w("%s&  %s& %s& %s& {\scriptsize$\\pm$ %s}\\\\\n" % (
                        tex_escape_underscope(bench_cell),
                        tex_escape_underscope(vm_cell),
                        tex_escape_underscope(variant_key), val_s, err_s))

        w("\\bottomrule\n")
        w("\\end{longtable}\n")
        w("\\newpage\n")


        # relative times
        w("\\begin{longtable}{cccrlrl}\n")
        w("\\toprule\n")
        w("Benchmark&   VM& Variant&    \multicolumn{2}{c}{$\\times$PyPy}&\multicolumn{2}{c}{$\\times$HippyVM}\\\\\n")

        last_bench_key, last_vm_key = None, None
        for bench_key, bench_data in row_data.iteritems():
            for vm_key, vm_data in bench_data.iteritems():
                for variant_key, variant_data in vm_data.iteritems():
                    val, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup = variant_data

                    vm_cline = True
                    if last_bench_key != bench_key:
                        w("\\midrule\n")
                        vm_cline = False
                        bench_rowspan = len(bench_data)
                        bench_cell = "\\multirow{%d}{*}{%s}" % (bench_rowspan, bench_key)
                        last_bench_key = bench_key
                    else:
                        bench_cell = ""

                    if last_vm_key != vm_key:
                        if vm_cline:
                            w("\\cline{2-7}\n")

                        vm_rowspan = len(vm_data)
                        vm_cell = "\\multirow{%d}{*}{%s}" % (vm_rowspan, vm_key)
                        last_vm_key = vm_key
                    else:
                        vm_cell = ""

                    if rel_pypy is not None:
                        rel_pypy_str = "%.4f" % rel_pypy
                        rel_pypy_err_str = "%.4f" % rel_pypy_err
                    else:
                        rel_pypy_str, rel_pypy_err_str = "n/a", "n/a"

                    if rel_hippy is not None:
                        rel_hippy_str = "%.4f" % rel_hippy
                        rel_hippy_err_str = "%.4f" % rel_hippy_err
                    else:
                        rel_hippy_str, rel_hippy_err_str = "n/a", "n/a"

                    w(("%s&  %s& %s&" + \
                      "%s&{\scriptsize$\\pm$ %s}&" + \
                      "%s&{\scriptsize$\\pm$ %s}\\\\\n") % (
                        tex_escape_underscope(bench_cell),
                        tex_escape_underscope(vm_cell),
                        tex_escape_underscope(variant_key), rel_pypy_str,
                        rel_pypy_err_str, rel_hippy_str, rel_hippy_err_str))

        w("\\bottomrule\n")
        w("\\end{longtable}\n")



        w("\\end{document}\n")

def make_ascii_table(row_data):

    tb = prettytable.PrettyTable(["Benchmark", "VM", "Variant", "Seconds", "Error"])
    tb.align["Benchmark"] = "l"
    tb.align["WarmIter"] = "r"
    tb.align["Seconds"] = "r"
    tb.align["Error"] = "r"
    tb.float_format = "4.6"

    # Make an ascii table on stdout
    for bench_key, bench_data in row_data.iteritems():
        for vm_key, vm_data in bench_data.iteritems():
            for variant_key, variant_data in vm_data.iteritems():
                val, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup = variant_data
                tb.add_row([bench_key, "%s (warm_upon=%d)" % (vm_key, warmup),
                            variant_key, val, err])
                sys.stdout.write(".")
                sys.stdout.flush()

    sys.stdout.write("\n")
    print(tb.get_string(sortby="Benchmark"))


if __name__ == "__main__":
    config_file = sys.argv[1]

    import_name = config_file[:-3]
    data_file = import_name + "_results.json"
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    ltx_dir = "tex"
    try:
        os.mkdir(ltx_dir)
    except OSError as e:
        pass # file exists

    latex_table_file = os.path.join(ltx_dir, import_name + "_results.tex")

    make_tables(config, data_file, latex_table_file)
