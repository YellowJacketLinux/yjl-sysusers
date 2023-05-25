yjl-sysusers
============

__PARTS OF THIS README NEED TO BE FIXED__

At present this is works except for the minor detail that it does not
*actually* work, see [TODO](TODO.md) for details.

This project includes a single utility and a JSON file. In the git
source, that utility is simply called `functions.py` but it gets
installed as `/usr/sbin/yjl-sysusers.py` with a single-line change
to specify the location on the filesystem of the JSON file.

I know the `.isascii()` function requires Python 3.8+ and I *believe*
some of the type hints require Python 3.9+.

I am developing this using Python 3.11.3 but I think it should work
in Python 3.9+ without issue.

The purpose is to provide an easy way to provide consistent user ID
and group ID numbers for system users (as opposed to human login users)
while also being able to on-the-fly use dynamic IDs if the static IDs
have already been used for something else.

My use case is for RPM `%pre` scriptlets to ensure that the appropriate
users and groups an RPM package needs exist when the package installs.

If the necessary parameters are described in the JSON file, the only
argument the script needs is the name of the user (or group) account
to create. If the necessary parameters are *not* described in the JSON
file or if the packager wants different parameters, every parameter
can be defined as an argument to the script *except* for the UID/GID
to request, that is only definable in the JSON file.

Note the script still works to create users and groups not defined in
the JSON file, it just uses appropriate dynamic IDs outside the range
reserved for static IDs.


yjl-sysusers.json
-----------------

This JSON file contains all the information needed to create system
users and groups for YellowJacket GNU/Linux.

It is largely based upon the static system user information from
LFS/BLFS 11.3 but there are some differences.

It is currently a work in progress, some of the JSON entries are not
complete and others are planned but missing.


The JSON Format
---------------

This describes the constraines of the JSON file.

### User and Group Names

If we view the imported JSON as a Python dictionary of JSON objects,
each object bears the name of a system user and/or group. I will refer
to these as the ‘Name Object’.

Valid GNU/Linux usernames are defined in __man 8 useradd__

    Usernames may contain only lower and upper case letters, digits,
    underscores, or dashes. They can end with a dollar sign. Dashes
    are not allowed at the beginning of the username. Fully numeric
    usernames and usernames . or .. are also disallowed. It is not
    recommended to use usernames beginning with . character as their
    home directories will be hidden in the ls output.

    Usernames may only be up to 32 characters long.

For *system* user/group names, these utilities are intentionally a bit
more picky. Specifically, upper case letters are not allowed and the
first letter must be a letter or an underscore, and a dot in the user
or group name is not allowed. This is the python regex I am using:

    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")

### User and Group ID Numbers

Every name object __MUST__ have a `myid` property that has the value
of a non-negative integer. With the noted exception of the `nobody`
user and the `nogroup` name objects, the `myid` property __MUST__ be
both unique and have a value below 1000.

The `nobody` and `nogroup` name objects in modern LSB compliant GNU/Linux
distributions should both have a `myid` property of `65534` however it
is worth noting that was not always the case, when I first started
using GNU/Linux a value of `99` was used for them. Some Unix-like systems
may still use `99` or a different value, there is no POSIX standard
for it.

The `myid` property *may* exceed a value of 499 but I *personally*
consider that to be a bad practice.

A name object __MUST__ have either a boolean `usr` or `grp` property
(or both) and at least one of them must be set to `true`.

When a name object has a `grp` property that is set to `true` and the
group account does not already exist, the `yjl-sysusers` utility will
create a group using the ID specified by the `myid` property if neither
a group or user already are using that ID.

When a name object has a `usr` property that is set to `true` and the
user account does not already exist, the `yjl-sysusers` utility will
create an account using the ID specified by the `myid` property if that
ID is available *unless* the group with same name was created with a
different ID, in which case that ID will be used.

When a name object has a `grp` property that is set to `false` and a
string property `group` exists, then that group will be created (if
it does not already exist) and be used as the primary group for the
user.

When a object has a `grp` property that is set to `false` and a string
property `group` *does not exist*, then the group `nogroup` will be
used as the primary group for the user.

### User Comment

When the object has a `usr` property set to `true` it *should* also have
a `comment` property containing a string that describes the purpose of
the account although that is not strictly necessary.

For the JSON name object, I am restricting the comments to 7-bit ASCII
printable characters excluding the `\` and `:` characters, and restricting
it to 60 characters in length.

The plan is to pass the string through GNU GetText so that when a
translation to the system language and locale are available, the comment
that ends up in the `/etc/passwd` file for the user is in the appropriate
language for the system.

Internationalized account comments is something I personally have not
yet seen any RPM do when creating a system user, I think it is a very
nice touch---assuming I actually get the translation system working.

### Homedir

When the object has a `usr` property set to `true`, it *may* also have a
`homedir` property containing a string filesystem path to a home directory
for the system user. The property __MUST__ be a legal absolute file path
starting with a `/` and __MUST NOT__ include white space.

For system users, valid paths should only contain lower-case alpha-numeric
characters plus `_` and `-` and should not end with a `/`.

When a `homedir` property is not set, `/dev/null` is used.

### Shell

When the object has a `usr` property set to `true`, it *may* also have a
`shell` property containing a string filesystem path to a login shell.
There are two valid values: `/bin/bash` and `/bin/sh`.

When there is not a `shell` property set, the `yjl-sysusers` utility
will set the shell to `/sbin/nologin` if it is installed on the system
and otherwise to `/bin/false`.

### Skeleton Files

When the object has a `homedir` property that is *not* `/dev/null` then
it *may* also have a boolean `skel` property. If set to `true` and the
home directory does not already exist, then `useradd` will be instructed
to create the home directory. That *usually* results in the contents of
`/etc/skel/` being copied into the home directory.

If the `skel` property is not set, it is treated as if it is `false`.

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

    %if 0%{?_yjl_sysusers:1} == 1
    Requires(pre): %{_yjl_sysusers}
    %endif

Then for the scriptlet:

    %pre
    %if 0%{?_yjl_sysusers:1} == 1
    %{_yjl_sysusers} plocate
    %else
    getent group plocate >/dev/null 2>&1 ||groupadd -r plocate
    %endif

When the RPM spec file is built on a system that has `yjl-sysusers`
as part of the RPM build environment, the package will require the
`/usr/sbin/yjl-sysusers` utility and then use it in the pre scriptlet
to create the group with the specified group ID, or an alternate in
the unlikely case a group with the specified ID already exists.

When the RPM spec file is built on another system, it will still create
the needed group if it does not already exist, but the group ID will
be selected based upon the `SYS_GID_MIN-SYS_GID_MAX` range as defined
in `login.defs`.

Thus, the spec file remains at least somewhat portable.

In the event the package installs on a system that does not have
`plocate` defined in the JSON file, it will still create the group---
but will also create a user as well as that is the default when the
JSON file does not tell it what to do for a user. That actually does
not hurt anything but you can avoid it by adding the `-p False` switch
to the `%{_yjl_sysusers}` command.

If you are creating RPM spec files for a distribution, you probably do
not need to mess with switches as long as JSON file is correct but if
you are creating generic RPM spec files, you probably do want to use
the switches to manually specify the needed parameters for user creation.

