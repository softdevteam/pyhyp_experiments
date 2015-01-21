# A quick script which generates confidence intervals for rough benchmarking
# Used during VM optimisation to get a rough idea if a change helped.

import sys
import json
import math

from pykalibera.data import Data

CONF_SIZE = "0.99"  # intentionally str
ITERATIONS = 10000

# XXX I would like to put this info in the config file at some point.
WARM_AFTER = {
    "PyPy":     5,
    "HippyVM":  5,
    "PyHyp":    5,
    "HHVM":     5,
    "CPython":  2,
    "Zend":     2,
}

def error(data):
    # lower, median, upper
    a, b, c = data.bootstrap_confidence_interval(
        ITERATIONS,
        confidence=CONF_SIZE)

    def avg(seq):
        return math.fsum(seq) / len(seq)

    return avg([b - a, c - b])


def make_confidence(config):
    with open(config.OUT_FILE, "r") as output_fh:
        results = json.load(output_fh)["data"]

    for exp_key in results.iterkeys():
        exp_data = results[exp_key]

        bench, vm, variant = exp_key.split(":")

        warmup = WARM_AFTER[vm]

        data_arg = {}
        total_execs = len(exp_data)
        for exec_n in range(total_execs):
            data_arg[(exec_n, )] = exp_data[exec_n][warmup:]

        import pdb; pdb.set_trace()

        kdata = Data(data_arg, [total_execs, len(data_arg[(0, )])])
        mean = kdata.mean()
        err = error(kdata)

        print("%30s (warm_after=%02d)\t: %10f (+/- %10f)" %
              (exp_key, warmup, mean, err))


if __name__ == "__main__":
    config_file = sys.argv[1]

    import_name = config_file[:-3]
    try:
        config = __import__(import_name)
    except:
        print("*** error importing config file!\n")
        raise

    make_confidence(config)
