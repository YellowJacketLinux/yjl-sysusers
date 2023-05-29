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
import os
import sys
from pathlib import Path
import re
import json
import grp
import pwd
import subprocess
import argparse

# Initial globals
NOGROUP = "nogroup"
DUPOK = []

# Dummy until gettext is used
def _(fubar):
    return fubar

APDICT = {
    "description": _("Add system users and groups. See: man 8 yjl-sysusers"),
    "comment": _("Specify the user comment passwd field."),
    "home": _("Specify the user home directory."),
    "shell": _("Specify the user login shell."),
    "uadd": _("Use False to disable user creation."),
    "gadd": _("Use False to disable group creation."),
    "group": _("Specify the default group NAME for the user."),
    "mkdir": _("Use True to create home directory."),
    "account": _("User or Group name to add.")
}

PSR = argparse.ArgumentParser(description=APDICT["description"])
PSR.add_argument("-c", "--comment", type=str, help=APDICT["comment"])
PSR.add_argument("-d", "--home", type=str, help=APDICT["home"])
PSR.add_argument("-s", "--shell", type=str, help=APDICT["shell"])
PSR.add_argument("--useradd", choices=('True', 'False'), help=APDICT["uadd"])
PSR.add_argument("--groupadd", choices=('True', 'False'), help=APDICT["gadd"])
PSR.add_argument("-g", "--group", type=str, help=APDICT["group"])
PSR.add_argument("--mkdir", choices=('True', 'False'), help=APDICT["mkdir"])
PSR.add_argument('account', type=str, help=APDICT["account"])

def myjson() -> str:
    """Sets the hard-coded location of the configuration file."""
    jsonfile = 'yjl-sysusers.json'
    cfgdir = ''
    if len(cfgdir) == 0:
        return jsonfile
    return cfgdir + '/' + jsonfile

def username_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user/group names."""
    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")
    if isinstance(checkme, str):
        if pattern.match(checkme):
            return True
    return False

def userid_check(checkme: int) -> bool:
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
        if (len(checkme) == 0) or (len(checkme) > 120):
            return False
        if onlyascii:
            return all(ord(char) < 128 for char in checkme)
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
    """Wrapper to the actual groupadd command. Returns GID on success."""
    mycmd = "/sbin/groupadd " + "-f -g " + str(gid) + " -r " + gpname
    myuid = os.getuid()
    if myuid == 0:
        try:
            subprocess.call(["groupadd", "-f", "-g", str(gid), "-r", gpname])
        except:
            sys.exit(_("Failed to create the specified group."))
    else:
        # this only happens in testing, main() checks for root
        print(mycmd)
        return gid
    try:
        existing = grp.getgrnam(gpname)
    except KeyError:
        sys.exit(_("Failed to create the specified group."))
    return existing.gr_gid

def load_id_list(desired: int) -> list:
    """Returns list of IDs to query for system group/user creation."""
    mylist = []
    if desired != 65535:
        mylist.append(desired)
    for i in range(300, 400):
        mylist.append(i)
    for i in range(500, 1000):
        mylist.append(i)
    return mylist

def find_group_id(gpname: str, desired: int) -> int:
    """Returns the ID associated with input group name."""
    try:
        existing = grp.getgrnam(gpname)
        return existing.gr_gid
    except KeyError:
        pass
    idlist = load_id_list(desired)
    for i in idlist:
        try:
            existing = grp.getgrgid(i)
        except KeyError:
            try:
                existing = pwd.getpwuid(i)
            except KeyError:
                return add_the_group(gpname, i)
    # Should never reach this point but if it does
    #  try to create group anyway
    return add_the_group(gpname, desired)

def request_gid_from_json(gpname: str, sysusers: dict) -> int:
    """Given a group name, attempts to find the preferred Group ID."""
    nameobject = sysusers[gpname]
    if nameobject.get('grp', False):
        return nameobject.get('myid', 65535)
    return 65535

def request_gpname_from_json(username: str, sysusers: dict) -> str:
    """Given a user name, attempts to find the primary group for the user."""
    nameobject = sysusers[username]
    if nameobject.get('grp', False):
        return username
    gpname = nameobject.get('group', NOGROUP)
    if username_check(gpname):
        return gpname
    return NOGROUP

def determine_useradd_gid_from_json(username: str, sysusers: dict) -> int:
    """Given a username, find the appropriate GID for useradd command."""
    gpname = request_gpname_from_json(username, sysusers)
    desired = request_gid_from_json(gpname, sysusers)
    return find_group_id(gpname, desired)

def determine_useradd_uid_from_json(username: str, sysusers: dict) -> int:
    """Given a username, find the appropriate UID for useradd command."""
    same_as_group = True
    nameobject = sysusers[username]
    same_as_group = nameobject.get('grp', False)
    if same_as_group:
        desired = determine_useradd_gid_from_json(username, sysusers)
    else:
        desired = nameobject.get('myid', 65535)
    if same_as_group:
        try:
            pwd.getpwuid(desired)
        except KeyError:
            return desired
        desired = 65535
    idlist = load_id_list(desired)
    for i in idlist:
        try:
            grp.getgrgid(i)
        except KeyError:
            try:
                pwd.getpwuid(i)
            except KeyError:
                return i
    # Should never ever happen
    sys.exit(_("There do not seem to be any available User IDs left for a system user."))

def ensure_home_dir(homedir: str) -> None:
    """Creates the parent directory of the home directory if necessary."""
    path = Path(homedir)
    parent = path.parent.absolute()
    if os.path.exists(parent):
        return
    myuid = os.getuid()
    if myuid == 0:
        try:
            subprocess.call(["mkdir", "-p", parent])
        except:
            pass

def add_the_user(username: str, sysusers: dict) -> None:
    """Wrapper to the actual useradd command."""
    gid = determine_useradd_gid_from_json(username, sysusers)
    try:
        #existing = pwd.getpwnam(username)
        pwd.getpwnam(username)
        return
    except KeyError:
        pass
    uid = determine_useradd_uid_from_json(username, sysusers)
    spclist = ["useradd", "-g", str(gid), "-u", str(uid)]
    nameobject = sysusers[username]
    extrashells = nameobject.get('extrashells', False)
    checkme = nameobject.get('comment', '')
    if usercomment_check(checkme):
        comment = translate_comment(checkme)
    else:
        comment = username + " " + _("system user account")
    spclist.append("-c")
    spclist.append(comment)
    checkme = nameobject.get('homedir', '/dev/null')
    if homedir_check(checkme):
        homedir = checkme
    else:
        homedir = "/dev/null"
    spclist.append("-d")
    spclist.append(homedir)
    checkme = nameobject.get('shell', '/sbin/nologin')
    if shell_check(checkme, extrashells):
        shell = checkme
    else:
        shell = "/bin/false"
    spclist.append("-s")
    spclist.append(shell)
    if homedir == "/dev/null":
        mkdir = False
    else:
        testme = nameobject.get('mkdir', False)
        if testme:
            if os.path.exists(homedir):
                mkdir = False
            else:
                mkdir = True
        else:
            mkdir = False
    if mkdir:
        ensure_home_dir(homedir)
        spclist.append("--create-home")
    spclist.append("-r")
    spclist.append(username)
    myuid = os.getuid()
    if myuid == 0:
        try:
            subprocess.call(spclist)
        except:
            sys.exit(_("Failed to create the specified user."))
    else:
        # this only happens in testing, main() checks for root.
        print(spclist)

def just_do_it(username: str, sysusers: dict) -> None:
    """Called by main() to creates the user/group account as needed."""
    nameobject = sysusers[username]
    createuser = nameobject.get('usr', False)
    if createuser:
        add_the_user(username, sysusers)
    else:
        #gid = determine_useradd_gid_from_json(username, sysusers)
        determine_useradd_gid_from_json(username, sysusers)

def validate_cfg(cfgdict: dict) -> None:
    """Validates the 000-CONFIG json object"""
    global NOGROUP
    global DUPOK
    NOGROUP = cfgdict.get("nogroup", "nogroup")
    DUPOK = cfgdict.get("dupok", [])
    if username_check(NOGROUP) is False:
        sys.exit(_("Invalid default nogroup in 000-CONFIG"))
    for i in DUPOK:
        if userid_check(i) is False:
            sys.exit(_("Invalid ID number in 000-CONFIG dupok"))
    return

def validate_json() -> int:
    """Validates the JSON configuration file and if successful, dumps contents to screen."""
    usedlist = []
    shells = ["/bin/bash", "/bin/sh"]
    jsonfile = myjson()
    try:
        with open(jsonfile) as data_file:
            sysusers = json.load(data_file)
    except:
        sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)
    keylist = list(sysusers.keys())
    if "000-CONFIG" in keylist:
        validate_cfg(sysusers["000-CONFIG"])
        keylist.remove("000-CONFIG")
    for username in keylist:
        if username_check(username) is False:
            sys.exit(_("The user/group '")
                     + username
                     + _("' is an invald name."))
        nameobject = sysusers[username]
        myid = nameobject.get('myid', 65535)
        if userid_check(myid) is False:
            sys.exit(_("The user/group '")
                     + username
                     + _("' has a missing or invalid 'myid' definition."))
        if myid in usedlist:
            sys.exit(_("The user/group '")
                     + username
                     + _("' has a duplicate 'myid' definition."))
        else:
            if myid not in DUPOK:
                usedlist.append(myid)
        usr = nameobject.get('usr', False)
        mygrp = nameobject.get('grp', False)
        if usr is False:
            if mygrp is False:
                sys.exit(_("The user/group '")
                         + username
                         + _("' must have at least one of 'usr' or 'grp' set to 'true'."))
        comment = nameobject.get('comment', 'A Valid String')
        if usercomment_check(comment) is False:
            sys.exit(_("The user/group '")
                     + username
                     + _("' has an invalid 'comment' definition."))
        homedir = nameobject.get('homedir', '/dev/null')
        if homedir_check(homedir) is False:
            sys.exit(_("The user/group '")
                     + username
                     + _("' has an invalid 'homedir' definition."))
        shell = nameobject.get('shell', '/bin/bash')
        atypshell = nameobject.get('atypshell', False)
        if atypshell:
            if path_check(shell) is False:
                sys.exit(_("The user/group '")
                         + username
                         + _("' has an invalid 'shell' definition."))
        elif shell not in shells:
            sys.exit(_("The user/group '")
                     + username
                     + _("' has an invalid 'shell' definition."))
    valid_json = json.dumps(sysusers)
    print(valid_json)
    return 0

def main(args) -> int:
    """Loads JSON file, applies argparse options."""
    if args.account == "000":
        validate_json()
        return 0
    myuid = os.getuid()
    if myuid != 0:
        sys.exit(_("Sorry, you must be root to run me."))
    if username_check(args.account):
        username = args.account
    else:
        sys.exit(args.account + " " + _("is not valid for a system user/group account name."))
    jsonfile = myjson()
    try:
        with open(jsonfile) as data_file:
            sysusers = json.load(data_file)
    except:
        sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)
    keylist = list(sysusers.keys())
    if "000-CONFIG" in keylist:
        validate_cfg(sysusers["000-CONFIG"])
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
    if args.useradd is not None:
        if args.useradd == "True":
            sysusers[username].update({"usr": True})
        else:
            sysusers[username].update({"usr": False})
    if args.groupadd is not None:
        if args.groupadd == "True":
            sysusers[username].update({"grp": True})
        else:
            sysusers[username].update({"grp": False})
    if args.group is not None:
        if username_check(args.group):
            if username == args.group:
                sysusers[username].pop("group")
                sysusers[username].update({"grp": True})
            else:
                sysusers[username].update({"group": args.group})
                sysusers[username].update({"grp": False})
    mytest = sysusers[username].get("usr")
    if mytest is False:
        sysusers[username].update({"grp": True})
    mytest = sysusers[username].get("grp")
    if mytest is False:
        sysusers[username].update({"usr": True})
    if args.mkdir is not None:
        if args.mkdir == "True":
            sysusers[username].update({"mkdir": True})
        else:
            sysusers[username].update({"mkdir": False})
    #
    just_do_it(username, sysusers)
    return 0


if __name__ == '__main__':
    sys.exit(main(PSR.parse_args()))

# EOF
