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
ITERATIONS = 1#0000

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

def make_tables(config, data_file, latex_table_file):

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

    # now process confidence, relative times, ...
    row_data = {}
    #for k, v in results.iteritems():
    #    bench, vm, variant = k.split(":")

    #    warmup = config.VMS[vm]["warm_upon_iter"]

    #    # Absolute
    #    kdata = make_kalibera_data(v, warmup)
    #    if kdata is not None:
    #        val = kdata.mean()
    #        val_err = error(kdata)

    #        # Relative to PyPy
    #        pypy_key = "%s:PyPy:mono-python" % bench
    #        has_pypy = True
    #        try:
    #            pypy_data = results[pypy_key]
    #        except KeyError:
    #            has_pypy = False

    #        if has_pypy:
    #            pypy_warmup = config.VMS["PyPy"]["warm_upon_iter"]
    #            pypy_kdata = make_kalibera_data(pypy_data, pypy_warmup)
    #            rel_pypy, rel_pypy_err = rel(kdata, pypy_kdata)
    #        else:
    #            rel_pypy, rel_pypy_err = None, None

    #        # Relative to Hippy
    #        hippy_key = "%s:HippyVM:mono-php" % bench
    #        has_hippy = True
    #        try:
    #            hippy_data = results[hippy_key]
    #        except KeyError:
    #            has_hippy = False

    #        if has_hippy:
    #            hippy_warmup = config.VMS["HippyVM"]["warm_upon_iter"]
    #            hippy_kdata = make_kalibera_data(hippy_data, hippy_warmup)
    #            rel_hippy, rel_hippy_err = rel(kdata, hippy_kdata)
    #        else:
    #            rel_hippy, rel_hippy_err = None, None
    #    else:  # kdata is None (missing result)
    #        val, val_err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err = [None] * 6

    #    ri = ResultInfo(val, val_err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup)
    #    row_data[k] = ri

    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        for vm_key, vm_data in sorted(config.VMS.iteritems()):
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
            kdata = make_kalibera_data(v, warmup)
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

    make_ascii_table(row_data)
    make_latex_table(config, row_data, latex_table_file)

def make_latex_table(config, row_data, latex_table_file):
    of = open(latex_table_file, "w")
    w = of.write

    short_vm_names = {
        "CPython": "CPy",
        "HHVM": "HH",
        "HippyVM": "Hpy",
        "PyHyp-mono": "PH-m",
        "PyHyp-comp": "PH-c",
        "PyPy": "PyPy",
        "Zend": "Zend",
    }

    short_bm_names = {
        "pb_return_simple": "pb_rs",
        "pb_total_list": "pb_t_l",
        "pb_scopes": "pb_scp",
        "fannkuch": "fkuch",
        "pb_sum_meth": "pb_smeth",
        "pb_termconstruction": "pb_tcons",
        "pb_sum": "pb_s",
        "pb_l1a0r": "pb_l1a0r",
        "pb_l1a1r": "pb_l1a1r",
        "pb_instchain": "pb_ichain",
        "pb_lists": "pb_lists",
        "deltablue": "dblue",
        "mandel": "mamdel",
        "pb_smallfunc": "pb_sfunc",
        "pb_ref_swap": "pb_rswap",
        "pb_ref_swap2": "pb_rswap2",
        "richards": "richds",
        "pb_sum_attr": "pb_sattr",
    }


    # header
    w("""\\documentclass{article}
    \\usepackage{longtable}
    \\usepackage{booktabs}
    \\usepackage{multicol}
    \\usepackage{multirow}
    \\usepackage{xspace}
    \\usepackage{amsmath}
    \\begin{document}""")

    w("\\hrule")
    w("\\footnotesize\n")

    # -- absolute times
    w("\\begin{longtable}{c%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")
    w("Benchmark")

    # emit header
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % short_vm_names[i])
    w("\\\\\n")
    w("\\toprule\n")

    last_bench_key, last_vm_key = None, None
    first = True
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        if not first:
            w("\\midrule\n")
        row = [tex_escape_underscore(short_bm_names[bench_key])]

        for vm_key, vm_data in sorted(config.VMS.iteritems()):
            variants = vm_data["variants"]

            # because we flattened pyhyp variants to separate vm entries
            assert len(variants) == 1
            variant_key = variants[0]

            rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)

            #if bench_key == "pb_ref_swap2":
            #    import pdb; pdb.set_trace()

            ri = row_data[rd_key]
            val = ri.val
            val_err = ri.val_err

            if val is None: # no result for that combo
                val_s = ""
            else:
                val_s = "$\substack{%.3f\\\\{\\pm %.3f}}$" % (val, val_err)

            row.append(val_s)

        # row is complete
        w("%s\\\\\n" % "&".join(row))
        first = False


    w("\\bottomrule\n")
    w("\\end{longtable}\n")
    w("\\newpage\n")
    w("\\end{document}\n")
    return


    # relative times
    w("\\begin{longtable}{cccrlrl}\n")
    w("\\toprule\n")
    w("Benchmark&   VM& Variant&    \multicolumn{2}{c}{$\\times$PyPy}&\multicolumn{2}{c}{$\\times$HippyVM}\\\\\n")

    last_bench_key, last_vm_key = None, None
    for bench_key, bench_data in row_data.iteritems():
        for vm_key, vm_data in sorted(bench_data.iteritems()):
            for variant_key, variant_data in vm_data.iteritems():
                val, err, rel_pypy, rel_pypy_err, rel_hippy, rel_hippy_err, warmup = variant_data

                if last_bench_key != bench_key:
                    w("\\midrule\n")
                    bench_rowspan = len(bench_data)
                    bench_cell = "\\multirow{%d}{*}{%s}" % (bench_rowspan, bench_key)
                    last_bench_key = bench_key
                else:
                    bench_cell = ""

                if last_vm_key != vm_key:
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
                    tex_escape_underscore(bench_cell),
                    tex_escape_underscore(vm_cell),
                    tex_escape_underscore(variant_key), rel_pypy_str,
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

    for k, v in row_data.iteritems():
        bench, vm, variant = k.split(":")
        tb.add_row([bench, "%s (warm=%d)" % (vm, v.warmup),
                   variant, v.val, v.val_err])

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
