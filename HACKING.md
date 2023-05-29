Hacking
=======

Largely notes to myself.

1) Copy the file `functions.py` to `fubar.py`

2) Edit the file `fubar.py`. In the function `myjson()` change
   `jsonfile = 'yjl-sysusers.json'` to `jsonfile = 'fubar.json'`

3) Further edit `fubar.py`. In the function `main()` change
   `if myuid != 0:` to `if myuid == 0:`

4) Whatever JSON file you want to work with, copy it to
   `fubar.json`

You can test the integrity of the JSON via:

    python3 fubar.py 000

You can test what it does when given arguments by:

    python3 fubar.py [options] somename

When done hacking, remember to run `pylint` on `fubar.py` and fix
what is reasonable, integrate any changes into `functions.py`
(using the `diff` command is useful) other than Steps 2 and 3 above,
and if applicable, merge any JSON changes.


New Version Notes
-----------------

Before pull request merging development into main:

1) Make sure both man pages reflect and changes.

2) Make sure to update `Modified:` date in both man pages (line 6).

3) Make sure to update the Month, year, and version in both man pages
   (`.TH` line 10)

4) run the script `make-docs.sh` (inside the `docs` dir) to regenerate
   the markdown pages.

5) Hand edit the resulting Markdown pages so they look good in both a
   console as plain text, and in github markdown web viewer.

6) Make sure version is correct in `yjl-sysusers.spec` file (the
   `%global gitv` in first line)

7) Make sure version is correct in README.md

8) Merge into `master` branch

9) create new tagged release `v` followed by version.
