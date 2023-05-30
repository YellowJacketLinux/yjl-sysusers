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

# Initial globals that get reset
NOGROUP = "nogroup"
DUPOK = []
ATYPSHELL = False
# used as non-collision dummy intiger to trigger dynamic
OS_MAX_PLUS_ONE = 65535

# Dummy until gettext is used
def _(fubar):
    return fubar

# JSON Validation Errors
def fail_invalid_definition(name: str, prop: str) -> None:
    """Exits with invalid definition error string."""
    sys.exit(_("The user/group '")
             + name
             + _("' has an invalid '")
             + prop
             + _("' definition."))

def fail_invalid_usrgrp(name: str) -> None:
    """Exits with invalid usr grp string."""
    sys.exit(_("The user/group '")
             + name
             + _("' must have at least one of 'usr' or 'grp' defined as 'true'"))

def fail_groupid_without_user(name: str) -> None:
    """Exits with invalid groupid usr string."""
    sys.exit(_("The user/group '")
             + name
             + _("' can not define 'groupid' if 'usr' is not defined as 'true'"))

def fail_groupid_without_group(name: str) -> None:
    """Exits with invalid groupid grp string."""
    sys.exit(_("The user/group '")
             + name
             + _("' can not define 'groupid' if 'grp' is not defined as 'true'"))

def fail_groupid_with_groupname(name: str) -> None:
    """Exits with invalid groupid and group string."""
    sys.exit(_("The user/group '")
             + name
             + _("' can not define a 'group' if 'groupid' is defined."))

def fail_duplicate_id(name: str, qaw: str, thenum: int) -> None:
    """Exits with dupplicate ID string."""
    sys.exit(_("The user/group '")
             + name
             + _("' in the '")
             + qaw
             + _("' property re-used the id '")
             + str(thenum) + "'")

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

def load_json() -> dict:
    """Loads the JSON file and returns a dictionary."""
    jsonfile = myjson()
    try:
        with open(jsonfile) as data_file:
            return json.load(data_file)
    except:
        sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)

def username_check(checkme: str) -> bool:
    """Validates input against YJL rules for system user/group names."""
    # pylint: disable=anomalous-backslash-in-string
    pattern = re.compile("^[a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}\$)$")
    # pylint: enable=anomalous-backslash-in-string
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
    if ATYPSHELL:
        return path_check(checkme)
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
    if desired != OS_MAX_PLUS_ONE:
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
        default = nameobject.get('myid', OS_MAX_PLUS_ONE)
        return nameobject.get('groupid', default)
    return OS_MAX_PLUS_ONE

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
    nameobject = sysusers[username]
    if nameobject.get('grp', False):
        test_a = nameobject.get('myid', OS_MAX_PLUS_ONE)
        test_b = nameobject.get('groupid', test_a)
        same_as_group = (test_a == test_b)
    else:
        same_as_group = False
    if same_as_group:
        desired = determine_useradd_gid_from_json(username, sysusers)
    else:
        desired = nameobject.get('myid', OS_MAX_PLUS_ONE)
    if same_as_group:
        try:
            pwd.getpwuid(desired)
        except KeyError:
            return desired
        desired = OS_MAX_PLUS_ONE
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

def determine_useradd_comment(username: str, nameobject: dict) -> str:
    """Returns string for useradd comment argument."""
    comment = nameobject.get('comment', '')
    if usercomment_check(comment):
        return translate_comment(comment)
    return username + " " + _("system user account")

def determine_useradd_homedir(nameobject: dict) -> str:
    """Returns string for useradd home argument."""
    homedir = nameobject.get('homedir', '/dev/null')
    if homedir_check(homedir):
        return homedir
    return "/dev/null"

def determine_useradd_shell(nameobject: dict) -> str:
    """Returns string for useradd shell argument."""
    extrashells = nameobject.get('extrashells', False)
    shell = nameobject.get('shell', '/sbin/nologin')
    if shell_check(shell, extrashells):
        return shell
    return "/bin/false"

def determine_useradd_mkdir(homedir: str, nameobject: dict) -> bool:
    """Returns True if useradd should create home directory."""
    if homedir == "/dev/null":
        return False
    if os.path.exists(homedir):
        return False
    return nameobject.get('mkdir', False)

def ensure_home_dir(homedir: str) -> None:
    """Creates the parent directory of the home directory if necessary."""
    # pylint: disable=no-member
    path = Path(homedir)
    parent = path.parent.absolute()
    # pylint: enable=no-member
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
    # comment field
    spclist.append("-c")
    spclist.append(determine_useradd_comment(username, nameobject))
    # home directory field
    homedir = determine_useradd_homedir(nameobject)
    spclist.append("-d")
    spclist.append(homedir)
    # login shell
    spclist.append("-s")
    spclist.append(determine_useradd_shell(nameobject))
    # create home directory
    if determine_useradd_mkdir(homedir, nameobject):
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
    """Validates the 000-CONFIG json object."""
    # pylint: disable=global-statement
    global NOGROUP
    global DUPOK
    # pylint: enable=global-statement
    NOGROUP = cfgdict.get("nogroup", "nogroup")
    DUPOK = cfgdict.get("dupok", [])
    if username_check(NOGROUP) is False:
        sys.exit(_("Invalid default nogroup in 000-CONFIG"))
    for i in DUPOK:
        if userid_check(i) is False:
            sys.exit(_("Invalid ID number in 000-CONFIG dupok"))
    return

def validate_no_groupid_conflicts(username: str, nameobject: dict) -> None:
    """Validates that groupid is used sanely."""
    myid = nameobject.get('myid', OS_MAX_PLUS_ONE)
    groupid = nameobject.get('groupid', OS_MAX_PLUS_ONE)
    group = nameobject.get('group', '')
    myusr = nameobject.get('usr', False)
    mygrp = nameobject.get('grp', False)
    if userid_check(groupid) is False:
        fail_invalid_definition(username, "grp")
    if myid == groupid:
        fail_invalid_definition(username, "groupid")
    if myusr is False:
        fail_groupid_without_user(username)
    if mygrp is False:
        fail_groupid_without_group(username)
    if len(group) > 0:
        fail_groupid_with_groupname(username)

def validate_user_group(username: str, nameobject: dict) -> None:
    """Validates the user and group id related definitions."""
    myid = nameobject.get('myid', OS_MAX_PLUS_ONE)
    groupid = nameobject.get('groupid', OS_MAX_PLUS_ONE)
    group = nameobject.get('group', '')
    myusr = nameobject.get('usr', False)
    mygrp = nameobject.get('grp', False)
    if isinstance(myusr, bool) is False:
        fail_invalid_definition(username, "usr")
    if isinstance(mygrp, bool) is False:
        fail_invalid_definition(username, "grp")
    if isinstance(group, str) is False:
        fail_invalid_definition(username, "group")
    if myusr is False:
        if mygrp is False:
            fail_invalid_usrgrp(username)
    if userid_check(myid) is False:
        fail_invalid_definition(username, "usr")
    if groupid != OS_MAX_PLUS_ONE:
        validate_no_groupid_conflicts(username, nameobject)

def validate_useradd_attributes(username: str, nameobject: dict) -> None:
    """Validates the optional useradd attributes."""
    shells = ["/bin/bash", "/bin/sh"]
    comment = nameobject.get('comment', 'A Valid String')
    homedir = nameobject.get('homedir', '/dev/null')
    shell = nameobject.get('shell', '/bin/bash')
    atypshell = nameobject.get('atypshell', False)
    if isinstance(atypshell, bool) is False:
        fail_invalid_definition(username, "atypshell")
    if usercomment_check(comment) is False:
        fail_invalid_definition(username, "comment")
    if homedir_check(homedir) is False:
        fail_invalid_definition(username, "homedir")
    if atypshell:
        if path_check(shell) is False:
            fail_invalid_definition(username, "shell")
    elif shell not in shells:
        fail_invalid_definition(username, "shell")

def validate_no_duplicates(username: str, myid: int, groupid: int, usedlist: list) -> list:
    """verifies accidental multiple assignment in JSON has not happened."""
    if myid not in DUPOK:
        if myid in usedlist:
            print(myid)
            fail_duplicate_id(username, 'myid', myid)
        else:
            usedlist.append(myid)
    if myid == groupid:
        return usedlist
    if groupid in DUPOK:
        return usedlist
    if groupid in usedlist:
        fail_duplicate_id(username, 'groupid', groupid)
    usedlist.append(groupid)
    return usedlist

def validate_json() -> int:
    """Validates the JSON configuration file and if successful, dumps contents to console."""
    usedlist = []
    sysusers = load_json()
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
        validate_user_group(username, nameobject)
        validate_useradd_attributes(username, nameobject)
        myid = nameobject.get('myid', OS_MAX_PLUS_ONE)
        groupid = nameobject.get('groupid', myid)
        usedlist = validate_no_duplicates(username, myid, groupid, usedlist)
        protected = nameobject.get('protected', False)
        if isinstance(protected, bool) is False:
            fail_invalid_definition(username, "protected")
    valid_json = json.dumps(sysusers)
    print(valid_json)
    return 0

def main(args) -> int:
    """Loads JSON file, applies argparse options."""
    # pylint: disable=global-statement
    global ATYPSHELL
    # pylint: enable=global-statement
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
    sysusers = load_json()
    keylist = list(sysusers.keys())
    if "000-CONFIG" in keylist:
        validate_cfg(sysusers["000-CONFIG"])
    if username not in keylist:
        sysusers[username] = {'myid': OS_MAX_PLUS_ONE, 'usr': True, 'grp': True}
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
    ATYPSHELL = sysusers[username].get("atypshell", False)
    just_do_it(username, sysusers)
    return 0


if __name__ == '__main__':
    sys.exit(main(PSR.parse_args()))

# EOF
