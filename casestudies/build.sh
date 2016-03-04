#!/bin/sh

# Download Squirrelmail
wget http://downloads.sourceforge.net/project/squirrelmail/stable/1.4.22/squirrelmail-webmail-1.4.22.tar.gz
tar xfz squirrelmail-webmail-1.4.22.tar.gz
cd squirrelmail-webmail-1.4.22/
mkdir _cache
chmod 777 _cache
patch -p0 < ../diffs/compose.diff
patch -p0 < ../diffs/imap_general.diff
patch -p0 < ../diffs/mailbox_display.diff
patch -p0 < ../diffs/mime.diff
cd ..

# patch hippy-c-cgi
patch -p0 < diffs/hippycgi.diff

# get sympy
wget https://github.com/sympy/sympy/archive/sympy-0.7.6.1.tar.gz
tar xfz sympy-0.7.6.1.tar.gz
mv sympy-sympy-0.7.6.1/sympy ../work/pyhyp/pypy-hippy-bridge/site-packages/

# install sqplugin
tar xfz sympy.tar.gz -C squirrelmail-webmail-1.4.22/plugins/
