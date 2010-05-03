LOCPYTHON="$(cat $(find | grep \\.py) | wc -l)"
LOCJS="$(cat $(find | grep \\.js | grep -v jquery | grep -v json) | wc -l)"
LOCHTML="$(cat $(find | grep \\.html) | wc -l)"
echo LoC python: $LOCPYTHON
echo LoC js: $LOCJS
echo LoC html: $LOCHTML
echo Total: $[ $LOCPYTHON + $LOCJS + $LOCHTML ]
