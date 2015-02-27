#!/usr/bin/env python2.7

"""
Benchmark, running many fresh processes.

usage: runner.py <config_file.py>
"""

ANSI_RED = '\033[91m'
ANSI_GREEN = '\033[92m'
ANSI_MAGENTA = '\033[95m'
ANSI_CYAN = '\033[36m'
ANSI_RESET = '\033[0m'

import os, subprocess, sys, subprocess, json, time
from collections import deque
import datetime

UNKNOWN_TIME_DELTA = "?:??:??"
ABS_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
UNKNOWN_ABS_TIME = "????-??-?? ??:??:??"

# XXX these bits are not very generic, should we wish to release this
# as a standalone benchmark runner.
# Devise an interface to specify variants.
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

def dump_json(config_file, out_file, all_results):
    # dump out into json file, incluing contents of the config file
    with open(config_file, "r") as f:
        config_text = f.read()

    to_write = {"config" : config_text, "data" : all_results}

    with open(out_file, "w") as f:
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
        self.key = "%s:%s:%s" % (self.benchmark, self.vm_name, self.variant)

    def get_estimated_exec_duration(self):
        return self.sched.get_estimated_exec_duration(self.key)

    def get_exec_estimate_time_formatter(self):
        return self.sched.get_exec_estimate_time_formatter(self.key)

    def __str__(self):
        return self.key

    __repr__ = __str__

    def add_exec_time(self, exec_time):
        """Feed back a rough execution time for ETA usage"""
        self.sched.add_eta_info(self.key, exec_time)

    def run(self):
        """Runs this job (execution)"""

        print("%sRunning '%s(%d)' (%s variant) under '%s'%s" %
                    (ANSI_CYAN, self.benchmark, self.parameter, self.variant,
                     self.vm_name, ANSI_RESET))

        benchmark_dir = os.path.join("benchmarks", self.benchmark)

        bench_file = os.path.join(benchmark_dir, VARIANT_TO_FILENAME[self.variant])
        iterations_runner = VARIANT_TO_ITERATIONS_RUNNER[self.variant]
        args = [self.vm_info["path"],
                iterations_runner, bench_file, str(self.vm_info["n_iterations"]),
                str(self.parameter)]

        # Print ETA for execution if available
        exec_start = datetime.datetime.now()
        exec_start_str = "%s" % exec_start.strftime(ABS_TIME_FORMAT)

        tfmt = self.get_exec_estimate_time_formatter()
        print("{}    {:<35s}: {}{}".format(ANSI_MAGENTA,
                                         "Current time",
                                         tfmt.start_str,
                                         ANSI_RESET))


        print("{}    {:<35s}: {} ({} from now){}".format(ANSI_MAGENTA,
                                         "Estimated completion (this exec)",
                                         tfmt.finish_str,
                                         tfmt.delta_str,
                                         ANSI_RESET))
        if BENCH_DEBUG:
            print("%s    DEBUG: %s%s" % (ANSI_GREEN, " ".join(args), ANSI_RESET))

        if BENCH_DRYRUN:
            return # don't actually do any benchmarks

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

    def __init__(self, config_file, out_file):
        self.work_deque = deque()

        # Record how long processes are taking so we can make a
        # rough ETA for the user.
        # Maps (bmark, vm, variant) -> [t_0, t_1, ...]
        self.eta_estimates = {}

        # Maps key to results:
        # (bmark, vm, variant) -> [[e0i0, e0i1, ...], [e1i0, e1i1, ...], ...]
        self.results = {}

        # file names
        self.config_file = config_file
        self.out_file = out_file

    def add_job(self, job):
        self.work_deque.append(job)

    def next_job(self):
        try:
            return self.work_deque.popleft()
        except IndexError:
            raise ScheduleEmpty() # we are done

    def __len__(self):
        return len(self.work_deque)

    def get_estimated_exec_duration(self, key):
        previous_exec_times = self.eta_estimates.get(key)
        if previous_exec_times:
            return mean(previous_exec_times)
        else:
            return None # we don't know

    def get_estimated_overall_duration(self):
        etas = [j.get_estimated_exec_duration() for j in self.work_deque]
        if None in etas:
            return None # we don't know
        return sum(etas)

    def get_exec_estimate_time_formatter(self, key):
        return TimeEstimateFormatter(self.get_estimated_exec_duration(key))

    def get_overall_time_estimate_formatter(self):
        return TimeEstimateFormatter(self.get_estimated_overall_duration())

    def add_eta_info(self, key, exec_time):
        self.eta_estimates[key].append(exec_time)

    def run(self):
        """Benchmark execution starts here"""
        # scaffold dicts
        for j in self.work_deque:
            self.eta_estimates[j.key] = []
            self.results[j.key] = []

        errors = False
        start_time = time.time() # rough overall timer, not used for actual results

        while True:
            jobs_left = len(self)
            print("%s%d jobs left in scheduler queue%s" %
                        (ANSI_CYAN, jobs_left, ANSI_RESET))

            if jobs_left == 0:
                break

            tfmt = self.get_overall_time_estimate_formatter()
            print("{}{:<25s}: {}{}".format(ANSI_CYAN,
                                             "Current time",
                                             tfmt.start_str,
                                             ANSI_RESET))


            print("{}{:<25s}: {} ({} from now){}".format(ANSI_CYAN,
                                             "Estimated completion",
                                             tfmt.finish_str,
                                             tfmt.delta_str,
                                             ANSI_RESET))
            job = self.next_job()
            exec_result = job.run()

            if not exec_result and not BENCH_DRYRUN:
                errors = True

            self.results[job.key].append(exec_result)

            # We dump the json after each experiment so we can monitor the
            # json file mid-run. It is overwritten each time.
            dump_json(self.config_file, self.out_file, self.results)

        end_time = time.time() # rough overall timer, not used for actual results

        print("Done: Results dumped to %s" % self.out_file)
        if errors:
            print("%s ERRORS OCCURRED! READ THE LOG!%s" % (ANSI_RED, ANSI_RESET))

        print("Completed in (roughly) %f seconds" % (end_time - start_time))

class TimeEstimateFormatter(object):
    def __init__(self, seconds):
        """Generates string representations of time estimates.
        Args:
        seconds -- estimated seconds into the future. None for unknown.
        """
        self.start = datetime.datetime.now()
        if seconds is not None:
            self.delta = datetime.timedelta(seconds=seconds)
            self.finish = self.start + self.delta
        else:
            self.delta = None
            self.finish = None

    @property
    def start_str(self):
        return str(self.start.strftime(ABS_TIME_FORMAT))

    @property
    def finish_str(self):
        if self.finish is not None:
            return str(self.finish.strftime(ABS_TIME_FORMAT))
        else:
            return UNKNOWN_ABS_TIME

    @property
    def delta_str(self):
        if self.delta is not None:
            return str(self.delta).split(".")[0]
        else:
            return UNKNOWN_TIME_DELTA


def print_session_summary(config):
    import socket

    print("\nBecnchmarking Session Summary")
    print("==============================\n\n")
    print("Now:         " + datetime.datetime.now().strftime(ABS_TIME_FORMAT))
    print("Platform:    " + sys.platform)
    print("Host:        " + socket.gethostname())
    print("Directory:   " + os.getcwd())
    print("config file: " + sys.argv[1])
    print("VMs:         " + str(config.VMS.keys()))
    print("#benchmarks: " + str(len(config.BENCHMARKS)))
    print("\n")

    print("Hit enter to proceed...")
    raw_input()

def should_skip(config, job):
    skips = config.SKIP
    this_key = job.key

    for skip_key in skips:
        skip_elems = skip_key.split(":")
        this_elems = this_key.split(":")

        # should be triples of: bench * vm * variant
        assert len(skip_elems) ==3 and len(this_elems) == 3

        for i in range(3):
            if skip_elems[i] == "*":
                this_elems[i] = "*"

        if skip_elems == this_elems:
            return True # skip

    return False

def main():
    try:
        config_file = sys.argv[1]
    except IndexError:
        usage()

    if not config_file.endswith(".py"):
        usage()

    import_name = config_file[:-3]
    out_file = import_name + "_results.json"
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    # Build job queue -- each job is an execution
    reported_skips = False
    sched = ExecutionScheduler(config_file, out_file)
    for exec_n in xrange(config.N_EXECUTIONS):
        for vm_name, vm_info in config.VMS.items():
            for bmark, param in config.BENCHMARKS.items():
                for variant in vm_info["variants"]:
                    job = ExecutionJob(sched, vm_name, vm_info, bmark, variant, param)

                    if not should_skip(config, job):
                        sched.add_job(job)
                    else:
                        if BENCH_DEBUG and not reported_skips:
                            print("%s    DEBUG: %s is in skip list. Not scheduling.%s" %
                                  (ANSI_GREEN, job.key, ANSI_RESET))
        reported_skips = True

    print_session_summary(config)

    sched.run() # does the benchmarking

    print("Time now is %s" % datetime.datetime.now().strftime(ABS_TIME_FORMAT))

if __name__ == "__main__":
    main()
