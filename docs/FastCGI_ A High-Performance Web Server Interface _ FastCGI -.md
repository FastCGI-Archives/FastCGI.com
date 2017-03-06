Open Market, Inc.

Technical White Paper  

# FastCGI:  
A High-Performance Web Server Interface

April 1996

* * *

## 1\. Introduction

The surge in the use of the Web by business has created a tremendous need for server extension applications that create dynamic content. These are the applications that will allow businesses to deliver products, services, and messages whose shape and content are in part determined by the interaction with, and knowledge of, the customers to which they are delivered.

This important movement away from static Web content is pushing the limits and exposing the weaknesses of the environment in which these applications are currently bound: CGI (Common Gateway Interface). Most importantly it does not offer the performance these applications require. A new communication infrastructure is needed to connect Web servers with these new applications. This is what led Open Market to develop FastCGI.

FastCGI is a fast, open, and secure Web server interface that solves the performance problems inherent in CGI, without introducing the overhead and complexity of proprietary APIs (Application Programming Interfaces).

This paper assumes that the reader has basic familiarity with Web technology and developing Web applications.

### Common Gateway Interface

The de facto standard interface for Web server applications is CGI, which was first implemented in the NCSA server. CGI has many benefits:

*   **Simplicity.** It is easy to understand.
*   **Language independence.** CGI applications can be written in nearly any language.
*   **Process isolation.** Since applications run in separate processes, buggy applications cannot crash the Web server or access the server's private internal state.
*   **Open standard.** Some form of CGI has been implemented on every Web server.
*   **Architecture independence.** CGI is not tied to any particular server architecture (single threaded, multi-threaded, etc.).

CGI also has some significant drawbacks. The leading problem is performance: Since a new process is created for each request and thrown away when the request is done, efficiency is poor.

CGI also has limited functionality: It only supports a simple "responder" role, where the application generates the response that is returned to the client. CGI programs can't link into other stages of Web server request processing, such as authorization and logging.

### Server APIs

In response to the performance problems for CGI, several vendors have developed APIs for their servers. The two most notable are NSAPI from Netscape and ISAPI from Microsoft. The freely available Apache server also has an API.

Applications linked into the server API may be significantly faster than CGI programs. The CGI startup/initialization problem is improved, because the application runs in the server process and is persistent across requests. Web server APIs also offer more functionality than CGI: you can write extensions that perform access control, get access to the server's log file, and link in to other stages in the server's request processing.

However, APIs sacrifice all of CGI's benefits. Vendor APIs have the following problems:

*   **Complexity.** Vendor APIs introduce a steep learning curve, with increased implementation and maintenance costs.
*   **Language dependence.** Applications have to be written in a language supported by the vendor API (usually C/C++). Perl, the most popular language for CGI programs, can't be used with any existing vendor API.
*   **No process isolation.** Since the applications run in the server's address space, buggy applications can corrupt the core server (or each other). A malicious or buggy application can compromise server security, and bugs in the core server can corrupt applications.
*   **Proprietary.** Coding your application to a particular API locks you into a particular vendor's server.
*   **Tie-in to server architecture.** API applications have to share the same architecture as the server: If the Web server is multi-threaded, the application has to be thread-safe. If the Web server has single-threaded processes, multi-threaded applications don't gain any performance advantage. Also, when the vendor changes the server's architecture, the API will usually have to change, and applications will have to be adapted or rewritten.

### FastCGI

The FastCGI interface combines the best aspects of CGI and vendor APIs. Like CGI, FastCGI applications run in separate, isolated processes. FastCGI's advantages include:

*   **Performance.** FastCGI processes are persistent-they are reused to handle multiple requests. This solves the CGI performance problem of creating new processes for each request.
*   **Simplicity, with easy migration from CGI.** The FastCGI application library (described on page 9) simplifies the migration of existing CGI applications. Applications built with the application library can also run as CGI programs, for backward compatibility with old Web servers.
*   **Language independence.** Like CGI, FastCGI applications can be written in any language, not just languages supported by the vendor API.
*   **Process isolation.** A buggy FastCGI application cannot crash or corrupt the core server or other applications. A malicious FastCGI application cannot steal any secrets (such as session keys for encryption) from the Web server.
*   **Non-proprietary.** FastCGI is supported in all of Open Market's server products, and support is under development for other Web servers, including the freely available Apache and NCSA servers, as well as commercial servers from Microsoft and Netscape.
*   **Architecture independence.** The FastCGI interface is not tied to a particular server architecture. Any Web server can implement the FastCGI interface. Also, FastCGI does not impose any architecture on the application: applications can be single or multi-threaded, regardless of the threading architecture of the Web server.
*   **Support for distributed computing.** FastCGI provides the ability to run applications remotely, which is useful for distributing load and managing external Web sites.

The following sections describe the FastCGI interface, protocol, application library, and support in Open Market's WebServer products.

## 2\. FastCGI Interface

The functionality provided by the FastCGI interface is very similar to that provided by CGI. To best understand the FastCGI protocol, we review the CGI interface here. Basic CGI request processing proceeds as follows:

1.  For each request, the server creates a new process and the process initializes itself.
2.  The Web server passes the request information (such as remote host, username, HTTP headers, etc.) to the CGI program in environment variables.
3.  The Web server sends any client input (such as user-entered field values from an HTML form) to the CGI program's standard input.
4.  The CGI program writes any output to be returned to the client on standard output. Error information written to standard error is logged by the Web server.
5.  When the CGI process exits, the request is complete.

FastCGI is conceptually very similar to CGI, with two major differences:

*   FastCGI processes are persistent: after finishing a request, they wait for a new request instead of exiting.
*   Instead of using operating system environment variables and pipes, the FastCGI protocol multiplexes the environment information, standard input, output and error over a single full-duplex connection. This allows FastCGI programs to run on remote machines, using TCP connections between the Web server and the FastCGI application.

Request processing in a single-threaded FastCGI application proceeds as follows:

1.  The Web server creates FastCGI application processes to handle requests. The processes may be created at startup, or created on demand.
2.  The FastCGI program initializes itself, and waits for a new connection from the Web server.
3.  When a client request comes in, the Web server opens a connection to the FastCGI process. The server sends the CGI environment variable information and standard input over the connection.
4.  The FastCGI process sends the standard output and error information back to the server over the same connection.
5.  When the FastCGI process closes the connection, the request is complete. The FastCGI process then waits for another connection from the Web server.

FastCGI applications can run locally (on the same machine as the Web server) or remotely. For local applications, the server uses a full-duplex pipe to connect to the FastCGI application process. For remote applications, the server uses a TCP connection.

FastCGI applications can be single-threaded or multi-threaded. For single threaded applications, the Web server maintains a pool of processes (if the application is running locally) to handle client requests. The size of the pool is user configurable. Multi-threaded FastCGI applications may accept multiple connections from the Web server and handle them simultaneously in a single process. (For example, Java's built-in multi-threading, garbage collection, synchronization primitives, and platform independence make it a natural implementation language for multi-threaded FastCGI applications.)

### Remote FastCGI

FastCGI's ability to run applications remotely (over a TCP connection) provides some major benefits. These benefits are described in this section, along with some of the security issues that affect remote FastCGI applications.

#### FastCGI with Firewalls

Applications that run on organizational (external) Web servers and depend on internal databases can be a challenge to administer. Figure 1 shows a typical organization, with an external Web server, a firewall restricting access to the internal network, and internal databases and applications.

![error-file:TidyOut.log](img00001.gif)<a name="_Ref352505891">Figure 1</a>

With CGI and vendor APIs, the application has to run on the Web server machine. This means the server administrator has to replicate the necessary database information onto the system hosting the Web server (which may be difficult to do in an automated way without compromising firewall security). Or, the administrator may build a "bridge" that allows access through the Web server to internal databases and applications (which is effectively re-inventing remote FastCGI).

With remote FastCGI, the applications can run on the internal network, simplifying the administrator's job. When used with appropriate firewall configuration and auditing, this approach provides a secure, high-performance, scalable way to bring internal applications and data to the external network.

#### Load Distribution

For resource-intensive CGI and API applications, the Web server machine quickly becomes the bottleneck for overall throughput. The usual way to solve this performance problem is to buy a bigger, faster Web server machine, or to partition the Web site across several Web servers.

With remote FastCGI, the resource-intensive applications can be moved off the Web server machine, giving the server administrator additional flexibility in configuring the Web server. The administrator can configure FastCGI applications "behind the scenes" without having to change any content links or the external view of the Web site. The administrator can use several smaller, inexpensive server machines for applications, and can tailor each machine to the application it is hosting.

#### Security Issues with Remote FastCGI

The two security issues with remote FastCGI connections are authentication and privacy. FastCGI applications should only accept connections from Web servers that they trust (the application library includes support for IP address validation). Future versions of the protocol will include support for applications authenticating Web servers, as well as support for running remote connections over secure transport protocols such as SSL or PCT.<!--This pargraph needs to be made stronger, going into the issues in a little more detail.-->

### The FastCGI Protocol

This section offers a brief introduction to the protocol used on the connection between the Web server and FastCGI application. Most application developers will use the FastCGI application library and won't have to worry about the protocol details. However, specialized applications are free to implement the FastCGI protocol directly.

FastCGI uses a simple packet record format on the connection between the application and the Web server. The same record format is used in both directions and is outlined in Figure 2.

![error-file:TidyOut.log](img00002.gif)<a name="_Ref352404075">Figure 2</a>

The protocol version field specifies the version of the FastCGI protocol that is in use. The type field specifies the type of the record (described in the following section). The request ID identifies this record to a particular request, allowing multiple requests to be multiplexed over a single connection. The data length field specifies the number of data bytes that follow.

The different FastCGI packet types are:

| Packet types | Descriptions |
|---|---|
|FCGI_PARAMS|Used for sending name/value pairs (CGI environment variables) from the Web server to the application.|
|FCGI_STDIN|Used for sending the standard input from the Web server to the application.|
|FCGI_DATA|Used for sending filter data to the application (for more information, see the filter role described on page 7.)|
|FCGI_STDOUT|Used to send standard output from the application to the Web server.|
|FCGI_STDERR|Used to send standard error information from the application to the Web server.|
|FCGI_END_REQUEST|Ends the request (can be sent by either the server or the application).|

For complete protocol details, see the _FastCGI Protocol Specification_, available from the Web site listed at the end of this paper.

## 3\. Application Roles

A major problem with CGI is its limited functionality: CGI programs can only provide simple responses to requests. FastCGI provides expanded functionality with support for three different application "roles":

*   **Responder.** This is the basic FastCGI role, and corresponds to the simple functionality offered by CGI today.
*   **Filter.** The FastCGI application filters the requested Web server file before sending it to the client.
*   **Authorizer.** The FastCGI program performs an access control decision for the request (such as performing a username/password database lookup).

Other roles will be defined in the future. For instance, a "logger" role would be useful, where the FastCGI program would receive the server's log entries for real-time processing and analysis.

The roles are described in more detail in the following sections.

### Responder Role

FastCGI's Responder role is identical to the functionality provided by CGI today. When a request comes into the server, the FastCGI program generates the response that's returned to the client (typically an HTML page).

### <a name="_Ref352404524">Filter Role</a>

The Filter role allows a FastCGI application to process a requested file before it is returned to the client.

Let's assume that the Web server is configured so that all files with the .<tt>sgml</tt> extension are processed by a SGML-to-HTML FastCGI filter application, and the user accesses the following URL:

<tt>/document.sgml</tt>

After the Web server makes an access control decision and maps this URL to a content file, it invokes the FastCGI filter application with this file available as input. The FastCGI program's HTML output is sent back to the client, just as in the responder role. The process is outlined in Figure 3.

![error-file:TidyOut.log](img00003.gif)<a name="_Ref352560526">Figure 3</a>

Filter applications can significantly improve performance by caching filter results (the server provides the modification time in the request information so that applications can flush the cache when the server file has been modified).

The Filter role is useful for:

*   On-the-fly format conversions
*   Dynamic documents (such as documents with embedded SQL queries, or dynamic advertisement insertion)
*   Applying a standard template: headers, footers, and backgrounds

### Authorizer Role

The Authorizer role allows a FastCGI application to make an access control decision for a request. The FastCGI application is invoked with all of the request information, just as in the Responder role. If the authorizer application generates a "200 OK" HTTP result, the Web server assumes that access is allowed and proceeds with the request. (The Web server may process other access checks, including other FastCGI authorizers, before access is ultimately allowed.) If the application generates any other response, that response is returned to the client and the request is ended. The response can be any valid HTTP response, including "Access Denied" or "Redirect".

The Authorizer role is useful for:

*   Access control based on username and password, where the user information is looked up in an external database.
*   Complex access policies, such as time-of-day based access.
*   Smart-card challenge/response authentication.
*   Dynamic redirects, where the user is sent to different pages based on the request profile.

## <a name="_Ref352251764">4\. FastCGI Application Library</a>

Open Market has developed a FastCGI application library that implements the FastCGI protocol (hiding the protocol details from the developer). This library makes implementing FastCGI programs as easy as writing CGI applications.

The application library provides a replacement for the C language standard I/O (stdio) routines, such as <tt>printf() and <tt>gets()</tt>. The library converts references to standard input, standard output, and standard error to the FastCGI protocol. References to other files "fall through" to the underlying operating system standard I/O routines.</tt>

This approach has several benefits:

*   Developers don't have to learn a new API to develop FastCGI applications.
*   Existing CGI programs can be migrated with minimal source changes (CGI migration is described in more detail in the following section).
*   FastCGI interpreters for Perl, Tcl, and other interpreted languages can be built without modifying the interpreter source code.

Here's a simple FastCGI application:

```
#include <fcgi_stdio.h>

void main(void)
{
    int count = 0;
    while(FCGI_Accept() >= 0) {
        printf("Content-type: text/html\r\n");
        printf("\r\n");
        printf("Hello world!<br>\r\n");
        printf("Request number %d.", count++);
    }
    exit(0);
}
```

This application returns a "Hello world" HTML response to the client. It also keeps a counter of the number of times it has been accessed, displaying the value of the counter at each request.

The <tt>fcgi_stdio.h</tt> header file provides the FastCGI replacement routines for the C standard I/O library. The <tt>FCGI_Accept()</tt> routine accepts a new request from the Web server.

### Migrating Existing CGI Programs

The application library was designed to make migration of existing CGI programs as simple as possible. Many applications can be converted by adding a loop around the main request processing code and recompiling with the FastCGI application library. FastCGI applications have the following structure, with an initialization section and a request processing loop:

```
_Initialize application_;  
while(FCGI_Accept() >= 0) {  
    _Process request_;  
}
```

To ease migration to FastCGI, executables built with the application library can run as either CGI or FastCGI programs, depending on how they are invoked. The library detects the execution environment and automatically selects FastCGI or regular I/O routines, as appropriate.

After migration, developers can clean up their FastCGI applications for best performance:

*   Fix any resource leaks. Many CGI programs do not attempt to manage memory or close files, because they assume the world is going to be cleaned up when they exit. (If you don't want to clean up your program, you can just have your process assume that it is leaking memory and exit after processing some fixed number of requests.) Purify from Pure Software is one of a number of excellent tools for finding leaks and other memory use problems.
*   Fix any problems with retained application state. The application must ensure that any state that it creates in processing one request has no unintended effects on later requests.
*   Collapse functionality. A common practice with CGI applications is to implement many small programs, with one function per program. CGI encourages this, because smaller programs load faster. With FastCGI, it's better to have related functionality in a single executable, so there are fewer processes to manage and applications can take advantage of sharing cached information across functions.

Applications written in Perl, Tcl, and other scripting languages can be migrated by using a language interpreter built with the application library. FastCGI-integrated Tcl and Perl interpreters for popular Unix platforms are available from Open Market. The interpreters are backward-compatible: They can run standard Tcl and Perl applications.

## 5\. FastCGI in the Open Market WebServer

This section describes the FastCGI support in the following Open Market server products:

*   Open Market WebServer V2.0
*   Open Market Secure WebServer V2.0
*   Open Market Secure WebServer (Global) V2.0

For more information about FastCGI support, see the _Open Market WebServer Installation and Configuration Guide_.

### Server Configuration

FastCGI applications are configured with the server's configuration file. Configuration has two parts.

First, the server administrator defines an _application class_. For local applications, the application class specifies the details of running the FastCGI application, such as:

*   The pathname of the application executable.
*   Any arguments and environment variables to pass to the process at startup.
*   The number of processes to run.

For remote applications, the class configuration information includes the host and TCP port to connect to. The Web server assumes that the FastCGI application has been started on the remote host. If a request comes in and the server can't connect to the FastCGI TCP port, the server logs an error and returns an error page to the client.

The second configuration step is mapping the application class to a role:

*   For responder roles, the administrator configures some part of the URL space to be handled by the FastCGI application. For example, all URLs beginning with /rollcall/ might be handled by the employee database application.
*   For filter roles, the administrator configures a file extension to be handled by a filter application. For example, all files with the .sql extension could be handled by a SQL query lookup filter.
*   For authorizer roles, the administrator configures an authorizer application in the same manner as other access methods (hostname, username/password, etc.) A request must pass _all_ access control checks (possibly including multiple FastCGI authorizers) before access is allowed.

### Basic FastCGI

To simplify migration for existing CGI programs, the WebServer provides a simple way to install new FastCGI programs without having to reconfigure the server. However, this approach doesn't offer all of the performance benefits of FastCGI application classes.

The WebServer treats any file with the extension .fcg as a FastCGI application. When a request corresponds to such a file, the WebServer creates a new FastCGI process to handle the request, and shuts down the process when the request is complete (just as in CGI). In this mode of operation performance is comparable to CGI. Future versions of the WebServer will improve performance by automatically caching processes and re-using them for subsequent requests.

### Session Affinity

FastCGI programs can improve performance by caching information in the application process. For applications that require frequent but expensive operations such as validating a username/password in an external database for each request, this technique can significantly improve performance.

To improve the effectiveness of this technique, the WebServer implements _session affinity_. When session affinity is enabled, the WebServer arranges for all requests in a user session to be handled by the same FastCGI application process. What constitutes a "session" is configurable. The default configuration uses the WebServer's built-in session tracking facility to identify user sessions. However, the server administrator can use any part of the request information for the session affinity mapping: the URL path, the client's hostname, the username, etc. <!--Talk about applications that need to hold onto resources for the user (such as open connections to the database).-->

## 6\. FastCGI Performance Analysis

How fast is FastCGI? The answer depends on the application. This section contains some real FastCGI performance measurements, as well as guidelines for estimating the FastCGI speedup.

### FastCGI vs CGI

We measured the relative performance of CGI, FastCGI, and static files on the Open Market WebServer, using a simple application that generates a fixed number of output bytes. The following table shows the measured request processing time for different request types on a typical platform. The times are measured from the client perspective and include client, server, and application processing time.

| Types | Processing time per KByte |
| --- | --- |
|Static file|21ms + 0.19ms per Kbyte|
|FastCGI|22ms + 0.28ms per Kbyte|
|CGI|59ms + 0.37ms per Kbyte|

FastCGI performance is comparable to serving static files, and significantly better than CGI (clearly showing the high overhead for process creation). Real applications have an additional time component: process initialization, which should be added to overall request processing time.

Let's use this data to estimate the speedup from migrating a typical database CGI application to FastCGI. Assume the application takes 50ms to initialize the database connection and generates 5K of output data. Request performance can be computed as follows:

| Types | Processing time |
| --- | --- |
|CGI|59ms + 50ms + (0.37ms)(5) = 111ms|
|FastCGI|22ms + (0.28ms)(5) = 23ms|

In this example, FastCGI has a 5x performance advantage over CGI, mostly due to savings from not having to create and initialize new processes for each request.<!--Need to talk about FastCGI vs proprietary APIs.-->

## 7\. Conclusions

Today's Web business applications need a platform that's fast, open, maintainable, straightforward, stable, and secure. FastCGI's design meets these requirements, and provides for a logical extension from proven and widely deployed CGI technology. This allows developers to take advantage of FastCGI's benefits without losing their existing investment in CGI applications.<!--Need to talk about NT.--> <!--Need to give "more punch" to this conclusion: include info about uses for FastCGI (accessing legacy data in databases, access control, distributed applications, apps that have to run in multiple OS environments. -->

## 8\. For More Information

For more information about Open Market and our products, visit our Web site at:[http://www.openmarket.com/](https://web.archive.org/web/20160305160340/http://www.openmarket.com/)

For more information about the FastCGI protocol and the developer's kit, and the latest information about FastCGI standardization and support in other Web servers, visit the FastCGI project page at: [fastcgi-archives.github.io](https://fastcgi-archives.github.io/)

This file is Copyright © 1996 Open Market, Inc.
