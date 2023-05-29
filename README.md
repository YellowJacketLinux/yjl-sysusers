yjl-sysusers
============

__VERSION 0.1.0 PRE-RELEASE__

For installation instructions, see [INSTALL.md](INSTALL.md)

This project includes a single utility and a JSON file. In the git
source, that utility is simply called `functions.py` but it gets
installed as `/usr/sbin/yjl-sysusers` with a single-line change
to specify the location on the filesystem of the JSON file.

This project is currently being developed using Python 3.11.3 but it
has been tested in Python 3.6.4 (CentOS 7) without issues.

The purpose is to provide an easy way to provide consistent static
user ID and group ID numbers for system users (as opposed to human login
users) while also being able to on-the-fly use dynamic IDs if the static
IDs have already been used for something else.

My use case is for RPM `%pre` scriptlets to ensure that the appropriate
users and groups an RPM package needs exist when the package installs.


yjl-sysusers
------------

With the `yjl-sysusers` utility, portable RPM spec files which produce
packages that are installable across multiple LSB compliant GNU/Linux
distributions (sometimes with a rebuild for shared library resolution)
becomes much easier.

Theoretically (not yet implemented or tested) with the `yjl-sysusers`
utility, translations of user comment (also called GECOS) field into
the default system locale will be automatic, when the translation is
available.

See the [yjl-sysusers.8](docs/yjl-sysusers.8.md) man page for usage.


yjl-sysusers.json
-----------------

The `yjl-sysusers.json` file in the top-level directory of the source
tarball is tailored to YellowJacket GNU/Linux.

The `yjl-sysusers.json` file installed by a package manager *should*
be tailored to the distribution the package is built for.

This JSON file includes the distribution-specific static UID/GID
assignments for certain users and groups, as well as distribution-
specific configurations for how to handle things like dynamic UID/GID
allocation.

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
that to be a bug I need to fix.

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


Distribution Packaging Rant
---------------------------

I literally __HATE__ distribution specific macros and how they have
proliferated in quantity and complexity since the ‘Good Old Days’.

Now get off my lawn, ya damn youngsters! Humor aside, it does seem RPM
packaging is losing the KISS 😛 concept and I think that is bad for
GNU/Linux.

A desktop user should not have to be a packaging guru in order to
successfully rebuild a spec file written for Distribution A on
the user’s Distribution B system. That is incredibly frustrating
and encourages users to just not utilize the package management
system, often leading to future problems and frustrations.

Something as simple and universal as ensuring the proper system users
and groups exist should not, for example, require a
`systemd-rpm-macros` package and the installation of a package-specific
user metadata file that often only have meaning to a specific distribution.

What the frack does SystemD have to do with basic Un•x user and group
management?

Yes, Fedora, I am talking smack about you. You are no longer the
distribution I loved when Red Hat Linux became Fedora Core.

Most RPM based distributions are guilty of the same thing, clearly
making RPM unsuitable as an LSB-mandated package manager.

I like it when used properly, but it is too easy for GNU/Linux
distributions to do the wrong thing and decrease cross-distribution
compatibility.

Some added complexity is sometimes necessary, but SystemD being
required for fundamental user and group management? No. Just No.

![Nancy Reagan: Just Say No (national archives PD)](justsayno.jpg)
