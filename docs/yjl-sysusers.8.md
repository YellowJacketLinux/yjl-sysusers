YJL-SYSUSERS
============

Section: System Management Commands (8)\
Updated: June 2023\
[Index](#index)

* * * * *

 

NAME
----

yjl-sysusers - Add system users and groups  

SYNOPSIS
--------

__yjl-sysusers__ [*OPTIONS*] *account*

 

DESCRIPTION
-----------

__yjl-sysusers__

is a wrapper script to the operating system `groupadd (8)` and
`useradd (8)` commands that allows respecting the operating system
static UID and GID assignment when available, without the need to assign
them manually.

Static UID and GID values, as well as some other parameters useful to
the `useradd (8)` command, are defined in the file `yjl-sysusers.json
(5)` which is normally located in the directory
`/usr/share/yjl-sysusers`.

`yjl-sysusers` was developed with RPM package scriptlets in mind.

 

OPTIONS
-------

Options can be used when *account* has not been described in the
`yjl-sysusers.json (5)` file or to override default settings for
*account* as defined in the `yjl-sysusers.json (5)` file.

### `-h`, `--help`

Display help message and exit.

### `-v`, `--version`

Display version information and exit.

### `--bootstrap`

Validate the `yjl-sysusers.json (5)` file and if valid, dump the JSON
to screen.

The `--bootstrap` option is intended to be used during installation
and packaging.

### `-c`, `--comment` *COMMENT*

Define the comment field to be used in the /etc/passwd file. This is
used to provide a brief description of *account*. *COMMENT* must be
printable ASCII, excluding the \\ and : characters. *COMMENT* must not
exceed 120 characters.

### `-d`, `--home` *HOME*

Define the home directory to be used with the system user account. It
must be full path and can only use lower-case alpha-numeric characters
plus underscore, forward-slash, and hyphen.

### `-s`, `--shell` *SHELL*

Define the login shell to be used with the system user account. If
*SHELL* is not present in /etc/shells or is not installed on the system,
then `/sbin/nologin` or `/bin/false` will be substituted.

Any argument that is not full-path is invalid, so you can just use
*noshell* as the *SHELL* arguement to guarantee that either
`/sbin/nologin` or `/bin/false` are used as the login shell.

`yjl-sysusers` will use `/sbin/nologin` for any *account* that does not
have a valid *SHELL* specified unless `/sbin/nologin` is not present on
the system. In such cases, `/bin/false` is used instead.

### `-g`, `--group` *GROUP*

Define the primary group for the user *account* with a different group
name than *account*.

If the group *GROUP* does not exist, it will be created automatically.

### `--onlyuser`

Boolean flag. When this flag is specified, only the user *account* will
be created. If a valid primary group is not specified with the `-g`,
`--group` *GROUP* option and a group of *account* name does not
already exist, then the user will be put in the "nogroup" equivalent.
See `yjl-sysusers.json (5)`.

### `--onlygroup`

Boolean flag. When this flag is specified, only the group *account* will
be created.

### `--userandgroup`

Boolean flag. When this flag is specified, both a user and group
*account* will be created. This is actually the default behavior but the
`yjl-sysusers.json (5)` file might be configured to only create one or
the other for the specified *account* name.

### `--mkdir`

Boolean flag. When this flag is specified, the *HOME* directory for
*account* will be created by `useradd (8)` if it does not already
exist.

The default with system accounts us not to create the *HOME* directory
automatically because that often copies the contents of `/etc/skel` into
the *HOME* directory, which is rarely desired for system accounts.

### `--delete`

As of version 0.1.5 this is not yet implemented.

This flag is used to specify that any user and group of the name
*account* should be deleted. It does does not delete any files owned by
the user or group *account*.

 

USAGE NOTES
-----------

Python 3 is needed for `yjl-sysusers`. Testing has been done with the
CentOS 7 packaged Python 3.6.4 (released 2017 December 19) and with
vanilla Python 3.11.3 (released 2023 April 05).

 

PACKAGER NOTES
--------------

When creating an RPM (or other) package that has files owned by non-root
users and groups, you should use `yjl-sysusers` in the package *%pre*
scriptlet to ensure the appropriate users and groups exist at the time
the files are installed.

RPM packagers should use the macro

    %{_yjl_sysusers}

rather than the command `yjl-sysusers` or `/usr/sbin/yjl-sysusers`.

RPM pacjagers should:

    BuildRequires: yjl-sysusers

RPM packagers should:

    Requires(pre): %{_yjl_sysusers}

Packagers should avoid using `-c`, `--comment` *COMMENT* as it can
interfere with the string being properly translated via gettext i18n
facilities into the preferred language of the end user system.

Packagers should usually avoid using `--mkdir`.

When `useradd (8)` creates the *HOME* directory, it also copies the
contents of /etc/skel into that directory. Usually that is not desired.
It is often better to have the RPM package create and own the *home*
directory when a home directory is needed.

Packagers should never assume the contents of the `yjl-sysusers.json
(5)` file are correct for the package, but should specify the correct
option parameters when ensuring that *account* exists.

The primary motivation for this wrapper script is to allow for truly
portable RPM spec files that can build and install on many GNU/Linux
distributions while still respecting the static GID/UID assignments for
system users and groups that a distribution (or system administrator)
wants to enforce.

A secondary motive for this wrapper script is to allow for the
internationalization of system user account descriptions (the *COMMENT*
field of /etc/passwd) at the time of package install.

Lazy packaging where the packager relies upon `yjl-sysusers.json (5)`
to have correct user account parameters is not a motive for this
package, although compensating for lazy packaging was a motive for
allowing sane `useradd (8)` defaults to be specified in that file.

 

CONFIGURATION
-------------

The default options on a per-*account* basis for accounts with preferred
static UID/GID assignment are in the `yjl-sysconfig.json (5)` file.
Most options except for the UID/GID, protection from deletion, and
positive creation of the *HOME* directory can be overriden with options
passed to `yjl-sysusers`.

 

FILES
-----

    /usr/sbin/yjl-sysusers

The Python 3 wrapper to `groupadd (8)` and `useradd (8)`. This man
page describes use of that Python wrapper.

    /usr/share/yjl-sysusers/yjl-sysusers.json

The JSON database on a per-*account* basis for preferred static UID/GID
and default options to pass to `useradd (8)`.

    /usr/lib/rpm/macros.d/macros.yjl-sysusers

The definition of the `%{_yjl_sysusers}` macro that is used with
`rpmbuild (8)` to create RPM packages that utilize `yjl-sysusers`.

 

EXAMPLES
--------

    yjl-sysusers --onlygroup plocate

Ensure the *plocate* group exists, without creating a *plocate* user.

    yjl-sysusers -g mail -h /var/lib/sendmail -s noshell sendmail

Ensure the *mail* group exists. Ensure the *sendmail* user exists,
creating it if necessary using `/var/lib/sendmail` as the *HOME*
directory, and using either `/sbin/nologin` or `/bin/false` as the login
shell.

If the *sendmail* user does not already exist, it will be created with
*mail* as the primary group it belongs to.

    yjl-sysusers --onlygroup mail && \
    yjl-sysusers --userandgroup  \
      -h /var/lib/sendmail -s noshell sendmail && \
    usermod -a -G mail sendmail

First ensure that the *mail* group exists. Then ensure that the
*sendmail* user exists as in the previous example, only if the user is
created, it is created with *sendmail* as the primary group. Finally,
add the *sendmail* user to the *mail* group.

As a packager, btw, that is my preferred method of dealing with system
users that need to belong to a system group of a different name.

 

EXIT STATUS
-----------

__0__ --- success

__1__ --- The program failed to create requested group and/or user.

 

TODO
----

Implement GNU gettext i18n and get some translations. Fix the bugs
listed below.

 

BUGS
----

There quite likely are some.

 

SEE ALSO
--------

* __[yjl-sysusers.json(5)](yjl-sysusers.json.5.md)__
* __passwd(5)__
* __group(5)__
* __login.defs(5)__
* __shells(5)__
* __groupadd(8)__
* __useradd(8)__
* __usermod(8)__
* __rpmbuild(8)__

 

COPYLEFT
--------

The `yjl-sysusers` utility is Copyright (c) 2023 YellowJacket
GNU/Linux.

License: [SPDX:MIT](https://spdx.org/licenses/MIT.html).

`yjl-sysusers` is free software: you are free to change and
redistribute it. There is no WARRANTY, to the extent permitted by law.

This man page is Copyright (c) 2023 YellowJacket GNU/Linux.

License: [SPDX:GFDL-1.3-or-later](https://spdx.org/licenses/GFDL-1.3-or-later.html).

Accuracy of this man page is stroven for but explicitly is not
guaranteed.

 

AUTHORS
-------

[Michael A. Peters](mailto:anymouseprophet@gmail.com)

* * * * *

 

Index
-----

[NAME](#name)

[SYNOPSIS](#synopsis)

[DESCRIPTION](#description)

[OPTIONS](#options)

[USAGE NOTES](#usage-notes)

[PACKAGER NOTES](#packager-notes)

[CONFIGURATION](#configuration)

[FILES](#files)

[EXAMPLES](#examples)

[EXIT STATUS](#exit-status)

[TODO](#todo)

[BUGS](#bugs)

[SEE ALSO](#see-also)

[COPYLEFT](#copyleft)

[AUTHORS](#authors)

* * * * *

This document was created by man2html, using the manual
pages.\
 Time: 07:08:43 GMT, June 02, 2023
