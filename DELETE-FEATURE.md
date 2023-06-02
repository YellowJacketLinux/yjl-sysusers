Planned Delete Feature
======================

With the planned `--delete` feature, what I hope to do is list all
users that use the group being deleted as their primary group and
then switch those users to use `nogroup` as their primary group.

In most cases that will be a list of one or zero but that can not
be assumed.

When deleting a user, first delete a group of same name as listed
above, then delete the user but in non-destructive to any files
owned by that user.
