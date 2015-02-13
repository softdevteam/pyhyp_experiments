# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math

from pykalibera.data import Data

CONF_SIZE = "0.99"  # intentionally str
ITERATIONS = 10000

def error(data):
    # lower, median, upper
    a, b, c = data.bootstrap_confidence_interval(
        ITERATIONS,
        confidence=CONF_SIZE)

    def avg(seq):
        return math.fsum(seq) / len(seq)

    return avg([b - a, c - b])


def make_confidence(config, out_file):

    with open(out_file, "r") as output_fh:
        results = json.load(output_fh)["data"]

    lines = []
    for exp_key in results.iterkeys():
        exp_data = results[exp_key]

        bench, vm, variant = exp_key.split(":")
        vm_info = config.VMS[vm]

        warmup = vm_info["warm_upon_iter"]

        data_arg = {}
        total_execs = len(exp_data)
        ok = False
        for exec_n in range(total_execs):
            exec_nowarmup = exp_data[exec_n][warmup - 1:]
            if not exec_nowarmup:
                print("\nMissing data for %s\n" % exp_key)
                break
            data_arg[(exec_n, )] = exec_nowarmup
        else:
            ok = True

        if not ok:
            continue

        kdata = Data(data_arg, [total_execs, len(data_arg[(0, )])])
        mean = kdata.mean()
        err = error(kdata)

        lines.append("{:<40} (warm={:2d})\t: {:3.6f} (+/- {:2.6f})".format(
              exp_key, warmup, mean, err))
        sys.stdout.write(".")
        sys.stdout.flush()

    sys.stdout.write("\n")
    for i in sorted(lines):
        print(i)


if __name__ == "__main__":
    config_file = sys.argv[1]

    import_name = config_file[:-3]
    out_file = import_name + "_results.json"
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    make_confidence(config, out_file)
