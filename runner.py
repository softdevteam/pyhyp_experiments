#!/usr/bin/env python2.7

"""
Benchmark, running many fresh processes.

usage: runner.py <config_file.py>
"""

ANSI_RED = '\033[91m'
ANSI_MAGENTA = '\033[95m'
ANSI_CYAN = '\033[36m'
ANSI_RESET = '\033[0m'

import os, subprocess, sys, subprocess, json, time

VARIANT_TO_FILENAME = {
    "mono-php": "mono.php",
    "mono-python": "mono.py",
    "composed": "comp.php",
}

VARIANT_TO_ITERATIONS_RUNNER = {
    "mono-php": "iterations_runner.php",
    "composed": "iterations_runner.php", # composed programs start in PHP
    "mono-python": "iterations_runner.py",
}

BENCH_DEBUG = os.environ.get("BENCH_DEBUG", False)
BENCH_DRYRUN = os.environ.get("BENCH_DRYRUN", False)

def usage():
    print(__doc__)
    sys.exit(1)

def mean(seq):
    return sum(seq) / float(len(seq))

def dump_json(config_file, all_results):
    # dump out into json file, incluing contents of the config file
    with open(config_file, "r") as f:
        config_text = f.read()

    to_write = {"config" : config_text, "data" : all_results}

    with open(config.OUT_FILE, "w") as f:
        f.write(json.dumps(to_write, indent=1, sort_keys=True))

class ExecutionJob(object):
    """Represents a single executions level benchmark run"""

    def __init__(self, sched, vm_name, vm_info, benchmark, variant, parameter):
        self.sched = sched
        self.vm_name, self.vm_info = vm_name, vm_info
        self.benchmark = benchmark
        self.variant = variant
        self.parameter = parameter

        # Used in results JSON and ETA dict
        self.key = "%s:%s:%s" % (bmark, vm_name, variant)

    def eta(self):
        previous_exec_times = self.sched.eta_estimates.get(self.key)
        if previous_exec_times:
            return mean(previous_exec_times)
        else:
            return None

    def __str__(self):
        return self.key

    __repr__ = __str__

    def add_exec_time(self, exec_time):
        """Feed back a rough execution time for ETA usage"""
        self.sched.eta_estimates[self.key].append(exec_time)

    def run(self):
        """Runs this job (execution)"""

        print("%sRunning '%s(%d)' (%s variant) under '%s'%s" %
                    (ANSI_CYAN, self.benchmark, self.parameter, self.variant,
                     self.vm_name, ANSI_RESET))

        benchmark_dir = os.path.join("benchmarks", bmark)

        bench_file = os.path.join(benchmark_dir, VARIANT_TO_FILENAME[variant])
        iterations_runner = VARIANT_TO_ITERATIONS_RUNNER[variant]
        args = [self.vm_info["path"],
                iterations_runner, bench_file, str(vm_info["n_iterations"]),
                str(param)]

        # Print ETA for execution if available
        this_exec_eta = self.eta()
        if this_exec_eta: # could return None, meaning "no idea yet"
            exec_eta_str = "%fs" % this_exec_eta
        else:
            exec_eta_str = "unknown"

        print("    %sETA for this execution: %s%s" % (ANSI_MAGENTA, exec_eta_str, ANSI_RESET))

        if BENCH_DEBUG:
            print("%s>>> %s%s" % (ANSI_MAGENTA, " ".join(args), ANSI_RESET))

        if BENCH_DRYRUN:
            returne # don't actually do any benchmarks

        # Rough ETA execution timer
        exec_start_rough = time.time()

        # run capturing output
        stdout, stderr = subprocess.Popen(
                args, stdout=subprocess.PIPE).communicate()

        exec_time_rough = time.time() - exec_start_rough

        try:
            iterations_results = eval(stdout) # we should get a list of floats
        except SyntaxError:
            print(ANSI_RED)
            print("=ERROR=" * 8)
            print("*error: benchmark didn't print a parsable list.")
            print("We got:\n---\n%s\n---\n" % stdout)
            print("When running: %s" % " ".join(args))
            print("=ERROR=" * 8)
            print(ANSI_RESET)
            print("")

            return []

        # Add to ETA estimation figures
        self.add_exec_time(exec_time_rough)

        print("")
        return iterations_results


class ScheduleEmpty(Exception):
    pass

class ExecutionScheduler(object):
    """Represents our entire benchmarking session"""

    def __init__(self):
        self.work_deque = deque()

        # Record how long processes are taking so we can make a
        # rough ETA for the user.
        # Maps (bmark, vm, variant) -> [t_0, t_1, ...]
        self.eta_estimates = {}

        # Maps key to results:
        # (bmark, vm, variant) -> [[e0i0, e0i1, ...], [e1i0, e1i1, ...], ...]
        self.results = {}

    def add_job(self, job):
        self.work_deque.append(job)

    def next_job(self):
        try:
            return self.work_deque.popleft()
        except IndexError:
            raise ScheduleEmpty() # we are done

    def num_jobs_left(self):
        return len(self.work_deque)

    def eta(self):
        etas = [j.eta() for j in self.work_deque]
        if None in etas:
            return None # we don't know
        return sum(etas)

    def run(self):
        """Benchmark execution starts here"""
        # scaffold dicts
        for j in self.work_deque:
            self.eta_estimates[j.key] = []
            self.results[j.key] = []

        errors = False
        start_time = time.time() # rough overall timer, not used for actual results

        while True:
            print("%s%d jobs left in scheduler queue%s" %
                        (ANSI_CYAN, self.num_jobs_left(), ANSI_RESET))

            # Try to tell the user how long this might take
            overall_eta = self.eta()
            if overall_eta:
                overall_eta_str = "%fs" % overall_eta
            else:
                overall_eta_str = "unknown"
            print("%sOverall ETA %s%s" % (ANSI_CYAN, overall_eta_str, ANSI_RESET))

            try:
                job = self.next_job()
            except ScheduleEmpty:
                break # done!

            exec_result = job.run()

            if not exec_result and not BENCH_DRYRUN:
                errors = True

            self.results[job.key].append(exec_result)

            # We dump the json after each experiment so we can monitor the
            # json file mid-run. It is overwritten each time.
            dump_json(config_file, self.results)

        end_time = time.time() # rough overall timer, not used for actual results

        print("Done: Results dumped to %s" % config.OUT_FILE)
        if errors:
            print("%s ERRORS OCCURRED! READ THE LOG!%s" % (ANSI_RED, ANSI_RESET))

        print("Completed in (roughly) %f seconds" % (end_time - start_time))

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

    # Build job queue -- each job is an execution
    from collections import deque

    sched = ExecutionScheduler()
    for exec_n in xrange(config.N_EXECUTIONS):
        for vm_name, vm_info in config.VMS.items():
            for bmark, param in config.BENCHMARKS.items():
                for variant in vm_info["variants"]:
                    job = ExecutionJob(sched, vm_name, vm_info, bmark, variant, param)
                    sched.add_job(job)
                    # scaffold dicts

    sched.run() # does the benchmarking

