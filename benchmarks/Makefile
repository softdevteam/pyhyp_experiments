# BSD make!

ECO =	eco

# So-called larger benchmarks
COMPOSED_OUTPUTS_LARGER =	fannkuch/comp.php \
				mandel/comp.php \
				richards/comp.php \
				deltablue/comp.php

# New pico benchmarks
COMPOSED_OUTPUTS_NEW_PICO =	pb_ref_swap/comp.php \
				pb_ref_swap2/comp.php \
				pb_return_simple/comp.php \
				pb_scopes/comp.php \
				pb_sum/comp.php \
				pb_sum_attr/comp.php \
				pb_total_list/comp.php \
				pb_sum_meth/comp.php \
				pb_instchain/comp.php # strictly from unipycation, but was unused

# Pico benchmarks ported from Unipycation
COMPOSED_OUTPUTS_UNIPY_PICO = 	pb_l1a0r/comp.php \
				pb_l1a1r/comp.php \
				pb_lists/comp.php \
				pb_smallfunc/comp.php \
				pb_termconstruction/comp.php

ALL_COMPOSED_OUTPUTS =	 	${COMPOSED_OUTPUTS_LARGER} \
				${COMPOSED_OUTPUTS_NEW_PICO} \
				${COMPOSED_OUTPUTS_UNIPY_PICO}

.SUFFIXES:.eco .php

.eco.php:
	${ECO} -e $< $@

all: ${ALL_COMPOSED_OUTPUTS}

clean:
	-rm -f ${ALL_COMPOSED_OUTPUTS}
