#! work/virtualenv/pypy/bin/pypy
# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math
import prettytable
import os
import collections

from pykalibera.data import Data, bootstrap_geomean
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
    def __init__(self, val, val_err, rel_pyhyp, rel_pyhyp_err, warmup):
        self.val, self.val_err = val, val_err
        self.rel_pyhyp, self.rel_pyhyp_err = rel_pyhyp, rel_pyhyp_err
        self.warmup = warmup

    @classmethod
    def missing(cls, warmup):
        return cls(None, None, None, None, warmup)

def make_tables(config, data_file, typ):

    with open(data_file, "r") as data_fh:
        raw_results = json.load(data_fh)["data"]

    # make pyhyp variants look like vms
    saw_pyhyp = False
    if config.VMS.has_key("PyHyp"):
        saw_pyhyp = True
        pyhyp_variants = config.VMS["PyHyp"]["variants"]

        if "mono-php" in pyhyp_variants:
            config.VMS["PyHyp-mono"] = config.VMS["PyHyp"].copy()
            config.VMS["PyHyp-mono"]["variants"] = ["mono-php"]

        if "composed" in pyhyp_variants:
            config.VMS["PyHyp-comp"] = config.VMS["PyHyp"].copy()
            config.VMS["PyHyp-comp"]["variants"] = ["composed"]

    if saw_pyhyp:
        del(config.VMS["PyHyp"])

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

    # mono PHP benchmark ref_swap2 are copies of ref_swap data
    if results.has_key("pb_ref_swap:Zend:mono-php"):
        results["pb_ref_swap2:Zend:mono-php"] = results["pb_ref_swap:Zend:mono-php"]

    if results.has_key("pb_ref_swap:HHVM:mono-php"):
        results["pb_ref_swap2:HHVM:mono-php"] = results["pb_ref_swap:HHVM:mono-php"]

    if results.has_key("pb_ref_swap:HippyVM:mono-php"):
        results["pb_ref_swap2:HippyVM:mono-php"] = results["pb_ref_swap:HippyVM:mono-php"]

    # now process confidence, relative times, ...
    row_data = {}
    geomeans = {}
    for vm_key, vm_data in sorted(config.VMS.iteritems()):
        # used to compute geomean
        bench_times = []
        baseline_times = []
        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
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

            # Relative to PyHyp (composed)
            pyhyp_key = "%s:PyHyp-comp:composed" % bench_key
            has_pyhyp = True
            try:
                pyhyp_data = results[pyhyp_key]
            except KeyError:
                has_pyhyp = False

            if has_pyhyp:
                pyhyp_warmup = config.VMS["PyHyp-comp"]["warm_upon_iter"]
                pyhyp_kdata = make_kalibera_data(pyhyp_data, pyhyp_warmup)
                rel_pyhyp, rel_pyhyp_err = rel(kdata, pyhyp_kdata)

                # Relative to itself, should be 1.0x
                if vm_key == "PyHyp-comp":
                    assert rel_pyhyp == 1.0

                bench_times.append(kdata)
                baseline_times.append(pyhyp_kdata)
            else:
                rel_pyhyp, rel_pyhyp_err = None, None

            ri = ResultInfo(val, val_err, rel_pyhyp, rel_pyhyp_err, warmup)
            row_data[rs_key] = ri

        # all benchmarks for this vm processed, now the geomean
        if bench_times:
            geomeans[vm_key] = \
                bootstrap_geomean(bench_times, baseline_times, ITERATIONS, CONF_SIZE)

    print("")

    if typ == "ascii":
        make_ascii_table(row_data)
    else:
        make_latex_tables(config, row_data, geomeans)


def conf_cell(val, err, width=".7cm"):
    if val is None: # no result for that combo
        return ""
    else:
        err_s = "\\pm %.4f" % err if err is not None else ""
        return "$\substack{\\mathmakebox[%s][r]{%.3f}\\\\{\\mathmakebox[%s][r]{\\scriptscriptstyle %s}}}$" % (width, val, width, err_s)

def header_cell(text, align="r", width="1.2cm"):
    return "\\makebox[%s][%s]{%s}" % (width, align, text)

MAKEFILE_CONTENTS = """
.SUFFIXES: .tex .pdf

.tex.pdf:
	pdflatex $*.tex
	pdflatex $*.tex
	pdflatex $*.tex

all: main.pdf
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

def make_latex_tables(config, row_data, geomeans):
    # makefile for tables
    with open(os.path.join(TEX_DIR, "Makefile"), "w") as fh:
        fh.write(MAKEFILE_CONTENTS)

    # test skeleton
    with open(os.path.join(TEX_DIR, "main.tex"), "w") as fh:
        write_latex_header(fh)
        w = fh.write

        w("\\input{results_abs}\n")
        w("\\input{results_rel_pyhyp}\n")
        w("\\end{document}")

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
    w = of.write

    w("\\begin{table*}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(short_vm_names[i]))
    w("\\\\\n")
    w("\\toprule\n")

    first = True
    for pico in [True, False]:
        if not pico:
            w("\\midrule\n")
        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
            if bench_key.startswith("pb_") != pico:
                continue
            if not first:
                w("\\addlinespace\n")

            bench_name = bench_key[3:] if \
                bench_key.startswith("pb_") else bench_key
            row = [tex_escape_underscore(bench_name)]

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
        first = True # no space for first large bm

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\caption{Absolute benchmark timings (PyHyp$_c =$ PyHyp composed, PyHyp$_m =$ PyHyp mono).}\n")
    w("\\end{table*}")
    of.close()

    # -- relative PyHyp times
    of = open(os.path.join(TEX_DIR, "results_rel_pyhyp.tex"), "w")
    w = of.write

    w("\\begin{table*}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(short_vm_names[i]))
    w("\\\\\n")
    w("\\toprule\n")

    first = True
    for pico in [True, False]:
        if not pico:
            w("\\midrule\n")
        was_data = False
        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
            if bench_key.startswith("pb_") != pico:
                continue
            if not first and was_data:
                w("\\addlinespace\n")

            was_data = False

            bench_name = bench_key[3:] if \
                bench_key.startswith("pb_") else bench_key
            row = [tex_escape_underscore(bench_name)]

            for vm_key, vm_data in sorted(config.VMS.iteritems()):
                variants = vm_data["variants"]

                # because we flattened pyhyp variants to separate vm entries
                assert len(variants) == 1
                variant_key = variants[0]

                rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)

                ri = row_data[rd_key]
                if vm_key == "PyHyp-comp":
                    row.append(conf_cell(ri.rel_pyhyp, None))
                else:
                    row.append(conf_cell(ri.rel_pyhyp, ri.rel_pyhyp_err))

                if ri.rel_pyhyp is not None:
                    was_data = True

            # row is complete
            if was_data:
                w("%s\\\\\n" % "&".join(row))
                first = False
        first = True # no space for first large bm

    # geomeans
    w("\\midrule\n")
    row = ["Geometric Mean"]
    for vm_key in sorted(config.VMS.iterkeys()):
        geo = geomeans.get(vm_key)
        if vm_key == "PyHyp-comp":
            row.append(conf_cell(geo.median, None))
        elif geo is not None:
            row.append(conf_cell(geo.median, geo.error))
        else:
            row.append("")
    w("%s\\\\\n" % "&".join(row))

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\label{tab:relresults}\n")
    w("\\caption{Benchmark timings relative to PyHyp composed (PyHyp$_c =$ PyHyp composed, PyHyp$_m =$ PyHyp mono).}\n")
    w("\\end{table*}")
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
    typ = sys.argv[2]

    assert typ in ["ascii", "tex"]

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

    make_tables(config, data_file, typ)
