<a name="PerlSignals">How do I handle signals in Perl?</a> There is a problem when Apache httpd terminates. Apache will send a USR1 or TERM signal. The Perl 5.8 (with safe signal handling) FastCGI application receives the signal, but defers the signal till the next op-code break. Apache then exits. The FastCGI application then continues waiting for a request that will never come. If such a request could come, then the signal would be handled after the system call. However, since a request can never come the FastCGI application hangs. The closest, but maybe not the best solution I found was to set this ENV var. FastCgiConfig -initial-env PERL_SIGNALS=unsafe This allows the signals to be processed immediately. Here's an example that ignores SIGPIPE:

```
#!/usr/local/bin/perl
use strict;
use warnings;

use FCGI;

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
#!/usr/local/bin/perl
use strict;
use warnings;

use FCGI;

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

<a name="Perlfork">How do I use fork or exec ?</a>

When a request handle object is destroyed that has accepted a connection without finishing it, the connection will automatically be finished. Usually, this is what you want, although it is preferable to explicitly call the Finish() method. When you fork, however, without calling exec as well, i.e. when you have two instance of perl running, the request handle object will (eventually) be destroyed in _both_ instances of perl. As a result, a possible request being handled will be finished when the object is destroyed for the first time. This is probably not what you expect, since you will usually only be handling the request in either the parent or the child. To inhibit this unwanted request finishing, you can send the Detach() message to the request handle object. In a detached state, destruction will not lead to any finishing of requests. It is advised you call Detach() before forking and Attach afterwards (in the process that will continue handling the request).

Before doing this though, please think about whether or not you really need to fork inside the accept loop. Since the FastCGI paradigm is different from the normal CGI one, you'll find that there are situations where you would fork in a CGI context, whereas it may not be necessary in a FastCGI context. In other cases, you're better off doing the forking before the accept loop.

Conversely, when you call exec without forking, the object will not be destroyed and no connection will automatically be finished, so in that case you are forced to do it yourself.

```
#!/usr/bin/perl 
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
```

<a name="perl_application_reload"></a>How can I get my application to reload when a new version is available? Mod_perl has Apache::Reload, and Apache::StatINC. Is there a similar mechanism for FastCGI? Assuming the application will automatically be restarted by mod_fastcgi (or another process manager), putting something like this at the end of your request loop should do it.

```
 
while ( $request->Accept() >= 0) {
    # handle request

    request->Finish();
    exit if -M $ENV{SCRIPT_FILENAME} < 0; # Autorestart

}
```
