#!/bin/sh

##
## This script will auto-generate the AUTHORS attribution file.
## If your name does not display correctly, then please
## update the .mailmap file in the root repo directory
##

echo '# Contributing authors listed in alphabetical order:\n' > ../AUTHORS
git log --reverse --format='%aN <%aE>' | sort -u >> ../AUTHORS
