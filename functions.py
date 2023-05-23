#!/usr/bin/env python3

import os
import string
import unicodedata
import re
import json

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
#  exceed 48 characters. Violations result in no user comment.
# In the JSON file, only ascii is allowed.
def usercomment_check(checkme, onlyascii=True):
    if isinstance(checkme, str) and checkme.isprintable():
        if checkme.__contains__(":") or checkme.__contains__("\\"):
            return False
        if (len(checkme) == 0) or (len(checkme) > 48):
            return False
        if onlyascii:
            return checkme.isascii()
        return True
    return False

# This function is clearly not finished, currently always returns the input
#  implement via https://docs.python.org/3/library/gettext.html#class-based-api
def translate_comment(myinput):
    translation = ""
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
    if syshells:
        with open('/etc/shells') as file:
            lines = [line.rstrip() for line in file]
            for entry in lines:
                if path_check(entry) and os.path.isfile(entry):
                    myshells.append(entry)
    if checkme in myshells:
        return True
    return False

