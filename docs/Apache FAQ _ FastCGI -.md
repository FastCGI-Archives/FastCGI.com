# Apache 1.3.X

*   [Why does **FastCgiSuexec On** use the wrong suexec wrapper?](#WrongSuexecWrapper)
*   [How can I tell mod_fastcgi not to restart my application?](#NoRestart)
*   [What does a typical httpd.conf look like?](#typical_httpd.conf)
*   [What is the path used with FastCGIExternalServer?](#FastCGIExternalServer)

* * *

*   <a name="WrongSuexecWrapper">Why does **FastCgiSuexec On** use the wrong suexec wrapper?</a>  
    If you have built mod_fastcgi as a DSO with apxs (see the INSTALL document) there is no way for mod_fastcgi to know where your suexec wrapper lives. You will have to use the _path_ argument to FastCgiSuexec.
*   <a name="NoRestart">How can I tell mod_fastcgi not to restart my application?</a>

    mod_fastcgi always maintains the configured number of processes for statically configured applications (see the -processes argument to FastCgiServer).

    Dynamically configured applications are allowed to die (crash, exit, or be signaled down) as long as the -restart argument to FastCgiConfig is not in effect.

    By default, mod_fastcgi will restart the _last_ process instance of a dynamic application if it dies. This behavior can be changed with the -singleThreshold argument to FastCgiConfig. Note that changing this can aggravate a bug in some OS when non-blocking connect()s are being used (see the -appConnTimeout argument). Changing -singleThreshold will allow mod_fastcgi to kill off (signal down) the last process instance of an application when the demand for it no longer warrants its presence. This is the only way the _last_ process instance of an application is allowed to die without being restarted (i.e. a crash or exit will always result in a restart).

    An another alternative is to configure the application as an FastCgiExternalServer and start and manage the application processes on your own (independent of mod_fastcgi's Process Manager).

*   <a name="typical_httpd.conf">What does a typical httpd.conf look like?</a> _Please_ consult the mod_fastcgi documentation for details (IOW read it).

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

        # Anything with one of these extensions is handled as a "dynamic"  server if not defined as
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

*   <a name="FastCGIExternalServer">What is the path used with FastCGIExternalServer?</a>

    Since all FastCGI directives are global (they are not configured in a server context), all FastCGI paths map to the filesystem. In the case of external servers, this path does not have anything to do with the file system; it is a virtual file system path. Since the connection between mod_fastcgi and the FastCGI app is by a socket (unix or tcp), mod_fastcgi does not care where the program is (it could be on a completely different machine). However, mod_fastcgi needs to know when a hit is calling for an external app, so it uses this path as if it were a local file system path. Apache translates a request URI to a filesystem path.

    There are two ways for getting external apps working:

    1.  Use a path that is within the server file system area

        Example:

        ```
{Some server document root /var/www/htdocs}
        FastCGIExternalServer /var/www/htdocs/extprog -host 127.0.0.1:9000
        ```

        This seems easiest but has some shortcomings. Firstly there is the combination of real and virtual filesystem locations in the same place. If you are trying to keep all your files well organized and you have source files for the external server in one place and map URIs to the file system into another, there is a less than clear demarcation between what is real and what is virtual. Most importantly, if you want to use the same external server for more than one server, site, or URI, giving it a virtual place within a real path makes all that more confusing.

    2.  Use a segregated path and use Alias to map requests to it.

        Example:

        ```
    FastCGIExternalServer /fastcgiext/extprog -host 127.0.0.1:9000

            {Some server docutment root /var/www/htdocs}
            Alias /extprog /fastcgiext/extprog
        ```

        This has the potential for more clarity. As a convention all external servers could be mapped into a virtual hierarchy and then aliases used to map into that from any and all places. This keeps the servers well organized and out of the way from file system locations and Aliases can map into them from where they are needed.
