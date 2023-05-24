#!/usr/bin/env python3

""" YJL System User and Group Setup 

This program installs system (non-human) users and groups using parameters
provided in '/var/lib/yjl-sysuers/yjl-sysuers.json', some of which can
be over-ridden with valid run-time arguments to this script. As such, it
needs to be run by the root user.

Copyright (C) 2023 YellowJacket GNU/Linux.

This program is released under terms of the MIT License.

    SPDX-License-Identifier: MIT

On GNU/Linux systems, there often is a copy of the license installed
in /usr/share/licenses/yjl-sysusers/ but if not, try:

    https://spdx.org/licenses/MIT.html

This script is currently developed on github.

    https://github.com/YellowJacketLinux/yjl-sysusers/

"""

# Copyright 2023 YellowJacket GNU/Linux. MIT license.
#  See https://github.com/YellowJacketLinux/yjl-sysusers/blob/main/LICENSE

import os
import sys
import string
import unicodedata
import re
import json
import grp
import pwd
from subprocess import run

def _(fubar: str) -> str:
    """Dummy function until gettext is set up."""
    return fubar

def username_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user/group names."""
    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")
    if isinstance(checkme, str):
        return pattern.match(checkme)
    return False

def userid_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user/group ID."""
    if isinstance(checkme, int) and (checkme >= 0):
        if (checkme < 1000) or (checkme == 65534):
            return True
    return False

# In the JSON file, only ascii is allowed.
def usercomment_check(checkme: str, onlyascii=True) -> bool:
    """Validates input against YJL rules for system user comment field."""
    if isinstance(checkme, str) and checkme.isprintable():
        if checkme.__contains__(":") or checkme.__contains__("\\"):
            return False
        if (len(checkme) == 0) or (len(checkme) > 60):
            return False
        if onlyascii:
            return checkme.isascii()
        return True
    return False

def translate_comment(myinput: str) -> str:
    """When available, outputs translation of system user comment field."""
    translation = _(myinput)
    if usercomment_check(translation, False):
        return translation
    return myinput

def path_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user home directory path."""
    pattern = re.compile("^[/][a-z0-9_/-]+$")
    doublecheck = re.compile("(.*[/]{2,}.*)|(.*[/]$)")
    if isinstance(checkme, str) and pattern.match(checkme):
        if doublecheck.match(checkme):
            return False
        return True
    return False

def homedir_check(checkme: str) -> bool:
    """Validates the input can be used as a system user home directory."""
    if checkme == "/dev/null":
        return True
    if path_check(checkme) is False:
        return False
    if os.path.isfile(checkme):
        return False
    return True

def shell_check(checkme: str, syshells=False) -> bool:
    """Validates the input can be used as a system user login shell."""
    myshells = ['/bin/bash', '/bin/sh']
    if os.path.isfile("/sbin/nologin"):
        myshells.append("/sbin/nologin")
    if syshells:
        with open('/etc/shells') as file:
            lines = [line.rstrip() for line in file]
            for entry in lines:
                if path_check(entry) and os.path.isfile(entry):
                    myshells.append(entry)
    if checkme in myshells:
        return True
    return False

def add_the_group(gpname: str, gid: int) -> int:
    """Attempts to create a system group using the specified ID, returns actual group ID when successful."""
    mycmd = "/sbin/groupadd " + "-f -g " + str(gid) + " -r " + gpname
    myuid = os.getuid()
    if myuid == 0:
        try:
            subprocess.run([mycmd])
        except:
            sys.exit(_("Failed to create the specified group."))
    else:
        # this only happens in testing, __main__ checks
        print(mycmd)
        return gid
    try:
        existing = grp.getgrnam(gpname)
    except KeyError:
        sys.exit(_("Failed to create the specified group."))
    return existing.gr_gid

def load_id_list(desired: int) -> list[int]:
    """Returns a list of IDs to query for appropriate system group/user creation."""
    mylist = []
    if desired != 65535:
        mylist.append(desired)
    for i in range(300,400):
        mylist.append(i)
    for i in range(500,1000):
        mylist.append(i)
    return mydict

def find_group_id(gpname: str, desired=65535) -> int:
    """Returns the ID associated with input group name, creating group first if needed."""
    try:
        existing = grp.getgrnam(gpname)
        return existing.gr_gid
    except KeyError:
        pass
    idlist = load_id_list(desired)
    for x in idlist:
        try:
            existing = grp.getgrgid(x)
            pass
        except KeyError:
            try:
                existing = pwd.getpwuid(x)
                pass
            except KeyError:
                return add_the_group(gpname, x)
    # Should never reach this point
    # throw error
    return desired

