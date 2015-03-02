# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math
import prettytable
import os

from pykalibera.data import Data

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

def make_tables(config, data_file, latex_table_file):

    with open(data_file, "r") as data_fh:
        results = json.load(data_fh)["data"]

    # key -> val * abs_err * warmup
    row_data = {}
    for exp_key in results.iterkeys():
        exp_data = results[exp_key]

        bench, vm, variant = exp_key.split(":")
        vm_info = config.VMS[vm]

        warmup = vm_info["warm_upon_iter"]

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

        row_data[exp_key] = mean, err, warmup

    make_ascii_table(row_data)
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
        w("\\begin{tabular}{|r|r|r|}\n")
        w("\\hline\n")
        w("Key&Time (secs)& Error\\\\\n")
        w("\\hline\n")
        for exp_key, row_data in row_data.iteritems():
            val, err, warmup = row_data
            w("%s&  %6f& %6f\\\\\n" % (tex_escape_underscope(exp_key), val, err))

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
