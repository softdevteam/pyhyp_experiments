# BSD make!
COMPOSED_OUTPUTS=	fannkuch/comp.php \
			mandel/comp.php \
			fasta/comp.php \
			richards/comp.php \
			deltablue/comp.php

ECO=			eco

.SUFFIXES:.eco .php

.eco.php:
	${ECO} -e $< $@

all: ${COMPOSED_OUTPUTS}
