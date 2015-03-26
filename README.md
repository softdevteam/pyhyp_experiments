# PyHyP Experiments

This repository contains benchmarks for our composed Python/PHP VM as well
as other VMs.

It is geared up to build on Linux/amd64.

## Dependencies

 * bunzip2
 * git
 * hg
 * python
 * svn
 * zip
 * unzip
 * libxml2
 * cmake
 * wget
 * GCC (and gcc-multilib).
 * virtualenv

## Case studies

The two case studies from the paper are also included.

### SquirrelMail
To run the case studies you need to setup a web-server, e.g. Apache,
Lighttpd, nginx. You'll then have to replace the PHP interpreter with PyHyp.
Here's an example configuration for lighttpd:

```
# /etc/lighttpd/conf.d/cgi.conf
cgi.assign = ( ".pl"  => "/usr/bin/perl",
               ".cgi" => "/usr/bin/perl",
               ".rb"  => "/usr/bin/ruby",
               ".erb" => "/usr/bin/eruby",
               ".php" => "PATH_TO_EXPERIMENTS/work/pyhyp/hippyvm/hippy-c-cgi",
               ".py"  => "/usr/bin/python2.7" )
```

Point the web server point to the SquirrelMail folder
(casestudies/squirrelmail-4.22.1/). From there follow SquirrelMail's
instructions on how to install.

# CFFI
Can be run with the PyHyp executable.
