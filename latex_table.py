#! work/virtualenv/pypy/bin/pypy
"""Generate latex tables"""

import sys
import json
import math
import os
from collections import OrderedDict

from pykalibera.data import Data, bootstrap_geomean

CONF_SIZE = "0.99"  # intentionally str

SHORT_VM_NAMES = {
    "CPython": "CPython",
    "HHVM": "HHVM",
    "HippyVM": "HippyVM",
    "PyHyp-mono": "PyHyp$_m$",
    "PyHyp-comp": "PyHyp$_c$",
    "PyHyp-comp-rev": "PyHyp$_{c2}$",
    "PyPy": "PyPy",
    "Zend": "Zend",
}

DB_ROW_N = 5
TEX_DIR = "tex"


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
    result = data.bootstrap_confidence_interval(
        ITERATIONS, confidence=CONF_SIZE)
    return result.error

def rel(data, other):
    cr = data.bootstrap_quotient(
        other, iterations=ITERATIONS, confidence=CONF_SIZE)
    return cr.median, cr.error

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
    for exec_n in range(total_execs):
        exec_nowarmup = exp_data[exec_n][warmup - 1:]
        if not exec_nowarmup:
            return None
        data_arg[(exec_n, )] = exec_nowarmup

    return Data(data_arg, [total_execs, len(data_arg[(0, )])])

class ResultInfo(object):
    def __init__(self, val, val_err, rel_val, rel_val_err, warmup):
        self.val, self.val_err = val, val_err
        self.rel_val, self.rel_val_err = rel_val, rel_val_err
        self.warmup = warmup

    @classmethod
    def missing(cls, warmup):
        return cls(None, None, None, None, warmup)

def make_tables(config, data_file):
    with open(data_file, "r") as data_fh:
        raw_results = json.load(data_fh)["data"]

    # make pyhyp variants look like vms
    saw_pyhyp = False
    if "PyHyp" in config.VMS:
        saw_pyhyp = True
        pyhyp_variants = config.VMS["PyHyp"]["variants"]

        if "mono-php" in pyhyp_variants:
            config.VMS["PyHyp-mono"] = config.VMS["PyHyp"].copy()
            config.VMS["PyHyp-mono"]["variants"] = ["mono-php"]

        if "composed" in pyhyp_variants:
            config.VMS["PyHyp-comp"] = config.VMS["PyHyp"].copy()
            config.VMS["PyHyp-comp"]["variants"] = ["composed"]

        if "composed-reverse" in pyhyp_variants:
            config.VMS["PyHyp-comp-rev"] = config.VMS["PyHyp"].copy()
            config.VMS["PyHyp-comp-rev"]["variants"] = ["composed"]

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
        elif variant == "composed-reverse":
            nkey = "%s:PyHyp-comp-rev:composed" % bench
        else:
            assert False

        results[nkey] = v

    row_data, geomeans = process_main_data(results)
    db_perms_row_data, db_mono_rel_mean = process_db_perms_data(results)

    make_latex_tables(config, row_data, geomeans,
                      db_perms_row_data, db_mono_rel_mean)
    os.system("cd tex && make")


def process_main_data(results):
    # now process confidence, relative times, ...
    row_data = {}
    geomeans = {}
    for vm_key, vm_data in sorted(config.VMS.iteritems()):
        # used to compute geomean
        bench_times = []
        baseline_times = []

        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
            # The permuatations of deltablue are special, skip them here
            if bench_key.startswith("deltablue_perm"):
                continue

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
                    rel_pyhyp = 1.0

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
    return row_data, geomeans


def process_db_perms_data(results):
    """Process data for deltablue permutations"""

    # We will display each permutation relative to the mono-php variant
    # of deltablue running under PyHyp.
    pyhyp_warmup = config.VMS["PyHyp-comp"]["warm_upon_iter"]

    db_perms_rel_to = results["deltablue:PyHyp-mono:mono-php"]
    db_rel_to_kdata = make_kalibera_data(db_perms_rel_to, pyhyp_warmup)
    db_row_data = OrderedDict()

    variant = "composed"
    vm_key = "PyHyp-comp"
    for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
        if not bench_key.startswith("deltablue_perm"):
            continue

        dot()

        rs_key = "%s:%s:%s" % (bench_key, vm_key, variant)
        rs = results[rs_key]
        kdata = make_kalibera_data(rs, pyhyp_warmup)
        val = kdata.mean()
        val_err = error(kdata)
        rel_mono, rel_mono_err = rel(kdata, db_rel_to_kdata)

        ri = ResultInfo(val, val_err, rel_mono, rel_mono_err, pyhyp_warmup)
        db_row_data[rs_key] = ri
    print("")

    return db_row_data, db_rel_to_kdata.mean()


def conf_cell(val, err, width=".7cm", suffix="", bold=False):
    if val is None: # no result for that combo
        return ""
    else:
        err_s = "\\pm %.4f" % err if err is not None else ""
        val_s = "%.3f" % val
        if bold:
            err_s = "\\mathbf{%s}" % err_s
            val_s = "\\mathbf{%s}" % val_s
        return ("$\substack{\\mathmakebox[%s][r]{%s}%s\\\\"
                "{\\mathmakebox[%s][r]{\\scriptscriptstyle %s}}}$"
                % (width, val_s, suffix, width, err_s))


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
    \\usepackage{slashbox}
    \\usepackage[table]{xcolor}
    \\begin{document}
    \\footnotesize\n""")

def make_latex_tables(config, row_data, geomeans,
                      db_perms_row_data, db_mono_rel_mean):
    # makefile for tables
    with open(os.path.join(TEX_DIR, "Makefile"), "w") as fh:
        fh.write(MAKEFILE_CONTENTS)

    # test skeleton
    with open(os.path.join(TEX_DIR, "main.tex"), "w") as fh:
        write_latex_header(fh)
        w = fh.write

        w("\\input{results_abs}\n")
        w("\\input{results_rel_pyhyp}\n")
        w("\\input{results_db_perms}\n")
        w("\\end{document}")

    make_latex_table_abs(config, row_data, geomeans)
    make_latex_table_rel(config, row_data, geomeans)
    make_latex_table_db_perms(config, db_perms_row_data, db_mono_rel_mean)


def make_latex_table_abs(config, row_data, geomeans):
    of = open(os.path.join(TEX_DIR, "results_abs.tex"), "w")
    w = of.write

    w("\\begin{table*}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(SHORT_VM_NAMES[i]))
    w("\\\\\n")
    w("\\toprule\n")

    first = True
    for pico in [True, False]:
        if not pico:
            w("\\midrule\n")
        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
            if bench_key.startswith("pb_") != pico:
                continue
            if bench_key.startswith("deltablue_perm"):
                continue  # in another table
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


def make_latex_table_rel(config, row_data, geomeans):
    of = open(os.path.join(TEX_DIR, "results_rel_pyhyp.tex"), "w")
    w = of.write

    w("\\begin{table*}\n")
    w("\\centering\n")
    w("\\begin{tabular}{l%s}\n" % ("r" * len(config.VMS)))
    w("\\toprule\n")

    # emit header
    w("Benchmark")
    for i in sorted(config.VMS.iterkeys()):
        w("&%s" % header_cell(SHORT_VM_NAMES[i]))
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
            if bench_key.startswith("deltablue_perm"):
                continue  # in another table
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
                    row.append(conf_cell(ri.rel_val, None))
                else:
                    row.append(conf_cell(ri.rel_val, ri.rel_val_err))

                if ri.rel_val is not None:
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

def colour_cells(cells, shade):
    if shade:
        new_cells = []
        for cell in cells:
            new_cells.append("\\cellcolor{black!10}%s" % cell)
        return new_cells
    else:
        return cells

def make_latex_table_db_perms(config, row_data, db_mono_rel_mean):
    of = open(os.path.join(TEX_DIR, "results_db_perms.tex"), "w")
    w = of.write

    w("\\addtolength{\\tabcolsep}{-.4em}\n")
    w("\\begin{table*}\n")
    w("\\small\n")
    w("\\centering\n")

    row_spec = "rrrp{.1em}" * (DB_ROW_N - 1)
    row_spec += "rrr"
    w("\\begin{tabular}{%s}\n" % (row_spec))
    w("\\toprule\n")

    # since we will draw cells downwards, we have to know ahead of time how
    # many rows we will need to draw.
    db_perm_benchs = [k for k in sorted(config.BENCHMARKS.keys()) if
                      k.startswith("deltablue_perm")]
    n_rows = int(math.ceil(float(len(db_perm_benchs)) / DB_ROW_N))

    row = []
    shade = False
    cell_count = 0
    vm_key = "PyHyp-comp"
    variant_key = "composed"
    for rowno in xrange(n_rows):
        for colno in xrange(DB_ROW_N):
            perm_no = (colno * n_rows) + rowno

            try:
                bench_key = db_perm_benchs[perm_no]
            except IndexError:
                # out of range -- done
                break

            assert bench_key.endswith(str(perm_no))

            rd_key = "%s:%s:%s" % (bench_key, vm_key, variant_key)
            ri = row_data[rd_key]

            rel_val_bold = False
            if not (0.75 <= ri.rel_val <= 1.25):
                rel_val_bold = True

            cell1 = "{\\tiny %s:}" % (perm_no + 1)
            cell2 = conf_cell(ri.val, ri.val_err, suffix="s", bold=rel_val_bold)
            cell3 = conf_cell(ri.rel_val, ri.rel_val_err,
                              suffix="\\times", bold=rel_val_bold)

            ext_cells = [cell1, cell2, cell3]

            row.extend(colour_cells(ext_cells, shade))

            # decide if we should add a spacing cell
            if (cell_count % DB_ROW_N) != DB_ROW_N - 1:
                # not the last cell on a row
                row.append("")

            cell_count += 1

        # row is complete
        w("%s\\\\\n" % "&".join(row))
        row = []
        shade = not shade

    assert row == []

    w("\\bottomrule\n")
    w("\\end{tabular}\n")
    w("\\label{tab:db_perms_results}\n")
    w("\\caption{Deltablue permutations: absolute times and times relative to "
      "PyHyp running mono-PHP deltablue (%.3f)}\n" % db_mono_rel_mean)
    w("\\end{table*}")
    w("\\addtolength{\\tabcolsep}{.4em}\n")
    of.close()

def usage():
    print("usage: %s <config-file>" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    err = False

    if len(sys.argv) != 2:
        usage()

    try:
        config_file = sys.argv[1]
    except IndexError:
        usage()

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
