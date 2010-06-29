{% comment %}
one day this template will do something like
	module load ltsmin/<version>
but since the module loading doesn't appear to be working at this time, we'll settle for an echo.
{% endcomment %}

echo 'Pretending to load {{ version }}'
