yjl-sysusers
============

__VERSION 0.1.0 PRE-RELEASE__

For installation instructions, see [INSTALL.md](INSTALL.md)

This project includes a single utility and a JSON file. In the git
source, that utility is simply called `functions.py` but it gets
installed as `/usr/sbin/yjl-sysusers` with a single-line change
to specify the location on the filesystem of the JSON file.

I am developing this using Python 3.11.3 but it has been tested in
Python 3.6.4 (CentOS 7) without issues.

The purpose is to provide an easy way to provide consistent user ID
and group ID numbers for system users (as opposed to human login users)
while also being able to on-the-fly use dynamic IDs if the static IDs
have already been used for something else.

My use case is for RPM `%pre` scriptlets to ensure that the appropriate
users and groups an RPM package needs exist when the package installs.

See the [yjl-sysusers.8](docs/yjl-sysusers.8.md) man page.


yjl-sysusers.json
-----------------

This JSON file contains all the information needed to create system
users and groups for YellowJacket GNU/Linux.

It is largely based upon the static system user information from
LFS/BLFS 11.3 but there are some differences.

It is currently a work in progress, some of the JSON entries are not
complete and others are planned but missing.

For the file format, see
[yjl-sysusers.json.5](docs/yjl-sysusers.json.5.md) man page.



Validation Failures and Handling
--------------------------------

If the user running the `yjl-sysgroups` utility does not have `root`
privileges, the utility will exit with a failure status.

If the JSON file is malformed, the `yjl-sysgroups` utility will exit
with a failure status. That should never happen unless the JSON file
is improperly modified after install.

If a username or groupname passed as an argument does not validate,
the `yjl-sysusers` utility will exit with a failure status.

If anything other than the case sensitive `True` or `False` is passed
with the `--useradd`, `--groupadd`, or `--mkdir` options, the
`yjl-sysusers` utility will exit with a failure status. I consider
that to be a bug.

If there are no available UIDs/GIDs left in the system user dynamic
range when one is needed, the `yjl-sysusers` utility will exit with
a failure status.

Other than those cases, failure of the program should be extremely
rare and considered a bug.

As the intended use is within RPM, it is better for the program to
choose a safe default and continue (such as using `/dev/null` for
the home directory or `/sbin/nologin` as the login shell) if a bad
value is passed to `yjl-sysusers` so that the user is created and
the proper assignment of files belonging to users and groups the
script is asked to create can still be made.
