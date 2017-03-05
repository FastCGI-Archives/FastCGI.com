*   [FastCGI: incomplete headers (d bytes) received from server "s"](#incomplete_headers)
*   [Why is Windows reporting that it is unable to locate a DLL?](#windows_dll)
*   [How do I use fork or exec?](#fork)
*   [How should I handle signals?](#signals)

* * *

*   <a name="incomplete_headers">FastCGI: incomplete headers (d bytes) received from server "s"</a>  

    The FastCGI application, s, did not terminate the headers properly. A total of d bytes were recieved.

    Headers are terminated by an empty line, e.g.

    <pre>    printf("Content-type: text/html\r\nStatus: 200 OK\r\n\r\n");
    </pre>

    See the [CGI specification](https://www.w3.org/CGI/) for more information.

*   <a name="windows_dll">Why is Windows reporting that it is unable to locate a DLL?</a>  

    Windows first searches the set of pre-installed DLLs such as the performance library (KERNEL32.DLL) and the security library (USER32.DLL). It then searches for the DLLs in the following sequence:

    1.  The directory where the executable module for the current process is located.
    2.  The current directory.
    3.  The Windows system directory. The GetSystemDirectory function retrieves the path of this directory.
    4.  The Windows directory. The GetWindowsDirectory function retrieves the path of this directory.
    5.  The directories listed in the PATH environment variable.

    Note that the LIBPATH environment variable is not used.

    mod_fastcgi, by default, clears the environment of FastCGI applications it starts (with the exception of SystemRoot). To pass or set an environment variable to a FastCGI application use the -initial-env argument to FastCgiConfig or FastCgiServer.

*   <a name="fork">How do I use fork or exec?</a>

    When a request handle object is destroyed that has accepted a connection without finishing it, the connection will automatically be finished. Usually, this is what you want, although it is preferable to explicitly call the Finish() method.

    When you fork, however, without calling exec as well, i.e. when you have two instance of perl running, the request handle object will (eventually) be destroyed in both instances of perl. As a result, a possible request being handled will be finished when the object is destroyed for the first time. This is probably not what you expect, since you will usually only be handling the request in either the parent or the child. To inhibit this unwanted request finishing, you can send the Detach() message to the request handle object. In a detached state, destruction will not lead to any finishing of requests. It is advised you call Detach() before forking and Attach afterwards (in the process that will continue handling the request).

    Before doing this though, please think about whether or not you really need to fork inside the accept loop. Since the FastCGI paradigm is different from the normal CGI one, you'll find that there are situations where you would fork in a CGI context, whereas it may not be necessary in a FastCGI context. In other cases, you're better off doing the forking before the accept loop.

    Conversely, when you call exec without forking, the object will not be destroyed and no connection will automatically be finished, so in that case you are forced to do it yourself.

    <pre>#!/usr/bin/perl
    use strict;
    use warnings;

    use FCGI;

    my $request = FCGI::Request();

    while ($request->Accept() >= 0) {
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

        # continue processing request

        $request->Finish();
    }
    </pre>

*   <a name="signals">How should I handle signals?</a>

    All FastCGI applications should handle PIPE and TERM , mod_fastcgi spawned applications should also handle USR1.

    PIPE occurs when trying to write/print to a file descriptor that has been closed. Under mod_fastcgi, if a client aborts a connection before it completes mod_fastcgi does too. At a minimum, SIGPIPE should be ignored (this is already setup in applications spawned by mod_fastcgi). Ideally, it should result in an early abort of the request handling within your application and a return to the top of the FastCGI accept() loop.

    USR1 may be received by FastCGI applications spawned by mod_fastcgi. Apache uses this signal to request a "graceful" process shutdown (e.g. its used by "apachectl restart"). When mod_fastcgi's Process Manager receives USR1 it sends TERM to all of the FastCGI applications it spawned and then exits (its gets restarted by Apache). This means that, under Apache/mod_fastcgi, a FastCGI application that receives USR1 from Apache will also receive TERM from the process manager. FastCGI applications expected to be run under the control of mod_fastcgi/Apache should handle USR1 by finishing any request in process and then shutting down.

    TERM is the standard signal sent to applications to request shutdown. Typically, this is considered a request for "clean" shutdown, i.e. finish anything your in the middle of (within reason), free resources such as database connections, and exit. When Apache receives TERM, it does not finish handling requests in progress. Whether or not you finish any request in process when TERM is received is your decision, but keep in mind that under mod_fastcgi/Apache the TERM may be a "graceful" request in disguise. I always finish any request in process before exiting.

    Handling signals can be tricky. Consult the documentation for your language and system for restrictions and idiosyncrasies. In general, its always best to do as little as possible from within a signal handler.
