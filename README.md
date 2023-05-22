yjl-sysusers
============

This project will (likely) include two utilities, primarily intended
to be used in RPM scriptlets (largely the `%pre` scriptlets).

The purpose is to provide an easy way to provide consistent user ID
and group ID numbers for system users (as opposed to human login users).


yjl-sysgroup
------------

This will be a utility for adding a system `group` user and will take
a single argument: the name of the group being added as a system group.

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

utility for adding system groups and users
