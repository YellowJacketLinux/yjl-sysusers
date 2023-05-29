WARNING
=======

If this is devel branch, or any branch other than main, some or all
of the JSON files may not be compatible with the current python code.

Fedora
------

Fedora JSON is based upon:

https://docs.fedoraproject.org/en-US/packaging-guidelines/UsersAndGroups/
(2023-05-28)

It still needs some useradd metadata and needs to be double-checked.

Also I do not think it is complete. For example, `apache` is not listed
there but at least historically, a static UID/GID was used in the
Red Hat/Fedora world for `apache`. 
