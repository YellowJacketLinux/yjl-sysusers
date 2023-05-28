# Python 3 required
PYTHON = python3
INSTALL = /usr/bin/install
CHMOD = /usr/bin/chmod
SED = /usr/bin/sed
# Filesystem paths
DATADIR = /usr/share
MANDIR = /usr/share/man
SBINDIR = /usr/sbin
RPMMACRODIR = /usr/lib/rpm/macros.d

install-macros:
	$(INSTALL) -Dm644 macros.yjl-sysusers $(DESTDIR)$(RPMMACRODIR)/macros.yjl-sysusers

install-man:
	$(INSTALL) -Dm644 docs/yjl-sysusers.8 $(DESTDIR)$(MANDIR)/man8/yjl-sysusers.8
	$(INSTALL) -Dm644 docs/yjl-sysusers.json.5 $(DESTDIR)$(MANDIR)/man5/yjl-sysusers.json.5

install-json:
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/yjl-sysusers
	$(PYTHON) functions.py 000 > $(DESTDIR)$(DATADIR)/yjl-sysusers/yjl-sysusers.json
	$(CHMOD) 0444 $(DESTDIR)$(DATADIR)/yjl-sysusers/yjl-sysusers.json

install-program:
	$(INSTALL) -d $(DESTDIR)$(SBINDIR)
	$(SED) -e s?"cfgdir = ''"?"cfgdir = '$(DATADIR)/yjl-sysusers'"? < functions.py > $(DESTDIR)$(SBINDIR)/yjl-sysusers
	$(CHMOD) 0750 $(DESTDIR)$(SBINDIR)/yjl-sysusers
