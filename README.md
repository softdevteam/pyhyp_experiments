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

### Prepare PyHyp

To be able to use Sympy we need to install it into PyHyp.
The easiest way to do this is to download the current Sympy version from
`https://github.com/sympy/sympy/archive/sympy-0.7.6.1.tar.gz`. Extract
the `sympy` folder from the archive into `pypy-hippy-bridge/site-packages/`.

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

#### Installing the plugins

Now we need to install the Sympy plugin into Squirrelmail. First extract the
plugin into squirrelmails `plugin` folder:

```
cd casestudies
tar xfz sympy.tar.gz -C squirrelmail-webmail-1.4.22/plugins
```

Then activate the plugin using Squirrelmails `configure`:

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

### CFFI
Can be run with the PyHyp executable.
