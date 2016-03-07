# PyHyP Experiments

This repository contains benchmarks for our composed Python/PHP VM as well
as other VMs.

## Building

If you are using the VirtualBox image, you can skip this stage, as the VMs come
pre-built.

To build yourself, first ensure you have the following installed on a
Linux/amd64 system:

 * bunzip2
 * git
 * hg
 * python
 * svn
 * unzip
 * wget
 * GCC (and gcc-multilib).
 * virtualenv
 * Dependencies of HHVM, PyPy, and HippyVM.

Then run:

```
$ sh build.sh
```

## Running the Benchmarks

First inspect the generated `config.py`. Here you can adjust (for example)
the number of iterations at each Kalibera level and the benchmark parameters.

Then run:

```
$ make bench
```

Results are written to `config_results.json`.

The source code for the benchmarks is in the 'benchmarks/' directory.

## Case studies

The two case studies from the paper are also included.

If you are using the VirtualBox image, then the case studies come ready to run.
Please see the post-login message for more information.

To set up the case studies manually, run:

```
$ cd casestudies & make
```

### Prepare PyHyp

PyHyP needs to have the environment variable `PYPY_PREFIX` set to the
`pypy-hippy-bridge` folder. If you don't want to set this variable globally, you
can just patch the `hippyvm/hippy-c-cgi` executable by adding the appropriate
`export`:

```
#!/bin/sh
export PYPY_PREFIX=PATH_TO_EXPERIMENTS/pypy-hippy-bridge/
HIPPY=`dirname $0`/hippy-c
exec $HIPPY --cgi "$@"
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
               ".php" => "PATH_TO_EXPERIMENTS/hippyvm/hippy-c-cgi",
               ".py"  => "/usr/bin/python2.7" )
```

#### Setup

Run `configure` to configure Squirrelmail. At the very least you will need to
change the following things:

* Enter your IMAP Server details in `2. Server-Settings -> Update IMAP Settings`.
* Change the `data` folder under `4. General Options -> Data Directory` to
  `../data`. Then change the ownership of `squirrelmail-4.22.1/data/` to be
  accessible by your webserver user, e.g. `chown -R http:http data/`.

Finally, point the web server to the SquirrelMail folder
(`casestudies/squirrelmail-webmail-1.4.22/`). Here's a minimal configuration
file for lighttpd:

```
# This is a minimal example config
# See /usr/share/doc/lighttpd
# and http://redmine.lighttpd.net/projects/lighttpd/wiki/Docs:ConfigurationOptions

server.modules = (
	"mod_access",
)

include "conf.d/cgi.conf"

server.port		= 80
server.username		= "http"
server.groupname	= "http"
server.document-root	= "PATH_TO_EXPERIMENTS/pyhyp_experiments/casestudies/"
server.errorlog		= "/var/log/lighttpd/error.log"
dir-listing.activate	= "enable"
index-file.names	= ( "index.html", "index.php" )
mimetype.assign		= (
				".html" => "text/html",
				".txt" => "text/plain",
				".css" => "text/css",
				".js" => "application/x-javascript",
				".jpg" => "image/jpeg",
				".jpeg" => "image/jpeg",
				".gif" => "image/gif",
				".png" => "image/png",
				"" => "application/octet-stream"
			)
```

#### Activating the plugin

Run Squirrelmails `configure` once more:

```
cd squirrelmail-webmail-1.4.22/
./configure
```

Select: `8. Plugins`, then select `nltk` and `sympy`.

#### Activate HTML emails

To be able to see rendered formulae within Squirrelmail we need to activate HTML
viewing of emails which is deactived by default. To do that, go to the local
Squirrelmail website, then navigate to `Options->Display Preferences` and check
the box `Show HTML Version by default` and `Submit`.

#### Troubleshooting

##### Sympy is missing

To be able to use Sympy we need to install it into PyHyp.
The easiest way to do this is to download the current Sympy version from
`https://github.com/sympy/sympy/archive/sympy-0.7.6.1.tar.gz`. Extract
the `sympy` folder from the archive into `pypy-hippy-bridge/site-packages/`.

### CFFI

This example can be run just using the PyHyp executable. Simply run:

```
PYPY_PREFIX=../work/pyhyp/pypy-hippy-bridge ../work/pyhyp/hippyvm/pyhyp cffi.php
```

