# Python 3 required
PYTHON = python3
INSTALL = /usr/bin/install
CHMOD = /usr/bin/chmod
SED = /usr/bin/sed
RM = /bin/rm
# Filesystem paths
DATADIR = /usr/share
MANDIR = /usr/share/man
SBINDIR = /usr/sbin
RPMMACRODIR = /usr/lib/rpm/macros.d

dummy:
	echo "run make install"

install: install-macros install-man install-json install-program

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

uninstall:
	$(RM) -f $(DESTDIR)$(RPMMACRODIR)/macros.yjl-sysusers
	$(RM) -f $(DESTDIR)$(MANDIR)/man8/yjl-sysusers.8
	$(RM) -f $(DESTDIR)$(MANDIR)/man5/yjl-sysusers.json.5
	$(RM) -f $(DESTDIR)$(DATADIR)/yjl-sysusers/yjl-sysusers.json
	$(RM) -f $(DESTDIR)$(SBINDIR)/yjl-sysusers
