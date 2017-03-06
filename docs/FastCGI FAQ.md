# FastCGI FAQ

Please feel free to contribute missing or incomplete pieces.

Last modified 22 Jan 2004

### <a name="top">General</a>

*   What is FastCGI?
*   How does it work?
*   What servers support it?
*   What if my server doesn't support it?
*   What languages is there library support for?
*   How fast is it?
*   [How can I get the latest source version?](#cvs_access)

### Apache / mod_fastcgi

#### Installation

*   [Cannot load /usr/lib/apache/1.3/mod_fastcgi.so into server: /usr/lib/apache/1.3/mod_fastcgi.so: undefined symbol: ap_os_is_path_absolute](#ap_os_is_path_absolute)  

#### Config

*   [Why does 'FastCgiSuexec On' use the wrong suexec wrapper?](#WrongSuexecWrapper)
*   [How can I tell mod_fastcgi not to restart my application?](#NoRestart)
*   [What does a typical httpd.conf look like?](#typical_httpd.conf)
*   [Does PHP work with FastCGI?](#PHP)
*   [What is the path used with FastCGIExternalServer?](#FastCGIExternalServer)
*   How do I authenticate users based on cookies?

#### Misc.

*   How does it compare with mod_perl?

### Application Development (Language Independent)

*   [How should I handle signals?](#Signals)
*   [Why does my application not work as a CGI?](#BrokenCGI)
*   [How can I get my application to reload when a new version is available?](#application_reload)
*   [How do I send an HTTP status other than 200 (the default, HTTP OK)](#httpstatus)
*   [How do I start an external FastCGI app (FastCGIExternalServer)](#startexternal)

### Perl

*   [How do I handle signals in Perl?](#PerlSignals)
*   [How do I use fork or exec?](#Perlfork)
*   How do I use CGI::Fast in the Authorizer Role?
*   [How can I get my application to reload when a new version is available?](#perl_application_reload)
*   [Mod_perl has Apache::Reload, and Apache::StatINC. Is there a similar mechanism for FastCGI?](#perl_application_reload)

### C

*   [Are there any C libs that handle common CGI operations?](#c_cgi_libs)

### Troubleshooting

*   [Why isn't my application producing a core dump?](#no_core_dump)
*   [Why is Windows reporting that it is unable to locate a DLL?](#no_dll)
*   How do I debug a FastCGI application?
*   Why is my application is exiting with status's I don't understand?
*   Why am I getting protocol errors?
*   I have a memory leak in my application
*   [FastCGI: incomplete headers (X bytes) received from server?](#incomplete_headers)

* * *

## General

#### <a name="cvs_access">How can I get the latest source version?</a>

Git HEAD can always be browsed [here](https://github.com/FastCGI-Archives/fcgi2).

##### [Back to Top](#top)

## Apache / mod_fastcgi

### Installation

#### <a name="ap_os_is_path_absolute">Cannot load /usr/lib/apache/1.3/mod_fastcgi.so into server: /usr/lib/apache/1.3/mod_fastcgi.so: undefined symbol: ap_os_is_path_absolute</a>

This is the result of a bug in the Apache header files (reported Sep 1999, PR# 5012, but never fixed).

The problem is due to the fact that httpd was compiled with optimization and ap_os_is_path_absolute() was inlined, but when mod_fastcgi.so was compiled optimization was not enabled and ap_os_is_path_absolute() was expected to be an external symbol.

Try this apxs invocation instead (it will turn on optimization and inline ap_os_is_path_apsolute()):
```
# apxs -Wc,-O -o mod_fastcgi.so -c *.c
```

##### [Back to Top](#top)

### Config

#### <a name="WrongSuexecWrapper">Why does 'FastCgiSuexec On' use the wrong suexec wrapper?</a>

If you've built mod_fastcgi as a DSO with apxs (see the INSTALL document) there is no way for mod_fastcgi to know where your suexec wrapper lives.  You'll have to use the _path_ argument to FastCgiSuexec.

##### [Back to Top](#top)

#### <a name="NoRestart">How can I tell mod_fastcgi not to restart my application?</a>

mod_fastcgi always maintains the configured number of processes for statically configured applications (see the -processes argument to FastCgiServer).

Dynamically configured applications are allowed to die (crash, exit, or be signaled down) as long as the -restart argument to FastCgiConfig is not in effect.

By default, mod_fastcgi will restart the _last_ process instance of a dynamic application if it dies.  This behavior can be changed with the -singleThreshold argument to FastCgiConfig.  Note that changing this can aggravate a bug in some OS when non-blocking connect()s are being used (see the -appConnTimeout argument).  Changing -singleThreshold will allow mod_fastcgi to kill off (signal down) the last process instance of an application when the demand for it no longer warrants its presence. This is the only way the _last_ process instance of an application is allowed to die without being restarted (i.e. a crash or exit will always result in a restart).

An another alternative is to configure the application as an FastCgiExternalServer and start and manage the application processes on your own (independent of mod_fastcgi's Process Manager).

##### [Back to Top](#top)

#### <a name="typical_httpd.conf">What does a typical httpd.conf look like?</a>

_Please_ consult the mod_fastcgi documentation for details (IOW read it).

```
LoadModule fastcgi_module modules/mod_fastcgi.so  

<IfModule mod_fastcgi.c>  

    # URIs that begin with /fcgi-bin/, are found in /var/www/fcgi-bin/  
    Alias /fcgi-bin/ /var/www/fcgi-bin/  

    # Anything in here is handled as a "dynamic" server if not defined as "static" or "external"  
    <Directory /var/www/fcgi-bin/>  
        SetHandler fastcgi-script  
        Options +ExecCGI  
    </Directory>  

    # Anything with one of these extensions is handled as a "dynamic" server if not defined as  
    # "static" or "external". Note: "dynamic" servers require ExecCGI to be on in their directory.  
    AddHandler fastcgi-script .fcgi .fpl  

    # Start a "static" server at httpd initialization inside the scope of the SetHandler  
    FastCgiServer /var/www/fcgi-bin/echo -processes 5  

    # Start a "static" server at httpd initialization inside the scope of the AddHandler  
    FastCgiServer /var/www/htdocs/some/path/echo.fcgi  

    # Start a "static" server at httpd initialization outside the scope of the Set/AddHandler  
    FastCgiServer /var/www/htdocs/some/path/coolapp  
    <Directory /var/www/htdocs/some/path/coolapp>  
        SetHandler fastcgi-script  
    </Directory>  

</IfModule>
```

#### <a name="PHP"></a>Does PHP work with FastCGI?

Yes! As a matter of fact, you can set up multiple versions of PHP, and also utilize suexec to support different users with their own instances of PHP. It reduces the memory footprint of your web server, but still gives you the speed and power of the entire PHP language.

##### Build PHP

First of all, build PHP. All of version 4 supports the FastCGI flag. Simply specify where to get the FastCGI libraries from (download and install them from the https://fastcgi-archives.github.io/ website), and do the normal build with whatever other options you require:

```
# ./configure --with-fastcgi=/usr/local
```

This creates a version of PHP which speaks the FastCGI protocol. Unfortunately, it no longer runs as a regular PHP application, so it will fail for use on the command line or in CRON. I recommend doing the configuration and builds twice, once as regular PHP with a full installation, and then a second time as a FastCGI version, but manually installing only the binary into your destination location. I call my regular one "php", and the other one "php-fcgi".a

##### Configure Part #1

Setting up Apache to use PHP is similar to the normal configuration. Simply add the following lines to your httpd.conf, either in a VirtualHost directive, or in the main context:

```
FastCgiServer /export/httpd/cgi-bin/php  
AddHandler php-fastcgi .php  
<Location /cgi-bin/php>  
    SetHandler fastcgi-script  
</Location>  
Action php-fastcgi /cgi-bin/php  
DirectoryIndex index.html index.shtml index.cgi index.php  
AddType application/x-httpd-php .php
```

Finally, copy or hard link your PHP binary from wherever you installed it to _/export/httpd/cgi-bin/php_. Now there is something there to run.

These lines set up the Web server to pass requests for things of type .php to your FastCgiServer for processing. It also enables index.php as a directory index.

##### Configure Part #2

PHP bypasses the normal FastCGI process manager, and uses its own system to control how many copies of the PHP binary are running, bringing up 8 by default. Since you often want finer control, I usually install a tiny shell script with configuration variables in it into the cgi-bin directory and have it run PHP instead:

```
#!/bin/sh

PHPRC="/usr/local/etc/php/client"  
export PHPRC  
PHP_FCGI_CHILDREN=4  
export PHP_FCGI_CHILDREN  
exec /usr/local/bin/php-fcgi
```

This script lets you set a specific .ini file. In the example, PHP will read in _/usr/local/etc/php/client/php.ini_ for configuration parameters. The number of running children is controlled by the other environment variable.

##### Configure Part #3 - suexec

One problem with PHP is that it is complicated to support multiple users without running into permission problems. By using the built-in FastCGI suexec features, you can have multiple versions of PHP running with a couple of children, each of which runs under the correct userid.

So, put the PHP configuration information into the VirtualHost directive, and then set the User and Group. Then, copy the shell scripts from section #2 above into that user's cgi-bin directory. Set the PHPRC environment variable to load a PHP configuration for that specific user, and you are all set! The power and flexibility of PHP, without the extra memory utilization on the Web server and with customers specific username information.

##### Notes

PHP is currently being used as a FastCGIExternalServer also, and works fine. However, if any includes are done by the PHP script, a duplicate copy of the relevant directories must exist on the remote machine.

##### [Back to Top](#top)

#### <a name="FastCGIExternalServer">What is the path used with FastCGIExternalServer?</a>

Since all FastCGI directives are global (they are not configured in a server context), all FastCGI paths map to the filesystem. In the case of external servers, this path does not have anything to do with the file system; it is a virtual file system path. Since the connection between mod_fastcgi and the FastCGI app is by a socket (unix or tcp), mod_fastcgi does not care where the program is (it could be on a completely different machine). However, mod_fastcgi needs to know when a hit is calling for an external app, so it uses this path as if it were a local filesystem path. Apache translates a request URI to a filesystem path.

There are two ways for getting external apps working:

1.  Use a path that is within the server filesystem area

    Example:

```
{Some server document root /var/www/htdocs}
FastCGIExternalServer /var/www/htdocs/extprog -host 127.0.0.1:9000
```

This seems easiest but has some shortcomings. Firstly there is the combination of real and virtual filesystem locations in the same place. If you are trying to keep all your files well organized and you have source files for the external server in one place and map URIs to the filesystem into another, there is a less than clear demarcation between what is real and what is virtual. Most importantly, if you want to use the same external server for more than one server, site, or URI, giving it a virtual place within a real path makes all that more confusing.

2.  Use a segregated path and use Alias to map requests to it.

    Example:

```
FastCGIExternalServer /fastcgiext/extprog -host 127.0.0.1:9000

{Some server docutment root /var/www/htdocs}
Alias /extprog /fastcgiext/extprog
```

This has the potential for more clarity. As a convention all external servers could be mapped into a virtual hierarchy and then aliases used to map into that from any and all places. This keeps the servers well organized and out of the way from filesystem locations and Aliases can map into them from where they are needed.

##### [Back to Top](#top)

* * *

## Application Development

#### <a name="Signals">How should I handle signals?</a>

All FastCGI applications should handle PIPE and TERM , mod_fastcgi spawned applications should also handle USR1.

PIPE occurs when trying to write/print to a file descriptor that has been closed.  Under mod_fastcgi, if a client aborts a connection before it completes mod_fastcgi does too.  At a minimum, SIGPIPE should be ignored (this is already setup in applications spawned by mod_fastcgi).  Ideally, it should result in an early abort of the request handling within your application and a return to the top of the FastCGI accept() loop.

USR1 may be received by FastCGI applications spawned by mod_fastcgi.  Apache uses this signal to request a "graceful" process shutdown (e.g. its used by "apachectl restart").  When mod_fastcgi's Process Manager receives USR1 it sends TERM to all of the FastCGI applications it spawned and then exits (its gets restarted by Apache).  This means that, under Apache/mod_fastcgi, a FastCGI application that receives USR1 from Apache will also receive TERM from the process manager.  FastCGI applications expected to be run under the control of mod_fastcgi/Apache should handle USR1 by finishing any request in process and then shutting down.

TERM is the standard signal sent to applications to request shutdown.  Typically, this is considered a request for "clean" shutdown, i.e. finish anything your in the middle of (within reason), free resources such as database connections, and exit.  When Apache receives TERM, it does not finish handling requests in progress.  Whether or not you finish any request in process when TERM is received is your decision, but keep in mind that under mod_fastcgi/Apache the TERM may be a "graceful" request in disguise.  I always finish any request in process before exiting.

Handling signals can be tricky.  Consult the documentation for your language and system for restrictions and idiosyncrasies.  In general, its always best to do as little as possible from within a signal handler.

See also [How do I handle signals in Perl](#PerlSignals).

##### [Back to Top](#top)

#### <a name="BrokenCGI">Why does my application not work as a CGI?</a>

You've most likely built your application based on the FCGX routines (see the echo2 application in the devkit examples).  These routines don't emulate stdin/stdout/stderr required by a CGI.  If CGI support is necessary use fcgi_stdio (C) or fcgio (C++) to override the stdio or iostream routines.

##### [Back to Top](#top)

#### <a name="application_reload"></a>How can I get my application to reload when a new version is available?

Applications started by mod_fastcgi can use the autoUpdate argument to FastCgiServer and/or FastCgiConfig (see the mod_fastcgi docs). A drawback to this approach is that, mod_fastcgi will check on every request for a new version of the application. A smarter implementation might have the application itself check periodically (either by number of requests handled or by time passed) and reload if a newer version of itself (or one of its libraries) exists. If a process manager, such as that embedded in mod_fastcgi, is responsible for the process, simply exiting will cause a new instance to be created.

One thing to consider when enabling an auto reload feature on a production server is that if there is any problem with the new script, you have no _good_ applications handling requests as you resolve the problem (assuming you notice it at all). Additionally, depending upon the reload mechanism, a _bad_ application could be started over and over if it fails (e.g. exits due to a syntax error).

##### [Back to Top](#top)

#### <a name="httpstatus"></a>How do I send an HTTP status other than 200 (the default, HTTP OK)

To return an HTTP status other than 200, add a 'Status:' header from your CGI. mod_fastcgi will look for that header and set the HTTP status. The Status: header is not sent to the client, but the HTTP status (first line of the server response) is.

Here's an example of what mod_fastcgi would send to the client if _Status: 400 Bad Request_ were sent from the CGI:

```
HTTP/1.1 400 Bad Request
Date: Thu, 22 Jan 2004 00:25:11 GMT
Server: Apache/1.3.26 (Unix) mod_jk mod_fastcgi/cvs AuthMySQL/2.20 mod_ssl/2.8.10 OpenSSL/0.9.6c
Connection: close
Content-Type: text/html; charset=iso-8859-1

...data...
```

##### [Back to Top](#top)

#### <a name="startexternal"></a>How do I start an external FastCGI app (FastCGIExternalServer)

There are a few ways of starting an external app that FastCGI can talk to. There is a direct API call in C, but some of the language implementations do not include it. The most portable way is to open a server socket (Unix or TCP) that matches your Apache directive parameters, then use the language's equivalent to C's dup2 to duplicate the server socket file descriptor to descriptor 0\. The FastCGI Accept call will select descriptor 0 for an incoming connection. Unfortunately your app will loose its stdin stream, so be careful if you have any expectations of taking input from the tty or program that starts the FastCGI app.

In Ruby, this is done as such:

```
require 'socket'
STDIN.reopen(TCPServer.new('127.0.0.1',9000))
```

##### [Back to Top](#top)

* * *

## Perl

#### <a name="PerlSignals">How do I handle signals in Perl?</a>

See also [How should I handle signals?](#Signals).  Here's an example that ignores SIGPIPE:

```
#!/usr/local/bin/perl -w  

use FCGI;  
use strict;  

my $count = 0;  
my $handling_request = 0;  
my $exit_requested = 0;  

my $request = FCGI::Request();  

sub sig_handler {  
    $exit_requested = 1;  
    exit(0) if !$handling_request;  
}  

$SIG{USR1} = \&sig_handler;  
$SIG{TERM} = \&sig_handler;  
$SIG{PIPE} = 'IGNORE';  

while ($handling_request = ($request->Accept() >= 0)) {  
    &do_request;  
    $handling_request = 0;  
    last if $exit_requested;  
}  

$request->Finish();  
exit(0);  

sub do_request() {  
    print("Content-type: text/html\r\n\r\n", ++$count);  
    $request->Finish();  
}
```

Here's an example that handles SIGPIPE in order to abort the request as quickly as possible:

```
#!/usr/local/bin/perl -w  

use FCGI;  
use strict;  

my $count = 0;  
my $handling_request = 0;  
my $exit_requested = 0;  

my $request = FCGI::Request();  

sub sig_handler {  
    $exit_requested = 1;  
    exit(0) if !$handling_request;  
}  

$SIG{USR1} = \&sig_handler;  
$SIG{TERM} = \&sig_handler;  
$SIG{PIPE} = sub {die 'SIGPIPE\n';};  

while ($handling_request = ($request->Accept() >= 0)) {  
    eval {&abort_request;} if (!eval {&do_request; 1;} && $@ ne 'SIGPIPE\n');  
    $handling_request = 0;  
    last if $exit_requested;  
}  

$request->Finish();  
exit(0);  

sub do_request() {  
    print("Content-type: text/html\r\n\r\n", ++$count);  
    $request->Finish();  
}  

sub abort_request() {  
    $exit_requested = 1; # assume the error isn't recoverable  
    print STDERR "fatal error, request aborted, shutting down: $@\n";  
    $request->Finish();  
}
```

##### [Back to Top](#top)

#### <a name="Perlfork">How do I use fork or exec ?</a>

When a request handle object is destroyed that has accepted a connection without finishing it, the connection will automatically be finished. Usually, this is what you want, although it is preferable to explicitly call the Finish() method.

When you fork, however, without calling exec as well, i.e. when you have two instance of perl running, the request handle object will (eventually) be destroyed in _both_ instances of perl. As a result, a possible request being handled will be finished when the object is destroyed for the first time. This is probably not what you expect, since you will usually only be handling the request in either the parent or the child. To inhibit this unwanted request finishing, you can send the Detach() message to the request handle object. In a detached state, destruction will not lead to any finishing of requests. It is advised you call Detach() before forking and Attach afterwards (in the process that will continue handling the request).

Before doing this though, please think about whether or not you really need to fork inside the accept loop. Since the FastCGI paradigm is different from the normal CGI one, you'll find that there are situations where you would fork in a CGI context, whereas it may not be necessary in a FastCGI context. In other cases, you're better off doing the forking before the accept loop.

Conversely, when you call exec without forking, the object will not be destroyed and no connection will automatically be finished, so in that case you are forced to do it yourself.

```
#!/usr/bin/perl -w  

use FCGI;  
use strict;  

my $request = FCGI::Request();`

`while ($request->Accept() >= 0) {  
    # do stuff with $request  

    $request->Detach();  

    my $child;  
    $child = fork;  
    if (!defined $child) {  
        # error handling  
    } elsif ($child == 0) {  
        # do child stuff  
    }  
    $request->Attach();  

    # continue processing request`

`    $request->Finish();  
}
```

##### [Back to Top](#top)

#### <a name="perl_application_reload"></a>How can I get my application to reload when a new version is available?  
Mod_perl has Apache::Reload, and Apache::StatINC. Is there a similar mechanism for FastCGI?

See the language independent [answer](#application_reload) to this question as well.

Assuming the application will automatically be restarted by mod_fastcgi (or another process manager), putting something like this at the end of your request loop should do it.

```

while ($request->Accept() >= 0) {  

     # handle request  

     request->Finish();  
     exit if -M $ENV{SCRIPT_FILENAME} < 0; # Autorestart  
}
```

##### [Back to Top](#top)

* * *

## C

#### <a name="c_cgi_libs">Are there any C libs that handle common CGI operations?</a>

I'm not sure which are FastCGI safe (let me know if you find one that is or isn't), but here's a few:

*   [ecgi](http://freshmeat.net/projects/ecgi/)
*   [cgic](http://www.boutell.com/cgic/)
*   [cgihtml](http://www.eekim.com/software/cgihtml/)
*   [cgilib](http://cgilib.sourceforge.net/) (C++)
*   [yacgi](http://www.geocities.com/SiliconValley/Bay/1927/yacgi.html)  

##### [Back to Top](#top)

* * *

## Troubleshooting

#### <a name="no_core_dump">Why isn't my application producing a core dump?</a>

A number of things could be preventing you from getting a core file:

*   The working directory of the process has to be writeable by the process.
*   The effective uid/gid can't be different than the real uid/gid of the process (the program can't be setuid or setgid).
*   The process resource limit, RLIMIT_CORE, has to be set large enough to accomodate the core file. See getrlimit(), setrlimit(), ulimit.

Assuming the process was spawned by mod_fastcgi:

*   The working directory is the directory of the program.
*   The effective/real/saved uid/gid is that of httpd's main User/Group directive if httpd was invoked as root. If httpd was not invoked as root, the uid/gid is that of the invoker.

Note that if a "wrapper" (such as suexec) is in use, its typically setuid/setgid.

##### [Back to Top](#top)

#### <a name="no_dll">Why is Windows reporting that it is unable to locate a DLL?</a>

Windows first searches the set of pre-installed DLLs such as the performance library (KERNEL32.DLL) and the security library (USER32.DLL). It then searches for the DLLs in the following sequence:

*   The directory where the executable module for the current process is located.
*   The current directory.
*   The Windows system directory. The GetSystemDirectory function retrieves the path of this directory.
*   The Windows directory. The GetWindowsDirectory function retrieves the path of this directory.
*   The directories listed in the `PATH` environment variable.

Note that the `LIBPATH` environment variable is not used.

mod_fastcgi, by default, clears the environment of FastCGI applications it starts (with the exception of `SystemRoot`). To pass or set an environment variable to a FastCGI application use the `-initial-env` argument to FastCgiConfig or FastCgiServer.

##### [Back to Top](#top)

#### <a name="incomplete_headers">FastCGI: incomplete headers (d bytes) received from server "s"</a>

The FastCGI application, s, didn't terminate the headers properly. A total of d bytes were recieved.

Headers are terminated by an empty line, e.g.

```
printf("Content-type: text/html\r\nStatus: 200 OK\r\n\r\n");
```

`See the [CGI specification](https://www.w3.org/CGI/) for more information.`

##### [Back to Top](#top)

* * *

*Copyright © 2000, 2001   Rob Saccoccio [robs @ fastcgi.com]   All rights reserved*
