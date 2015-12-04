.PHONY: bench latex-tables
all:
	cd benchmarks && ${MAKE}

bench:
	env PYPY_PREFIX=`pwd`/work/pyhyp/pypy-hippy-bridge \
		python2.7 runner.py config.py

latex-tables:
	pypy latex_table.py config.py
