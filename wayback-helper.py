#!/usr/bin/env python3
# The idea is for this to be reproducible.

from urllib.request import urlopen
from urllib.parse import quote, urlsplit, urlunsplit
from base64 import b32decode
from binascii import hexlify
import json
import re

# Wayback Machine CDX search API documentation is at
# https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md#basic-usage

# Get the most recent 200 response recorded by the Wayback Machine.
with urlopen('https://web.archive.org/cdx/search/cdx?url=fastcgi.com/dist&matchType=prefix&filter=statuscode:200&collapse=digest&fl=urlkey,timestamp,original,mimetype,statuscode,digest,length') as u:
    assert u.status == 200
    result = u.read()
    with open("tmp/searchresult.cdx.txt", "wb") as f:
        f.write(result)

with open("tmp/file-list.txt", "w") as file_list:
    # Sort the
    cdx_entries = []
    for line in result.decode('utf-8').split("\n"):
        if line == '':
            continue
        urlkey, timestamp, original, mimetype, statuscode, digestb32, length = line.split()
        assert re.match('^\d+$', timestamp)
        cdx_entries.append((urlkey, timestamp, original, mimetype, statuscode, digestb32, length))
    cdx_entries.sort(key=lambda x: x[1])    # by timestamp
    cdx_entries.reverse()

    seen_paths = set()
    for urlkey, timestamp, original, mimetype, statuscode, digestb32, length in cdx_entries:
        sha1digest = b32decode(digestb32)
        sha1hex = hexlify(sha1digest).decode('utf-8')

        assert re.match('^\d+$', timestamp)
        archive_url = 'http://web.archive.org/web/{0}id_/{1}'.format(timestamp, quote(original))
        _, _, path, query, _ = urlsplit(original)
        if query:
            #path += '?' + query
            continue

        assert path.startswith("/dist")
        trimmed_path = re.sub(r'^/dist/', '', path)
        assert not trimmed_path.startswith('/')
        if path.endswith('/'):
            trimmed_path += '_index.html'   # call it _index.html so that anyone looking in the directory can see the whole tree

        dupnum = 0
        local_path = trimmed_path
        while local_path in seen_paths:
            dupnum += 1
            local_path = trimmed_path + '.%d' % dupnum
        seen_paths.add(local_path)

        print("{0} {1} {2}".format(sha1hex, archive_url, local_path), file=file_list)
