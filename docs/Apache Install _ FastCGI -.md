#  Install instructions Problems

*   <a name="ap_os_is_path_absolute">Cannot load /usr/lib/apache/1.3/mod_fastcgi.so into server: /usr/lib/apache/1.3/mod_fastcgi.so: undefined symbol: ap_os_is_path_absolute</a>

    This is the result of a bug in the Apache header files (reported Sep 1999, PR# 5012, but never fixed).

    The problem is due to the fact that httpd was compiled with optimization and ap_os_is_path_absolute() was inlined, but when mod_fastcgi.so was compiled optimization was not enabled and ap_os_is_path_absolute() was expected to be an external symbol.

    Try this apxs invocation instead (it will turn on optimization and inline ap_os_is_path_apsolute()):

    <pre>apxs -Wc,-O -o mod_fastcgi.so -c *.c
    </pre>
