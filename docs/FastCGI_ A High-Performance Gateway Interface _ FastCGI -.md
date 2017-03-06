# FastCGI: A High-Performance Gateway Interface

Position paper for the workshop "Programming the Web - a search for APIs",  
Fifth International World Wide Web Conference, 6 May 1996, Paris, France.  

Mark R. Brown  
Open Market, Inc.  

2 May 1996  

**Copyright © 1996 Open Market, Inc. 245 First Street, Cambridge, MA 02142 U.S.A.**

* * *

### Abstract

FastCGI is a fast, open, and secure Web server interface that solves the performance problems inherent in CGI without introducing any of the new problems associated with writing applications to lower-level Web server APIs. Modules to support FastCGI can be plugged into Web server APIs such as Apache API, NSAPI, and ISAPI. Key considerations in designing FastCGI included minimizing the cost of migrating CGI applications (including applications written in popular scripting languages such as Perl), supporting both single-threaded and multi-threaded application programming, supporting distributed configurations for scaling and high availability, and generalizing the roles that gateway applications can play beyond CGI's "responder" role.

For more information on FastCGI, including an interface specification and a module for the Apache server, visit the [fastcgi-archives.github.io Web site](https://fastcgi-archives.github.io/).

### 1\. Introduction

The surge in the use of the Web by business has created great demand for applications that create dynamic content. These applications allow businesses to deliver products, services, and messages whose shape and content are influenced by interaction with and knowledge of users.

This move towards dynamic Web content has highlighted the performance limits of CGI (Common Gateway Interface). In response there has been a proliferation of Web server APIs. These APIs address some (though not all) of the performance problems with CGI, but are not designed to meet the need of business applications. When applied to business applications, Web server APIs suffer from these problems:

*   **Complexity.** Server APIs introduce a steep learning curve, with increased implementation and maintenance costs.
*   **Language dependence.** Applications have to be written in a language supported by the server API (usually C/C++). Perl, the most popular language for CGI programs, can't be used with any existing server API.
*   **No process isolation.** Since the applications run in the server's address space, buggy applications can corrupt the core server (or each other). A malicious or buggy application can compromise server security, and bugs in the core server can corrupt applications.
*   **Proprietary.** Coding your application to a particular API locks you into a particular server.
*   **Tie-in to server architecture.** API applications have to share the same architecture as the server: If the Web server is multi-threaded, the application has to be thread-safe. If the Web server has single-threaded processes, multi-threaded applications don't gain any performance advantage. Also, when the server's architecture changes, the API will usually have to change, and applications will have to be adapted or rewritten.

Web server APIs are suitable for applications that require an intimate connection to the core Web server, such as security protocols. But using a Web server API for a Web business application would be much like using an old-fashioned TP monitor, which required linking applications right into the monitor, for a modern business transaction processing application. The old-fashioned solution suffers a huge development and maintenance cost penalty because it ignores 30 years of progress in computing technology, and may end up providing inferior performance to boot. Nobody uses the old technology unless they are already locked into it.

FastCGI is best viewed as a new implementation of CGI, designed to overcome CGI's performance problems. The major implementation differences are:

*   FastCGI processes are persistent: after finishing a request, they wait for a new request instead of exiting.
*   Instead of using operating system environment variables and pipes, the FastCGI protocol multiplexes the environment information, standard input, output, and error over a single full-duplex connection. This allows FastCGI programs to run on remote machines, using TCP connections between the Web server and the FastCGI application.

FastCGI communicates the exact same information as CGI in a different way. Because FastCGI _is_ CGI, and like CGI runs applications in separate processes, it suffers none of the server API problems listed above.

### 2\. Migration from CGI

Open Market has developed a FastCGI application library that implements the FastCGI protocol, hiding the protocol details from the developer. This library, which is freely available, makes writing FastCGI programs as easy as writing CGI applications.

The application library provides replacements for the C language standard I/O (stdio) routines such as <tt>printf()</tt> and <tt>gets()</tt>. The library converts references to environment variables, standard input, standard output, and standard error to the FastCGI protocol. References to other files "fall through" to the underlying operating system standard I/O routines. This approach has several benefits:

*   Developers don't have to learn a new API to develop FastCGI applications.
*   Existing CGI programs can be migrated with minimal source changes.
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

This application returns a "Hello world" HTML response to the client. It also keeps a counter of the number of times it has been accessed, displaying the value of the counter at each request. The <tt>fcgi_stdio.h</tt> header file provides the FastCGI replacement routines for the C standard I/O library. The <tt>FCGI_Accept()</tt> routine accepts a new request from the Web server.

The application library was designed to make migration of existing CGI programs as simple as possible. Many applications can be converted by adding a loop around the main request processing code and recompiling with the FastCGI application library. To ease migration to FastCGI, executables built with the application library can run as either CGI or FastCGI programs, depending on how they are invoked. The library detects the execution environment and automatically selects FastCGI or regular I/O routines, as appropriate.

Applications written in Perl, Tcl, and other scripting languages can be migrated by using a language interpreter built with the application library. FastCGI-integrated Tcl and Perl interpreters for popular Unix platforms are available from the [fastcgi-archives.github.io](https://fastcgi-archives.github.io/) Web site. The interpreters are backward-compatible: They can run standard Tcl and Perl applications.

### 3\. Single-threaded and multi-threaded applications

FastCGI gives developers a free choice of whether to develop applications in a single-threaded or multi-threaded style. The FastCGI interface supports multi-threading in two ways:

*   Applications can accept concurrent Web server connections to provide concurrent requests to multiple application threads.
*   Applications can accept multiplexed Web server connections, in which concurrent requests are communicated over a single connection to multiple application threads.

Multi-threaded programming is complex -- concurrency makes programs difficult to test and debug -- so many developers will prefer to program in the familiar single-threaded style. By having several concurrent processes running the same application it is often possible to achieve high performance with single-threaded programming.

The FastCGI interface allows Web servers to implement _session affinity_, a feature that allows applications to maintain caches of user-related data. With session affinity, when several concurrent processes are running the same application, the Web server routes all requests from a particular user to the same application process. Web server APIs don't provide this functionality to single-threaded applications, so the performance of an API-based application is often inferior to the performance of the corresponding FastCGI application.

### 4\. Distributed FastCGI

Because FastCGI can communicate over TCP/IP connections, it supports configurations in which applications run remotely from the Web server. This can provide scaling, load balancing, high availability, and connections to systems that don't have Web servers.

Distributed FastCGI can also provide security advantages. A Web server outside a corporate firewall can communicate through the firewall to internal databases. For instance, an application might need to authenticate incoming users as customers in order to give access to certain documents on the external Web site. With FastCGI this authentication can be done without replicating data and without compromising security.

### 5\. Roles

A problem with CGI is its limited functionality: CGI programs can only provide responses to requests. FastCGI provides expanded functionality with support for three different application "roles":

*   **Responder.** This is the basic FastCGI role, and corresponds to the simple functionality offered by CGI today.
*   **Filter.** The FastCGI application filters the requested Web server file before sending it to the client.
*   **Authorizer.** The FastCGI program performs an access control decision for the request (such as performing a username/password database lookup).

Other roles will be defined in the future. For instance, a "logger" role would be useful, where the FastCGI program would receive the server's log entries for real-time processing and analysis.

### 6\. Conclusions

Today's Web business applications need a platform that's fast, open, maintainable, straightforward, stable, and secure. FastCGI's design meets these requirements, and provides a logical migration path from the proven and widely deployed CGI technology. This allows developers to take advantage of FastCGI's benefits without losing their existing investment in CGI applications.

For more information about FastCGI, visit the [fastcgi-archives.github.io Web site](https://fastcgi-archives.github.io/).

**© Copyright 1996 - 2014 Open Market, Rob Saccoccio & others, All rights reserved. [Web design](http://www.cosmicsitedesign.com/) by CosmicSiteDesign.com**
