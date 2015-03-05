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

try:
    debug = os.environ["TABLE_DEBUG"]
    ITERATIONS = 1
except KeyError:
    ITERATIONS = 10000

def dot():
    sys.stdout.write(".")
    sys.stdout.flush()

def tex_escape_underscore(s):
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

class ResultInfo(object):
    def __init__(self, val, val_err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup):
        self.val, self.val_err = val, val_err
        self.rel_pypy, self.rel_pypy_err = rel_pypy, rel_pypy_err
        self.rel_hippy, self.rel_hippy_err = rel_hippy, rel_hippy_err
        self.warmup = warmup

    @classmethod
    def missing(cls, warmup):
        return cls(None, None, None, None, None, None, warmup)

def make_tables(config, data_file):

    with open(data_file, "r") as data_fh:
        raw_results = json.load(data_fh)["data"]

    # make pyhyp variants look like vms
    config.VMS["PyHyp-mono"] = config.VMS["PyHyp"].copy()
    config.VMS["PyHyp-comp"] = config.VMS["PyHyp"].copy()

    config.VMS["PyHyp-mono"]["variants"] = ["mono-php"]
    config.VMS["PyHyp-comp"]["variants"] = ["composed"]

    del(config.VMS["PyHyp"])

    # "bench:vm:variant" -> ResultInfo
    results = {}
    for k, v in raw_results.iteritems():
        bench, vm, variant = k.split(":")

        if vm != "PyHyp":
            results[k] = v
            continue

        # is a pyhyp entry, make variant look like a separate vm
        if variant == "composed":
            nkey = "%s:PyHyp-comp:composed" % bench
        elif variant == "mono-php":
            nkey = "%s:PyHyp-mono:mono-php" % bench
        else:
            assert False

        results[nkey] = v

    # mono PHP benchmark ref_swap2 arecopies of ref_swap data
    results["pb_ref_swap2:Zend:mono-php"] = results["pb_ref_swap:Zend:mono-php"]
    results["pb_ref_swap2:HHVM:mono-php"] = results["pb_ref_swap:HHVM:mono-php"]
    results["pb_ref_swap2:HippyVM:mono-php"] = results["pb_ref_swap:HippyVM:mono-php"]

    # now process confidence, relative times, ...
    row_data = {}
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        for vm_key, vm_data in sorted(config.VMS.iteritems()):
            dot()
            variants = vm_data["variants"]

            # because we flattened pyhyp variants to separate vm entries
            assert len(variants) == 1
            variant_key = variants[0]

            warmup = vm_data["warm_upon_iter"]

            rs_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)
            try:
                rs = results[rs_key]
            except KeyError:
                row_data[rs_key] = ResultInfo.missing(warmup)
                continue

            # Absolute
            kdata = make_kalibera_data(rs, warmup)
            if kdata is None:
                # not enough data to be useful
                row_data[rs_key] = ResultInfo.missing(warmup)
                continue

            val = kdata.mean()
            val_err = error(kdata)

            # Relative to PyPy
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

            # Relative to Hippy
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

            ri = ResultInfo(val, val_err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup)
            row_data[rs_key] = ri

    print("")
    make_ascii_table(row_data)
    make_latex_tables(config, row_data)


def conf_cell(val, err, width=".7cm"):
    if val is None: # no result for that combo
        return ""
    else:
        return "$\substack{\\mathmakebox[%s][r]{%.3f}\\\\{\\mathmakebox[%s][r]{\\scriptscriptstyle\\pm %.4f}}}$" % (width, val, width, err)

def header_cell(text, align="r", width="1.2cm"):
    return "\\makebox[%s][%s]{%s}" % (width, align, text)

MAKEFILE_CONTENTS = """
FILES=results_abs.pdf results_rel_pypy.pdf results_rel_hippy.pdf

.SUFFIXES: .tex .pdf

.tex.pdf:
	pdflatex $*.tex
	pdflatex $*.tex
	pdflatex $*.tex

all: ${FILES}
"""

def write_latex_header(fh):
    fh.write("""\\documentclass{article}
    \\usepackage[a4paper,margin=1cm,footskip=.5cm]{geometry}
    \\usepackage{mathtools}
    \\usepackage{booktabs}
    \\usepackage{multicol}
    \\usepackage{multirow}
    \\usepackage{xspace}
    \\usepackage{amsmath}
    \\begin{document}
    \\footnotesize\n""")

def make_latex_tables(config, row_data):
    # makefile for tables
    with open(os.path.join(TEX_DIR, "Makefile"), "w") as fh:
        fh.write(MAKEFILE_CONTENTS)

    short_vm_names = {
        "CPython": "CPython",
        "HHVM": "HHVM",
        "HippyVM": "HippyVM",
        "PyHyp-mono": "PyHyp$_m$",
        "PyHyp-comp": "PyHyp$_c$",
        "PyPy": "PyPy",
        "Zend": "Zend",
    }

    #short_bm_names = {
    #    "pb_return_simple": "pb_rs",
    #    "pb_total_list": "pb_t_l",
    #    "pb_scopes": "pb_scp",
    #    "fannkuch": "fkuch",
    #    "pb_sum_meth": "pb_smeth",
    #    "pb_termconstruction": "pb_tcons",
    #    "pb_sum": "pb_s",
    #    "pb_l1a0r": "pb_l1a0r",
    #    "pb_l1a1r": "pb_l1a1r",
    #    "pb_instchain": "pb_ichain",
    #    "pb_lists": "pb_lists",
    #    "deltablue": "dblue",
    #    "mandel": "mamdel",
    #    "pb_smallfunc": "pb_sfunc",
    #    "pb_ref_swap": "pb_rswap",
    #    "pb_ref_swap2": "pb_rswap2",
    #    "richards": "richds",
    #    "pb_sum_attr": "pb_sattr",
    #}

    # -- absolute times
    of = open(os.path.join(TEX_DIR, "results_abs.tex"), "w")
    write_latex_header(of)
    w = of.write

    w("\\section{Abs}\n")
    w("\\begin{table}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(short_vm_names[i]))
    w("\\\\\n")
    w("\\toprule\n")

    last_bench_key, last_vm_key = None, None
    first = True
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        if not first:
            w("\\addlinespace\n")
        row = [tex_escape_underscore(bench_key)]

        for vm_key, vm_data in sorted(config.VMS.iteritems()):
            variants = vm_data["variants"]

            # because we flattened pyhyp variants to separate vm entries
            assert len(variants) == 1
            variant_key = variants[0]

            rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)


            ri = row_data[rd_key]
            row.append(conf_cell(ri.val, ri.val_err))
            if ri.val is not None:
                was_data = True

        # row is complete
        if was_data:
            w("%s\\\\\n" % "&".join(row))
            first = False

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\caption{Absolute benchmark timings (PyHyp$_c =$ PyHyp composed, PyHyp$_m =$ PyHyp mono).}\n")
    w("\\end{table}")
    w("\\end{document}\n")
    of.close()

    # -- relative PyPy times
    of = open(os.path.join(TEX_DIR, "results_rel_pypy.tex"), "w")
    write_latex_header(of)
    w = of.write

    w("\\section{Rel to PyPy}\n")
    w("\\begin{table}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(short_vm_names[i]))
    w("\\\\\n")
    w("\\toprule\n")

    last_bench_key, last_vm_key = None, None
    first = True
    was_data = False
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        if not first and was_data:
            w("\\addlinespace\n")

        was_data = False
        row = [tex_escape_underscore(bench_key)]

        for vm_key, vm_data in sorted(config.VMS.iteritems()):
            variants = vm_data["variants"]

            # because we flattened pyhyp variants to separate vm entries
            assert len(variants) == 1
            variant_key = variants[0]

            rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)

            ri = row_data[rd_key]
            row.append(conf_cell(ri.rel_pypy, ri.rel_pypy_err))
            if ri.rel_pypy is not None:
                was_data = True

        # row is complete
        if was_data:
            w("%s\\\\\n" % "&".join(row))
            first = False

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\caption{Benchmark timings relative to PyPy (PyHyp$_c =$ PyHyp composed, PyHyp$_m =$ PyHyp mono).}\n")
    w("\\end{table}")
    w("\\centering\n")
    w("\\end{document}\n")
    of.close()

    # -- relative Hippy times
    of = open(os.path.join(TEX_DIR, "results_rel_hippy.tex"), "w")
    write_latex_header(of)
    w = of.write

    w("\\section{Rel to Hippy}\n")
    w("\\begin{table}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(short_vm_names[i]))
    w("\\\\\n")
    w("\\toprule\n")

    last_bench_key, last_vm_key = None, None
    first = True
    was_data = False
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        if not first and was_data:
            w("\\addlinespace\n")

        was_data = False
        row = [tex_escape_underscore(bench_key)]

        for vm_key, vm_data in sorted(config.VMS.iteritems()):
            variants = vm_data["variants"]

            # because we flattened pyhyp variants to separate vm entries
            assert len(variants) == 1
            variant_key = variants[0]

            rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)

            ri = row_data[rd_key]
            row.append(conf_cell(ri.rel_hippy, ri.rel_hippy_err))
            if ri.rel_hippy is not None:
                was_data = True

        # row is complete
        if was_data:
            w("%s\\\\\n" % "&".join(row))
            first = False

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\caption{Benchmark timings relative to HippyVM (PyHyp$_c =$ PyHyp composed, PyHyp$_m =$ PyHyp mono).}\n")
    w("\\end{table}")
    w("\\end{document}\n")
    of.close()

    os.system("cd tex && make")


def make_ascii_table(row_data):

    tb = prettytable.PrettyTable(["Benchmark", "VM", "Variant", "Seconds", "Error"])
    tb.align["Benchmark"] = "l"
    tb.align["WarmIter"] = "r"
    tb.align["Seconds"] = "r"
    tb.align["Error"] = "r"
    tb.float_format = "4.6"

    for k, v in row_data.iteritems():
        bench, vm, variant = k.split(":")
        tb.add_row([bench, "%s (warm=%d)" % (vm, v.warmup),
                   variant, v.val, v.val_err])

    sys.stdout.write("\n")
    print(tb.get_string(sortby="Benchmark"))


TEX_DIR = "tex"

if __name__ == "__main__":
    config_file = sys.argv[1]

    import_name = config_file[:-3]
    data_file = import_name + "_results.json"
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    try:
        os.mkdir(TEX_DIR)
    except OSError as e:
        pass # file exists

    make_tables(config, data_file)
