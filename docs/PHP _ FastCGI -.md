**Does PHP work with FastCGI?**

Yes! As a matter of fact, you can set up multiple versions of PHP, and also utilize suexec to support different users with their own instances of PHP. It reduces the memory footprint of your web server, but still gives you the speed and power of the entire PHP language.  
Build PHP

First of all, build PHP. All of versions 4 and versions 5 supports the FastCGI flag. Simply specify where to get the FastCGI libraries from (download and install them from the [http://www.fastcgi.com](https://github.com/FastCGI-Archives/FastCGI.com/raw/master/original_snapshot/fcgi-2.4.1-SNAP-0910052249.tar.gz) website), and do the normal build with whatever other options you require:

`./configure [ your options ] --with-fastcgi=/usr/local`

This creates a version of PHP which speaks the FastCGI protocol. Unfortunately, depending on which version of PHP you are running, you may have one or two versions which run the FastCGI protocol. In particular:

*   Older 4.X versions produce a binary which _only_ runs FastCGI  

*   Newer 4.X versions and the 5.0.X and 5.1.X versions produce a binary which runs both regular and FastCGI versions  
    5.2.3 introduced two versions again - a php and php-cgi binary. The php-cgi binary is the one you want  

**Configure Part #1 (Apache 1.X)**

Setting up Apache to use PHP is similar to the normal configuration. Simply add the following lines to your httpd.conf, either in a VirtualHost directive, or in the main context:

```
FastCgiServer /export/httpd/cgi-bin/php  
AddHandler php-fastcgi .php

SetHandler fastcgi-script

Action php-fastcgi /cgi-bin/php  
DirectoryIndex index.html index.shtml index.cgi index.php  
AddType application/x-httpd-php .php
```

Finally, copy or hard link your PHP binary from wherever you installed it to /export/httpd/cgi-bin/php. Now there is something there to run.

These lines set up the Web server to pass requests for things of type .php to your FastCgiServer for processing. It also enables index.php as a directory index.

**Configure Part #2**

PHP can run in two modes - as a normal FastCGI application, and also bypassing the normal FastCGI process manager, using its own system to control how many copies of the PHP binary are running. The default mode is to run it's own process manager, bringing up 8 by default.

Depending on your configuration, you may want to pre-fork threads with the FastCGI process manager, or else run it as a typical dynamic application. Since you'll want to set environment variables, and those can't easily be set for FastCGI, I usually install a tiny shell script with configuration variables in it into the cgi-bin directory and have it run PHP instead:

```  
#!/bin/sh

PHPRC="/usr/local/etc/php/client"  
export PHPRC  
PHP_FCGI_CHILDREN=4  
export PHP_FCGI_CHILDREN  
exec /usr/local/bin/php-fcgi  
```

This script lets you set a specific .ini file. In the example, PHP will read in /usr/local/etc/php/client/php.ini for configuration parameters. The number of running children is controlled by the PHP_FCGI_CHILDREN variable. If this is set to 0, then PHP will not fork a process manager but instead run only as a worker thread. If you are worried about memory leaks (memory leaks? In PHP?) then you can set PHP_FCGI_MAX_REQUESTS, to cause worker children to exit after that many requests.

A script like this also lets you easily control which versions you're running - on our servers, we might have three, four, or more versions running all at the same time. This is very handy when testing upgrades, because you don't have to touch the web server across the board, only on a per-domain basis.

The README.FastCGI file, located in the PHP source, provides additional details on these and some other useful variables.

**Confusing FastCGI and PHP Process Managers**

One of the problems people seem to run into most often is when you have competing process managers - if you run with both PHP and FastCGI thinking they are responsible for spawning worker threads, you will have a train wreck!

**Some Last Notes**

*   If you are using a dynamic application environment, make sure that PHP_FCGI_CHILDREN is always set to 0; that way, PHP will never try to manage worker threads.  

*   If you are using a static environment, decide where you're going to control it and make it clear in the comments in your httpd.conf so you remember six months later!  

*   Don't make too many PHP threads; usually your machine will die of CPU overload if you try to do too much work in the threads; allow httpd to buffer the network requests. More worker threads and CPU threads in your machine is usually counter-productive.  

*   Don't put "callout" code into your PHP threads - that means, don't have a PHP script make an http call to an external source (or back to itself). You'll end up with threads that are just sitting around waiting, rather than processing. You can even get into a deadlock if you make a call back to the web server that the PHP process itself is serving - you'll run out of threads, possible, and then the web server will grind to a halt!
