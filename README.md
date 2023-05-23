yjl-sysusers
============

At present this is vaporware.

This project will (likely) include two utilities, primarily intended
to be used in RPM scriptlets (largely the `%pre` scriptlets).

The purpose is to provide an easy way to provide consistent user ID
and group ID numbers for system users (as opposed to human login users).


yjl-sysgroup
------------

This will be a utility for adding a system `group` and will take a
single argument: the name of the group being added as a system group.

If the group already exists, `yjl-sysgroup` will simply return the ID
of the existing group.

If the group *does not* already exist, the utility will check with the
`yjl-sysusers.json` file to determine if there is a preferred Group ID
for the specified group name.

When there is a preferred Group ID, the utility will check to see if
the specified Group ID is already in use. When it is not already in
use, the utility will create the group and return the ID of the freshly
created group.

When there *is not* a preferred Group ID or if the preferred Group ID
is *already in use*, the utility will use the first available Group ID
between 300 and 399 inclusive, or the first available Group ID above
499 in the highly unlikely event all Group IDs between 300 and 399 are
already used, and then return the ID of the freshly created group.


yjl-sysuser
-----------

This will be a utility for adding a system `user` and will take a single
arguement plus options to override defaults. The single argument will
be the username of the system user to add.

If the user already exists, `yjl-sysuser` will simply return the ID of
the existing user.

If the user *does not* already exist, the utility will check with the
`yjl-sysusers.json` file to determine if there is a preferred User ID
for the user, and what group the user should belong to.

If the `group` was specified as an option, that group *always* takes
precedence. Otherwise, if a group name is specified in the `yjl-sysusers.json`
file, that is used as the group name. Others, if the `yjl-sysusers.json`
specifies both a `uid` and a `gid` that are identical, then the requested
username is used as the default group name. Otherwide, the group `nogroup`
will be used.

The `yjl-sysgroup` utility is used with the determined group name to
retrieve the associated Group ID (creating the group if necessary).

If the `yjl-sysusers.json` has a preferred User ID that is not already
in use, that is the User ID that will be used in combination with the
Group ID.

If the User ID is not specified in the `yjl-sysusers.json` file, then
the first available user ID between 300 and 399 inclusive will be used,
or the first available User ID above 499 in the highly unlikely event
all User IDs between 300 and 399 are already used.

If the `comment` was specified as an option, that comment takes precedence.
Otherwise if a default `comment` is specified in the `yjl-sysusers.json`
file, that comment is used. Otherwise no comment is used.

If the `homedir` was specified as an option, that directory is used
as the `home` directory for the user. Otherwise if a `home` directory
is specified in the `yjl-sysusers.json` file, that will be used as the
home directory. Otherwise `/dev/null` is used as the home directory.

If `/dev/null` is the home directory, then `/bin/false` will be the
login shell. On the other hand if an actual directory is used used
as the home directory and a *valid* `shell` was specified as an option,
that shell is used as the default command shell. If a *valid* `shell`
was not specified but a default exists in the `yjl-sysusers.json` file,
that will be used as the defaut shell (of course verifying it is a
valid shell as well). When there is no valid shell specified, then
`/bin/false` is used.

When a valid shell is specified and the boolean option `skel` is set
to `true` then the `/etc/skel` files will be copied into the home
directory. When the boolean option `skel` is not specified but the
`yjl-sysusers.json` file specifies it for that user and it is set
to `true` then `/etc/skel` files will be copied into the home directory.

Once the user is created, `yjl-sysuser` will return the ID of the
created user.

Adding a system user to groups other than the primary group for that
user is *not directly supported*. To accomplish that task should it
actually be necessary, use the `yjl-sysgroup` utility first to ensure
the group exists and then use `usermod` command.


yjl-sysusers.json
-----------------

This JSON file contains all the information needed to create system
users and groups for YellowJacket GNU/Linux.

It is currently a work in progress.

It is based on the users and groups used by LFS/BLFS 11.3 with some
minor modifications:

* All of the various systemd users have been moved to start with a
  UID/GID of 180, freeing up nine UID/GID combinations under 100.

* The Group ID 23 (formerly associated with `systemd-journal`) is now
  associated with the `plocate` group. Note there is no `plocate` user.

* The `mail` Group has been moved to Group ID 30 (formerly unused) so
  that it does not share the same ID as the `sendmail` user. The
  `sendmail` Group has been defined with Group ID 34 to match the
  `sendmail` user. This user and and group may be removed in the
  future, along with the `smmsp` user and group.

* The UID/GID combination of 40/40 has been changed from `mysql` to
  `mariadb` but *I might* revert that when I package MariaDB.

Initially I was going to try to keep in sync with LFS/BLFS but I do
not think that is of any particular benefit, so I probably will use
their numbering system initially but likely further diverge as time
goes by.

With respect to YJL, there is some already likely some technical debt
within the assigned numbers. For example, YJL will almost certainly
*never* package [BIND](https://www.isc.org/bind/) so the UID/GID
associated with `named` *probably* should be considered recyclable.

If YJL ever has the need to package an authoritative name server, it
would almost certainly be [NSD](https://www.nlnetlabs.nl/projects/nsd/about/)
although I kind of doubt a hobbyist desktop distribution needs an
authoritative naneserver.

[Sendmail](https://www.proofpoint.com/us/products/email-protection/open-source-email-solution)
is another daemon likely to never be packaged for YJL, [Exim](https://www.exim.org/)
or [Postfix](https://www.postfix.org/) are much more appropriate for
hobbyist mail server needs (both also usually do well in Enterprise).

### JSON Format

This describes the constraines of the JSON file.

#### User and Group Names

Every object represents a user and/or group name and thus must be a
valid Unix username as defined in __man 8 useradd__

    Usernames may contain only lower and upper case letters, digits,
    underscores, or dashes. They can end with a dollar sign. Dashes
    are not allowed at the beginning of the username. Fully numeric
    usernames and usernames . or .. are also disallowed. It is not
    recommended to use usernames beginning with . character as their
    home directories will be hidden in the ls output. In regular
    expression terms: [a-zA-Z0-9_.][a-zA-Z0-9_.-]*[$]?

    Usernames may only be up to 32 characters long.

The JSON file itself does not care but since the utilities will validate
a username before querying the JSON file, invalid usernames in the JSON
file will never be used.

For system users and groups, I am actually included to restrict it to
lowercase alphanumeric strings no longer than 24 characters.

#### User and Group ID Numbers

Every object __MUST__ have a `uid` and/or `gid` property that points
to an appropriate non-negative integer value not used by another object.
When an object has both, they must be defined to the same integer.

For *most* system users, the `uid` and/or `gid` __MUST__ not exceed
65534. However with the exception of user `nobody` and group `nogroup`
the values in the JSON file really have no reason to ever exceed 499.

In YJL, the range 0--179 is used for most system-related users and groups
that are typically found on GNU/Linux systems, with the exception of
SystemD related users. When possible, non-SystemD system-related users
should be kept below 100 when possible but that may not always be possible.

In YJL, the range 180--199 is used for SystemD related users and groups.

In YJL, the range 200--299 is reserved for future special interest use.

In YJL, the range 300--399 is used for cases when the requested UID/GID
is already in use on the system. Normally that will not happen, but
there may be cases when a system administrator need to use a specific
UID/GID for something else.

The JSON file thus should not specify IDs in the 200-399 range, however
the 200--299 range *could* be used in the future for special interest
needs.

In YJL, the range 400--499 is reserved for YJL specific use cases, such
as UID/GID 450 for the TeXLive administrator.

In YJL, the range 500--999 is for System Adminstrator to use for their
own non-human user needs. The JSON file thus should not specify IDs
above 499 with the noted exception of `nobody` and `nogroup`.

#### User Comment

When the object has a `uid` it *should* also have a `comment` property
that describes the purpose of the account although that is not strictly
necessary.

For system users, I am restricting the comments to 7-bit ASCII printable
characters excluding the `\`, `#`, and `:` characters, and restricting
it to 48 characters in length.

#### Homedir

When the object has a `uid` it *may* also have a `homedir` property.
The property __MUST__ be a legal absolute file path starting with a
`/` and __MUST NOT__ include white space. Best practice, each directory
name should be lower case `[a-z]` and Linux FHS compliant for the purpose
of the system user account.

#### Shell

When the object has a `homedir` it *may* also have a `shell` property,
although in most cases it likely will not.

If the shell is not in `/etc/shells` then `/bin/false` will be used.
The entries `/bin/bash` and `/bin/sh` are *always* valid on GNU/Linux
systems, so the JSON file is restricted to those values for the `shell`
property.

#### Skeleton Files

When the object has a `shell` property it *may* alsi have a `skel`
property. This is a boolean property. If present *and* it evaluates
to `true`, then the home directory will be created and the contents
of `/etc/skel` copied to it.


Validation Failures and Handling
--------------------------------

If the user running the `yjl-sysgroup` and `yjl-sysuser` does not
have `root` privileges, the utilities will exit with a failure status.

If the JSON file is malformed, both the `yjl-sysgroup` and `yjl-sysuser`
utilities will exit with a failure status. That should never happen
unless the JSON file is improperly modified after install.

If a username or groupname passed as an argument does not validate,
the `yjl-sysgroup` and `yjl-sysuser` utilities will exit with a failure
status.

If the `yjl-sysgroup` utility is used with a group name contained as an
object in the JSON file which does not have a valid `gid` property, the
`yjl-sysgroup` utility will fail with a failure status. If the JSON entry
has a `gid` property that should never happen unless the JSON file is
improperly modified after install.

If the `gid` provided by the JSON file already has either a group or
a user assigned to that ID, the `yjl-sysgroup` will treat the assigned
ID as in use and select a group ID that is not already in use for either
a group or a user.

If the `groupadd` program called by the `yjl-sysgroup` utility should
fail with a bad exit status, the `yjl-sysgroup` utility will fail with
a bad exit status. That should never happen unless the operating system
is broken.

When `yjl-sysgroup` is successful, it will return a group ID and exit
with a 0 status.

If the `yjl-sysuser` utility is used with a user name contained as an
object in the JSON file which does not have a valid `uid` property, the
`yjl-sysuser` utility will fail with a failure status. If the JSON entry
has a `uid` property that should never happen unless the JSON file is
improperly modified after install.

If the `yjl-sysuser` command calls the `yjl-sysgroup` command and it
returns with a failure status, then the `yjl-sysuder` command will also
return a failure status.

If the `group` option is passed to the `yjl-sysuser` command and the
group name does not validate, the `yjl-sysuser` command will ignore
it.

If the `yjl-sysuser` command retrieves a `group` from the JSON file
that does not validate, the `yjl-sysuser` command will fail with a
bad exit status. That should never happen unless the JSON file is
improperly modified after install.

If the `comment` option is passed to the `yjl-sysuser` command and the
comment does not validate, the `yjl-sysuser` command will ignore it.

If the `yjl-sysuser` command retrieves a `comment` from the JSON file
that does not validate, the `yjl-sysuser` command will not fail but
will ignore it. That should never happen unless the JSON file is
improperly modified after install.

If the `homedir` option is passed to the `yjl-sysuser` command and the
directory does not validate, the `yjl-sysuser` command will ignore it.

If the `yjl-sysuser` command retrieves a `homedir` from the JSON file
that does not validate, the `yjl-sysuser` command will fail with a
bad exit status. That should never happen unless the JSON file is
improperly modified after install.

If the `shell` option is passed to the `yjl-sysuser` command and the
shell is not contained within `/etc/shell`, the `yjl-sysuser` command
will ignore it.

If the `yjl-sysuser` command retrieves a `shell` from the JSON file
that is not `/bin/bash` or `/bin/sh`, then `/bin/false` will be used
instead. That should never happen unless the JSON file is improperly
modified after install.

If the `skel` option is passed to the `yjl-sysuser` command and does
not evaluate to `true` then it will be assigned a value of `false`.

If the `yjl-sysuser` command retrieves a `skel` from the JSON file
that does not evaluate to `true` then it will be assigned a value of
false.

If the `useradd` program called by the `yjl-sysuser` utility should
fail with a bad exit status, the `yjl-sysuser` utility will fail with
a bad exit status. That should never happen unless the operating system
is broken.

Example Usage in RPM
--------------------

For a package like `plocate` that only needs a group added, add the
following conditional `Requires`:

    %if 0%{?_yjl_sysgroup:1} == 1
    Requires(pre): %{_yjl_sysgroup}
    %endif

Then for the scriptlet:

    %pre
    %if 0%{?_yjl_sysgroup:1} == 1
    %{_yjl_sysgroup} plocate
    %else
    getent group plocate >/dev/null 2>&1 ||groupadd -r plocate
    %endif

When the RPM spec file is built on YJL systems, it will require the
`/usr/sbin/yjl-sysgroup` utility and then use it in the pre scriptlet
to create the group with the specified group ID, or an alternate in
the unlikely case a group with the specified ID already exists.

When the RPM spec file is built on another system, it will still create
the needed group if it does not already exist, but the group ID will
be selected based upon the `SYS_GID_MIN-SYS_GID_MAX` range as defined
in `login.defs`.

Thus, the spec file remains at least somewhat portable while still
catering to YJL.

