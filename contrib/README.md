WARNING
=======

Fedora
------

Fedora JSON is based upon:

https://docs.fedoraproject.org/en-US/packaging-guidelines/UsersAndGroups/
(2023-05-28)

It still needs some useradd metadata and needs to be double-checked.

I was not able to find published information on what Fedora currently uses
as `SYS_UID_MIN` or `SYS_UID_MAX` so I did not specify that within the
__000-CONFIG__ section.

Also I do not think it is complete. For example, `apache` is not listed
there but at least historically, a static UID/GID was used in the
Red Hat/Fedora world for `apache`.

The Fedora JSON file however should be a decent base for someone more
familiar with current Fedora to start with, assuming there is interest. 
