Generating Docs
===============

__NOTE:__ In the development branch, the markdown version of man pages
may lag behind their corresponding roff man page.

Markdown conversion is done as a final step before merge with main.

---------------

Initially I tried writing the yjl-sysusers.8 man page in markdown and
then converting to man via pandoc.

It worked but the results were mediocre at best.

I then created the man page manually in vim. That produced a very good
looking man page.

I attempted to go from the man page to markdown, but it seens pandoc
(at least the version on CentOS 7) can only *generate* man pages, it
can not read them.

I then converted the man page to HTML:

    man2html yjl-sysusers.8 > yjl-sysusers.8.html

The version of `man2html` in CentOS 7 produces ugly looking HTML syntax
however I could then go from html to markdown via pandoc:

    pandoc -t markdown yjl-sysusers.8.html > yjl-sysusers.8.md

The result was fairly decent when viewed in the GitHub markdown
renderer but it needs some work to be useful when viewing in a a
console from the command line as a text file.

The plan currently is to manually create and edit the man pages and
then go through that conversion process just before a tagged release,
manually adjusting the markdown for optimal text file viewing.

Long term, I *probably* need to learn how to use DocBook, especially
if there will be translations of the man pages ever made.


