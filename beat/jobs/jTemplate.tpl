
{% include "pbs_header.tpl" %}

{% include "modules.tpl" %}

{% include "setstack.tpl" %}

echo command: {{ prefix }} memtime {{ toolname }} {{ tooloptions }} {{ modelname }} {{ postfix }}

{% include "header.tpl" %}

{{ prefix }} memtime {{ toolname }} {{ tooloptions }} {{ modelname }} {{ postfix }}

echo REPORT ENDS HERE