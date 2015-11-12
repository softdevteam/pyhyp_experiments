#! work/virtualenv/pypy/bin/pypy
# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math
import prettytable
import os

from pykalibera.data import Data

CONF_SIZE = "0.99"  # intentionally str

try:
    debug = os.environ["TABLE_DEBUG"]
    ITERATIONS = 1
except KeyError:
    ITERATIONS = 10000


def dot():
    sys.stdout.write(".")
    sys.stdout.flush()


def avg(seq):
    return math.fsum(seq) / len(seq)


def error(data):
    # lower, median, upper
    a, b, c = data.bootstrap_confidence_interval(
        ITERATIONS,
        confidence=CONF_SIZE)

    return avg([b - a, c - b])


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
    def __init__(self, val, val_err, warmup):
        self.val, self.val_err = val, val_err
        self.warmup = warmup

    @classmethod
    def missing(cls, warmup):
        return cls(None, None, warmup)


def make_tables(config, data_file):
    with open(data_file, "r") as data_fh:
        results = json.load(data_fh)["data"]

    row_data = {}
    for vm_key, vm_data in sorted(config.VMS.iteritems()):
        for bench_key, bench_data in sorted(config.BENCHMARKS.iteritems()):
            dot()
            variants = vm_data["variants"]

            for variant_key in variants:
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

                ri = ResultInfo(val, val_err, warmup)
                row_data[rs_key] = ri
    print("")
    make_ascii_table(row_data)


def make_ascii_table(row_data):
    tb = prettytable.PrettyTable(
        ["Benchmark", "VM", "Variant", "Seconds", "Error"])
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


def usage():
    print("usage: %s <config-file>" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()

    try:
        config_file = sys.argv[1]
    except KeyError:
        usage()

    import_name = config_file[:-3]
    data_file = import_name + "_results.json"
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    make_tables(config, data_file)
