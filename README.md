The `rebuild.sh` script downloads what we can from the Wayback Machine archive
of [http://www.fastcgi.com/dist/](http://www.fastcgi.com/dist/) (now defunct)
and stores it under the `dist/` directory.  The result should be reproducible,
so you can run `./rebuild.sh && git status` and you should see no differences.

    ./nuke.sh
    ./rebuild.sh
    git status

Unfortunately, as of this writing, none of the files under the old/ directory
are archived.

See also the [FastCGI.com Archives](https://fastcgi-archives.github.io/)
