% YJL-SYSUSERS(1) yjl-sysusers 0.1.0
% YellowJacket GNU/Linux
% May 2023

# NAME
yjl-sysusers - Add system users and groups

# SYNOPSIS
**yjl-sysusers** [*OPTIONS*] NAME

# DESCRIPTION
**yjl-sysusers** is a wrapper script to the operating system **groupadd**
and **useradd** commands that allows respecting the operating system
static UID and GID assignment when available, without the need to assign
them manually.

Static UID and GID values, as well as some other parameters useful to the
**useradd** command, are defined in the file **yjl-sysusers.json** which
is normally located in the directory /var/lib/yjl-sysusers.

**yjl-sysusers** was developed with RPM package scriptlets in mind.

# OPTIONS
**-h**, **--help**
: Display help message and exit.

**-c**, **--comment** *COMMENT*  
: Define the comment field to be used in the /etc/passwd file. *COMMENT*
  must be printable ASCII, excluding the \ and : characters. *COMMENT*
  must not exceed 60 characters.

**-d**, **--home** *HOME*  
: Define the home directory to be used with the system user account.
  It must be full path and can only use lower-case alpha-numeric
  characters plus underscore, forward-slash, and hyphen.

**-s**, **--shell** *SHELL*  
: Define the login shell to be used with the system user account. If
  *SHELL* is not present in /etc/shells or is not installed on the
  system, then /sbin/nologin or /bin/false will be substituted.

**-g**, **--group** *GROUP*  
: Define the primary group the user should belong to, if different
  from the login user name. If **GROUP** does not exist, it will be
  created automatically. When *GROUP* is defined, a group will not
  be created for **NAME**.

**--useradd** *{True,False}*  
: Define whether or not the user specified by **NAME** should be
  created. If set to *False* then **--groupadd** must be set to
  *True*.

**--groupadd** *{True,False}*  
: Define whether or not the group specified by **NAME** should be
  created. Setting this to *False* will not prevent a group specified
  by the **-g**, **--group** from being created. If set to *False*
  then **--useradd** must be set to *True*.

# EXAMPLES
**yjl-sysusers** *somename*  
: If *somename* is defined in /var/lib/yjl-sysusers.json then the
  user and/or group will be created according to the paramaters in
  that file. If *somename* is **NOT** defined in that file, then
  both a user and group will be created using /dev/null as the home
  directory and /sbin/login (or /bin/false) as the login shell.

**yjl-sysusers** **-g** *mail* *sendmail*  
: If *mail* is defined in /var/lib/yjl-sysusers.json then the group
  *mail* will be created using the *GID* defined there, unless already
  in use. Otherwise it will created with a *GID* from the dynamic range
  for system groups. If the user *sendmail* is defined in
  /var/lib/yjl-sysuers.json then the user *sendmail* will be created
  using the parameters defined there, but will be created using *mail*
  as the primary group regardless of the parameters in that file.

# EXIT STATUS
**0**  
: Success

**1**  
: The program failed to create requested group and/or user.

# BUGS
Yes, I have seen Starship Troopers. Bugs can be very insideous and hard
to get rid of, but I expect them to be random and light.

# COPYRIGHT
Copyright (c) 2023 YellowJacket GNU/Linux. License MIT
<https://spdx.org/licenses/MIT.html>. This is free software: you are
free to change and redistribute it. There is no WARRANTY, to the extent
permitted by law.
