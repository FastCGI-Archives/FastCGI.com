# FastCGI

### FastCGI Developer's Kit

Mark R. Brown  
Open Market, Inc.  

Document Version: 1.08  
11 June 1996  

##### Copyright © 1996 Open Market, Inc. 245 First Street, Cambridge, MA 02142 U.S.A.  

* * *

*   [1\. Introduction](#S1)
*   [2\. Getting started](#S2)
*   [3\. Writing applications](#S3)
    *   [3.1 Using the <tt>fcgi_stdio</tt> library](#S3.1)
    *   [3.2 Using the <tt>fcgiapp</tt> library](#S3.2)
    *   [3.3 Using Perl and Tcl](#S3.3)
    *   [3.4 Using Java](#S3.4)
*   [4\. Running applications](#S4)
    *   [4.1 Using a Web server that supports FastCGI](#S4.1)
    *   [4.2 Using <tt>cgi-fcgi</tt> with any Web server](#S4.2)
*   [5\. Known problems](#S5)
*   [6\. Getting support](#S6)

* * *

### <a name="S1">1\. Introduction</a>

FastCGI is an open extension to CGI that provides high performance for all Internet applications without the penalties of Web server APIs.

FastCGI is designed to be layered on top of existing Web server APIs. For instance, the <tt>mod_fastcgi</tt> Apache module adds FastCGI support to the Apache server. FastCGI can also be used, with reduced functionality and reduced performance, on any Web server that supports CGI.

This FastCGI Developer's Kit is designed to make developing FastCGI applications easy. The kit currently supports FastCGI applications written in C/C++, Perl, Tcl, and Java.

This document:

*   Describes how to configure and build the kit for your development platform.
*   Tells how to write applications using the libraries in the kit.
*   Tells how to run applications using Web servers that support FastCGI or using any Web server and <tt>cgi-fcgi</tt>.

The kit includes a [technical white paper](https://htmlpreview.github.io/?https://github.com/FastCGI-Archives/fcgi2/blob/master/doc/fastcgi-whitepaper/fastcgi.htm), <tt>doc/fastcgi-whitepaper/fastcgi.htm</tt>. You should read at least the first three sections of the technical white paper before starting to write FastCGI applications. The [performance paper](https://htmlpreview.github.io/?https://github.com/FastCGI-Archives/fcgi2/blob/master/doc/fcgi-perf.htm) will help you understand how application design affects performance with FastCGI.

The [FastCGI Specification](https://htmlpreview.github.io/?https://github.com/FastCGI-Archives/fcgi2/blob/master/doc/fcgi-spec.html), <tt>doc/fcgi-spec.html</tt>, defines the interface between a FastCGI application and a Web server that supports FastCGI. The software in the kit implements the specification. You don't need to read the specification in order to write applications.

Additional information is provided in the [FAQ](FastCGI%20FAQ.md) document, which contains frequently asked questions about application development using FastCGI, as well as some general information.

Experience with CGI programming will be extremely valuable in writing FastCGI applications. If you don't have enough experience with CGI programming, you should read one of the popular books on the topic or study the [CGI Spécification at W3 page](https://www.w3.org/CGI/).

### <a name="S2">2\. Getting started</a>

The kit is a compressed tar (tar.Z) file, distributed via the [fastcgi-archives.github.io](https://fastcgi-archives.github.io/) Web page. Unpacking the tar file creates a new directory <tt>fcgi-devel-kit</tt>.

Open the kit's index page, <tt>fcgi-devel-kit/index.html</tt>, using the "Open File" command in your Web browser. The index page gives you an overview of the kit structure and helps you navigate the kit. The index page also contains links that run some example applications, but the applications won't work when index.html is opened using the "Open File" command because they aren't aren't being accessed through a Web server.

In order to use the kit in earnest you'll need a Web server that you control, a Web server running with your user ID. The Web server will be starting FastCGI applications that you will need to debug; this will be a lot more convenient for you if these processes run with your user ID. It is best to have a Web server that supports FastCGI. [Section 4](#S4) discusses Web server issues.

If you can, keep the kit on a file system accessible from your personal workstation, do your builds on your workstation, and run your Web server on your workstation. If that's not possible, arrange a configuration such that the kit is accessible from the machine that's going to run your Web server, and build the kit and your applications on a machine that's configured exactly the same way (same processor architecture, operating system, etc.) as the machine that's going to run your Web server.

To build the kit you execute this sequence of commands in the <tt>fcgi-devel-kit</tt> directory:

```
% ./configure
% make
```

We've built and exercised the kit on these platforms (listed in alphabetical order):

*   BSD/OS 1.1 (Intel Pentium), gcc
*   Digital UNIX V3.2 148 (Alpha), gcc/cc
*   Hewlett-Packard HP-UX A.09.05 C and B.10.01 A (PA-RISC), gcc/cc
*   IBM AIX 1 4 (RS/6000), gcc
*   Silicon Graphics IRIX 5.3 11091812 (MIPS), gcc
*   Sun Solaris 2.4 and 2.5 (SPARC), gcc/cc
*   Sun SunOS 4.1.4 (SPARC), gcc

Once you've built the kit, follow the directions in [Section 4](#S4) to bring up your Web server and run the example applications.

### <a name="S3">3\. Writing applications</a>

#### <a name="S3.1">3.1 Using the <tt>fcgi_stdio</tt> library</a>

The <tt>fcgi_stdio</tt> library provides the easiest transition for C CGI programs and C CGI programmers to FastCGI. Using this library your application can run using either CGI or FastCGI, with the same binary for both situations.

To introduce the <tt>fcgi_stdio</tt> library we give a pair of examples: a tiny CGI program and the translation of this program to FastCGI. These two example programs are included in the kit.

The CGI program is <tt>examples/tiny-cgi.c</tt>:

```
#include <stdio.h>

#include <stdlib.h>

void main(void)
{
    int count = 0;
    printf("Content-type: text/html\r\n"
           "\r\n"
           "<title>CGI Hello!</title>"

           "<h1>CGI Hello!</h1>"
           "Request number %d running on host <i>%s</i>\n",
           ++count, getenv("SERVER_NAME"));
}
```

The key features of this tiny CGI program are:

*   The program sends data to the Web server by writing to <tt>stdout</tt>, using <tt>printf</tt> in this example. The CGI program first sends a <tt>Content-type</tt> header, then a small HTML document. The program includes <tt>stdio.h</tt> in order to get access to the <tt>printf</tt> function.
*   The program obtains parameters provided by the Web server by reading environment variables. The CGI program reads the <tt>SERVER_NAME</tt> variable using <tt>getenv</tt> and includes the value in the HTML document. The program includes <tt>stdlib.h</tt> in order to get access to the <tt>getenv</tt> function.

The <tt>count</tt> variable is degenerate in this example; the CGI program runs a single request, so the request number is always one. This variable will be more interesting in the FastCGI example.

<a name="S3.1.1">The</a> corresponding FastCGI program is <tt>examples/tiny-fcgi.c</tt>:

```
#include "fcgi_stdio.h"
#include <stdlib.h>

void main(void)
{
    int count = 0;
    while(FCGI_Accept() >= 0)
        printf("Content-type: text/html\r\n"
               "\r\n"

               "<title>FastCGI Hello!</title>"
               "<h1>FastCGI Hello!</h1>"
               "Request number %d running on host <i>%s</i>\n",
                ++count, getenv("SERVER_NAME"));
}
```

The key features of this tiny FastCGI program are:

*   The program is structured as a loop that begins by calling the function <tt>FCGI_Accept</tt>. The <tt>FCGI_Accept</tt> function blocks until a new request arrives for the program to execute. The program includes <tt>fcgi_stdio.h</tt> in order to get access to the <tt>FCGI_Accept</tt> function.
*   Within the loop, <tt>FCGI_Accept</tt> creates a CGI-compatible world. <tt>printf</tt> and <tt>getenv</tt> operate just as in the CGI program. <tt>stdin</tt> and <tt>stderr</tt>, not used by this tiny program, also operate just as in a CGI program.

The <tt>count</tt> variable increments each time through the loop, so the program displays a new request number each time. You can use the reload button in your browser to demonstrate this, once you've got the program built and running.

#### Building the program

If you can build <tt>examples/tiny-cgi.c</tt>, it will be straightforward for you to build <tt>examples/tiny-fcgi.c</tt>. You need to:

*   Add the directory containing the <tt>fcgi_stdio.h</tt> header to the compiler's include search path. The kit calls this directory <tt>include</tt>.
*   Add the library <tt>libfcgi.a</tt> to the linker's command line so that it will be searched when linking. The <tt>libfcgi.a</tt> library implements the functions defined in <tt>fcgi_stdio.h</tt>. The kit calls the directory containing this library <tt>libfcgi</tt>.
*   Determine whether or not the linker on your platform searches the Berkeley socket library by default, and if not, add linker directives to force this search.

See <tt>examples/Makefile</tt> (created by <tt>configure</tt>) for a Makefile that builds both programs. Autoconf handles the platform-dependent linking issues; to see how, examine <tt>configure.in</tt> and <tt>examples/Makefile.in</tt>.

#### Running the program

[Section 4](#S4) is all about how to run FastCGI applications.

You can use CGI to run application binaries built with the <tt>fcgi_stdio</tt> library. The <tt>FCGI_Accept</tt> function tests its environment to determine how the application was invoked. If it was invoked as a CGI program, the first call to FCGI_Accept is essentially a no-op and the second call returns <tt>-1</tt>. In effect, the request loop disappears.

Of course, when a FastCGI application is run using CGI it does not get the benefits of FastCGI. For instance, the application exits after servicing a single request, so it cannot maintain cached information.

#### Implementation details

<tt>fcgi_stdio.h</tt> works by first including <tt>stdio.h</tt>, then defining macros to replace essentially all of the types and procedures defined in <tt>stdio.h</tt>. (<tt>stdio.h</tt> defines a few procedures that have nothing to do with <tt>FILE *</tt>, such as <tt>sprintf</tt> and <tt>sscanf</tt>; <tt>fcgi_stdio.h</tt> doesn't replace these.) For instance, <tt>FILE</tt> becomes <tt>FCGI_FILE</tt> and <tt>printf</tt> becomes <tt>FCGI_printf</tt>. You'll only see these new names if you read <tt>fcgi_stdio.h</tt> or examine your C source code after preprocessing.

Here are some consequences of this implementation technique:

*   On some platforms the implementation will break if you include <tt>stdio.h</tt> after including <tt>fcgi_stdio.h</tt>, because <tt>stdio.h</tt> often defines macros for functions such as <tt>getc</tt> and <tt>putc</tt>. Fortunately, on most platforms <tt>stdio.h</tt> is protected against multiple includes by lines near the top of the file that look like

```
#ifndef _STDIO_H
#define _STDIO_H
```

The specific symbol used for multiple-include protection, `_STDIO_H` in this example, varies from platform to platform. As long as your platform protects `stdio.h` against multiple includes, you can forget about this issue.

*   If your application passes <tt>FILE *</tt> to functions implemented in libraries for which you have source code, then you'll want to recompile these libraries with <tt>fcgi_stdio.h</tt> included. Most C compilers provide a command-line option for including headers in a program being compiled; using such a compiler feature allows you to rebuild your libraries without making source changes. For instance the gcc command line

```
# gcc -include /usr/local/include/fcgi_stdio.h wonderlib.c
```

causes gcc to include `fcgi_stdio.h` before it even begins to read the module `wonderlib.c`.

*   If your application passes <tt>FILE *</tt> to functions implemented in libraries for which you do not have source code, then you'll need to include the headers for these libraries _before_ you include <tt>fcgi_stdio.h</tt>. You can't pass the <tt>stdin</tt>, <tt>stdout</tt>, or <tt>stderr</tt> streams produced by <tt>FCGI_Accept</tt> to any functions implemented by these libraries. You can pass a stream on a Unix file to a library function by following this pattern:

```
FILE *myStream = fopen(path, "r");
answer = MungeStream(FCGI_ToFile(myStream));
```

Here <tt>MungeStream</tt> is a library function that you can't recompile and <tt>FCGI_ToFile</tt> is a macro that converts from <tt>FCGI_FILE *</tt> to <tt>FILE *</tt>. The macro <tt>FCGI_ToFile</tt> is defined in <tt>fcgi_stdio.h</tt>.

#### Converting CGI programs

The main task in converting a CGI program into a FastCGI program is separating the code that needs to execute once, initializing the program, from the code that needs to run for each request. In our tiny example, initializing the <tt>count</tt> variable is outside the loop, while incrementing the <tt>count</tt> variable goes inside.

Retained application state may be an issue. You must ensure that any application state created in processing one request has no unintended effects on later requests. FastCGI offers the possibility of significant application performance improvements, through caching; it is up to you to make the caches work correctly.

Storage leaks may be an issue. Many CGI programs don't worry about storage leaks because the programs don't run for long enough for bloating to be a problem. When converting to FastCGI, you can either use a tool such as [_Purify_](http://www.pure.com/) from Pure Software to discover and fix storage leaks, or you can run a C garbage collector such as [_Great Circle_](http://www.geodesic.com/) from Geodesic Systems.

#### Limitations

Currently there are some limits to the compatibility provided by the <tt>fcgi_stdio</tt> library:

*   The library does not provide FastCGI versions of the functions <tt>fscanf</tt> and <tt>scanf</tt>. If you wish to apply <tt>fscanf</tt> or <tt>scanf</tt> to <tt>stdin</tt> of a FastCGI program, the workaround is to read lines or other natural units into memory and then call <tt>sscanf</tt>. If you wish to apply <tt>fscanf</tt> to a stream on a Unix file, the workaround is to follow the pattern:

```
FILE *myStream = fopen(path, "r");
count = fscanf(FCGI_ToFile(myStream), format, ...);
```

#### Reference documentation

The [<tt>FCGI_Accept</tt> manpage](https://raw.githubusercontent.com/FastCGI-Backups/fcgi2/master/doc/FCGI_Accept.3), <tt>doc/FCGI_Accept.3</tt>, describes the function in the traditional format.

The [<tt>FCGI_Finish</tt>](https://raw.githubusercontent.com/FastCGI-Backups/fcgi2/master/doc/FCGI_Finish.3) (<tt>doc/FCGI_Finish.3</tt>), [<tt>FCGI_SetExitStatus</tt>](https://raw.githubusercontent.com/FastCGI-Backups/fcgi2/master/doc/FCGI_SetExitStatus.3) (<tt>doc/FCGI_SetExitStatus.3</tt>), and [<tt>FCGI_StartFilterData</tt>](https://raw.githubusercontent.com/FastCGI-Backups/fcgi2/master/doc/FCGI_StartFilterData.3) (<tt>doc/FCGI_StartFilterData.3</tt>) manpages document capabilities of the <tt>fcgi-stdio</tt> library that are not illustrated above.

#### <a name="S3.2">3.2 Using the <tt>fcgiapp</tt> library</a>

The <tt>fcgiapp</tt> library is a second C library for FastCGI. It does not provide the high degree of source code compatibility provided by <tt>fcgi_stdio</tt>; in return, it does not make such heavy use of <tt>#define</tt>. <tt>fcgi_stdio</tt> is implemented as a thin layer on top of <tt>fcgiapp</tt>.

Applications built using the <tt>fcgiapp</tt> library cannot run as CGI programs; that feature is provided at the <tt>fcgi_stdio</tt> level.

Functions defined in <tt>fcgiapp</tt> are named using the prefix <tt>FCGX_</tt> rather than <tt>FCGI_</tt>. For instance, <tt>FCGX_Accept</tt> is the <tt>fcgiapp</tt> version of <tt>FCGI_Accept</tt>.

Documentation of the <tt>fcgiapp</tt> library takes the form of extensive comments in the header file <tt>include/fcgiapp.h</tt>. The sample programs <tt>examples/tiny-fcgi2.c</tt> and <tt>examples/echo2.c</tt> illustrate how to use <tt>fcgiapp</tt>.

#### <a name="S3.3">3.3 Using Perl and Tcl</a>

A major advantage of the FastCGI approach to high-performance Web applications is its language-neutrality. CGI scripts written in popular languages such as Perl and Tcl can be evolved into high-performance FastCGI applications.

We have produced FastCGI-integrated Perl and Tcl interpreters. Doing so was easy, since Perl and Tcl are conventional C applications and <tt>fcgi_stdio</tt> was designed for converting conventional C applications. Essentially no source code changes were required in these programs; a small amount of code was added in order to make <tt>FCGI_Accept</tt> and other FastCGI primitives available in these languages. And because these interpreters were developed using <tt>fcgi_stdio</tt>, they run standard Perl and Tcl applications (e.g. CGI scripts) as well as FastCGI applications.

See the [fastcgi-archives.github.io](https://fastcgi-archives.github.io/) Web page for more information about the Perl and Tcl libraries.

Here are the Perl and Tcl versions of <tt>tiny-fcgi</tt>:

```
#!./perl
use FCGI;
$count = 0;
while(FCGI::accept() >= 0) {
    print("Content-type: text/html\r\n\r\n",
          "<title>FastCGI Hello! (Perl)</title>\n",
          "<h1>FastCGI Hello! (Perl)</h1>\n";
          "Request number ",  ++$count,
          " running on host <i>";$env(SERVER_NAME)</i>");
}
```

```
#!./tclsh
set count 0 
while {[FCGI_Accept] >= 0 } {
    incr count
    puts -nonewline "Content-type: text/html\r\n\r\n"
    puts "<title>FastCGI Hello! (Tcl)</title>"
    puts "<h1>FastCGI Hello! (Tcl)</h1>"

    puts "Request number $count running on host <i>$env(SERVER_NAME)</i>"
}
```

Converting a Perl or Tcl CGI application to FastCGI is not fundamentally different from converting a C CGI application to FastCGI. You separate the portion of the application that performs one-time initialization from the portion that performs per-request processing. You put the per-request processing into a loop controlled by <tt>FCGI::accept</tt> (Perl) or <tt>FCGI_Accept</tt> (Tcl).

#### <a name="S3.4">3.4 Using Java</a>

Java is not just for browser-based applets. It is already suitable for writing some Web server applications, and its range of applicability will only grow as Java compilers and other Java tools improve. Java's modules, garbage collection, and threads are especially valuable for writing long-lived application servers.

The <tt>FCGIInterface</tt> class provides facilities for Java applications analogous to what <tt>fcgi_stdio</tt> provides for C applications. Using this library your Java application can run using either CGI or FastCGI.

The kit includes separate companion document on [using FastCGI with Java](https://htmlpreview.github.io/?https://github.com/FastCGI-Archives/fcgi2/blob/master/doc/fcgi-java.htm). The source code for FastCGI classes is contained in directory <tt>java/src</tt> and the compiled code in <tt>java/classes</tt>.

Here is the Java version of <tt>tiny-fcgi</tt>:

```
import FCGIInterface;

class TinyFCGI { 
    public static void main (String args[]) {  
        int count = 0;
        while(new FCGIInterface().FCGIaccept()>= 0) {
            count ++;
            System.out.println("Content-type: text/html\r\n\r\n");
            System.out.println(
                    "<title>FastCGI Hello! (Java)</title>");
            System.out.println("<h1>FastCGI Hello! (Java)</h1>");
            System.out.println(
                    "request number " + count + " running on host <i>" +
                    System.getProperty("SERVER_NAME") + "</i>");
        }
    }
}
```

### <a name="S4">4\. Running applications</a>

### <a name="S4.1">4.1 Using a Web server that supports FastCGI</a>

For a current listing of Web servers that support FastCGI, see the [fastcgi-archives.github.io](https://fastcgi-archives.github.io/) Web page.

Some of the Web servers that support FastCGI perform management of FastCGI applications. You don't need to start and stop FastCGI applications; the Web server takes care of this. If an application process should crash, the Web server restarts it.

Web servers support FastCGI via new configuration directives. Since these directives are server-specific, get more information from the documentation that accompanies each server.

### <a name="S4.2">4.2 Using <tt>cgi-fcgi</tt> with any Web server</a>

The program <tt>cgi-fcgi</tt> allows you to run FastCGI applications using any Web server that supports CGI.

Here is how <tt>cgi-fcgi</tt> works. <tt>cgi-fcgi</tt> is a standard CGI program that uses Unix domain or TCP/IP sockets to communicate with a FastCGI application. <tt>cgi-fcgi</tt> takes the path name or host/port name of a listening socket as a parameter and <tt>connect</tt>s to the FastCGI application listening on that socket. <tt>cgi-fcgi</tt> then forwards the CGI environment variables and <tt>stdin</tt> data to the FastCGI application, and forwards the <tt>stdout</tt> and <tt>stderr</tt> data from the FastCGI application to the Web server. When the FastCGI application signals the end of its response, <tt>cgi-fcgi</tt> flushes its buffers and exits.

Obviously, having <tt>cgi-fcgi</tt> is not as good as having a server with integrated FastCGI support:

*   Communication is slower than with a Web server that avoids the fork/exec overhead on every FastCGI request.
*   <tt>cgi-fcgi</tt> does not perform application management, so you need to provide this yourself.
*   <tt>cgi-fcgi</tt> supports only the Responder role.

But <tt>cgi-fcgi</tt> does allow you to develop applications that retain state in memory between connections, which often provides a major performance boost over normal CGI. And all the applications you develop using <tt>cgi-fcgi</tt> will work with Web servers that have integrated support for FastCGI.

The file <tt>examples/tiny-fcgi.cgi</tt> demonstrates a way to use <tt>cgi-fcgi</tt> to run a typical application, in this case the <tt>examples/tiny-fcgi</tt> application:

```
#!../cgi-fcgi/cgi-fcgi -f -connect sockets/tiny-fcgi tiny-fcgi
```

On most Unix platforms, executing this command-interpreter file runs <tt>cgi-fcgi</tt> with arguments <tt>-f</tt> and <tt>examples/tiny-fcgi.cgi</tt>. (Beware: On some Unix platforms, including HP-UX, the first line of a command-interpreter file cannot contain more than 32 characters, including the newline; you may need to install the <tt>cgi-fcgi</tt> application in a standard place like <tt>/usr/local/bin</tt> or create a symbolic link to the <tt>cgi-fcgi</tt> application in the directory containing your application.) The <tt>cgi-fcgi</tt> program reads the command-interpreter file and connects to the FastCGI application whose listening socket is <tt>examples/sockets/tiny-fcgi</tt>.

Continuing the example, if <tt>cgi-fcgi</tt>'s connection attempt fails, it creates a new process running the program <tt>examples/tiny-fcgi</tt> and listening on socket <tt>examples/sockets/tiny-fcgi</tt>. Then <tt>cgi-fcgi</tt> retries the connection attempt, which now should succeed.

The <tt>cgi-fcgi</tt> program has two other modes of operation. In one mode it connects to applications but does not start them; in the other it starts applications but does not connect to them. These modes are required when using TCP/IP. The [<tt>cgi-fcgi</tt> manpage](https://raw.githubusercontent.com/FastCGI-Backups/fcgi2/master/doc/cgi-fcgi.1), <tt>doc/cgi-fcgi.1</tt>, tells the full story.

To run the example applications using <tt>cgi-fcgi</tt>, start your Web server and give it the directory <tt>fcgi-devel-kit</tt> as the root of its URL space. If the machine running your server is called <tt>bowser</tt> and your server is running on port <tt>8888</tt>, you'd then open the URL <tt>http://bowser:8888/index.html</tt> to reach the kit's index page. Now the links on the index page that run example applications via <tt>cgi-fcgi</tt> should be active.

### <a name="S5">5\. Known problems</a>

On Digital UNIX 3.0 there's a problem with Unix domain listening sockets on NFS file systems. The symptom when using cgi-fcgi is an exit status of 38 (<tt>ENOTSOCK</tt>: socket operation on non-socket), but cgi-fcgi may dump core in this case when compiled optimized. Work-around: Store your Unix domain listening sockets on a non NFS file system, upgrade to Digital UNIX 3.2, or use TCP sockets.

On AIX there's a problem with shared listening sockets. The symptoms can include application core dumps and kernel panic. Work-around: Run a single FastCGI application server per listening socket.

### <a name="S6">6\. Getting support</a>

The mailing list <tt>fastcgi-developers</tt> is used for discussions of issues in developing FastCGI applications. Topics include announcement of FastCGI-capable Web servers or changes to such servers, announcement of new application libraries or changes to such libraries, announcement of known bugs, discussion of design trade-offs in FastCGI application programming, and discussion of development plans and experiences. To join the list, see [http://fastcgi.com/fastcgi-developers](http://fastcgi.com/fastcgi-developers).

A link to a mail archive can be found on the FastCGI home page, [fastcgi-archives.github.io](https://fastcgi-archives.github.io/)

* * *

**© Copyright 1996, Open Market, Inc. / mbrown@openmarket.com**
