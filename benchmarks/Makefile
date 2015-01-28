# BSD make!
COMPOSED_OUTPUTS=	fannkuch/comp.php \
			mandel/comp.php \
			fasta/comp.php \
			richards/comp.php \
			deltablue/comp.php \
			gcbench/comp.php \
			heapsort/comp.php \
			pb_ref_swap/comp.php \
			pb_return_simple/comp.php \
			pb_scopes/comp.php \
			pb_sum/comp.php

ECO=			eco

.SUFFIXES:.eco .php

.eco.php:
	${ECO} -e $< $@

all: ${COMPOSED_OUTPUTS}
