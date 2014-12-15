#!/usr/bin/env python2.7

"""
Benchmark, running many fresh processes.

usage: runner.py <config_file.py>
"""

ANSI_RED = '\033[91m'
ANSI_MAGENTA = '\033[95m'
ANSI_RESET = '\033[0m'

import os, subprocess, sys, subprocess, json

def usage():
    print(__doc__)
    sys.exit(1)

def run_exec(vm, benchmark, variant, n_executions, n_iterations, param):
    """ Runs multiple executions of a benchmark """

    executions_results = []
    for e in xrange(n_executions):
        print("%sExecution %3d/%3d%s" % (ANSI_MAGENTA, e + 1, n_executions, ANSI_RESET))
        bench_file = os.path.join(benchmark, variant + ".php")

        args = [vm, "iterations_runner.php", bench_file,
                str(n_iterations), str(param)]

        # run capturing output
        stdout, stderr = subprocess.Popen(
                args, stdout=subprocess.PIPE).communicate()

        try:
            iterations_results = eval(stdout) # we should get a list of floats
        except SyntaxError:
            print("*error: benchmark didn't print a parsable list.")
            print("We got:\n---\n%s\n---\n" % stdout)
            print("When running: %s" % " ".join(args))
            sys.exit(1)
        executions_results.append(iterations_results)

    print("")
    return executions_results

def dump_json(config_file, all_results):
    # dump out into json file, incluing contents of the config file
    with open(config_file, "r") as f:
        config_text = f.read()

    to_write = {"config" : config_text, "data" : all_results}

    with open(config.OUT_FILE, "w") as f:
        f.write(json.dumps(to_write, indent=1))

if __name__ == "__main__":

    try:
        config_file = sys.argv[1]
    except IndexError:
        usage()

    if not config_file.endswith(".py"):
        usage()

    import_name = config_file[:-3]
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise
    print(config)

    all_results = {} # stash results here
    for bmark, param in config.BENCHMARKS.items():

        for vm_executable, vm_info in config.VMS.items():
            vm_name = vm_info["name"]

            for variant in vm_info["variants"]:

                print("%sRunning '%s(%d)' (%s variant) under '%s'%s" %
                        (ANSI_RED, bmark, param, variant, vm_name, ANSI_RESET))
                exec_results = run_exec(vm_executable, bmark, variant,
                        config.N_EXECUTIONS, config.N_ITERATIONS, param)

                result_key = "%s:%s:%s" % (bmark, vm_name, variant)
                all_results[result_key] = exec_results

                # We dump the json after each experiment so we can monitor the
                # json file mid-run. It is overwritten each time.
                dump_json(config_file, all_results)

    print("Done: Results dumped to %s" % config.OUT_FILE)
