#!/bin/sh

missing=0
check_for () {
	which $1 > /dev/null 2> /dev/null
    if [ $? -ne 0 ]; then
        echo "Error: can't find $1 binary"
        missing=1
    fi
}

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

HERE=`pwd`
WRKDIR=${HERE}/work
mkdir -p ${WRKDIR}
PATCH_DIR=${HERE}/patches

# GCC
GCC_VERSION_MAJOR=4.8
GCC_VERSION=${GCC_VERSION_MAJOR}.3
GCC_TARBALL=gcc-${GCC_VERSION}.tar.gz
GCC_DIR=gcc-${GCC_VERSION}
GCC_DOWNLOAD_URI=ftp://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/${GCC_TARBALL}
GCC_INST_DIR=${WRKDIR}/gcc-${GCC_VERSION}-inst
GCC_BINARY=${GCC_INST_DIR}/bin/gcc
GXX_BINARY=${GCC_INST_DIR}/bin/g++

do_gcc() {
	if [ ! -f "${GCC_BINARY}" ]; then
	    cd ${WRKDIR}
	    echo "\\n===> Download and build GCC ${GCC_VERSION}\\n"
	    if [ ! -f "${GCC_TARBALL}" ]; then
		    wget ${GCC_DOWNLOAD_URI}
	    fi
	    tar xzf ${GCC_TARBALL}
	    cd ${GCC_DIR}
	    ./contrib/download_prerequisites
	    cd ..
	    mkdir objdir
	    cd objdir
	    ../${GCC_DIR}/configure --prefix=${GCC_INST_DIR}
	    make || exit $?
	    make install || exit $?
	else
	    echo "\\n===> GCC ${GCC_VERSION} already done\\n"
	fi
}

# HHVM 3.4.0 and deps of that time.
HHVM_VERSION=817b3a07fc4e509ce15635dbc87778e5b3496663
HHVM_GIT_URI=git://github.com/facebook/hhvm.git
HHVM_DIR=${WRKDIR}/hhvm
HHVM_BINARY=${HHVM_DIR}/hphp/hhvm/hhvm
GLOG_SVN_URI=http://google-glog.googlecode.com/svn/trunk/
GLOG_VERSION=143
GLOG_DIR=google-glog

do_hhvm() {
	if [ ! -f "${HHVM_BINARY}" ]; then
	    cd ${WRKDIR}
	    echo "\\n===> Download and build HHVM\\n"
	    git clone ${HHVM_GIT_URI}
	    cd hhvm
	    git checkout ${HHVM_VERSION}
	    git submodule update --init --recursive
	    patch -Ep1 < ${PATCH_DIR}/hhvm.diff
	    cd ..

	    echo "\\n===> Download and build GLOG\\n"
	    export CMAKE_PREFIX_PATH=`pwd`/glog
	    if [ ! -e "${GLOG_DIR}" ]; then
		    svn checkout ${GLOG_SVN_URI} ${GLOG_DIR}
	    fi
	    cd ${GLOG_DIR}
	    ./configure --prefix=$CMAKE_PREFIX_PATH CC=${GCC_BINARY} CXX=${GXX_BINARY}
	    make || exit $?
	    make install || exit $?
	    cd ${WRKDIR}

	    cd hhvm 
	    echo "\\n===> Building HHVM\\n"
	    export LD_LIBRARY_PATH=${GCC_INST_DIR}/lib64/
	    cmake . -DCMAKE_CXX_COMPILER=${GXX_BINARY} -DCMAKE_C_COMPILER=${GCC_BINARY} || exit $?
	    make || exit $?
	else
	    echo "\\n===> HHVM already done\\n"
	fi
}

# CPython

CPYTHON_VERSION=2.7.7
CPYTHON_DIR=${WRKDIR}/Python-${CPYTHON_VERSION}
CPYTHON_TARBALL=Python-${CPYTHON_VERSION}.tgz
CPYTHON_DOWNLOAD_URI=http://python.org/ftp/python/${CPYTHON_VERSION}/${CPYTHON_TARBALL}
CPYTHON_BINARY=${CPYTHON_DIR}/python

do_cpython() {
	if [ ! -f "${CPYTHON_BINARY}" ]; then
	    echo "\\n===> Download and build CPython\\n"
	    cd ${WRKDIR}
	    wget ${CPYTHON_DOWNLOAD_URI} || exit $?
	    tar xfz Python-${CPYTHON_VERSION}.tgz || exit $?
	    cd ${CPYTHON_DIR}
	    ./configure || exit $?
	    ${MYMAKE} || exit $?
	    #cp ${WRKDIR}/cpython/Lib/test/pystone.py ${WRKDIR}/benchmarks/dhrystone.py
	else
	    echo "\\n===> CPython already done\\n"
	fi
}

# Zend PHP

ZEND_VERSION=5.5.13
ZEND_TARBALL=php-${ZEND_VERSION}.tar.bz2
ZEND_DOWNLOAD_URI=http://uk3.php.net/get/${ZEND_TARBALL}/from/this/mirror
ZEND_DIR=php-${ZEND_VERSION}
ZEND_BINARY=${WRKDIR}/${ZEND_DIR}/sapi/cli/php

echo ${ZEND_BINARY}
do_zend() {
	if [ ! -f "${ZEND_BINARY}" ]; then
	    echo "\\n===> Download and build Zend PHP\\n"
	    cd ${WRKDIR}
	    wget -O ${ZEND_TARBALL} ${ZEND_DOWNLOAD_URI} || exit $?
	    bunzip2 -c - ${ZEND_TARBALL} | tar xf - || exit $?
	    cd ${ZEND_DIR}
	    patch -Ep1 < ${PATCH_DIR}/zend.diff
	    ./configure || exit $?
	    ${MYMAKE} || exit $?
	    # Zend PHP can run out of the build dir, so no 'make install'.
	else
	    echo "\\n===> PHP already done\\n"
	fi
}

# Download and build PyPy

PYPY_VERSION=2.4.0
PYPY_TARBALL=pypy-${PYPY_VERSION}-src.tar.bz2
PYPY_DIR=${WRKDIR}/pypy-${PYPY_VERSION}-src
PYPY_GOAL_DIR=${PYPY_DIR}/pypy/goal
PYPY_BINARY=${PYPY_GOAL_DIR}/pypy
PYPY_DOWNLOAD_URI=https://bitbucket.org/pypy/pypy/downloads/${PYPY_TARBALL}

do_pypy() {
	if [ ! -f "${PYPY_BINARY}" ]; then
	    echo "\\n===> Download PyPy\\n"
	    sleep 3
	    cd ${WRKDIR}
	    wget https://bitbucket.org/pypy/pypy/downloads/pypy-${PYPY_VERSION}-src.tar.bz2 || exit $?
	    bunzip2 -c - ${PYPY_TARBALL} | tar xf -
	    cd ${PYPY_DIR}
	    # Patches in two parts from pypy-hippy-bridge repo
	    patch -Ep1 < ${PATCH_DIR}/pypy.diff || exit $?
	    patch -Ep1 < ${PATCH_DIR}/pypy2.diff || exit $?
	    cd ${PYPY_GOAL_DIR}
	    echo "\\n===> Build normal PyPy\\n"
	    usession=`mktemp -d`
	    PYPY_USESSION_DIR=${usession} ${PYTHON} ../../rpython/bin/rpython -Ojit --output=pypy || exit $?
	    rm -rf ${usession}
	else
	    echo "\\n===> PyPy already done\\n"
	fi
}

# PyHyP
# Uses a patched PyPy and HippyVM

PYHYP_PYPY_DIR=${WRKDIR}/pypy-hippy-bridge
PYHYP_PYPY_VERSION=hippy_bridge # XXX freeze
PYHYP_HIPPY_VERSION=pypy_bridge # XXX freeze
PYHYP_HIPPY_DIR=${WRKDIR}/hippyvm
PYHYP_BINARY=${PYHYP_HIPPY_DIR}/pyhyp
PYHYP_PYPY_HG_URI=https://bitbucket.org/softdevteam/pypy-hippy-bridge
PYHYP_HIPPY_GIT_URI=https://github.com/hippyvm/hippyvm.git

RPLY_VERSION=0.5.1
RPLY_TARBALL=rply-0.5.1.tar.gz
RPLY_DOWNLOAD_URI=https://pypi.python.org/packages/source/r/rply/${RPLY_TARBALL}
RPLY_DIR=rply-${RPLY_VERSION}

do_pyhyp() {
	if [ ! -f "${PYHYP_BINARY}" ]; then
	    echo "\\n===> Download  and build PyHyP\\n"
	    cd ${WRKDIR}
	    if [ ! -d "${PYHYP_PYPY_DIR}" ]; then
		hg clone ${PYHYP_PYPY_HG_URI}
	    fi
	    if [ ! -d "${PYHYP_HIPPY_DIR}" ]; then
		git clone ${PYHYP_HIPPY_GIT_URI}
	        wget ${RPLY_DOWNLOAD_URI}
	        tar xfz ${RPLY_TARBALL}
	        cp -r ${RPLY_DIR}/rply ${PYHYP_HIPPY_DIR}
	    fi
	    cd ${PYHYP_PYPY_DIR}
	    hg up ${PYHYP_PYPY_VERSION}
	    cd ${PYHYP_HIPPY_DIR}
	    git checkout ${PYHYP_HIPPY_VERSION}
	    ${PYPY_BINARY} ${PYHYP_PYPY_DIR}/rpython/bin/rpython \
		    -Ojit targethippy.py || exit $?
	    mv hippy-c pyhyp
	else
	    echo "\\n===> PyHyp already done\\n"
	fi
}

# Hippy

HIPPY_DIR=${WRKDIR}/hippyvm
HIPPY_BINARY=${HIPPY_DIR}/hippy-c
HIPPY_GIT_URI=https://github.com/hippyvm/hippyvm.git
HIPPY_VERSION=master	# XXX freeze

do_hippy() {
	if [ ! -f "${HIPPY_BINARY}" ]; then
	    echo "\\n===> Download and build Hippy\\n"
	    cd ${WRKDIR}
	    if [ ! -d "${HIPPY_DIR}" ]; then
		git clone ${HIPPY_GIT_URI}
	        wget ${RPLY_DOWNLOAD_URI}
	        tar xfz ${RPLY_TARBALL}
	        cp -r ${RPLY_DIR}/rply ${HIPPY_DIR}
	    fi
	    cd ${HIPPY_DIR}
	    git checkout ${HIPPY_VERSION}
	    patch -Ep1 < ${PATCH_DIR}/hippyvm.diff || exit $?
	    # Here we re-use RPython from the earlier PyPy build
	    ${PYPY_BINARY} ${PYPY_DIR}/rpython/bin/rpython -Ojit targethippy.py || exit $?
	else
	    echo "\\n===> Hippy already done\\n"
	fi
}

CONFIG_FILE="${HERE}/config.py"

gen_config() {
	echo "Writing config file to ${CONFIG_FILE}"

	echo "# Autogenerated by build.sh -- DO NOT EDIT" > ${CONFIG_FILE}
	echo "VMS = {" >> ${CONFIG_FILE}

	# HHVM
	echo "\t'${HHVM_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'HHVM'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['mono-php']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}

	# CPython
	echo "\t'${CPYTHON_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'CPython'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['mono-python']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}

	# Zend PHP
	echo "\t'${ZEND_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'Zend'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['mono-php']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}

	# PyPy
	echo "\t'${PYPY_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'PyPy'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['mono-python']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}

	# PyHyp
	echo "\t'${PYHYP_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'PyHyp'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['composed']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}

	# HippyVM
	echo "\t'${HIPPY_BINARY}': {" >> ${CONFIG_FILE}
	echo "\t\t'name': 'HippyVM'," >> ${CONFIG_FILE}
	echo "\t\t'variants': ['mono-php']," >> ${CONFIG_FILE}
	echo "\t}," >> ${CONFIG_FILE}
	echo "}\n" >> ${CONFIG_FILE}

	# Add benchmarks
	echo "BENCHMARKS = {" >> ${CONFIG_FILE}
	echo "\t'richards': 11," >> ${CONFIG_FILE}
	echo "}\n" >> ${CONFIG_FILE}

	# Repetitions
	echo "N_EXECUTIONS = 1" >> ${CONFIG_FILE}	
	echo "N_ITERATIONS = 5\n" >> ${CONFIG_FILE}

	# Output
	echo "OUT_FILE = 'output.json'" >> ${CONFIG_FILE}

	# check syntax
	${CPYTHON_BINARY} -c 'import config'
}

#
# MAIN
#

do_gcc;
do_hhvm;
do_cpython;
do_zend;
do_pypy;
do_pyhyp;
do_hippy;

gen_config;

# XXX install cffi someplace we can use it

echo "We are done! Here are your interpreters:"
echo "  HHVM:		${HHVM_BINARY}"
echo "  CPYTHON:	${CPYTHON_BINARY}"
echo "  ZEND PHP:	${ZEND_BINARY}"
echo "  PyPy:		${PYPY_BINARY}"
echo "  PyHyp:	${PYHYP_BINARY}"
echo "  HippyVM:	${HIPPY_BINARY}"

