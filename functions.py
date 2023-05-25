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
import argparse

# Dummy until gettext is used
def _(fubar):
    return fubar

parser = argparse.ArgumentParser(description='Add system users and groups.')
parser.add_argument("-c", "--comment", type=str, help=_("Specify the user comment passwd field."))
parser.add_argument("-d", "--home", type=str, help=_("Specify the user home directory."))
parser.add_argument("-s", "--shell", type=str, help=_("Specify the user login shell."))
parser.add_argument("-g", "--group", type=str, help=_("Specify the default group NAME for the user."))

def cfg() -> str:
    """Sets the hard-coded location of the configuration file."""
    jsonfile = 'yjl-sysusers.json'
    cfgdir = ''
    if len(cfgdir) == 0:
        return jsonfile
    return(cfgdir + '/' + jsonfile)

def username_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user/group names."""
    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")
    if isinstance(checkme, str):
        if pattern.match(checkme):
            return True
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
    if os.path.isfile('/sbin/nologin'):
        myshells.append('/sbin/nologin') 
    if syshells:
        try:
            with open('/etc/shells') as file:
                lines = [line.rstrip() for line in file]
                for entry in lines:
                    if path_check(entry) and os.path.isfile(entry):
                        myshells.append(entry)
        except:
            pass
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

def find_group_id(gpname: str, desired: int) -> int:
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
        except KeyError:
            try:
                existing = pwd.getpwuid(x)
            except KeyError:
                return add_the_group(gpname, x)
    # Should never reach this point but if it does
    #  try to create group anyway
    return add_the_group(gpname, desired)

def request_gid_from_json(gpname: str, sysusers: list[dict]) -> int:
    """Given a group name, attempts to find the preferred Group ID."""
    nameobject = sysusers[gpname]
    if nameobject.get('grp', False):
        return nameobject.get('myid', 65535)
    return 65535

def request_gpname_from_json(username: str, sysusers: list) -> str:
    """Given a user name, attempts to find the primary group for the user."""
    nameobject = sysusers[username]
    if nameobject.get('grp', False):
        return username
    gpname = nameobject.get('group', 'nogroup')
    if username_check(gpname):
        return gpname
    return "nogroup"

def determine_useradd_gid_from_json(username: str, sysusers: list) -> int:
    """Given a username, find the appropriate GID for useradd command."""
    gpname = request_gpname_from_json(username, sysusers)
    desired = request_gid_from_json(gpname, sysusers)
    """ NOTE: If group does not exist, it will be created.
            The *actual* GID will be returned which may
            differ from the "desired" value.
    """
    return find_group_id(gpname, desired)

def determine_useradd_uid_from_json(username: str, sysusers: list) -> int:
    """Given a username, find the appropriate UID for useradd command."""
    sameAsGroup = True
    nameobject = sysusers[username]
    sameAsGroup = nameobject.get('grp', False)
    if sameAsGroup:
        desired = determine_useradd_gid_from_json(username, sysusers)
    else:
        desired = nameobject.get('myid', 65535)
    if sameAsGroup:
        try:
            existing = pwd.getpwuid(desired)
            desired = 65535
        except KeyError:
            return desired
    idlist = load_id_list(desired)
    for x in idlist:
        try:
            existing = grp.getgrgid(x)
        except KeyError:
            try:
                existing = pwd.getpwuid(x)
            except KeyError:
                return x
    # Should never ever happen
    sys.exit(_("There do not seem to be any available User IDs left for a system user."))

def add_the_user(username: str, sysusers: list) -> None:
    gid = determine_useradd_gid_from_json(username, sysusers)
    try:
        existing = pwd.getpwnam(username)
        return
    except KeyError:
        pass
    uid = determine_useradd_uid_from_json(username, sysusers)
    nameobject = sysusers[username]
    extrashells = nameobject.get('extrashells', False)
    checkme = nameobject.get('comment', '')
    if usercomment_check(checkme):
        comment = translate_comment(checkme)
    else:
        comment = username + " " + _("system user account")
    checkme = nameobject.get('homedir', '/dev/null')
    if homedir_check(checkme):
        homedir = checkme
    else:
        homedir = "/dev/null"
    checkme = nameobject.get('shell', '/sbin/nologin')
    if shell_check(checkme, extrashells):
        shell = checkme
    else:
        shell = "/bin/false"
    if homedir == "/dev/null":
        skel = False
    else:
        testme = nameobject.get('skel', False)
        if testme:
            if os.path.exists(homedir):
                skel = False
            else:
                skel = True
        else:
            skel = False
    myPREcmd = "/sbin/useradd -g " + str(gid) + " -u " + str(uid) + " -c \"" + comment + "\" -d " + homedir + " -s " + shell
    if skel:
        mycmd = myPREcmd + " --create-home -r " + username
    else:
        mycmd = myPREcmd + " -r " + username
    myuid = os.getuid()
    if myuid == 0:
        try:
            subprocess.run([mycmd])
        except:
            sys.exit(_("Failed to create the specified user."))
    else:
        # this only happens in testing, __main__ checks
        print(mycmd)

def just_do_it(username: str, sysusers: list) -> None:
    """Called by __main__ to creates the user/group account as needed."""
    nameobject = sysusers[username]
    createuser = nameobject.get('usr', False)
    if createuser:
        add_the_user(username, sysusers)
    else:
        gid = determine_useradd_gid_from_json(username, sysusers)

def validate_cfg() -> int:
    """Validates the JSON configuration file and if successful, dumps contents to screen."""
    usedlist = []
    shells = ["/bin/bash", "/bin/sh"]
    jsonfile = cfg()
    try:
        with open(jsonfile) as data_file:
            sysusers = json.load(data_file)
    except:
        sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)
    keylist = list(sysusers.keys())
    for username in keylist:
        check = username_check(username)
        if username_check(username) is False:
            sys.exit(_("The user/group '") + username + _("' is an invald name."))
        nameobject = sysusers[username]
        myid = nameobject.get('myid', 65535)
        if myid == 65535:
            sys.exit(_("The user/group '") + username + _("' has a missing or invalid 'myid' definition."))
        if myid in usedlist:
            sys.exit(_("The user/group '") + username + _("' has a duplicate 'myid' definition."))
        else:
            if myid != 65534:
                usedlist.append(myid)
        usr = nameobject.get('usr', False)
        grp = nameobject.get('grp', False)
        if usr is False:
            if grp is False:
                sys.exit(_("The user/group '") + username + _("' must have at least one of 'usr' or 'grp' set to 'true'."))
        comment = nameobject.get('comment', 'A Valid String')
        if usercomment_check(comment) is False:
            sys.exit(_("The user/group '") + username + _("' has an invalid 'comment' definition."))
        homedir = nameobject.get('homedir', '/dev/null')
        if homedir_check(homedir) is False:
            sys.exit(_("The user/group '") + username + _("' has an invalid 'homedir' definition."))
        shell = nameobject.get('shell', '/bin/bash')
        if shell not in shells:
            sys.exit(_("The user/group '") + username + _("' has an invalid 'shell' definition."))
    myjson = json.dumps(sysusers)
    print(myjson)
    return 0

def main(args) -> int:
    """Does some things. Not finished."""
    if args.name == "000":
        validate_cfg()
        return 0
    myuid = os.getuid()
    if myuid != 0:
        sys.exit(_("Sorry, you must be root to run me."))
    if username_check(args.name):
        username = args.name
    else:
        sys.exit(args.name + " " + _("is not valid for a system user/group name."))
    jsonfile = cfg()
    try:
        with open(jsonfile) as data_file:
            sysusers = json.load(data_file)
    except:
       sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)
    keylist = list(sysusers.keys())
    if username in keylist:
        pass
    else:
        sysusers[username] = {'myid': 65535, 'usr': True, 'grp': True}
    # modify sysusers[username] based upon arguements
    if args.comment is not None:
        if usercomment_check(args.comment):
            sysusers[username].update({"comment": args.comment})
    if args.home is not None:
        if homedir_check(args.home):
            sysusers[username].update({"homedir": args.home})
    if args.shell is not None:
        if shell_check(args.shell, True):
            sysusers[username].update({"shell": args.shell})
            sysusers[username].update({"extrashells": True})
    if args.group is not None:
        if username_check(args.group):
            if username == args.group:
                sysusers[username].pop("group")
                sysusers[username].update({"grp": True})
            else:
                sysusers[username].update({"group": args.group})
                sysusers[username].update({"grp": False})
    #
    just_do_it(username, sysusers)
    return 0


if __name__ == '__main__':
    sys.exit(main(parser.parse_args()))

# EOF
