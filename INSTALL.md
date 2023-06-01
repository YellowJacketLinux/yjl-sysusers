INSTALL
=======

__First__, modify the `yjl-sysusers.json` file for your distribution.
The current setup from github is for [YellowJacket GNU/Linux](YJL-Notes.md)
which I know you are not running because I have not created an installer
for YJL yet.

If you are lucky, the `contrib` directory has a JSON file for your
GNU/Linux distribution that you can use.

See the [yjl-sysusers.json.5](docs/yjl-sysusers.json.5.md) for information
about that file and valid entries.

Your version must be named `yjl-sysusers.json` and in the source directory,
top level where the `functions.py` file is.

__Second__, test your version of the `yjl-sysusers.json` file by running
the following command:

    python3 functions.py --bootstrap 000

If your JSON is valid and your properties are valid, a bunch of JSON
will be dumped to screen but the exit status will be 0.

If you have a mistake, there should be a human-readable error message
and the exit status will be 1.

__Third__, look at the Makefile and change anything that is wrong for
your distribution. If your distribution is FHS compliant, nothing
should need changing *unless* you want stuff put in `/usr/local`.

__Fourth__, run the command

    make install

More properly when building an RPM package:

    DESTDIR=%{buildroot} make install-rpm

See the reference `yjl-sysusers.spec` file.

__Fifth__, if your `yjl-sysusers.json` file is complete for the
static UID/GID assignments of your GNU/Linux distribution, consider
contacting me about adding it to the `contrib` directory.
