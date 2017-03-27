![[APACHE FEATHER BANNER]](http://httpd.apache.org/docs/images/sub.gif)

# Module mod_fastcgi

This 3<sup>rd</sup> party module provides support for the FastCGI protocol. FastCGI is a language independent, scalable, open extension to CGI that provides high performance and persistence without the limitations of server specific APIs.

FastCGI applications are not limited to a particular development language (the protocol is open). FastCGI application libraries currently exist for Perl, C/C++, Java, Python, TCL, SmallEiffel, and Smalltalk.

FastCGI applications use TCP or Unix sockets to communicate with the web server. This scalable architecture allows applications to run on the same platform as the web server or on many machines scattered across an enterprise network.

FastCGI applications are portable to other web server platforms. FastCGI is supported either directly or through commercial extensions by most popular web servers.

FastCGI applications are fast because they're persistent. There is no per-request startup and initialization overhead. This makes possible the development of applications which would otherwise be impractical within the CGI paradigm (e.g. a huge Perl script, or an application which requires a connection to one or more databases).

See the FastCGI [website](http://www.fastcgi.com/) for more information. To receive FastCGI related announcements and notifications of software updates, subscribe to [fastcgi-announce](http://fastcgi.com/fastcgi-announce). To participate in the discussion of `mod_fastcgi` and FastCGI application development, subscribe to [fastcgi-developers](http://fastcgi.com/fastcgi-developers).

## Summary

For information about building and installing the module, see the INSTALL document that came with the distribution.

FastCGI applications under `mod_fastcgi` are defined as one of three types: static, dynamic, or external. They're configured using the [FastCgiServer](#fastcgiserver), [FastCgiConfig](#FastCgiConfig), and [FastCgiExternalServer](#FastCgiExternalServer) [directives](#directives) respectively. Any URI that Apache identifies as a FastCGI application and which hasn't been explicitly configured using a [FastCgiServer](#fastcgiserver) or [FastCgiExternalServer](#FastCgiExternalServer) directive is handled as a dynamic application (see the [FastCgiConfig](#FastCgiConfig) directive for more information).

FastCGI static and dynamic applications are spawned and managed by the FastCGI Process Manager, fcgi-pm. The process manager is spawned by Apache at server initialization. External applications are presumed to be started and managed independently.

Apache must be configured to identify requests for FastCGI URIs. `mod_fastcgi` registers (with Apache) a handler type of `fastcgi-script` for this purpose.

To configure Apache to handle all files (within the scope of the directive) as FastCGI applications (e.g. for a fcgi-bin directory):

> [SetHandler](http://httpd.apache.org/docs/mod/mod_mime.html#sethandler) fastcgi-script

To configure Apache to handle files (within the scope of the directive) with the specified extension(s) as FastCGI applications:

> [AddHandler](http://httpd.apache.org/docs/mod/mod_mime.html#addhandler) fastcgi-script fcg fcgi fpl

Consult the Apache documentation for more information regarding these and other directives which affect request handling (such as [Action](http://httpd.apache.org/docs/mod/mod_actions.html#action)).

Dynamic FastCGI applications require the `ExecCGI` option be enabled (see the [`Options`](http://httpd.apache.org/docs/mod/core.html#options) directive) in the application's directory.

## Notes

`mod_fastcgi` logs FastCGI application error (stderr) output to the server log associated with the request. Errors reported by the FastCGI process manager, fcgi-pm, are reported to the main server log (typically, logs/error_log). Data written to stdout or stderr before entering the FastCGI _accept_ loop or via a mechanism that is not FastCGI protocol aware will also be directed to the main server log. If Apache's [`LogLevel`](http://httpd.apache.org/docs/mod/core.html#loglevel) is set to `info` additional informational messages are printed to the logs, these messages may be especially helpful while debugging a configuration.

Under Unix, expect your FastCGI application to see SIGPIPE, SIGUSR1, and SIGTERM. The latest FastCGI C, C++ and Perl application library installs default handlers if none are installed by the application. If an http client aborts a request before it completes, mod_fastcgi does too - this results in a SIGPIPE to the FastCGI application. At a minimum, SIGPIPE should be ignored (applications spawned by mod_fastcgi have this setup automatically). Ideally, it should result in an early abort of the request handling within your application and a return to the top of the FastCGI accept() loop. Apache uses SIGUSR1 to request a "graceful" process restart/shutdown. It is sent to Apache's process group (which includes applications spawned by mod_fastcgi). Ideally, it should result in a FastCGI application finishing the current request, if any, and then an exit. The mod_fastcgi process manager isn't particularly patient though (there's room for improvement here) and since it has to shutdown too, sends a SIGTERM to all of the FastCGI applications it is responsible for. Apache will restart the process manager and it will restart its managed applications (as if the server was just started). SIGTERM is, well, SIGTERM - your application should exit quickly.

Under Windows, there are no signals. A shutdown event is used instead. This is setup by mod_fastcgi and honored by the latest version of the C, C++, and Perl application library. If your using a library which doesn't support this, your application will not get shutdown during an Apache restart/shutdown (there's room for improvement here).

To pass per-request environment variables to FastCGI applications, have a look at: [`mod_env`](http://httpd.apache.org/docs/mod/mod_env.html) (`SetEnv`, `PassEnv`, `UnSetEnv`), [`mod_setenvif`](http://httpd.apache.org/docs/mod/mod_setenvif.html) (`BrowserMatch`, `BrowserMatchNoCase`, `SetEnvIf`, `SetEnvIfNoCase`), and [`mod_rewrite`](http://httpd.apache.org/docs/mod/mod_rewrite.html) (if you're feeling adventurous).

FastCGI application output is buffered by default. This is not the case for CGI scripts (under Apache 1.3). To override the default behavior, use the `-flush` option (not available for dynamic applications).

Redirects are handled similarly to CGI. Location headers with values that begin with "/" are treated as internal-redirects; otherwise, they are treated as external redirects (302).

Session affinity (as well as distribution) should be achievable outside of `mod_fastcgi` using [`mod_rewrite`](http://httpd.apache.org/docs/mod/mod_rewrite.html). If you get this working, please post the details to [fastcgi-developers@fastcgi.com](mailto:fastcgi-developers@fastcgi.com) so they can be included here.

## FastCGI Specification Compliance

The FastCGI specification is not implemented in its entirety and I've deviated a bit as well resulting in some Apache specific features.

The file descriptors for stdout and stderr are left open. This is prohibited by the specification. I can't see any reason to require that they be closed, and leaving them open prevents FastCGI applications which were not completely ported to FastCGI from failing miserably. This does not mean the applications shouldn't be fixed such that this doesn't occur, but is invaluable when using a 3<sup>rd</sup> party library (without source code) which expects to be able to write to stderr. Anything written to stdout or stderr in this manner will be directed to the main server log.

The Filter and Log Roles are not supported. The Filter Role has little value in Apache until the output of one handler can be piped into another (Apache 2.0 is expected to support this). The Log Role has some value, but Apache's "piped logs" feature is similar (and is even more CPU friendly).

The FastCGI protocol supports a feature, described in the specificiation as "multiplexing", that allows a single client-server connection to be simultaneously shared by multiple requests. This is not supported. This does *not* prevent FastCGI applications from supporting multiple simultaneous requests over independent connections. Of course, the application has to be specifically designed to do so by using a threaded or select/poll based server model.

The Authorizer Role has three variations corresponding to three specific Apache request handling phases:  Authentication, Authorization, and Access Control. `mod_fastcgi` sets up the (Apache specific) environment variable "FCGI_APACHE_ROLE" to indicate which Apache authorizer phase is being performed.

Authorizers under `mod_fastcgi` are sent nearly all of the standard environment variables typically available to CGI/FastCGI request handlers including some explicitly precluded by the FastCGI specification (for authorizers); I didn't see the point in leaving them out. All headers returned by a FastCGI Authorizer in a successful response (Status: 200) are passed to sub-processes (CGI/FastCGI invocations) as environment variables rather than just those prefixed by `Variable-` as the FastCGI specification calls for; I didn't see the point in leaving them out either. FastCGI specification compliant authorizer behavior can be obtained by using the `-compat` option to the Auth server directives.

Custom failure responses from FastCGI authorizer applications are not supported (speak up if you need this). See the [ErrorDocument](http://httpd.apache.org/docs/mod/core.html#errordocument) directive for a workaround (a CGI/FastCGI application can serve the error document).

## <a name="directives">Directives</a>

*   [FastCgiServer](#FastCgiServer)
*   [FastCgiConfig](#FastCgiConfig)
*   [FastCgiExternalServer](#FastCgiExternalServer)
*   [FastCgiIpcDir](#FastCgiIpcDir)
*   [FastCgiWrapper](#FastCgiWrapper)
*   [FastCgiAuthenticator](#FastCgiAuthenticator)
*   [FastCgiAuthenticatorAuthoritative](#FastCgiAuthenticatorAuthoritative)
*   [FastCgiAuthorizer](#FastCgiAuthorizer)
*   [FastCgiAuthorizerAuthoritative](#FastCgiAuthorizerAuthoritative)
*   [FastCgiAccessChecker](#FastCgiAccessChecker)
*   [FastCgiAccessCheckerAuthoritative](#FastCgiAccessCheckerAuthoritative)

* * *

## <a name="FastCgiServer">FastCgiServer</a>

| | |
|  --- | --- |
|**[Syntax:](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)**|FastCgiServer _filename_ _[option ...]_|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|server config, virtual host|

The `FastCgiServer` directive defines _filename_ as a static FastCGI application. If the filename does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot).

By default, the Process Manager will start one instance of the application with the default configuration specified (in parentheses) below. Should a static application instance die for any reason `mod_fastcgi` will spawn another to replace it and log the event (at the `warn` [`LogLevel`).](http://httpd.apache.org/docs/mod/core.html#loglevel)

**Note:** Using `FastCgiServer` within a [VirtualHost](http://httpd.apache.org/docs/mod/core.html#virtualhost) does not necessarily limited access to that host. If _filename_ is accessible via other virtual hosts, they too can leverage the same definition.

_Option_ can be one of (case insensitive):

<dl>

<dt>-appConnTimeout _n_ (0 seconds)</dt>

<dd>**Unix: ** The number of seconds to wait for a connection to the FastCGI application to complete or 0 to indicate a blocking `connect()` should be used. Blocking `connect()`s have an OS dependent internal timeout`.` If the timeout expires, a SERVER_ERROR results. For non-zero values, this is the amount of time used in a `select()` to write to the file descriptor returned by a non-blocking `connect().` Non-blocking `connect()`s are troublesome on many platforms. See also `-idle-timeout`, it produces similar results but in a more portable manner.  
**Windows NT: ** TCP based applications work as above. Named pipe based applications (static applications configured without the `-port` option and dynamic applications) use this value successfully to limit the amount of time to wait for a connection (i.e. it's not "troublesome"). By default, this is 90 seconds (FCGI_NAMED_PIPE_CONNECT_TIMEOUT in mod_fastcgi.h).</dd>

<dt>-group _groupname|#gid_ (none)</dt>

<dd>**Unix (only):** When [FastCgiWrapper](#FastCgiWrapper) is in use, the group is used to invoke the wrapper. The `-group` option must be used together with `-user`.</dd>

<dt>-idle-timeout _n_ (30 seconds)</dt>

<dd>The number of seconds of FastCGI application inactivity allowed before the request is aborted and the event is logged (at the `error` [`LogLevel`](http://httpd.apache.org/docs/mod/core.html#loglevel)). The inactivity timer applies only as long as a connection is pending with the FastCGI application. If a request is queued to an application, but the application doesn't respond (by writing and flushing) within this period, the request will be aborted. If communication is complete with the application but incomplete with the client (the response is buffered), the timeout does not apply.</dd>

<dt>-initial-env _name[=[value]]_ (none)</dt>

<dd>A name-value pair to be passed in the FastCGI application's _initial_ environment. To pass a variable from Apache's environment, don't provide the "=" (if the variable isn't actually in the environment, it will be defined without a value). To define a variable without a value, provide the "=" without any value. The option can be used repeatedly.</dd>

<dt>-init-start-delay _n_ (1 second)</dt>

<dd>The minimum number of seconds between the spawning of instances of this application. This delay decreases the demand placed on the system at server initialization.</dd>

<dt>-flush (none)</dt>

<dd>Force a write to the client as data is received from the application. By default, `mod_fastcgi` buffers data in order to free the application as quickly as possible.</dd>

<dt>-listen-queue-depth _n_ (100)</dt>

<dd>The depth of `listen()` queue (also known as the backlog) shared by all of the instances of this application. A deeper listen queue allows the server to cope with transient load fluctuations without rejecting requests; it does not increase throughput. Adding additional application instances may increase throughput/performance, depending upon the application and the host.</dd>

<dt>-min-server-life _n_ (30)</dt>

<dd>The minimum number of seconds the application must run for before its restart interval is increased to 600 seconds. The server will get 3 tries to run for at least this number of seconds.</dd>

<dt>-nph</dt>

<dd>Instructs mod_fastcgi not to parse the headers. See the Apache documentation for more information about _nph_ (non parse header) scripts.</dd>

<dt>-pass-header _header_ (none)</dt>

<dd>The name of an HTTP Request Header to be passed in the _request_ environment. This option makes available the contents of headers which are normally not available (e.g. Authorization) to a CGI environment.</dd>

<dt>-port _n_ (none)</dt>

<dd>The TCP port number (1-65535) the application will use for communication with the web server. This option makes the application accessible from other machines on the network (as well as this one). The `-socket` and `-port` options are mutually exclusive.</dd>

<dt>-priority _n_ (0)</dt>

<dd>The process priority to be assigned to the application instances (using `setpriority()`).</dd>

<dt>-processes _n_ (1)</dt>

<dd>The number of instances of the application to spawn at server initialization.</dd>

<dt>-restart-delay _n_ (5 seconds)</dt>

<dd>The minimum number of seconds between the respawning of failed instances of this application. This delay prevents a broken application from soaking up too much of the system.</dd>

<dt>-socket _filename_ (generated)</dt>

<dd>**Unix: ** The filename of the Unix domain socket that the application will use for communication with the web server. The module creates the socket within the directory specified by `[FastCgiIpcDir](#FastCgiIpcDir)`. This option makes the application accessible to other applications (e.g. `cgi-fcgi`) on the same machine or via an external FastCGI application definition (`[FastCgiExternalServer](#FastCgiExternalServer)`). If neither the `-socket` nor the `-port` options are given, the module generates a Unix domain socket filename. The `-socket` and `-port` options are mutually exclusive.</dd>

<dd>**Windows NT: ** The name of the named pipe that the application will use for communication with the web server. The module creates the named pipe under the named pipe root specified by `[FastCgiIpcDir](#FastCgiIpcDir)`. This option makes the application accessible to other applications (e.g. `cgi-fcgi`) on the same machine or via an external FastCGI application definition (`[FastCgiExternalServer](#FastCgiExternalServer)`). If neither the `-socket` nor the `-port` options are given, the module generates a name for the named pipe. The `-socket` and `-port` options are mutually exclusive.</dd>

<dt>-user _username|#uid_ (none)</dt>

<dd>**Unix (only):** When [FastCgiWrapper](#FastCgiWrapper) is in use, the user is used to invoke the wrapper. The `-user` option must be used together with `-group`.</dd>

</dl>

* * *

## <a name="FastCgiConfig">FastCgiConfig</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiConfig _option [option ...]_|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|server config|

The `FastCgiConfig` directive defines the default parameters for _all_ dynamic FastCGI applications. This directive does not affect static or external applications in any way.

Dynamic applications are not started at server initialization, but upon demand. If the demand is heavy, additional application instances are started. As the demand fades, application instances are killed off. Many of the options govern this process.

_Option_ can be one of (case insensitive):

<dl>

<dt>-appConnTimeout _n_ (0 seconds)</dt>

<dd>**Unix: ** The number of seconds to wait for a connection to the FastCGI application to complete or 0 to indicate a blocking `connect()` should be used. Blocking `connect()`s have an OS dependent internal timeout. If the timeout expires, a SERVER_ERROR results. For non-zero values, this is the amount of time used in a `select()` to write to the file descriptor returned by a non-blocking `connect()`. Non-blocking `connect()`s are troublesome on many platforms. See also `-idle-timeout`, it produces similar results but in a more portable manner.  
**Windows NT: ** TCP based applications work as above. Named pipe based applications (static applications configured without the `-port` option and dynamic applications) use this value successfully to limit the amount of time to wait for a connection (i.e. it's not "troublesome"). By default, this is 90 seconds (FCGI_NAMED_PIPE_CONNECT_TIMEOUT in mod_fastcgi.h).</dd>

<dt>-autoUpdate (none)</dt>

<dd>Causes mod_fastcgi to check the modification time of the application on disk before processing each request. If the application on disk has been changed, the process manager is notified and all running instances of the application are killed off. In general, it's preferred that this type of functionality be built-in to the application (e.g. every 100th request it checks to see if there's a newer version on disk and exits if so). There may be an outstanding problem (bug) when this option is used with `-restart`.</dd>

<dt>-flush (none)</dt>

<dd>Force a write to the client as data is received from the application. By default, `mod_fastcgi` buffers data in order to free the application as quickly as possible.</dd>

<dt>-gainValue _n_ (0.5)</dt>

<dd>A floating point value between 0 and 1 used as an exponent in the computation of the exponentially decayed connection times load factor of the currently running dynamic FastCGI applications. Old values are scaled by (`1 - gainValue`), so making it smaller weights old values more than the current value (which is scaled by `gainValue`).</dd>

<dt>-idle-timeout _n_ (30 seconds)</dt>

<dd>The number of seconds of FastCGI application inactivity allowed before the request is aborted and the event is logged (at the `error` [`LogLevel`](http://httpd.apache.org/docs/mod/core.html#loglevel)). The inactivity timer applies only as long as a connection is pending with the FastCGI application. If a request is queued to an application, but the application doesn't respond (by writing and flushing) within this period, the request will be aborted. If communication is complete with the application but incomplete with the client (the response is buffered), the timeout does not apply.</dd>

<dt>-initial-env _name[=[value]]_ (none)</dt>

<dd>A name-value pair to be passed in the initial environment when instances of applications are spawned. To pass a variable from the Apache environment, don't provide the "=" (if the variable isn't actually in the environment, it will be defined without a value). To define a variable without a value, provide the "=" without any value. The option can be used repeatedly.</dd>

<dt>-init-start-delay _n_ (1 second)</dt>

<dd>The minimum number of seconds between the spawning of instances of applications. This delay decreases the demand placed on the system at server initialization.</dd>

<dt>-killInterval _n_ (300 seconds)</dt>

<dd>Determines how often the dynamic application instance killing policy is implemented within the process manager. Smaller numbers result in a more aggressive policy, larger numbers a less aggressive policy.</dd>

<dt>-listen-queue-depth _n_ (100)</dt>

<dd>The depth of `listen()` queue (also known as the backlog) shared by all instances of applications. A deeper listen queue allows the server to cope with transient load fluctuations without rejecting requests; it does not increase throughput. Adding additional application instances may increase throughput/performance, depending upon the application and the host.</dd>

<dt>-maxClassProcesses _n_ (10)</dt>

<dd>The maximum number of dynamic FastCGI application instances allowed to run for any one FastCGI application. It must be <= to -maxProcesses (this is not programmatically enforced).</dd>

<dt>-maxProcesses _n_ (50)</dt>

<dd>The maximum total number of dynamic FastCGI application instances allowed to run at any one time. It must be >= to -maxClassProcesses (this is not programmatically enforced).</dd>

<dt>-min-server-life _n_ (30)</dt>

<dd>The minimum number of seconds a dynamic FastCGI application must run for before its restart interval is increased to 600 seconds. The server will get 3 tries to run for at least this number of seconds.</dd>

<dt>-minProcesses _n_ (5)</dt>

<dd>The minimum total number of dynamic FastCGI application instances allowed to run at any one time without being killed off by the process manager (due to lack of demand).</dd>

<dt>-multiThreshold _n_ (50)</dt>

<dd>An integer between 0 and 100 used to determine whether any one instance of a FastCGI application should be terminated. If the application has more than one instance currently running, this attribute will be used to decide whether one of them should be terminated. If only one instance remains, `singleThreshold` is used instead.  
For historic reasons the mis-spelling `multiThreshhold` is also accepted.</dd>

<dt>-pass-header _header_ (none)</dt>

<dd>The name of an HTTP Request Header to be passed in the _request_ environment. This option makes available the contents of headers which are normally not available (e.g. Authorization) to a CGI environment.</dd>

<dt>-priority _n_ (0)</dt>

<dd>The process priority to be assigned to the application instances (using `setpriority()`).</dd>

<dt>-processSlack _n_ (5)</dt>

<dd>If the sum of the number of all currently running dynamic FastCGI applications and `processSlack` exceeds `maxProcesses`, the process manager invokes the killing policy. This is to improve performance at higher loads by killing some of the most inactive application instances before reaching `maxProcesses`.</dd>

<dt>-restart (none)</dt>

<dd>Causes the process manager to restart dynamic applications upon failure (similar to static applications).</dd>

<dt>-restart-delay _n_ (5 seconds)</dt>

<dd>The minimum number of seconds between the respawning of failed instances of applications. This delay prevents a broken application from soaking up too much of the system.</dd>

<dt>-singleThreshold _n_ (0)</dt>

<dd>An integer between 0 and 100 used to determine whether the last instance of a FastCGI application can be terminated. If the process manager computed load factor for the application is lower than the specified threshold, the last instance is terminated. In order to make your executables run in the "idle" mode for the long time, you would specify a value closer to 1, however if memory or CPU time is of primary concern, a value closer to 100 would be more applicable. A value of 0 will prevent the last instance of an application from being terminated; this is the default value, changing it is not recommended (especially if `-appConnTimeout` is set).  
For historic reasons the mis-spelling `singleThreshhold` is also accepted.</dd>

<dt>-startDelay _n_ (3 seconds)</dt>

<dd>The number of seconds the web server waits patiently while trying to connect to a dynamic FastCGI application. If the interval expires, the process manager is notified with hope it will start another instance of the application. The `startDelay` must be less than `appConnTimeout` to be effective.</dd>

<dt>-updateInterval _n_ (300 seconds)</dt>

<dd>The updateInterval determines how often statistical analysis is performed to determine the fate of dynamic FastCGI applications.</dd>

</dl>

* * *

## <a name="FastCgiExternalServer">FastCgiExternalServer</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiExternalServer _filename_ -host _hostname:port [option ...]_|
| |FastCgiExternalServer _filename_ -socket _filename [option ...]_|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|server config, virtual host|

The `FastCgiExternalServer` directive defines _filename_ as an external FastCGI application. If _filename_ does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot). The _filename_ does not have to exist in the local filesystem. URIs that Apache resolves to this _filename_ will be handled by this external FastCGI application.

External FastCGI applications are not started by the process manager, they are presumed to be started and managed "external" to Apache and mod_fastcgi. The FastCGI devkit provides a simple tool, `cgi-fcgi`, for starting FastCGI applications independent of the server (applications can also be _self-starting_, see the devkit).

**Note:** Using `FastCgiServer` within a [VirtualHost](http://httpd.apache.org/docs/mod/core.html#virtualhost) does not necessarily limited access to that host. If _filename_ is accessible via other virtual hosts, they too can leverage the same definition.

_Option_ can be one of (case insensitive):

<dl>

<dt>-appConnTimeout _n_ (0 seconds)</dt>

<dd>**Unix: ** The number of seconds to wait for a connection to the FastCGI application to complete or 0 to indicate a blocking `connect()` should be used. Blocking `connect()`s have an OS dependent internal timeout. If the timeout expires, a SERVER_ERROR results. For non-zero values, this is the amount of time used in a `select()` to write to the file descriptor returned by a non-blocking `connect()`. Non-blocking `connect()`s are troublesome on many platforms. See also `-idle-timeout`, it produces similar results but in a more portable manner.  
**Windows NT: ** TCP based applications work as above. Named pipe based applications (static applications configured without the `-port` option and dynamic applications) use this value successfully to limit the amount of time to wait for a connection (i.e. it's not "troublesome"). By default, this is 90 seconds (FCGI_NAMED_PIPE_CONNECT_TIMEOUT in mod_fastcgi.h).</dd>

<dt>-group _groupname|#gid_ (none)</dt>

<dd>**Unix (only):** When [FastCgiWrapper](#FastCgiWrapper) is in use, the group is used to invoke the wrapper. The `-group` option must be used together with `-user`.</dd>

<dt>-idle-timeout _n_ (30 seconds)</dt>

<dd>The number of seconds of FastCGI application inactivity allowed before the request is aborted and the event is logged (at the `error` [`LogLevel`](http://httpd.apache.org/docs/mod/core.html#loglevel)). The inactivity timer applies only as long as a connection is pending with the FastCGI application. If a request is queued to an application, but the application doesn't respond (by writing and flushing) within this period, the request will be aborted. If communication is complete with the application but incomplete with the client (the response is buffered), the timeout does not apply.</dd>

<dt>-flush (none)</dt>

<dd>Force a write to the client as data is received from the application. By default, `mod_fastcgi` buffers data in order to free the application as quickly as possible.</dd>

<dt>-host _hostname:port_ (none)</dt>

<dd>The hostname or IP address and TCP port number (1-65535) the application uses for communication with the web server. The `-socket` and `-host` options are mutually exclusive.</dd>

<dt>-nph</dt>

<dd>Instructs mod_fastcgi not to parse the headers. See the Apache documentation for more information about _nph_ (non parse header) scripts.</dd>

<dt>-pass-header _header_ (none)</dt>

<dd>The name of an HTTP Request Header to be passed in the _request_ environment. This option makes available the contents of headers which are normally not available (e.g. Authorization) to a CGI environment.</dd>

<dt>-socket _filename_ (none)</dt>

<dd>**Unix: ** The filename of the Unix domain socket the application uses for communication with the web server. The filename is relative to the `[FastCgiIpcDir](#FastCgiIpcDir)`. The `-socket` and `-port` options are mutually exclusive.</dd>

<dd>**Windows NT: ** The name of the named pipe the application uses for communicating with the web server. the name is relative to the `[FastCgiIpcDir](#FastCgiIpcDir)`. The `-socket` and `-port` options are mutually exclusive.</dd>

<dt>-user _username|#uid_ (none)</dt>

<dd>**Unix (only):** When [FastCgiWrapper](#FastCgiWrapper) is in use, the user is used to invoke the wrapper. The `-user` option must be used together with `-group`.</dd>

</dl>

* * *

## <a name="FastCgiIpcDir">FastCgiIpcDir</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|**Unix:** FastCgiIpcDir _directory_|
| |**Windows NT:** FastCgiIpcDir _name_|
|[**Default:**](http://httpd.apache.org/docs/mod/directive-dict.html#Default)|**Unix/Apache:** FastCgiIpcDir logs/fastcgi|
| |**Unix/Apache2:** FastCgiIpcDir RUNTIMEDIR/fastcgi|
| |**Windows NT:** FastCgiIpcDir \\\\.\\pipe\\ModFastCgi\\|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|server config|

**Unix:** The `FastCgiIpcDir` directive specifies _directory_ as the place to store (and in the case of external FastCGI applications, find) the Unix socket files used for communication between the applications and the web server. If the directory does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot). If the directory doesn't exist, an attempt is made to create it with appropriate permissions. Do not specify a directory that is not on a local filesystem! If you use the default directory (or another directory within `/tmp`), `mod_fastcgi` will break if your system periodically deletes files from `/tmp`.

**Windows NT:** The `FastCgiIpcDir` directive specifies _name_ as the root for the named pipes used for communication between the application and the web server. The _name_ must be in the form of **\\\\.\\pipe\\**_pipename_ (notice that the backslashes are escaped). The _pipename_ can contain any character other than a backslash.

The `FastCgiIpcDir` directive must precede any [`FastCgiServer`](#FastCgiServer) or [`FastCgiExternalServer`](#FastCgiExternalServer) directives (which make use of Unix sockets). The directory must be readable, writeable, and executable (searchable) by the web server, but otherwise should not be accessible to anyone.

`FastCgiIpcDir` is typically used move the directory someplace more suitable (than the default) for the platform or to prevent multiple Apache instances from sharing FastCGI application instances.

* * *

## <a name="FastCgiWrapper">FastCgiWrapper</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiWrapper _On | Off | filename_|
|[**Default:**](http://httpd.apache.org/docs/mod/directive-dict.html#Default)|FastCgiWrapper Off|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|server config|


**Unix (only):** The `FastCgiWrapper` directive is used to enable support for a wrapper such as [suexec](http://httpd.apache.org/docs/suexec.html) (included with Apache in the support directory) or [cgiwrap](http://cgiwrap.sourceforge.net/). To use the same wrapper used by Apache, set `FastCgiWrapper` to _On_ (NOTE - mod_fastcgi cannot reliably determine the wrapper used by Apache when built as a DSO). The _On_ argument requires suexec be enabled in Apache (for CGI). To use a specific wrapper, specify a _filename_. If the filename does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot). The wrapper is used to invoke all FastCGI applications (in the future this directive will have directory context).

When `FastCgiWrapper` is enabled, no assumptions are made about the target application and thus presence and permissions checks cannot be made. This is the responsibility of the wrapper.

The wrapper is invoked with the following arguments: username, group, application. The username and group are determined as described below. The application is the "filename" Apache resolves the requested URI to (dynamic) or the filename provided as an argument to another FastCGI (server or authorizer) directive. These arguments may or may not be used by the wrapper (e.g. suexec uses them, cgiwrap parses the URI and ignores them). The environment passed to the wrapper is identical to the environment passed when a wrapper is not in use.

When `FastCgiWrapper` is enabled, the location of static or external FastCGI application directives can be important. Under Apache 1.3, they inherit their user and group from the `user and group` of the virtual server in which they are defined. `[User](http://httpd.apache.org/docs/mod/core.html#user)` and `[Group](http://httpd.apache.org/docs/mod/core.html#group)` directives _<u>must</u>_ precede FastCGI application definitions. Under Apache 2.0, the `-user` and `-group` options to [FastCgiServer](#FastCgiServer) and [FastCgiExternalServer](#FastCgiExternalServer) directives must be used (dynamic applications still use the virtual server's user and group).

Note that access to (use of) FastCGI applications is <u>_not_</u> limited to the virtual server in which they were defined. The application is used to service requests from any virtual server with the same user and group.

If a request is received for a FastCGI application without an existing matching definition already running with the correct user and group, a dynamic instance of the application is started with the correct user and group. This can lead to multiple copies of the same application running with different user/group. If this is a problem, preclude navigation to the application from other virtual servers or configure the virtual servers with the same User and Group.

See the Apache documentation for more information about suexec (make sure you fully understand the security implications).

* * *

## <a name="FastCgiAuthenticator">FastCgiAuthenticator</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAuthenticator _filename_ [-compat]|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

The `FastCgiAuthenticator` directive is used to define a FastCGI application as a per-directory authenticator. Authenticators verify the requestor is who he says he is by matching the provided username and password against a list or database of known users and passwords. FastCGI based authenticators are useful primarily when the user database is maintained within an existing independent program or resides on a machine other than the web server.

If the FastCGI application _filename_ does not have a corresponding static or external server definition, it is started as a dynamic FastCGI application. If the filename does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot).

`FastCgiAuthenticator` is used within [`Directory`](http://httpd.apache.org/docs/mod/core.html#directory) or [`Location`](http://httpd.apache.org/docs/mod/core.html#location) containers and must include an [`AuthType`](http://httpd.apache.org/docs/mod/core.html#authtype) and [`AuthName`](http://httpd.apache.org/docs/mod/core.html#authname) directive. Only the `Basic` user authentication type is supported. It must be accompanied by a [`require`](http://httpd.apache.org/docs/mod/core.html#require) or `[FastCgiAuthorizer](#FastCgiAuthorizer)` directive in order to work correctly.

```
<Directory htdocs/protected>
  AuthType Basic
  AuthName ProtectedRealm
  FastCgiAuthenticator fcgi-bin/authenticator
  require valid-user
</Directory>
```

`mod_fastcgi` sends nearly all of the standard environment variables typically available to CGI/FastCGI request handlers. All headers returned by a FastCGI authentication application in a successful response (Status: 200) are passed to sub-processes (CGI/FastCGI invocations) as environment variables. All headers returned in an unsuccessful response are passed on to the client. FastCGI specification compliant behavior can be obtained by using the `-compat` option.

`mod_fastcgi` sets the environment variable "FCGI_APACHE_ROLE" to "AUTHENTICATOR" to indicate which (Apache specific) authorizer phase is being performed.

Custom failure responses from FastCGI authorizer applications are not (yet?) supported. See the [ErrorDocument](http://httpd.apache.org/docs/mod/core.html#errordocument) directive for a workaround (a FastCGI application can serve the document).

* * *

## <a name="FastCgiAuthenticatorAuthoritative">FastCgiAuthenticatorAuthoritative</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAuthenticatorAuthoritative _On | Off_|
|[**Default:**](http://httpd.apache.org/docs/mod/directive-dict.html#Default)|FastCgiAuthenticatorAuthoritative On|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

Setting the `FastCgiAuthenticatorAuthoritative` directive explicitly to _Off_ allows authentication to be passed on to lower level modules (as defined in the `Configuration` and `modules.c` files) if the FastCGI application fails to authenticate the user.

A common use for this is in conjunction with a well protected [`AuthUserFile`](http://httpd.apache.org/docs/mod/mod_auth.html#authuserfile) containing a few (administration related) users.

By default, control is not passed on and an unknown user will result in an Authorization Required reply. Disabling the default should be carefully considered.

* * *

## <a name="FastCgiAuthorizer">FastCgiAuthorizer</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAuthorizer _filename_ [-compat]|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

The `FastCgiAuthorizer` directive is used to define a FastCGI application as a per-directory authorizer. Authorizers validate whether an authenticated requestor is allowed access to the requested resource. FastCGI based authorizers are useful primarily when there is a dynamic component to the authorization decision such as a time of day or whether or not the user has paid his bills.

If the FastCGI application _filename_ does not have a corresponding static or external server definition, it is started as a dynamic FastCGI application. If the filename does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot).

`FastCgiAuthorizer` is used within [`Directory`](http://httpd.apache.org/docs/mod/core.html#directory) or [`Location`](http://httpd.apache.org/docs/mod/core.html#location) containers and must include an [`AuthType`](http://httpd.apache.org/docs/mod/core.html#authtype) and [`AuthName`](http://httpd.apache.org/docs/mod/core.html#authname) directive. It must be accompanied by an authentication directive such as [`FastCgiAuthenticator`](#FastCgiAuthenticator), [`AuthUserFile`](http://httpd.apache.org/docs/mod/mod_auth.html#authuserfile), [`AuthDBUserFile`](http://httpd.apache.org/docs/mod/mod_auth_db.html#authdbuserfile) or [`AuthDBMUserFile` in order to work correctly.](http://httpd.apache.org/docs/mod/mod_auth_dbm.html#authdbmuserfile)

```
<Directory htdocs/protected>
   AuthType Basic
   AuthName ProtectedRealm
   AuthDBMUserFile conf/authentication-database
   FastCgiAuthorizer fcgi-bin/authorizer
</Directory>
```

`mod_fastcgi` sends nearly all of the standard environment variables typically available to CGI/FastCGI request handlers. All headers returned by a FastCGI authorizer application in a successful response (Status: 200) are passed to sub-processes (CGI/FastCGI invocations) as environment variables. All headers returned in an unsuccessful response are passed on to the client. FastCGI specification compliant behavior can be obtained by using the `-compat` option.

`mod_fastcgi` sets the environment variable "FCGI_APACHE_ROLE" to "AUTHORIZER" to indicate which (Apache specific) authorizer phase is being performed.

Custom failure responses from FastCGI authorizer applications are not (yet?) supported. See the [ErrorDocument](http://httpd.apache.org/docs/mod/core.html#errordocument) directive for a workaround (a FastCGI application can serve the document).

* * *

## <a name="FastCgiAuthorizerAuthoritative">FastCgiAuthorizerAuthoritative</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAuthorizerAuthoritative _On | Off_|
|[**Default:**](http://httpd.apache.org/docs/mod/directive-dict.html#Default)|FastCgiAuthorizerAuthoritative On|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

Setting the `FastCgiAuthorizerAuthoritative` directive explicitly to _Off_ allows authorization to be passed on to lower level modules (as defined in the `Configuration` and `modules.c` files) if the FastCGI application fails to authorize the user.

By default, control is not passed on and an unauthorized user will result in an Authorization Required reply. Disabling the default should be carefully considered.

* * *

## <a name="FastCgiAccessChecker">FastCgiAccessChecker</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAccessChecker _filename_ [-compat]|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

The `FastCgiAccessChecker` (suggestions for a better name are welcome) directive is used to define a FastCGI application as a per-directory access validator. The Apache Access phase precede user authentication and thus the decision to (dis)allow access to the requested resource is based on the HTTP headers submitted with the request. FastCGI based authorizers are useful primarily when there is a dynamic component to the access validation decision such as a time of day or whether or not a domain has paid his bills.

If the FastCGI application _filename_ does not have a corresponding static or external server definition, it is started as a dynamic FastCGI application. If the filename does not begin with a slash (/) then it is assumed to be relative to the [ServerRoot](http://httpd.apache.org/docs/mod/core.html#serverroot).

`FastCgiAccessChecker` is used within [`Directory`](http://httpd.apache.org/docs/mod/core.html#directory) or [`Location`](http://httpd.apache.org/docs/mod/core.html#location) containers.

```
<Directory htdocs/protected>
  FastCgiAccessChecker fcgi-bin/access-checker
</Directory>
```

`mod_fastcgi` sends nearly all of the standard environment variables typically available to CGI/FastCGI request handlers. All headers returned by a FastCGI access-checker application in a successful response (Status: 200) are passed to sub-processes (CGI/FastCGI invocations) as environment variables. All headers returned in an unsuccessful response are passed on to the client. FastCGI specification compliant behavior can be obtained by using the `-compat` option.

`mod_fastcgi` sets the environment variable "FCGI_APACHE_ROLE" to "ACCESS_CHECKER" to indicate which (Apache specific) authorizer phase is being performed.

Custom failure responses from FastCGI authorizer applications are not (yet?) supported. See the [ErrorDocument](http://httpd.apache.org/docs/mod/core.html#errordocument) directive for a workaround (a FastCGI application can serve the document).

* * *

## <a name="FastCgiAccessCheckerAuthoritative">FastCgiAccessCheckerAuthoritative</a>

| | |
|  --- | --- |
|[**Syntax:**](http://httpd.apache.org/docs/mod/directive-dict.html#Syntax)|FastCgiAccessCheckerAuthoritative _On | Off_|
|[**Default:**](http://httpd.apache.org/docs/mod/directive-dict.html#Default)|FastCgiAccessCheckerAuthoritative On|
|[**Context:**](http://httpd.apache.org/docs/mod/directive-dict.html#Context)|directory|

Setting the `FastCgiAccessCheckerAuthoritative` directive explicitly to _Off_ allows access checking to be passed on to lower level modules (as defined in the `Configuration` and `modules.c` files) if the FastCGI application fails to allow access.

By default, control is not passed on and a failed access check will result in a Forbidden reply. Disabling the default should be carefully considered.

**© Copyright 1996 - 2008 Open Market, Rob Saccoccio & others, All rights reserved. [Web design](http://www.cosmicsitedesign.com/) by CosmicSiteDesign.com**

