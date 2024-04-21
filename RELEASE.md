# Release process

## To release a new version of **swmmio** on GitHub and PyPi:

**1.)** Ensure you have the latest version from upstream and update your fork

    git pull upstream master
    git push origin master

**2.)** Update [CHANGELOG.md](https://github.com/aerispaha/swmmio/blob/master/CHANGELOG.md), using loghub

`loghub aerispaha/swmmio -m <milestone> -u <username> -ilr "complete" -ilg "feature" "New Features" -ilg "enhancement" "Enhancements" -ilg "bug" "Bugs fixed"`

**3.)** Copy paste the text from [CHANGELOG.temp] to [CHANGELOG.md]

**4.)** Update [`swmmio/__init__.py`](https://github.com/aerispaha/swmmio/blob/master/swmmio/__init__.py) (set release version, remove 'dev0')

**5.)** Update the version number in [README.md](https://github.com/aerispaha/swmmio/blob/master/README.md)

**6.)** Update the AUTHORS by running the [update_authors.sh](tools/update-authors.sh)

**6.)** Commit changes

    git add .
    git commit -m "Set release version"

**7.)** Add release tag and push to origin

    git tag -a vX.X.X -m 'Release version'
    git push  --follow-tags

**7.)** Update `__init__.py` (add 'dev0' and increment minor)

**8.)** Commit changes

    git add .
    git commit -m "Restore dev version"

**9.)** Push changes

    git push upstream master
    git push origin master