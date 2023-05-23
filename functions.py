#!/usr/bin/env python3
# Copyright 2023 YellowJacket GNU/Linux. MIT license.
#  See https://github.com/YellowJacketLinux/yjl-sysusers/blob/main/LICENSE

import os
import string
import unicodedata
import re
import json
import grp
import pwd

# Dummy until gettext is used
def _(fubar):
    return fubar

# For system user accounts, no uppercase and MUST begin with a letter
#  or an underscore. Violation results in program failure.
def username_check(checkme):
    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")
    if isinstance(checkme, str):
        return pattern.match(checkme)
    return False

# A system user/group id must be a non-negative integer below 1000 except
#  for nobody/nogroup which are 65534. Violation result in program failure.
def userid_check(checkme):
    if isinstance(checkme, int) and (checkme >= 0):
        if (checkme < 1000) or (checkme == 65534):
            return True
    return False

# A system user comment must be printable unicode w/o : or \ and not
#  exceed 60 characters. Violations result in no user comment.
# In the JSON file, only ascii is allowed.
def usercomment_check(checkme, onlyascii=True):
    if isinstance(checkme, str) and checkme.isprintable():
        if checkme.__contains__(":") or checkme.__contains__("\\"):
            return False
        if (len(checkme) == 0) or (len(checkme) > 60):
            return False
        if onlyascii:
            return checkme.isascii()
        return True
    return False

# if available, returns translation of the user comment
def translate_comment(myinput):
    translation = _(myinput)
    if usercomment_check(translation, False):
        return translation
    return myinput

# This function verifies a valid path starting with a / and only consisting of
#  lower case alphanumeric, _, and - and not ending with a / or containing //
# It does NOT verify the path exists.
def path_check(checkme):
    pattern = re.compile("^[/][a-z0-9_/-]+$")
    doublecheck = re.compile("(.*[/]{2,}.*)|(.*[/]$)")
    if isinstance(checkme, str) and pattern.match(checkme):
        if doublecheck.match(checkme):
            return False
        return True
    return False

# If the specified home directory exists, it MUST be either /dev/null or a
#  directory. If it does not exist, that is okay.
def homedir_check(checkme):
    if checkme == "/dev/null":
        return True
    if path_check(checkme) is False:
        return False
    if os.path.isfile(checkme):
        return False
    return True

# This function verifies login shell is valid
def shell_check(checkme, syshells=False):
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

# This function will add the group
def add_the_group(gpname, gid):
    return gid

# Returns a list of IDs to try
def load_id_list(desired):
    mylist = []
    if desired != 65535:
        mylist.append(desired)
    for i in range(300,400):
        mylist.append(i)
    for i in range(500,1000):
        mylist.append(i)
    return mydict

# Takes the group name and if provided, potential group ID.
#  When it returns an ID, the group exists.
def find_group_id(gpname, desired=65535):
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

