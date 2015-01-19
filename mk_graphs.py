#!/usr/bin/env python2.7
"""
usage:
    mk_graphs.py <json file> <# warmup iters> <# graphs per experiment>
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

def emit_report_header(json_filename, warmup, n_graphs):
    page = html.HTML("html")

    head = page.head("")
    head.style("pre { background-color: #cccccc; }")

    title = "Kalibera Dimensioning Information for %s" % json_filename
    page.title(title)

    body = page.body("")

    body.h1(title)

    body.text("This report was generated using the following parameters:")
    body.pre(data_dct["config"])

    ul = body.ul("")
    ul.li("Report invocation:" + " ".join(sys.argv))
    ul.li("Warmup iters discarded: %s" % warmup)
    ul.li("Number of graphs per experiment: %s" % n_graphs)
    ul.li("Generated: %s" % time.asctime())

    return page, body

def emit_quick_links(data_dct, body):
    body.h2("Quick Links")
    ul = body.ul("")
    for key in sorted(data_dct["data"].keys()):
        ul.li("").a(key, href="#%s" % key)

def report(json_filename, warmup, n_graphs, data_dct):
    """ dumps out a report in HTML format """

    page, body = emit_report_header(json_filename, warmup, n_graphs)
    emit_quick_links(data_dct, body)

    try:
        os.mkdir(OUTDIR)
    except OSError:
        pass

    # Iterate over keys in the json file drawing some graphs
    keys = sorted(data_dct["data"].keys())
    for key in keys:
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
    try:
        json_file = sys.argv[1]
        warmup = sys.argv[2]
        n_graphs = sys.argv[3]
    except IndexError:
        usage()

    warmup = int(warmup)
    n_graphs = int(n_graphs)

    with open(json_file, "r") as f:
        data_dct = json.loads(f.read())

    report(json_file, warmup, n_graphs, data_dct)
