YJL-SYSUSERS
============

Section: System Management Commands (8)\
Updated: May 2023\
[Index](#index)

* * * * *

 

NAME
----

yjl-sysusers - Add system users and groups  

SYNOPSIS
--------

**yjl-sysusers** [*OPTIONS*] *account*

 

DESCRIPTION
-----------

`yjl-sysusers` is a wrapper script to the operating system `groupadd
(8)` and `useradd (8)` commands that allows respecting
the operating system static UID and GID assignment when available,
without the need to assign them manually.

Static UID and GID values, as well as some other parameters useful to
the `useradd (8)` command, are defined in the file `yjl-sysusers.json
(5)` which is normally located in the directory `/var/lib/yjl-sysusers`.

`yjl-sysusers` was developed with RPM package scriptlets in mind.

 

OPTIONS
-------

Options can be used when *account* has not been described in the
`yjl-sysusers.json (5)` file or to override default settings for
*account* as defined in the `yjl-sysusers.json (5)` file.

* `-h`, `--help`  
  Display help message and exit.

* `-c`, `--comment` *COMMENT*  
  Define the comment field to be used in the `/etc/passwd` file. This is
  used to provide a brief description of *account*. *COMMENT* must be
  printable ASCII, excluding the \\ and : characters. *COMMENT* must not
  exceed 60 characters.

* `d`, `--home` *HOME*  
  Define the home directory to be used with the system user account. It
  must be full path and can only use lower-case alpha-numeric characters
  plus underscore, forward-slash, and hyphen.

* `-s`, `--shell` *SHELL*  
  Define the login shell to be used with the system user account. If
  *SHELL* is not present in /etc/shells or is not installed on the system,
  then `/sbin/nologin` or `/bin/false` will be substituted.

  Any argument that is not full-path is invalid, so you can just use
  *noshell* as the *SHELL* arguement to guarantee that either
  `/sbin/nologin` or `/bin/false` are used as the login shell.

  `yjl-sysuers` will use `/sbin/nologin` for any *account* that does have
  a valid *SHELL* specified unless `/sbin/nologin` is not present on the
  system. In such cases, `/bin/false` is used instead.

* `--useradd` *{True,False}*  
  Define whether or not the user name *account* should be created.

  When `--useradd` is set to *False* then `--groupadd` is
  automatically set to *True*.

* `--groupadd` *{True,False}*  
  Define whether or not the group name *account* should be created.

  When `--groupadd` is set to *False* then `--useradd` is
  automatically set to *True*.

* `-g`, `--group` *GROUP*  
  Define the primary group for the user *account* with a different group
  name than *account*.

  If the group *GROUP* does not exist, it will be created automatically.

  When *GROUP* is defined, the group *account* will not be created
  regardless of `--groupadd` and the user *account* will be created
  regardless of `--useradd`.

* `--mkdir` *{True,False}*  
  Define whether or not the home directory for user *account* should be
  created. The default with system accounts is not to create the directory
  automatically.

 

USAGE NOTES
-----------

Python 3 is needed for **yjl-sysusers**. Testing has been done with the
CentOS 7 packaged Python 3.6.4 (released 2017 December 19) and with
vanilla Python 3.11.3 (released 2023 April 05).

The boolean options (**--useradd**, **--groupadd**, and **--mkdir**) are
case sensitive *True* or *False*.

When **--groupadd** *False* is used without using **-g**, **--group**
*GROUP* then the system group *nogroup* will be used as the primary
group for *account*.

 

PACKAGER NOTES
--------------

When creating an RPM (or other) package that has files owned by non-root
users and groups, you should use **yjl-sysusers** in the package *%pre*
scriptlet to ensure the appropriate users and groups exist at the time
the files are installed.

RPM packagers should use the macro **%{\_yjl\_sysusers}** rather than
the command **yjl-sysusers** or **/usr/sbin/yjl-sysusers**.

RPM packagers should **Requires(pre): %{\_yjl\_sysusers}**.

Packagers should avoid using **-c**, **--comment** *COMMENT* as it can
interfere with the string being properly translated via gettext i18n
facilities into the preferred language of the system.

Packagers should usually avoid using **--mkdir** *True*.

When **useradd** creates the *HOME* directory, it also copies the
contents of /etc/skel into that directory. Usually that is not desired.
It is often better to have the package create the **home** directory
when a home directory is needed.

Packagers should never assume the contents of the **yjl-sysusers.json**
file are correct for the package, but should specify the correct option
parameters when ensuring that *account* exists.

The primary motivation for this wrapper script is to allow for truly
portable RPM spec files that can build and install on many GNU/Linux
distributions while still respecting the static GID/UID assignments for
system users and groups that a distribution (or system administrator)
wants to enforce.

A secondary motive for this wrapper script is to allow for the
internationalization of system user account descriptions (the *COMMENT*
of /etc/passwd) at the time of package install.

Lazy packaging where the packager relies upon **yjl-sysusers.json** to
have correct user account parameters is not a motive for this package,
although compensating for lazy packaging was a motive for allowing sane
**useradd** defaults to be specified in that file.

 

CONFIGURATION
-------------

The default options on a per-*account* basis for accounts with preferred
static UID/GID assignment are in the **yjl-sysconfig.json** file. All
options except for the UID/GID can be overriden with options passed to
**yjl-sysusers**.

The range of dynamically generated UID/GID values is currently
hard-coded within the load\_id\_list() function. A future version of
this program will make that easier to configure.

The current default group name to use for user accounts created with
**--groupadd** *False* and without **-g**, **--group** *GROUP* is
currently hard-coded within the request\_gpname\_from\_json() function.
A future version of this program will make that easier to configure.

 

FILES
-----

/usr/sbin/yjl-sysusers

The Python 3 wrapper to **groupadd (8)** and **useradd (8)**&. This man
page describes use of that Python wrapper.

/var/lib/yjl-sysusers/yjl-sysusers.json

The JSON database on a per-*account* basis for preferred static UID/GID
and default options to pass to **useradd (8)**.

/usr/lib/rpm/macros.d/macros.yjl-sysusers

The definition of the **%{\_yjl\_sysusers}** macro that is used with
**rpmbuild (8)** to create RPM packages that utilize **yjl-sysusers**.

 

EXAMPLES
--------

**yjl-sysusers** **--useradd** *False* *plocate*

Ensure the *plocate* group exists, without creating a *plocate* user.

**yjl-sysusers** **-g** *mail* **-h** */var/lib/sendmail* **-s**
*noshell* *sendmail*

Ensure the *mail* group exists. Ensure the *sendmail* user exists,
creating it if necessary using */var/lib/sendmail* as the *HOME*
directory, using either /sbin/nologin or /bin/false as the login shell.

If the *sendmail* user does not already exist, it will be created with
*mail* as the primary group it belongs to.

**yjl-sysusers** **--useradd** *False* *mail* && \
 **yjl-sysusers** **--groupadd** *True* **--useradd** *True* \\ \

**-h** */var/lib/sendmail* **-s** *noshell* *sendmail* &&

\
 **usermod** **-a** **-G** *mail* *sendmail*

First ensure that the *mail* group exists. Then ensure that the
*sendmail* user exists as in the previous example, only if the user is
created, it is created with *sendmail* as the primary group. Finally,
add the *sendmail* user to the *mail* group.

As a packager, btw, that is my preferred method of dealing with system
users that need to belong to a system group of a different name.

 

EXIT STATUS
-----------

*0*

success

*1*

The program failed to create requested group and/or user.

 

TODO
----

Implement GNU gettext i18n and get some translations. Fix the bugs
listed below.

 

BUGS
----

The program should not be case sensitive with respect to the boolean
option parameters.

Default nogroup name and the dynamic range for system UID/GID should be
configurable without modifiying the **yjl-sysusers** script.

 

SEE ALSO
--------

**[yjl-sysusers.json](yjl-sysusers.json.5.md)(5)**,
**passwd(5)**,
**group(5)**,
**login.defs(5)**,
**shells(5)**,
**groupadd(8)**,
**useradd(8)**,
**usermod(8)**,
**rpmbuild(8)**

 

COPYLEFT
--------

The **yjl-sysusers** utility is Copyright (c) 2023 YellowJacket
GNU/Linux.

License SPDX:MIT
\<[https://spdx.org/licenses/MIT.html](https://spdx.org/licenses/MIT.html)\>.

**yjl-sysusers** is free software: you are free to change and
redistribute it. There is no WARRANTY, to the extent permitted by law.

This man page is Copyright (c) 2023 YellowJacket GNU/Linux.

License SPDX:GFDL-1.3-or-later \

\<[https://spdx.org/licenses/GFDL-1.3-or-later.html](https://spdx.org/licenses/GFDL-1.3-or-later.html)\>.

Accuracy of this man page is stroven for but explicitly is not
guaranteed.

 

AUTHORS
-------

Michael A. Peters \

\<[anymouseprophet@gmail.com](mailto:anymouseprophet@gmail.com)\>

* * * * *

 

Index
-----

[NAME](#lbAB)

[SYNOPSIS](#lbAC)

[DESCRIPTION](#lbAD)

[OPTIONS](#lbAE)

[USAGE NOTES](#lbAF)

[PACKAGER NOTES](#lbAG)

[CONFIGURATION](#lbAH)

[FILES](#lbAI)

[EXAMPLES](#lbAJ)

[EXIT STATUS](#lbAK)

[TODO](#lbAL)

[BUGS](#lbAM)

[SEE ALSO](#lbAN)

[COPYLEFT](#lbAO)

[AUTHORS](#lbAP)

* * * * *

This document was created by man2html, using the manual
pages.\
 Time: 00:36:48 GMT, May 28, 2023
