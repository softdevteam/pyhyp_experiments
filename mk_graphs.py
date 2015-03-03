#!/usr/bin/env python2.7
"""
usage:
    mk_graphs.py <config file>
"""

import sys, json, time, random, os
import pykalibera.graphs
import html     # pip install html
import matplotlib

# Set figure size for plots
matplotlib.pyplot.figure(figsize=(2.5, 2.5), tight_layout=True)

# Set font size
font = {
    'family' : 'sans',
    'weight' : 'regular',
    'size'   : '6',
}
matplotlib.rc('font', **font)

OUTDIR = "report"
LAGS = [1, 2, 3]

def usage():
    print(__doc__)
    sys.exit(1)

def chop_warmups(executions, warmup):
    chopped = [x[warmup:] for x in executions]

    if len(chopped) == 0:
        print("no data after warmup")
        sys.exit(1)

    return chopped

def run_sequence_plot(key, execution, execution_no, filename):
    title = "Exec %d" % (execution_no)
    pykalibera.graphs.run_sequence_plot(
            execution, title=title, filename=filename)

def lag_plot(key, execution, execution_no, lag, filename):
    title = "Exec %d" % execution_no
    pykalibera.graphs.lag_plot(
            execution, lag=lag, title=title, filename=filename)

def acr_plot(key, execution, execution_no, filename):
    title = "Exec %d" % execution_no
    pykalibera.graphs.acr_plot(execution, title=title, filename=filename)

def key_to_safe_filename(k):
    return k.replace(" ", "_").replace(":", "-")

def run_seq_plot_filename(key, exec_num):
    return "run_seq_%s_%d" % (key_to_safe_filename(key), exec_num)

def acr_plot_filename(key, exec_num):
    return "acr_%s_%d" % (key_to_safe_filename(key), exec_num)

def lag_plot_filename(key, exec_num, lag):
    return "lag%d_seq_%s_%d" % (lag, key_to_safe_filename(key), exec_num)

def progress():
    sys.stdout.write(".")
    sys.stdout.flush()

def emit_graphs(body, key, executions, chosen_exec_nums):
    if len(executions) == 0 or len(executions[0]) == 0:
        body.text("missing data?")
        print("")
        return

    # Run sequences
    body.h3("Run Sequence Graphs")
    for exec_no in chosen_exec_nums:
        execution = executions[exec_no]
        filename = run_seq_plot_filename(key, exec_no)
        run_sequence_plot(key, execution, exec_no,
                filename=os.path.join(OUTDIR, filename))
        body.img(src=filename + ".png")
        progress()

    # Lag Plots
    body.h3("Lag Plots")
    body.text("For lags: %s" % LAGS)
    for lag in LAGS:
        body.h4("Lag %d" % lag)
        for exec_no in chosen_exec_nums:
            execution = executions[exec_no]
            filename = lag_plot_filename(key, exec_no, lag)
            lag_plot(key, execution, exec_no, lag,
                    filename=os.path.join(OUTDIR, filename))
            body.img(src=filename + ".png")
            progress()

    # ACR plots
    body.h3("Autocorellation Plots")
    for exec_no in chosen_exec_nums:
        execution = executions[exec_no]
        filename = acr_plot_filename(key, exec_no)
        acr_plot(key, execution, exec_no,
                filename=os.path.join(OUTDIR, filename))
        body.img(src=filename + ".png")
        progress()

    print("")

def emit_report_header(config, config_filename, data_dct):
    page = html.HTML("html")

    head = page.head("")
    head.style("pre { background-color: #cccccc; }")

    title = "Kalibera Dimensioning Information for %s" % config_filename
    page.title(title)

    body = page.body("")

    body.h1(title)

    body.pre(json.dumps(config.VMS, indent=4))

    return page, body

def emit_quick_links(data_dct, body):
    body.h2("Quick Links")
    ul = body.ul("")
    for key in sorted(data_dct["data"].keys()):
        ul.li("").a(key, href="#%s" % key)

def report(config, config_filename, data_dct):
    """ dumps out a report in HTML format """

    page, body = emit_report_header(config, config_filename, data_dct)
    emit_quick_links(data_dct, body)

    n_graphs = config.N_GRAPHS_PER_BENCH

    try:
        os.mkdir(OUTDIR)
    except OSError:
        pass

    # Iterate over keys in the json file drawing some graphs
    keys = sorted(data_dct["data"].keys())
    for key in keys:
        bench, vm, variant = key.split(":")

        warmup = config.VMS[vm]["warm_upon_iter"]

        sys.stdout.write("%s: " % key)
        sys.stdout.flush()

        body.a("", name=key)
        body.h2(key)

        executions = data_dct["data"][key]

        if n_graphs > len(executions):
            print("too few results for %d graphs per experiment" % n_graphs)
            sys.exit(1)

        executions = chop_warmups(executions, warmup)
        all_exec_nums = range(len(executions))
        random.shuffle(all_exec_nums)
        chosen_exec_nums = all_exec_nums[0:n_graphs]

        body.text("Chose execution numbers: %s" % chosen_exec_nums)

        emit_graphs(body, key, executions, chosen_exec_nums)

    with open(os.path.join(OUTDIR, "index.html"), "w") as f:
        f.write(str(page))

# ----

if __name__ == "__main__":
    from util import read_config
    config_base, config = read_config(sys.argv[1])

    json_file = config_base + "_results.json"

    with open(json_file, "r") as fh:
        data_dct = json.load(fh)

    report(config, sys.argv[1], data_dct)
