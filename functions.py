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
from datetime import datetime, timezone

MYVERSION = "0.1.5"
# Initial globals that get reset
NOGROUP = "nogroup"
DUPOK = []
# A list of dictionaries, gets reset by 000-CONFIG
DYNAMIC = [{'min': 201, 'max': 499}]
ATYPSHELL = False
CFGDESC = ""
CFGMAIN = ""
CFGMODT = ""
CFGVALT = ""
# used as non-collision dummy intiger to trigger dynamic
OS_MAX_PLUS_ONE = 65535
# by default, like GID/UID for same account name to match
COMMONID = True

# Dummy function until gettext is used
def _(fubar):
    return fubar

def fail_not_root() -> None:
    """Exits with invalid permissions error."""
    sys.exit(_("Sorry, you must be root to run me. Try with ") + "'sudo'" + ".")

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

def fail_badcfg_property(prop: str, strict: bool) -> None:
    """If strict, exits with message about bad 000-CONFIG property."""
    if strict:
        sys.exit(_("The property '")
                 + prop
                 + _("' in '000-CONFIG' is invalid."))

def fail_invalid_usergroup(name: str) -> None:
    """Exits with invalid username/groupname message."""
    sys.exit(_("The user/group name '")
             + name
             + _("' is not valid."))

def fail_load_json(jsonfile: str) -> None:
    """Exits with invalid JSON message."""
    sys.exit(_("Could not load the JSON data file:") + " " + jsonfile)

def fail_addaccount(accountname: str, ugtype: str) -> None:
    """Exits with message about failed user/group creation."""
    sys.exit(_("Failed to add the '")
             + accountname
             + "' "
             + ugtype
             + _(" account."))

def fail_nouids_left(accountname: str) -> None:
    """Exits with message about insufficient UIDs."""
    sys.exit(_("Failed to add the '")
             + accountname
             + _("' due to insufficient remaining dynamic system UIDs"))

APDICT = {
    "description": _("Add system users and groups. See:") + " 'man 8 yjl-sysusers'",
    "version": _("show version information and exit"),
    "bootstrap": _("bootstrap validate the JSON file"),
    "comment": _("specify the user comment passwd field"),
    "home": _("specify the user home directory"),
    "shell": _("specify the user login shell"),
    "group": _("specify the default group NAME for the user"),
    "uadd": _("only add a user, do not add a group"),
    "gadd": _("only add a group, do not add a user"),
    "badd": _("require creation of both a user and group"),
    "mkdir": _("create the user home directory with useradd"),
    "delete": _("delete the specified user and group"),
    "account": _("user or group name to add")
}

# class from https://gist.github.com/jmoiron/6543743
class Parser(argparse.ArgumentParser):
    """Allows some getparse options to shortcircuit positional argument."""
    has_errors = False

    def error(self, message):
        self.has_errors = True
        self.error_message = message

    def handle_error(self):
        if self.has_errors:
            super(Parser, self).error(self.error_message)

PSR = Parser(description=APDICT["description"])
#PSR = argparse.ArgumentParser(description=APDICT["description"])
PSR.add_argument("-v", "--version", action='store_true', help=APDICT["version"])
PSR.add_argument("--bootstrap", action='store_true', help=APDICT["bootstrap"])
PSR.add_argument("-c", "--comment", type=str, help=APDICT["comment"])
PSR.add_argument("-d", "--home", type=str, help=APDICT["home"])
PSR.add_argument("-s", "--shell", type=str, help=APDICT["shell"])
PSR.add_argument("-g", "--group", type=str, help=APDICT["group"])
PSR.add_argument("--onlyuser", action='store_true', help=APDICT["uadd"])
PSR.add_argument("--onlygroup", action='store_true', help=APDICT["gadd"])
PSR.add_argument("--userandgroup", action='store_true', help=APDICT["badd"])
PSR.add_argument("--mkdir", action='store_true', help=APDICT["mkdir"])
PSR.add_argument("--delete", action='store_true', help=APDICT["delete"])
PSR.add_argument('account', type=str, help=APDICT["account"])

def showinfo() -> None:
    """prints version and related information and exits."""
    print(_("This is ") + "yjl-sysusers " + _("version ") + str(MYVERSION))
    print(_("Copyright (c)") + " 2023 YellowJacket GNU/Linux. MIT License.")
    mysum = len(CFGDESC) + len(CFGMAIN) + len(CFGMODT) + len(CFGVALT)
    if mysum == 0:
        return
    print()
    print("yjl-sysusers.json " + _("information:"))
    if len(CFGDESC) > 0:
        print(_("      Decription: ") + CFGDESC)
    if len(CFGMAIN) > 0:
        print(_("      Maintainer: ") + CFGMAIN)
    if len(CFGMODT) > 0:
        print(_("   Last Modified: ") + CFGMODT)
    if len(CFGVALT) > 0:
        print(_("  JSON Validated: ") + CFGVALT)

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
        fail_load_json(jsonfile)

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
            fail_addaccount(gpname, "group")
    else:
        # this only happens in testing, main() checks for root
        print(mycmd)
        return gid
    try:
        existing = grp.getgrnam(gpname)
    except KeyError:
        fail_addaccount(gpname, "group")
    return existing.gr_gid

def load_id_list(desired: int) -> list:
    """Returns list of IDs to query for system group/user creation."""
    mylist = []
    if desired != OS_MAX_PLUS_ONE:
        mylist.append(desired)
    for dydict in DYNAMIC:
        mymin = dydict.get('min', 500)
        mymax = dydict.get('max', 999) + 1
        if mymax > mymin:
            for i in range(mymin, mymax):
                if i not in mylist:
                    mylist.append(i)
    return mylist

def find_group_id(gpname: str, desired: int, unipair=True) -> int:
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
            if not unipair:
                return add_the_group(gpname, i)
            else:
                try:
                    existing = pwd.getpwuid(i)
                except KeyError:
                    return add_the_group(gpname, i)
        unipair = True
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
    return find_group_id(gpname, desired, COMMONID)

def determine_useradd_uid_from_json(username: str, sysusers: dict) -> int:
    """Given a username, find the appropriate UID for useradd command."""
    nameobject = sysusers[username]
    if COMMONID:
        desired = determine_useradd_gid_from_json(username, sysusers)
    else:
        desired = nameobject.get('myid', OS_MAX_PLUS_ONE)
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
    fail_nouids_left(username)

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
            fail_addaccount(username, "user")
    else:
        # this only happens in testing, main() checks for root.
        print(spclist)

def just_do_it(username: str, sysusers: dict) -> None:
    """Called by main() to creates the user/group account as needed."""
    # pylint: disable=global-statement
    global COMMONID
    # pylint: enable=global-statement
    nameobject = sysusers[username]
    test_a = nameobject.get('myid', OS_MAX_PLUS_ONE)
    test_b = nameobject.get('groupid', test_a)
    COMMONID = (test_a == test_b)
    createuser = nameobject.get('usr', False)
    if createuser:
        add_the_user(username, sysusers)
    else:
        # this causes group to be added
        determine_useradd_gid_from_json(username, sysusers)

def val_cfg_string(prop: str, checkme: str, strict: bool) -> str:
    """Validates a string from cfg is a string."""
    if isinstance(checkme, str) is False:
        fail_badcfg_property(prop, strict)
        return ""
    if checkme.isprintable():
        return checkme
    else:
        fail_badcfg_property(prop, strict)
    return ""

def validate_dynamic(mydynamic: list, strict: bool) -> list:
    """Validates the dynamic UID/GID range and return it."""
    valid = []
    for mydict in mydynamic:
        try:
            mymin = mydict.get("min")
        except KeyError:
            fail_badcfg_property("dynamic", strict)
        try:
            mymax = mydict.get("max")
        except KeyError:
            fail_badcfg_property("dynamic", strict)
        if mymin < mymax:
            valid.append({'min': mymin, 'max': mymax})
        else:
            fail_badcfg_property("dynamic", strict)
    if not valid:
        # empty list
        return DYNAMIC
    return valid

def validate_cfg(cfgdict: dict, strict: bool) -> None:
    """Validates the 000-CONFIG json object."""
    # pylint: disable=global-statement
    global NOGROUP
    global DUPOK
    global DYNAMIC
    # cfg metadata
    global CFGDESC
    global CFGMAIN
    global CFGMODT
    global CFGVALT
    # pylint: enable=global-statement
    NOGROUP = cfgdict.get("nogroup", "nogroup")
    DUPOK = cfgdict.get("dupok", [])
    if username_check(NOGROUP) is False:
        fail_badcfg_property("nogroup", strict)
        NOGROUP = "nogroup"
    for i in DUPOK:
        if userid_check(i) is False:
            fail_badcfg_property("dupok", strict)
            DUPOK = []
    mydnamic = cfgdict.get("dynamic", DYNAMIC)
    DYNAMIC = validate_dynamic(mydnamic, strict)
    #
    CFGDESC = val_cfg_string("description", cfgdict.get("description", ""), strict)
    CFGMAIN = val_cfg_string("maintainer", cfgdict.get("maintainer", ""), strict)
    CFGMODT = val_cfg_string("modified", cfgdict.get("modified", ""), strict)
    CFGVALT = val_cfg_string("validated", cfgdict.get("validated", ""), strict)
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

def validate_json(sysusers: dict) -> None:
    """Validates the JSON configuration file and if successful, dumps contents to console."""
    usedlist = []
    keylist = list(sysusers.keys())
    if "000-CONFIG" in keylist:
        validate_cfg(sysusers["000-CONFIG"], True)
        keylist.remove("000-CONFIG")
    else:
        sysusers["000-CONFIG"] = {}
    for username in keylist:
        if username_check(username) is False:
            fail_invalid_usergroup(username)
        nameobject = sysusers[username]
        validate_user_group(username, nameobject)
        validate_useradd_attributes(username, nameobject)
        myid = nameobject.get('myid', OS_MAX_PLUS_ONE)
        groupid = nameobject.get('groupid', myid)
        usedlist = validate_no_duplicates(username, myid, groupid, usedlist)
        protected = nameobject.get('protected', False)
        if isinstance(protected, bool) is False:
            fail_invalid_definition(username, "protected")
    now = datetime.now(timezone.utc).isoformat('T', 'seconds')
    sysusers['000-CONFIG'].update({"validated": now})
    valid_json = json.dumps(sysusers)
    print(valid_json)

def adjust_username_object(args, username: str, sysusers: dict) -> dict:
    """Adjust the sysuser object for the argparse arguments"""
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
    if args.onlyuser:
        sysusers[username].update({"usr": True})
        sysusers[username].update({"grp": False})
    elif args.onlygroup:
        sysusers[username].update({"usr": False})
        sysusers[username].update({"grp": True})
    elif args.userandgroup:
        sysusers[username].update({"usr": True})
        sysusers[username].update({"grp": True})
    if args.mkdir:
        sysusers[username].update({"mkdir": True})
    if args.group == args.account:
        args.group = None
    if args.group is not None:
        if username_check(args.group):
            keylist = list(sysusers.keys())
            if args.group not in keylist:
                sysusers[args.group] = {'myid': OS_MAX_PLUS_ONE, 'usr': False, 'grp': True}
            sysusers[username].update({"usr": True})
            sysusers[username].update({"grp": False})
            sysusers[username].update({"group": args.group})
        else:
            fail_invalid_usergroup(args.group)
    return sysusers

def main(args) -> int:
    """Loads JSON file, applies argparse options."""
    bypass_error = False
    if args.bootstrap:
        bypass_error = True
    if args.version:
        bypass_error = True
    if PSR.has_errors and not bypass_error:
        PSR.handle_error()
    if args.delete:
        # not yet implemented
        return 0
    # pylint: disable=global-statement
    global ATYPSHELL
    # pylint: enable=global-statement
    sysusers = load_json()
    if args.bootstrap:
        validate_json(sysusers)
        return 0
    try:
        validate_cfg(sysusers["000-CONFIG"], False)
    except KeyError:
        pass
    if args.version:
        showinfo()
        return 0
    myuid = os.getuid()
    if myuid != 0:
        fail_not_root()
    if username_check(args.account):
        username = args.account
    else:
        fail_invalid_usergroup(args.account)
    keylist = list(sysusers.keys())
    if username not in keylist:
        sysusers[username] = {'myid': OS_MAX_PLUS_ONE, 'usr': True, 'grp': True}
    # modify sysusers[username] based upon arguements
    sysusers = adjust_username_object(args, username, sysusers)
    #
    ATYPSHELL = sysusers[username].get("atypshell", False)
    just_do_it(username, sysusers)
    return 0


if __name__ == '__main__':
    sys.exit(main(PSR.parse_args()))

# EOF
