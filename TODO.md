TODO
====

Right now it mostly works except it does not work.

To actually add the group and user, `subprocess.run()` is used. It
is not however *used correctly* so it does not work. I have to learn
how to properly use subprocess. All other things seem to work.

It needs to be integrated with gettext for string i18n string
translation.

With respect to `argparse` I still have to add boolean options to
allow specifying/over-riding the creation of users/groups and the
`/etc/skel` options.

Then after `argparse` processing, `main()` needs to verify that both
user and group creation have not been turned off.

There is a typehint that needs to be made, I do not (yet) know how to
typehint when a default is specified. That should be simple.

Need to make a `man 1` and a `man 5` page. Initially this will be
done by writing them in markdown and converting to man via

    pandoc yjl-sysusers.1.md -s -t man -o yjl-sysusers.1

(previewed with:)

    pandoc yjl-sysusers.1.md -s -t man |/usr/bin/man -l -

However I suspect long term the other-way-around will be used. 