YJL-SYSUSERS.JSON
=================

Section: File Formats (5)\
Updated: May 2023\
[Index](#index)

* * * * *

 

NAME
----

yjl-sysusers.json - static system user UID/GID database  

DESCRIPTION
-----------

The **yjl-sysusers.json** file is a JSON dictionary of system user and
group names which have desired static assignment of User ID (UID) and
Group ID (GID).

JSON (JavaScript Object Notation) was chosen because of both its ease of
use with Python and its ubiquity with programming languages in general.

The **yjl-sysusers.json** file is used by the **yjl-sysusers (8)**
wrapper to **useradd (8)** and **groupadd (8)** system administration
utilities.

In addition to static UID and GID assignments, **yjl-sysusers.json**
also has optional default options to pass to the **useradd (8)** command
when creating the specified system user account.

Additionally, the **yjl-sysusers.json** file may have an entry titled
**00-CONFIG** that configures how the **yjl-sysusers (8)** utility
handles dynamically assigned system UID and GID numbers.

 

FILE LOCATION
-------------

Ordinarily this file should be installed as:

**/var/lib/yjl-sysusers/yjl-sysusers.json**

The file is a configuration file but it is also a read-only database and
once installed it should not be modified except by re-installation of
the package that provides it.

 

ACCOUNT NAME INDEX
------------------

Every potential system user and group account for which a statically
assigned UID/GID desired should have an **ACCOUNT NAME OBJECT**.

The **ACCOUNT NAME INDEX** is the index of that object in the
**yjl-sysusers.json** file and must match the name of the potential
system user or group account.

The **yjl-sysusers (8)** utility is stricter about system account names
than the **useradd (8)** utility. It only allows lower-case ASCII
alpha-numeric names with the addition of an underscore and hyphen dash,
and the first character must be a letter or underscore. A \$ at the end
of a system user or group name is also allowed.

 

ACCOUNT NAME OBJECTS
--------------------

Each system user and/or group account for which a static ID is desired
should have an **ACCOUNT NAME OBJECT** using the **ACCOUNT NAME** as the
index for the object.

The following case sensitive properties of an **ACCOUNT NAME** describe
the defaults for the **ACCOUNT**:

*myid*

Integer. Required.

This property is the static UID/GID that should be used, if not already
in use, when creating a user and/or group of the **ACCOUNT NAME**.

The **nobody** and **nogroup** entries may share the same *myid* values
but all other **ACCOUNT NAME OBJECTS** must have a unique *myid* value.

The **nobody** and **nogroup** entries may have a *myid* value of
*65534* but all other **ACCOUNT NAME OBJECTS** must have a value below
*1000*.

The **root** entry must have a *myid* value of *0*.

The *myid* property should not be within the dynamically assigned system
user range identified by *SYS\_UID\_MIN* and *SYS\_UID\_MAX* in the
GNU/Linux distribution default **/etc/login.defs** configuration file.
See **man 5 login.defs**.

*usr*

Boolean. Recommended. Default value is *false*.

This property defines whether the default action of **yjl-sysusers (8)**
should be to create a user account with the the user name of the
**ACCOUNT NAME INDEX**.

If the *usr* property is either not defined or defined to *false* then
the *gpr* property must be defined to *true*.

*grp*

Boolean. Recommended. Default value is *false*.

This property defines whether the default action of **yjl-sysusers (8)**
should be to create a group account with the group name of the **ACCOUNT
NAME INDEX**.

If the *grp* property is either not defined or defined to *false* then
the *usr* property must be defined to *true*.

*group*

String. Optional, rarely appropriate.

When present, this property defines the primary group that a user of the
same name as the **ACCOUNT NAME INDRX** should belong to when a group of
the same name is not to be created.

When the *group* property is present, the *usr* property must be defined
as *true* and the *grp* property should either not be defined or defined
as *false*.

When the *group* property is present, the string value should match the
name of another **ACCOUNT NAME INDEX** that has a *grp* property of
*true*.

*comment*

String. Optional, recommended.

When present, this property defines the default ASCII English version of
the *COMMENT* (also called *GECOS*) field of the /etc/passwd file (see
**man 5 passwd**) when **yjl-sysusers (8)** creates a user account using
the name **ACCOUNT NAME INDEX**.

When the *comment* property is not defined, **yjl-sysusers (8)** will
default to using "**ACCOUNT NAME INDEX** system user account" as the
*COMMENT* when it creates a user account using the name **ACCOUNT NAME
INDEX**.

The *comment* property must be printable ASCII of no more than 60
characters in length and must not contain a colon or a back-slash.

When translations are available, **yjl-sysusers (8)** will use
translations of this property as provided by GNU gettext for systems
that uses a non-English default language.

*homedir*

String. Optional. Defaults to /dev/null.

When present, this property defines the default *directory* field of the
/etc/passwd file (see **man 5 passwd**) when **yjl-sysusers (8)**
creates a user account using the name **ACCOUNT NAME INDEX**.

This is usually called the "home directory" because it defines the
*HOME* environment variable for the user account.

The **yjl-sysusers (8)** utility enforces stricter rules for system
accounts, only allowing *homedir* values that are lower case
alpha-numeric plus underscore, forward-slash, and hyphen dashes.

*shell*

String. Optional, rarely appropriate.

When present, this property defines the default *shell* field of the
/etc/passwd file (see **man 5 passwd**) when **yjl-sysusers (8)**
creates a user account using the name **ACCOUNT NAME INDEX**.

The only valid values for the *shell* property of an **ACCOUNT NAME
OBJECT** in the **yjl-sysusers.conf** file are */bin/bash* and
*/bin/sh*.

Additional values may be specified to the **yjl-sysusers (8)** utility
as long as the specified shell is in /etc/shells (see **man 5 shells**).

When the **ACCOUNT NAME OBJECT** does not have a *shell* property and a
valid *SHELL* option is not passed to the **yjl-sysusers (8)** utility,
the **yjl-sysusers (8)** utility will use **/sbin/nologin** (if it
exists on the system) or **/bin/false** for the *shell* field of the
/etc/passwd file when it creates a user account named **ACCOUNT NAME
INDEX**.

*mkdir*

Boolean. Optional, defaults to *false*.

When this property is set to *true* then the default behavior of
**yjl-sysusers (8)** will be to create the home directory for **ACCOUNT
NAME** if the directory does not already exist when **yjl-sysusers (8)**
is asked to create a user account for **ACCOUNT NAME INDEX**.

In most cases, that is not desired for system user accounts because it
will copy the contents of /etc/skel into the created directory.

If the *mkdir* property is either not set or is st to *false* then the
default behavior of **yjl-sysusers (8)** will be to NOT create the home
directory for **ACCOUNT NAME INDEX** when it is asked to add the
**ACCOUNT NAME INDEX** user.

 

000-CONFIG
----------

This space is reserved for future content when the feature is
implemented, likely in June 2023.

 

EXAMPLE
-------

The following is a brief example of a valid **yjl-sysusers.json** file.

{

"root": {

"myid": 0, \
 "usr": true, \
 "grp": true, \
 "comment": "root super-user account", \
 "homedir": "/root", \
 "shell": "/bin/bash", \
 "mkdir": true

}, \
 "plocate": {

"myid": 23, \
 "usr": false, \
 "grp": true

}, \
 "fetchmail": {

"myid": 38, \
 "usr": true, \
 "grp": false, \
 "group": "nogroup"

}, \
 "nobody": {

"myid": 65534, \
 "usr": true, \
 "grp": false, \
 "group": "nogroup", \
 "comment": "Unprivileged system user"

}, \
 "nogroup": {

"myid": 65534, \
 "usr": false, \
 "grp": true

}

}

Obviously the **root** user does not need to be mentioned in the JSON
file, that user must exist on the system before the **yjl-sysusers (8)**
utility can be used, but it is good to have it for completeness as well
as a rather complete example entry.

 

MODIFICATION
------------

I recommend against modifications being applied to an installed
**yjl-sysusers.json** file. A JSON mistake will break the ability of
**yjl-sysusers (8)** to function.

It is better to update the JSON in the **yjl-sysusers** source package
and build an updated package, so that the modification will be validated
during package creation.

 

FILES
-----

/var/lib/yjl-sysuers/yjl-sysusers.json

 

SEE ALSO
--------

**[yjl-sysusers](/man/man2html?8+yjl-sysusers)(8)**,
**[passwd](/man/man2html?5+passwd)(5)**,
**[group](/man/man2html?5+group)(5)**,
**[login.defs](/man/man2html?5+login.defs)(5)**,
**[shells](/man/man2html?5+shells)(5)**,
**[groupadd](/man/man2html?8+groupadd)(8)**,
**[useradd](/man/man2html?8+useradd)(8)**

 

COPYLEFT
--------

The **yjl-sysusers (8)** utility is Copyright (c) 2023 YellowJacket
GNU/Linux.

License SPDX:MIT
\<[https://spdx.org/licenses/MIT.html](https://spdx.org/licenses/MIT.html)\>.

**yjl-sysusers** is free software: you are free to change and
redistribute it. There is no WARRANTY, to the extent permitted by law.

This man page is Copyright (c) 2023 YellowJacket GNU/Linux.

License SPDX:GFDL-1.3-or-later \

\<[https://spdx.org/licenses/GFDL-1.3-or-later.html](https://spdx.org/licenses/GFDL-1.3-or-later.html)\>.

Accuracy of this man page is stroven for but is explicitly not
guaranteed.

 

AUTHORS
-------

Michael A. Peters \

\<[anymouseprophet@gmail.com](mailto:anymouseprophet@gmail.com)\>

* * * * *

 

Index
-----

[NAME](#lbAB)

[DESCRIPTION](#lbAC)

[FILE LOCATION](#lbAD)

[ACCOUNT NAME INDEX](#lbAE)

[ACCOUNT NAME OBJECTS](#lbAF)

[000-CONFIG](#lbAG)

[EXAMPLE](#lbAH)

[MODIFICATION](#lbAI)

[FILES](#lbAJ)

[SEE ALSO](#lbAK)

[COPYLEFT](#lbAL)

[AUTHORS](#lbAM)

* * * * *

This document was created by man2html, using the manual
pages.\
 Time: 00:35:00 GMT, May 28, 2023
