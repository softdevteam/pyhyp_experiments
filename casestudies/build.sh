#!/bin/sh

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
