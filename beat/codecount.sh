LOCPYTHON="$(cat $(find | grep \\.py) | wc -l)"
LOCJS="$(cat $(find | grep \\.js | grep -v jquery | grep -v json) | wc -l)"
LOCHTML="$(cat $(find | grep \\.html) | wc -l)"
LOCCSS="$(cat $(find | grep \\.css) | wc -l)"
echo LoC python: $LOCPYTHON
echo LoC js: $LOCJS
echo LoC html: $LOCHTML
echo LoC css: $LOCCSS
echo Total: $[ $LOCPYTHON + $LOCJS + $LOCHTML + $LOCCSS ]
