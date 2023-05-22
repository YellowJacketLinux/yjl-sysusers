yjl-sysusers
============

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
