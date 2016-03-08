#!/bin/sh

missing=0
check_for () {
    which $1 > /dev/null 2> /dev/null
    if [ $? -ne 0 ]; then
        echo "Error: can't find $1 binary"
        missing=1
    fi
}

# but not if in "config generation only" mode
if [ "$1" != "gen_config" ]; then
    echo "===> Checking dependencies"
    check_for cc
    check_for g++
    check_for bunzip2
    check_for git
    check_for hg
    check_for python
    check_for svn
    check_for unzip
    check_for xml2-config
    check_for cmake
    check_for virtualenv

    which pypy > /dev/null 2> /dev/null
    if [ $? -eq 0 ]; then
        PYTHON=`which pypy`
    else
        PYTHON=`which python`
    fi
    which gmake > /dev/null 2> /dev/null
    if [ $? -eq 0 ]; then
        MYMAKE=gmake
    else
        MYMAKE=make
    fi

    if [ $missing -eq 1 ]; then
        exit 1
    fi
else
    echo "CONFIG GENERATION ONLY!";
fi

HERE=`pwd`
WRKDIR=${HERE}/work
mkdir -p ${WRKDIR}
PATCH_DIR=${HERE}/patches

# HHVM 3.4.0 and deps of that time.
HHVM_VERSION=817b3a07fc4e509ce15635dbc87778e5b3496663
HHVM_GIT_URI=git://github.com/facebook/hhvm.git
HHVM_DIR=${WRKDIR}/hhvm
HHVM_BINARY=${HHVM_DIR}/hphp/hhvm/hhvm
GLOG_SVN_URI=http://google-glog.googlecode.com/svn/trunk/
GLOG_VERSION=143
GLOG_DIR=google-glog

do_hhvm() {
    echo "===> HHVM"
    cd ${WRKDIR} || exit $?

    export CMAKE_PREFIX_PATH=`pwd`/glog
    if [ ! -e "${GLOG_DIR}" ]; then
        svn checkout ${GLOG_SVN_URI} ${GLOG_DIR} || exit $?
    fi

    if ! [ -d  "${WRKDIR}/glog" ]; then
        cd ${GLOG_DIR} || exit $?
        ./configure --prefix=$CMAKE_PREFIX_PATH || exit $?
        make || exit $?
        make install || exit $?
    fi

    cd ${WRKDIR} || exit $?
    if ! [ -d "hhvm" ]; then
        git clone ${HHVM_GIT_URI} || exit $?
        cd hhvm || exit $?
        git checkout ${HHVM_VERSION} || exit $?
        git submodule update --init --recursive || exit $?
        patch -Ep1 < ${PATCH_DIR}/hhvm.diff || exit $?
        patch -Ep1 < ${PATCH_DIR}/hhvm_cmake.diff || exit $?
        cd ..
    fi

    if ! [ -f "${HHVM_BINARY}" ]; then
        cd ${WRKDIR}/hhvm
        cmake . || exit $?
        make || exit $?
    fi
}

# CPython

CPYTHON_VERSION=2.7.10
CPYTHON_DIR=${WRKDIR}/Python-${CPYTHON_VERSION}
CPYTHON_TARBALL=Python-${CPYTHON_VERSION}.tgz
CPYTHON_DOWNLOAD_URI=http://python.org/ftp/python/${CPYTHON_VERSION}/${CPYTHON_TARBALL}
CPYTHON_INST_DIR=${WRKDIR}/cpython-inst
CPYTHON_BINARY=${CPYTHON_INST_DIR}/bin/python

PYCPARSER_VERSION=2.14
PYCPARSER_TARBALL=pycparser-${PYCPARSER_VERSION}.tar.gz
PYCPARSER_DOWNLOAD_URL=https://pypi.python.org/packages/source/p/pycparser/${PYCPARSER_TARBALL}

SETUPTOOLS_VERSION=18.3.2
SETUPTOOLS_TARBALL=setuptools-${SETUPTOOLS_VERSION}.tar.gz
SETUPTOOLS_DOWNLOAD_URL=https://pypi.python.org/packages/source/s/setuptools/${SETUPTOOLS_TARBALL}

CFFI_VERSION=1.2.1
CFFI_TARBALL=cffi-${CFFI_VERSION}.tar.gz
CFFI_DOWNLOAD_URL=https://pypi.python.org/packages/source/c/cffi/${CFFI_TARBALL}

do_cpython() {
    echo "===> CPython"

    cd ${WRKDIR}
    if ! [ -f "${CPYTHON_TARBALL}" ]; then
        wget ${CPYTHON_DOWNLOAD_URI} || exit $?
    fi

    if ! [ -d "${CPYTHON_DIR}" ]; then
        tar xfz ${CPYTHON_TARBALL} || exit $?
    fi

    if ! [ -f "${CPYTHON_BINARY}" ]; then
        cd ${CPYTHON_DIR}
        ./configure --prefix=${CPYTHON_INST_DIR} || exit $?
        ${MYMAKE} || exit $?
        ${MYMAKE} install || exit $?
    fi

    # pycparser
    cd ${WRKDIR}
    if ! [ -f "${PYCPARSER_TARBALL}" ]; then
        wget ${PYCPARSER_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -d "${CPYTHON_INST_DIR}/lib/python2.7/site-packages/pycparser" ]; then 
        tar xvf ${PYCPARSER_TARBALL} || exit $?
        cd pycparser-${PYCPARSER_VERSION} || exit $?
        ${CPYTHON_BINARY} setup.py install || exit $?
    fi

    # setuptools
    cd ${WRKDIR}
    if ! [ -f "${SETUPTOOLS_TARBALL}" ]; then
        wget ${SETUPTOOLS_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -f "${CPYTHON_INST_DIR}/lib/python2.7/site-packages/setuptools.pth" ]; then 
        tar xvf ${SETUPTOOLS_TARBALL} || exit $?
        cd setuptools-${SETUPTOOLS_VERSION} || exit $?
        ${CPYTHON_BINARY} setup.py install || exit $?
    fi

    # cffi
    cd ${WRKDIR}
    if ! [ -f "${CFFI_TARBALL}" ]; then
        wget ${CFFI_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -d "${CPYTHON_INST_DIR}/lib/python2.7/site-packages/cffi-${CFFI_VERSION}-py2.7-linux-x86_64.egg" ]; then 
        tar xvf ${CFFI_TARBALL} || exit $?
        cd cffi-${CFFI_VERSION} || exit $?
        ${CPYTHON_BINARY} setup.py install || exit $?
    fi
}

# Zend PHP

ZEND_VERSION=5.5.13
ZEND_TARBALL=php-${ZEND_VERSION}.tar.bz2
ZEND_DOWNLOAD_URI=http://uk3.php.net/get/${ZEND_TARBALL}/from/this/mirror
ZEND_DIR=php-${ZEND_VERSION}
ZEND_BINARY=${WRKDIR}/${ZEND_DIR}/sapi/cli/php

do_zend() {
    echo "===> Zend"
    if [ ! -f "${ZEND_BINARY}" ]; then
        cd ${WRKDIR}
        wget -O ${ZEND_TARBALL} ${ZEND_DOWNLOAD_URI} || exit $?
        bunzip2 -c - ${ZEND_TARBALL} | tar xf - || exit $?
        cd ${ZEND_DIR}
        patch -Ep1 < ${PATCH_DIR}/zend.diff || exit $?
        ./configure || exit $?
        ${MYMAKE} || exit $?
        # Zend PHP can run out of the build dir, so no 'make install'.
    fi
}

# Download and build PyPy

PYPY_VERSION=2.6.0
PYPY_TARBALL=pypy-${PYPY_VERSION}-src.tar.bz2
PYPY_DIR=${WRKDIR}/pypy-${PYPY_VERSION}-src
PYPY_GOAL_DIR=${PYPY_DIR}/pypy/goal
PYPY_BINARY=${PYPY_GOAL_DIR}/pypy-c
PYPY_DOWNLOAD_URI=https://bitbucket.org/pypy/pypy/downloads/${PYPY_TARBALL}
PYPY_SITE_PKGS=${PYPY_DIR}/site-packages

PTABLE_VERSION=0.7.2
PTABLE_TARBALL=prettytable-${PTABLE_VERSION}.tar.bz2
PTABLE_DOWNLOAD_URL=https://pypi.python.org/packages/source/P/PrettyTable/${PTABLE_TARBALL}

APPDIRS_VERSION=1.4.0
APPDIRS_TARBALL=appdirs-${APPDIRS_VERSION}.tar.gz
APPDIRS_DOWNLOAD_URL=https://pypi.python.org/packages/source/a/appdirs/${APPDIRS_TARBALL}

RPLY_VERSION=0.7.4
RPLY_TARBALL=rply-${RPLY_VERSION}.tar.gz
RPLY_DOWNLOAD_URL=https://pypi.python.org/packages/source/r/rply/${RPLY_TARBALL}

do_pypy() {
    echo "===> PyPy"

    cd ${WRKDIR}
    if ! [ -f "${PYPY_TARBALL}" ]; then
        wget ${PYPY_DOWNLOAD_URI} || exit $?
    fi

    if ! [ -d "${PYPY_DIR}" ]; then
        bunzip2 -c - ${PYPY_TARBALL} | tar xf -
        cd ${PYPY_DIR}
        # Patch from pypy-hippy-bridge repo
        patch -Ep1 < ${PATCH_DIR}/pypy-2.5.diff || exit $?
    fi

    if [ ! -f "${PYPY_BINARY}" ]; then
        cd ${PYPY_GOAL_DIR}
        usession=`mktemp -d`
        PYPY_USESSION_DIR=${usession} ${PYTHON} \
            ../../rpython/bin/rpython -Ojit || exit $?
        rm -rf ${usession}
    fi

    # setuptools
    cd ${WRKDIR}
    if ! [ -f "${SETUPTOOLS_TARBALL}" ]; then
        wget ${SETUPTOOLS_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -f "${PYPY_SITE_PKGS}/setuptools.pth" ]; then
        tar xvf ${SETUPTOOLS_TARBALL} || exit $?
        cd setuptools-${SETUPTOOLS_VERSION} || exit $?
        ${PYPY_BINARY} setup.py install || exit $?
    fi

    # appdirs
    cd ${WRKDIR}
    if ! [ -f "${APPDIRS_TARBALL}" ]; then
        wget ${APPDIRS_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -f "${PYPY_SITE_PKGS}/appdirs-${APPDIRS_VERSION}-py2.7.egg" ]; then 
        tar xvf ${APPDIRS_TARBALL} || exit $?
        cd appdirs-${APPDIRS_VERSION} || exit $?
        ${PYPY_BINARY} setup.py install || exit $?
    fi

    # rply
    cd ${WRKDIR}
    if ! [ -f "${RPLY_TARBALL}" ]; then
        wget ${RPLY_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -f "${PYPY_SITE_PKGS}/rply-${RPLY_VERSION}-py2.7.egg" ]; then
        tar xvf ${RPLY_TARBALL} || exit $?
        cd rply-${RPLY_VERSION} || exit $?
        ${PYPY_BINARY} setup.py install || exit $?
    fi

    # prettytable
    cd ${WRKDIR}
    if ! [ -f "${PTABLE_TARBALL}" ]; then
        wget ${PTABLE_DOWNLOAD_URL} || exit $?
    fi
    if ! [ -f "${PYPY_SITE_PKGS}/prettytable-${PTABLE_VERSION}-py2.7.egg" ]; then
        tar xvf ${PTABLE_TARBALL} || exit $?
        cd prettytable-${PTABLE_VERSION} || exit $?
        ${PYPY_BINARY} setup.py install || exit $?
    fi
}

# PyHyP
# Uses a patched PyPy and HippyVM (patches already in-branch)

PYHYP_DIR=${WRKDIR}/pyhyp

PYHYP_PYPY_DIR=${PYHYP_DIR}/pypy-hippy-bridge
PYHYP_PYPY_VERSION=ecoop16_artefact_0_1
PYHYP_PYPY_HG_URI=https://bitbucket.org/softdevteam/pypy-hippy-bridge

PYHYP_HIPPY_VERSION=ecoop16_artefact_0_1
PYHYP_HIPPY_DIR=${PYHYP_DIR}/hippyvm
PYHYP_HIPPY_GIT_URI=https://github.com/hippyvm/hippyvm.git

PYHYP_BINARY=${PYHYP_HIPPY_DIR}/pyhyp

do_pyhyp() {
    echo "===> PyHyP"
    mkdir -p ${PYHYP_DIR}

    if [ ! -f "${PYHYP_BINARY}" ]; then

        cd ${PYHYP_DIR}
        if [ ! -d "${PYHYP_PYPY_DIR}" ]; then
            hg clone ${PYHYP_PYPY_HG_URI}
        fi

        if [ ! -d "${PYHYP_HIPPY_DIR}" ]; then
            git clone ${PYHYP_HIPPY_GIT_URI}
        fi

        # Checkout correct versions
        cd ${PYHYP_PYPY_DIR}
        hg up ${PYHYP_PYPY_VERSION}
        cd ${PYHYP_HIPPY_DIR}
        git checkout ${PYHYP_HIPPY_VERSION}

        # Translate using the PyPy we built earlier
        ${PYPY_BINARY} ${PYHYP_PYPY_DIR}/rpython/bin/rpython \
            -Ojit targethippy.py || exit $?
        mv hippy-c pyhyp
    fi
}

# Hippy

HIPPY_DIR=${WRKDIR}/hippyvm

HIPPY_HIPPY_DIR=${HIPPY_DIR}/hippyvm
HIPPY_HIPPY_GIT_URI=https://github.com/hippyvm/hippyvm.git
HIPPY_HIPPY_VERSION=2ae35b80023dbc4f0735e1388528d28ed7b234fd

HIPPY_BINARY=${HIPPY_HIPPY_DIR}/hippy-c

do_hippy() {
    echo "===> HippyVM"
    mkdir -p ${HIPPY_DIR}

    if [ ! -f "${HIPPY_BINARY}" ]; then
        cd ${HIPPY_DIR}

        if [ ! -d "${HIPPY_HIPPY_DIR}" ]; then
            git clone ${HIPPY_HIPPY_GIT_URI} || exit $?
        fi

        cd ${HIPPY_HIPPY_DIR}
        git checkout ${HIPPY_HIPPY_VERSION}
        patch -Ep1 < ${PATCH_DIR}/hippyvm.diff || exit $?

        ${PYPY_BINARY} ${PYPY_DIR}/rpython/bin/rpython -Ojit \
            targethippy.py || exit $?
    fi
}

KALIBERA_GIT_URI=https://github.com/softdevteam/libkalibera.git
KALIBERA_DIR=${WRKDIR}/libkalibera
do_kalibera() {
    echo "===> libkalibera"
    if [ ! -d "${KALIBERA_DIR}" ]; then
        cd ${WRKDIR}
        git clone ${KALIBERA_GIT_URI} || exit $?
    fi
    ln -sf ${KALIBERA_DIR}/python/pykalibera ${HERE}/pykalibera
}

# Make config file

CONFIG_FILE="${HERE}/config.py"
WARM_UPON_ITER=1 # user will need to tweak this

gen_config() {
    n_iterations=20 # default value tweaked by experimenter on a per-vm basis

    echo "===> Generate ${CONFIG_FILE}"

    echo "# Autogenerated by build.sh -- COPY BEFORE MAKING EDITS" > ${CONFIG_FILE}

    # Variants
    echo "# Variants" >> ${CONFIG_FILE}
    echo "VARIANTS = {" >> ${CONFIG_FILE}
    echo "    'mono-php': {" >> ${CONFIG_FILE}
    echo "        'filename' : 'mono.php'," >> ${CONFIG_FILE}
    echo "        'iter_runner': 'iterations_runner.php'," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}
    echo "    'mono-python': {" >> ${CONFIG_FILE}
    echo "        'filename': 'mono.py'," >> ${CONFIG_FILE}
    echo "        'iter_runner': 'iterations_runner.py'," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}
    echo "    'composed': {" >> ${CONFIG_FILE}
    echo "        'filename': 'comp.php'," >> ${CONFIG_FILE}
    echo "        'iter_runner': 'iterations_runner.php'," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}
    echo "    'composed-reverse': {" >> ${CONFIG_FILE}
    echo "        'filename': 'comp_rev.php'," >> ${CONFIG_FILE}
    echo "        'iter_runner': 'iterations_runner.php'," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}
    echo "}\n" >> ${CONFIG_FILE}

    echo "VMS = {" >> ${CONFIG_FILE}

    # HHVM
    echo "    'HHVM': {" >> ${CONFIG_FILE}
    echo "        'path': '${HHVM_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['mono-php']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}

    # CPython
    echo "    'CPython': {" >> ${CONFIG_FILE}
    echo "        'path': '${CPYTHON_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['mono-python']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}

    # Zend PHP
    echo "    'Zend': {" >> ${CONFIG_FILE}
    echo "        'path': '${ZEND_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['mono-php']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}

    # PyPy
    echo "    'PyPy': {" >> ${CONFIG_FILE}
    echo "        'path': '${PYPY_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['mono-python']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}

    # PyHyp
    echo "    'PyHyp': {" >> ${CONFIG_FILE}
    echo "        'path': '${PYHYP_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['composed', 'composed-reverse', 'mono-php']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}

    # HippyVM
    echo "    'HippyVM': {" >> ${CONFIG_FILE}
    echo "        'path': '${HIPPY_BINARY}'," >> ${CONFIG_FILE}
    echo "        'variants': ['mono-php']," >> ${CONFIG_FILE}
    echo "        'n_iterations': ${n_iterations}," >> ${CONFIG_FILE}
    echo "        'warm_upon_iter': ${WARM_UPON_ITER}," >> ${CONFIG_FILE}
    echo "    }," >> ${CONFIG_FILE}
    echo "}\n" >> ${CONFIG_FILE}

    # Add benchmarks
    echo "DELTABLUE_PARAM = 4000\n" >> ${CONFIG_FILE}

    echo "BENCHMARKS = {" >> ${CONFIG_FILE}
    # new micro
    echo "    'pb_ref_swap': 110000000," >> ${CONFIG_FILE}
    echo "    'pb_return_simple': 300000000," >> ${CONFIG_FILE}
    echo "    'pb_scopes': 160000000," >> ${CONFIG_FILE}
    echo "    'pb_sum':      100000000," >> ${CONFIG_FILE}
    echo "    'pb_sum_meth_attr': 100000000," >> ${CONFIG_FILE}
    echo "    'pb_sum_meth': 100000000," >> ${CONFIG_FILE}
    echo "    'pb_total_list': 280000," >> ${CONFIG_FILE}
    echo "    'pb_instchain': 1200," >> ${CONFIG_FILE}

    # unipycation micro
    echo "    'pb_l1a0r': 44000," >> ${CONFIG_FILE}
    echo "    'pb_l1a1r': 30000," >> ${CONFIG_FILE}
    echo "    'pb_lists': 3600," >> ${CONFIG_FILE}
    echo "    'pb_smallfunc': 45000000," >> ${CONFIG_FILE}
    echo "    'pb_walk_list': 390," >> ${CONFIG_FILE}

    # larger
    echo "    'fannkuch': 10," >> ${CONFIG_FILE}
    echo "    'mandel': 750," >> ${CONFIG_FILE}
    echo "    'richards': 100," >> ${CONFIG_FILE}
    echo "    'deltablue': DELTABLUE_PARAM," >> ${CONFIG_FILE}


    echo "}\n" >> ${CONFIG_FILE}

    # deltablue permutations
    echo "\nN_DELTABLUE_PERMS = 79" >> ${CONFIG_FILE}
    echo "for i in xrange(N_DELTABLUE_PERMS):" >> ${CONFIG_FILE}
    echo "    BENCHMARKS['deltablue_perm_%03d' % i] = DELTABLUE_PARAM" >> ${CONFIG_FILE}
    echo "" >> ${CONFIG_FILE}

    # Skips
    echo "SKIP = [" >> ${CONFIG_FILE}
    # these use refs, which python doesn't have
    echo "    'mandel:*:mono-python'," >> ${CONFIG_FILE}
    echo "    'pb_ref_swap:*:mono-python'," >> ${CONFIG_FILE}
    # These embed foreign methods in classes, which we can only do
    # when the class is a PHP class. We can't embed PHP methods
    # in Python classes.
    for b in "richards" "deltablue" "pb_instchain" "pb_sum_meth" "pb_sum_meth_attr"; do
        echo "    '${b}:*:composed-reverse'," >> ${CONFIG_FILE}
    done

    echo "]\n\n" >> ${CONFIG_FILE}

    # deltablue permutations can only run on the composd variant.
    echo "for i in xrange(N_DELTABLUE_PERMS):" >> ${CONFIG_FILE}
    echo "    SKIP.append('deltablue_perm_%03d:*:mono-python' % i)" >> ${CONFIG_FILE}
    echo "    SKIP.append('deltablue_perm_%03d:*:mono-php' % i)" >> ${CONFIG_FILE}
    echo "    SKIP.append('deltablue_perm_%03d:*:composed-reverse' % i)" >> ${CONFIG_FILE}
    echo "" >> ${CONFIG_FILE}

    # Repetitions
    echo "N_EXECUTIONS = 20" >> ${CONFIG_FILE}

    # for mk_graphs.py
    echo "N_GRAPHS_PER_BENCH = 3" >> ${CONFIG_FILE}
}

do_deltablue_permutations() {
    echo "===> Generate deltablue permutations"

    cd ${HERE}/deltablue_perms && ${CPYTHON_BINARY} make.py || exit $?
    n_perms=`ls ../benchmarks | grep -e '^deltablue_perm_*' | wc -l`

    expect_n_perms=79
    if [ $n_perms != ${expect_n_perms} ]; then
        echo "wrong number of permutations!"
        echo "Got ${n_perms} expect ${expect_n_perms}"
        exit 1
    fi
}

#
# MAIN
#

# pass "gen_config" to only generate config file
if [ ! "$1" = "gen_config" ]; then
    do_hhvm;
    do_cpython;
    do_zend;
    do_pypy;
    do_pyhyp;
    do_hippy;
    do_kalibera;
    do_deltablue_permutations
fi

gen_config;

echo "\n-------------------------------------------------------"
echo "HHVM:\n  ${HHVM_WRAPPER}\n"
echo "CPython:\n  ${CPYTHON_BINARY}\n"
echo "ZEND PHP:\n  ${ZEND_BINARY}\n"
echo "PyPy:\n  ${PYPY_BINARY}\n"
echo "PyHyp:\n  ${PYHYP_BINARY}\n"
echo "HippyVM:\n ${HIPPY_BINARY}"
echo "--------------------------------------------------------\n"

