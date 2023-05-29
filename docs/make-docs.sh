#/bin/bash

for manfile in yjl-sysusers.8 yjl-sysusers.json.5; do
  man2html ${manfile} > ${manfile}.html
  pandoc -t markdown ${manfile}.html > ${manfile}.md
  rm -f ${manfile}.html
done
