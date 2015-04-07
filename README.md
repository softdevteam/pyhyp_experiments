# PyHyP Experiments

This repository contains benchmarks for our composed Python/PHP VM as well
as other VMs.

## Building

First ensure you have the following installed on a Linux/amd64 system:

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

Next build the VMs:

```
$ sh build.sh
```

Then inspect the generated `config.py`. Here you can adjust (for example)
the number of iterations at each Kalibera level and the benchmark parameters.

Now run:

```
$ python runner.py config.py
```

Results are written to `config_results.json`.

## Case studies

The two case studies from the paper are also included. Set them up by running

```
$ cd casestudies & make
```

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

### CFFI
Can be run with the PyHyp executable.
