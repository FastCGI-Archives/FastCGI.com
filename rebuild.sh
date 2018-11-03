#!/bin/sh
set -e

./nuke.sh

mkdir -p dist tmp

# This writes:
#   tmp/searchresult.cdx.txt
#   tmp/file-list.txt
./wayback-helper.py

rm -f tmp/SHA1SUMS
rm -f tmp/manifest.txt
while read -r sha1hex archive_url local_path
do
    mkdir -p "$(dirname "dist/$local_path")"
    echo "${sha1hex} *${local_path}" >> tmp/SHA1SUMS
    echo "${local_path}" >> tmp/manifest.txt
    wget -O "dist/$local_path" "$archive_url"
done < tmp/file-list.txt

# Sort into nice alphabetical order
LC_ALL=C.UTF-8 sort -t ' ' -k2 < tmp/SHA1SUMS > dist/SHA1SUMS
LC_ALL=C.UTF-8 sort tmp/manifest.txt > tmp/manifest.sorted.txt

cd dist

# SHA1SUMS came from our search results.  Check it.
sha1sum -c SHA1SUMS

# Generate a stronger hash.
cat ../tmp/manifest.sorted.txt | tr '\n' '\0' | xargs -0 sha256sum -b > SHA256SUMS
