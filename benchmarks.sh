#!/bin/sh

echo "===> Checking out benchmarks"
git clone https://l.diekmann@bitbucket.org/softdevteam/pypy_bridge_examples.git

cp config.py pypy_bridge_examples/
cd pypy_bridge_examples

# LD_LIBRARY must be set to the gcc that was used to build hhvm
export LD_LIBRARY_PATH=/home/lukas/gcc-4.8.3/lib64:$LD_LIBRARY_PATH
./runner.py config.py
