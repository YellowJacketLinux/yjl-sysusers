YJL-SYSUSERS.JSON
=================

Section: File Formats (5)\
Updated: June 2023\
[Index](#index)

* * * * *

 

NAME
----

yjl-sysusers.json - static system account UID/GID database  

DESCRIPTION
-----------

The `yjl-sysusers.json` file is a JSON dictionary of system user and
group names which have desired static assignment of User ID (UID) and
Group ID (GID).

JSON (JavaScript Object Notation) was chosen because of both its ease of
use with Python and its ubiquity with programming languages in general.

The `yjl-sysusers.json` file is used by the `yjl-sysusers (8)`
wrapper to the `useradd (8)` and `groupadd (8)` system administration
utilities.

In addition to static UID and GID assignments, `yjl-sysusers.json`
also has optional default options to pass to the `useradd (8)` command
when creating the specified system user account.

Additionally, the `yjl-sysusers.json` file may have an entry titled
__00-CONFIG__ that configures how the `yjl-sysusers (8)` utility
handles dynamically assigned system UID and GID numbers.

 

FILE LOCATION
-------------

Ordinarily this file should be installed as:

    /usr/share/yjl-sysusers/yjl-sysusers.json

The file is a configuration file but it is also a read-only database and
once installed it should not be modified except by re-installation of
the package that provides it.

 

ACCOUNT NAME INDEX
------------------

Every potential system user and group account for which a statically
assigned UID/GID desired should have an __ACCOUNT NAME OBJECT__.

The __ACCOUNT NAME INDEX__ is the index of that object in the
`yjl-sysusers.json` file and must match the name of the potential
system user or group account.

The `yjl-sysusers (8)` utility is stricter about system account names
than the `useradd (8)` utility. It only allows lower-case ASCII
alpha-numeric names with the addition of an underscore and hyphen dash,
and the first character must be a letter or underscore. A \$ at the end
of a system user or group name is also allowed.

 

ACCOUNT NAME OBJECTS
--------------------

Each system user and/or group account for which a static ID is desired
should have an __ACCOUNT NAME OBJECT__ using the __ACCOUNT NAME__ as the
index for the object.

The following case sensitive properties of an __ACCOUNT NAME OBJECT__
describe the defaults for the system user/group accounts of the name
__ACCOUNT NAME INDEX__:

### `myid`

Integer. Required.

This property is the static UID/GID that should be used, if not already
in use, when creating a user and/or group of the __ACCOUNT NAME INDEX__.

Any cases where a user and group of different names share the same
UID/GID, such as is often the case with the `nobody` and `nogroup`
entries, the `dupok` list property in the __000-CONFIG__ configuration
entry must have that ID in the list.

The `root` entry must have a `myid` value of `0`.

The `myid` property should not be within the dynamically assigned system
user range identified by `SYS_UID_MIN` and `SYS_UID_MAX` in the
GNU/Linux distribution default `/etc/login.defs` configuration file.
See `man 5 login.defs`.

### `groupid`

Integer. Optional.

This property is exclusively for cases where both a user and group with
the name __ACCOUNT NAME INDEX__ should be created, but with a statically
assigned GID that differs from the UID.

In this special case, both boolean properties `usr` and `grp` must be
assigned values of `true` and the string property `group` must not be
set.

The `groupid` property should not be within the dynamically assigned
system user range identified by `SYS_UID_MIN` and `SYS_UID_MAX` in
the GNU/Linux distribution default `/etc/login.defs` configuration
file. See `man 5 login.defs`.

### `usr`

Boolean. Recommended. Default value is *false*.

This property defines whether the default action of `yjl-sysusers (8)`
should be to create a user account with the the user name of the
__ACCOUNT NAME INDEX__.

If the `usr` property is either not defined or defined to *false* then
the `grp` property must be defined to *true*.

### `grp`

Boolean. Recommended. Default value is *false*.

This property defines whether the default action of `yjl-sysusers (8)`
should be to create a group account with the group name of the __ACCOUNT
NAME INDEX__.

If the `grp` property is either not defined or defined to *false* then
the `usr` property must be defined to *true*.

### `group`

String. Optional, rarely appropriate.

When present, this property defines the primary group that a user of the
same name as the __ACCOUNT NAME INDRX__ should belong to when a group of
the same name is not to be created.

When the `group` property is present, the `usr` property must be defined
as *true* and the `grp` property should either not be defined or defined
as *false*.

When the `group` property is present, the string value should match the
name of another __ACCOUNT NAME INDEX__ that has a `grp` property of
*true*.

The `group` property can not be set in combination with the `groupid`
property.

### `comment`

String. Optional, recommended.

When present, this property defines the default ASCII English version of
the *COMMENT* (also called *GECOS*) field of the /etc/passwd file (see
`man 5 passwd`) when `yjl-sysusers (8)` creates a user account using
the name `ACCOUNT NAME INDEX`.

When the `comment` property is not defined, `yjl-sysusers (8)` will
default to using "__ACCOUNT NAME INDEX__ system user account" as the
`COMMENT` when it creates a user account using the name __ACCOUNT NAME
INDEX__.

The `comment` property must be printable ASCII of no more than 120
characters in length and must not contain a colon or a back-slash.

When translations are available, `yjl-sysusers (8)` will use
translations of this property as provided by GNU gettext for systems
that uses a non-English default language.

### `homedir`

String. Optional. Defaults to `/dev/null`.

When present, this property defines the default `directory` field of the
`/etc/passwd` file (see `man 5 passwd`) when `yjl-sysusers (8)`
creates a user account using the name __ACCOUNT NAME INDEX__.

This is usually called the "home directory" because it defines the
*HOME* environment variable for the user account.

The `yjl-sysusers (8)` utility enforces stricter rules for system
accounts, only allowing *homedir* values that are lower case
alpha-numeric plus underscore, forward-slash, and hyphen dashes.

### `shell`

String. Optional, rarely appropriate.

When present, this property defines the default `shell` field of the
`/etc/passwd` file (see `man 5 passwd`) when `yjl-sysusers (8)`
creates a user account using the name __ACCOUNT NAME INDEX__.

The only valid values for the `shell` property (unless the `atypshell`
property is set to *true*) of an __ACCOUNT NAME OBJECT__ in the
`yjl-sysusers.conf` file are `/bin/bash` and `/bin/sh`.

Additional values may be specified to the `yjl-sysusers (8)` utility
as long as the specified shell is in `/etc/shells` (see `man 5 shells`).

When the __ACCOUNT NAME OBJECT__ does not have a `shell` property and a
valid *SHELL* option is not passed to the `yjl-sysusers (8)` utility,
the `yjl-sysusers (8)` utility will use `/sbin/nologin` (if it
exists on the system) or `/bin/false` for the `shell` field of the
`/etc/passwd` file when it creates a user account named __ACCOUNT NAME
INDEX__.

### `atypshell`

Boolean. Optional, defaults to *false*.

When this property is *true*, no validation of the `shell` is performed
except to verify it is a valid filesystem path.

### `mkdir`

Boolean. Optional, defaults to *false*.

When this property is set to *true* then the default behavior of
`yjl-sysusers (8)` will be to create the home directory for __ACCOUNT
NAME INDEX__ if the directory does not already exist when `yjl-sysusers
(8)` is asked to create a user account for __ACCOUNT NAME INDEX__.

In most cases, that is not desired for system user accounts because it
will copy the contents of `/etc/skel` into the created directory.

If the `mkdir` property is either not set or is set to *false* then the
default behavior of `yjl-sysusers (8)` will be to NOT create the home
directory for __ACCOUNT NAME INDEX__ when it is asked to add the
__ACCOUNT NAME INDEX__ user.

### `protected`

Boolean. Optional, defaults to *false*.

This property defines whether or not __ACCOUNT NAME INDEX__ should be
protected from deletion by the `yjl-sysusers (8)` utility.

When the `protected` option is set to *true*, attempts to delete a group
or user with the __ACCOUNT NAME INDEX__ name by the `yjl-sysusers (8)`
utility will be ignored.

 

000-CONFIG
----------

This section of the `yjl-sysusers.json` file modifies some of the
default behavior of `yjl-sysusers (8)`.

### `description`

String. Optional.

A UTF-8 string describing the GNU/Linux distribution and version the
`yjl-sysusers.conf` file was created for.

### `maintainer`

String. Optional.

A UTF-8 string identifying the maintainer of the `yjl-sysusers.conf`
file.

### `modified`

String, ISO-8601 Timestamp, Optional.

Information about when the `yjl-sysusers.json` file was last modified.

When used, it must include at least the date and should be in ISO-8601
format, e.g. `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`.

### `nogroup`

String. Optional, defaults to "*nogroup*".

An ASCII string following the rules of an __ACCOUNT NAME INDEX__ that
defines what group a system user should use for its primary group if a
group of the same name is not to be created and a specified group name
is not provided.

### `dupok`

List of Integers. Optional, defaults to empty list.

A JSON list of integers for which more than one __ACCOUNT NAME OBJECT__
may share the same `myid` or `mygroup` value.

This is necessary when a static UID/GID is assigned to a different user
name and group name.

This also can also be used for cases where two different services
provide the same capabilities resulting in them not likely to be
installed at the same time, such as the multiple different
implementations of the `locate (1)` database.

### `dynamic`

List of Object Dictionaries. Optional.

Each object dictionary in the list describes a range of suitable IDs
that `yjl-sysusers (8)` can use when it needs a dynanic UID/GID.

Each object dictionary must have a `min` property and a `max` property
which reference an integer value.

The integer associated with the `max` property must be larger than the
integer associated with the `min` property and the range between should
not include any IDs that are used for static allocation.

When the `dynamic` list of dictionary properties is not specified,
`yjl-systemusers (8)` will use the single range of 200 to 499.

 

EXAMPLE
-------

The following is a brief example of a valid `yjl-sysusers.json` file.

    {
        "000-CONFIG": {
            "description": "A generic yjl-sysusers.json file.",
            "maintainer": "Joe Cool <joe@example.org>",
            "modified": "2023-06-01",
            "dupok": [65534],
            "dynamic": [{
                "min": 200,
                "max": 999
            ]},
        },
        "root": {
            "myid": 0,
            "usr": true,
            "grp": true,
            "comment": "root super-user account",
            "homedir": "/root",
            "shell": "/bin/bash",
            "mkdir": true
        },
        "plocate": {
            "myid": 23,
            "usr": false,
            "grp": true
        },
        "fetchmail": {
            "myid": 38,
            "usr": true,
            "grp": false,
            "group": "nogroup"
        },
        "nobody": {
            "myid": 65534,
            "usr": true,
            "grp": false,
            "group": "nogroup",
            "comment": "Unprivileged system user"
        },
        "nogroup": {
            "myid": 65534,
            "usr": false,
            "grp": true
        }
    }

It is a good idea to pass your `yjl-sysusers.json` file through a JSON
validator such as [https://jsonlint.com/](https://jsonlint.com/)
before trying to use it with `yjl-sysusers (8)`.

 

MODIFICATION
------------

I recommend against modifications being applied to an installed
`yjl-sysusers.json` file. A JSON mistake will break the ability of
`yjl-sysusers (8)` to function.

It is better to update the JSON in the `yjl-sysusers` source package
and build an updated package, so that the modification will be validated
during package creation.

 

FILES
-----

    /usr/share/yjl-sysusers/yjl-sysusers.json

 

SEE ALSO
--------

* __[yjl-sysusers(8)](yjl-sysusers.8.md)__
* __passwd(5)__
* __group(5)__
* __login.defs(5)__
* __shells(5)__
* __groupadd(8)__
* __useradd(8)__

 

COPYLEFT
--------

The `yjl-sysusers (8)` utility is Copyright (c) 2023 YellowJacket
GNU/Linux.

License: [SPDX:MIT](https://spdx.org/licenses/MIT.html).

`yjl-sysusers` is free software: you are free to change and
redistribute it. There is no WARRANTY, to the extent permitted by law.

This man page is Copyright (c) 2023 YellowJacket GNU/Linux.

License [SPDX:GFDL-1.3-or-later](https://spdx.org/licenses/GFDL-1.3-or-later.html).

Accuracy of this man page is stroven for but is explicitly not
guaranteed.

 

AUTHORS
-------

[Michael A. Peters](mailto:anymouseprophet@gmail.com)

* * * * *

 

Index
-----

[NAME](#name)

[DESCRIPTION](#description)

[FILE LOCATION](#file-location)

[ACCOUNT NAME INDEX](#account-name-index)

[ACCOUNT NAME OBJECTS](#account-name-objects)

[000-CONFIG](#000-config)

[EXAMPLE](#example)

[MODIFICATION](#modification)

[FILES](#files)

[SEE ALSO](#see-also)

[COPYLEFT](#copyleft)

[AUTHORS](#authors)

* * * * *

This document was created by man2html, using the manual
pages.\
 Time: 07:08:43 GMT, June 02, 2023
