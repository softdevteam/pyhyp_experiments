# BSD make!

ECO =	eco

# Composed variant #1
COMPOSED_OUTPUTS =	fannkuch/comp.php \
			mandel/comp.php \
			richards/comp.php \
			deltablue/comp.php \
			pb_ref_swap/comp.php \
			pb_return_simple/comp.php \
			pb_scopes/comp.php \
			pb_sum/comp.php \
			pb_sum_meth_attr/comp.php \
			pb_total_list/comp.php \
			pb_sum_meth/comp.php \
			pb_instchain/comp.php \
			pb_l1a0r/comp.php \
			pb_l1a1r/comp.php \
			pb_lists/comp.php \
			pb_smallfunc/comp.php \
			pb_walk_list/comp.php

# Composed variant #2 (reverse of #1)
COMPOSED_OUTPUTS +=	mandel/comp_rev.php \
			pb_ref_swap/comp_rev.php \
			pb_return_simple/comp_rev.php \
			pb_scopes/comp_rev.php \
			pb_sum/comp_rev.php \
			pb_total_list/comp_rev.php \
			pb_l1a0r/comp_rev.php \
			pb_l1a1r/comp_rev.php \
			pb_lists/comp_rev.php \
			pb_smallfunc/comp_rev.php \
			pb_walk_list/comp_rev.php

.SUFFIXES:.eco .php

.eco.php:
	${ECO} -e $< $@

all: ${COMPOSED_OUTPUTS}

clean:
	-rm -f ${COMPOSED_OUTPUTS}
