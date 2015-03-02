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
ITERATIONS = 1# 0000

def tex_escape_underscope(s):
    return s.replace("_", "\\_")

def error(data):
    # lower, median, upper
    a, b, c = data.bootstrap_confidence_interval(
        ITERATIONS,
        confidence=CONF_SIZE)

    def avg(seq):
        return math.fsum(seq) / len(seq)

    return avg([b - a, c - b])

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

def make_tables(config, data_file, latex_table_file):

    with open(data_file, "r") as data_fh:
        results = json.load(data_fh)["data"]

    # bench -> vm -> variant -> val * abs_err * warmup
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
                try:
                    exp_data = results[exp_key]
                except KeyError:
                    if should_skip(config, exp_key):
                        continue
                    else:
                        print("Error, missing non-skipped data: %s" % exp_key)
                        sys.exit(1)

                #bench, vm, variant = exp_key.split(":")
                #vm_info = config.VMS[vm]

                warmup = vm_info["warm_upon_iter"]
                variant_info = config.VARIANTS[variant_key]

                data_arg = {}
                total_execs = len(exp_data)
                ok = False
                for exec_n in range(total_execs):
                    exec_nowarmup = exp_data[exec_n][warmup - 1:]
                    if not exec_nowarmup:
                        print("\nMissing data for %s\n" % exp_key)
                        break
                    data_arg[(exec_n, )] = exec_nowarmup
                else:
                    ok = True

                if not ok:
                    continue

                kdata = Data(data_arg, [total_execs, len(data_arg[(0, )])])
                mean = kdata.mean()
                err = error(kdata)

                row_data[bench_key][vm_key][variant_key] = mean, err, warmup

    # need to sort by key to ensure things work out
    row_data = collections.OrderedDict(sorted(row_data.items()))

    #make_ascii_table(row_data)
    make_latex_table(row_data, latex_table_file)

def make_latex_table(row_data, latex_table_file):
    with open(latex_table_file, "w") as of:

        w = of.write

        # header
        w("""\\documentclass{article}
        \\usepackage{booktabs}
        \\usepackage{multicol}
        \\usepackage{multirow}
        \\usepackage{xspace}
        \\usepackage{amsmath}
        \\begin{document}\n""")

        # absolute times
        w("\\begin{tabular}{|r|r||r|r|r|}\n")
        w("\\hline\n")
        w("Benchmark&   VM& Variant&    Time (secs)& Error\\\\\n")

        last_bench_key, last_vm_key = None, None
        for bench_key, bench_data in row_data.iteritems():
            for vm_key, vm_data in bench_data.iteritems():
                for variant_key, variant_data in vm_data.iteritems():
                    val, err, warmup = variant_data

                    if last_bench_key != bench_key:
                        w("\\hline\n")
                        bench_rowspan = len(bench_data)
                        bench_cell = "\\multirow{%d}{*}{%s}" % (bench_rowspan, bench_key)
                        last_bench_key = bench_key
                    else:
                        bench_cell = ""

                    if last_vm_key != vm_key:
                        w("\\cline{2-5}\n")
                        vm_rowspan = len(vm_data)
                        vm_cell = "\\multirow{%d}{*}{%s}" % (vm_rowspan, vm_key)
                        last_vm_key = vm_key
                    else:
                        vm_cell = ""

                    w("%s&  %s& %s& %6f& %6f\\\\\n" % (
                        tex_escape_underscope(bench_cell),
                        tex_escape_underscope(vm_cell),
                        tex_escape_underscope(variant_key), val, err))

        w("\\hline\n")
        w("\\end{tabular}\n")
        w("\\end{document}\n")

def make_ascii_table(row_data):

    tb = prettytable.PrettyTable(["Benchmark", "Warm Iter", "Seconds", "Error"])
    tb.align["Benchmark"] = "l"
    tb.align["WarmIter"] = "r"
    tb.align["Seconds"] = "r"
    tb.align["Error"] = "r"
    tb.float_format = "4.6"

    # Make an ascii table on stdout
    for exp_key, row_data in row_data.iteritems():
        val, err, warmup = row_data
        tb.add_row([exp_key, warmup, val, err])
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
