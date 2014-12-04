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

wrkdir=`pwd`

# Build gcc 4.8
GCC_VERSION_MAJOR=4.8
GCC_VERSION=${GCC_VERSION_MAJOR}.3
GCC_TARBALL=gcc-${GCC_VERSION}.tar.gz
GCC_DIR=gcc-${GCC_VERSION}
GCC_BINARY=${wrkdir}/gcc-${GCC_VERSION_MAJOR}/bin/gcc
GXX_BINARY=${wrkdir}/gcc-${GCC_VERSION_MAJOR}/bin/g++
GCC_DOWNLOAD_URI=ftp://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/${GCC_TARBALL}

if [ ! -f "${GCC_BINARY}" ]; then
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
    ../${GCC_DIR}/configure --prefix=$wrkdir/gcc-${GCC_VERSION_MAJOR}
    make || exit $?
    make install || exit $?
else
    echo "\\n===> GCC ${GCC_VERSION} already done\\n"
fi

# HHVM
# XXX only build if not installed

# XXX checkout an explicit version of HHVM, but also figure
# out how to get a fixed version of the submodules too.

#HHVM_VERSION=f4c9d79f648fc30f44bf0af809da86d0fe9d188a
HHVM_GIT_URI=git://github.com/facebook/hhvm.git

# XXX get a fixed version of GLOG
GLOG_SVN_URI=http://google-glog.googlecode.com/svn/trunk/
#GLOG_VERSION=...
GLOG_DIR=google-glog


if [ ! -f "hhvm/hphp/hhvm/hhvm" ]; then
    cd $wrkdir
    echo "\\n===> Download and build HHVM\\n"
    sleep 3
    git clone ${HHVM_GIT_URI} --depth=1
    #git clone ${HHVM_GIT_URI} --depth=1
    cd hhvm
    #git checkout ${HHVM_VERSION}
    git submodule update --init --recursive
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
    cd $wrkdir

    cd hhvm 
    echo "\\n===> Building HHVM\\n"
    export LD_LIBRARY_PATH=$wrkdir/${GCC_DIR}/lib64/
    cmake . -DCMAKE_CXX_COMPILER=${GXX_BINARY} -DCMAKE_C_COMPILER=${GCC_BINARY} || exit $?
    make || exit $?
else
    echo "\\n===> HHVM already done\\n"
fi

# CPython

if [ ! -f "cpython/python" ]; then
    echo "\\n===> Download and build CPython\\n"
    sleep 3
    CPYTHONV=2.7.7
    cd $wrkdir
    wget http://python.org/ftp/python/${CPYTHONV}/Python-${CPYTHONV}.tgz || exit $?
    tar xfz Python-${CPYTHONV}.tgz || exit $?
    mv Python-${CPYTHONV} cpython
    cd cpython
    ./configure || exit $?
    $MYMAKE || exit $?
    cp $wrkdir/cpython/Lib/test/pystone.py $wrkdir/benchmarks/dhrystone.py
else
    echo "\\n===> CPython already done\\n"
fi

# PHP

if [ ! -f "php/sapi/cli/php" ]; then
    echo "\\n===> Download and build PHP\\n"
    sleep 3
    PHPV=5.5.13
    cd $wrkdir
    wget -O php-${PHPV}.tar.bz2 http://uk3.php.net/get/php-${PHPV}.tar.bz2/from/this/mirror || exit $?
    bunzip2 -c - php-${PHPV}.tar.bz2 | tar xf - || exit $?
    mv php-${PHPV} php
    cd php
    ./configure || exit $?
    $MYMAKE || exit $?
else
    echo "\\n===> PHP already done\\n"
fi

# Download and build PyPy

if [ ! -f "pypy/pypy/goal/pypy" ]; then
    echo "\\n===> Download PyPy\\n"
    sleep 3
    PYPYV=2.3.1
    cd $wrkdir
    wget https://bitbucket.org/pypy/pypy/downloads/pypy-${PYPYV}-src.tar.bz2 || exit $?
    bunzip2 -c - pypy-${PYPYV}-src.tar.bz2 | tar xf -
    mv pypy-${PYPYV}-src pypy
    cd pypy/pypy/goal/
    echo "\\n===> Build normal PyPy\\n"
    sleep 3
    usession=`mktemp -d`
    PYPY_USESSION_DIR=$usession $PYTHON ../../rpython/bin/rpython -Ojit --output=pypy || exit $?
    rm -rf $usession
else
    echo "\\n===> PyPy already done\\n"
fi

# PyHyP
if [ ! -f "hippyvm/pyhyp" ]; then
    echo "\\n===> Download  and build PyHyP\\n"
    PYTHON=$wrkdir/pypy/pypy/goal/pypy # needs rply
    sleep 3
    cd $wrkdir
    if [ ! -d "pypy-hippy-bridge" ]; then
        hg clone https://l.diekmann@bitbucket.org/softdevteam/pypy-hippy-bridge
    fi
    if [ ! -d "hippyvm" ]; then
        git clone https://github.com/hippyvm/hippyvm.git
    fi
    wget https://pypi.python.org/packages/source/r/rply/rply-0.5.1.tar.gz
    tar xfz rply-0.5.1.tar.gz
    cp -r rply-0.5.1/rply hippyvm/
    rm rply-0.5.1.tar.gz
    cd pypy-hippy-bridge/
    hg up hippy_bridge
    cd ..
    cd hippyvm/
    git checkout pypy_bridge
    $PYTHON ../pypy-hippy-bridge/rpython/bin/rpython -Ojit targethippy.py || exit $?
    mv hippy-c pyhyp
else
    echo "\\n===> Hippy already done\\n"
fi

# Hippy
if [ ! -f "hippyvm/hippy-c" ]; then
    echo "\\n===> Download  and build Hippy\\n"
    PYTHON=$wrkdir/pypy/pypy/goal/pypy
    sleep 3
    cd $wrkdir
    if [ ! -d "hippyvm" ]; then
        git clone https://github.com/hippyvm/hippyvm.git
    fi
    cd pypy-hippy-bridge/
    hg up default
    cd ..
    cd hippyvm/
    git checkout master
    $PYTHON ../pypy-hippy-bridge/rpython/bin/rpython -Ojit targethippy.py || exit $?
else
    echo "\\n===> Hippy already done\\n"
fi

