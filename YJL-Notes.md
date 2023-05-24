YellowJacket GNU/Linux User and Group Notes
===========================================

The Linux Standards Base (apparently now defunct) was a good concept
but had some bad results, such as specifyung RPM as a package manager.

That being said, much of what it did produce can be seen as ‘good practices’
that distributions should adhere to unless there is a reason to (e.g.
no distribution should be compelled to support installation of third-party
packages via RPM when plain old `tar` has been used for that in Un-x
for decades).

With respect users and groups, the LSB did not have much to say, although
it did suggest that UID/GID range 0--99 should be for statically allocated
users and groups with UID/GID range 100--499 reserved for dynamic
allocation by the system, basically suggesting the following in
`/etc/login.defs`:

    SYS_UID_MIN               100
    SYS_UID_MAX               499

Note that is a *recommondation* and not an LSB *requirement*.

YJL is actually using the 0--299 and the 400--499 range for ‘statically
allocated’, broken up into four sub-groups:

1. __0--179__  
   Majority of common system users and groups excluding SystemD users.
2. __180--199__  
   SystemD users and groups.
3. __200--299__  
   Special Interest Group integration.
4. __400--499__  
   YJL Specific users and groups that are less likely to be found on
   other GNU/Linux systems (like `texlive:texlive` at `450:450`)

YJL is actually using the 300--399 and the 500--999 range for ‘dynamically
allocated’, broken up into two sub-groups:

1. __300--399__  
   Used for users and groups for which static allocation fails because
   the system (for whatever unforseen reason) has already allocated the
   preferred static UID/GID to something else.
2. __500--999__  
   Used by `groupadd -s` dynamic allocation by the system.

Thus in the YJL `/etc/login.defs`:

    SYS_UID_MIN               500
    SYS_UID_MAX               999


Special Interest Group Integration
----------------------------------

One of the goals of YJL is to allow for special interest groups to form
that have their own package repositories outside the scope of YJL. Such
package repositories may have the need for system users and groups.

For example, a Citizen Science SIG may want to package a daemon that
allows home weather station data to be shared, or an Educational Software
SIG may need a daemon for retrieval of education content from a central
server.

In such cases, dynamic allocation of users and groups work just fine
but static assignment may be preferable especially if the user ever
has to reinstall the operating system but with preserved data.

Even if the packages are not part of YJL itself, allowing the assigment
of the UID/GID in the `yjl-sysusers.json` file is in my opinion a
reasonable thing to do.


YJL Specific Users and Groups
-----------------------------
YJL itself will have users and groups that are not necessarily ‘generic’
across GNU/Linux distributions.

For example, despite TeXLive itself being fairly ubiquitous across
GNU/Linux distributions, most distributions package it instead of
using the OS agnostic packaging.

YJL prefers the OS agnostic packaging but to make the install available
to many users, it then needs a specific user and group that is used for
keeping the install up-to-date.

I am also *toying* with the idea of home LAN backup software that does
not have the complexity of enterprise backup software. That also will
likely want its own user and group.
