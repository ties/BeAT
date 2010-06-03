echo BEGIN OF HEADER

echo Nodename: $(uname -n)
echo Hardware-name: $(uname -m)
echo OS: $(uname -o)\n
echo Kernel-name: $(uname -s)
echo Kernel-release: $(uname -r)
echo Kernel-version: $(uname -v)
echo Hardware-platform: $(uname -i)
echo Processor: $(uname -p)
echo Memory-total: $(cat /proc/meminfo | grep MemTotal | tr -s \" \" | cut -d\" \" -f 2 -)
echo DateTime: $(date '+%Y %m %d %H %M %S') $[ $(date '+%-N') / 1000 ]

echo ToolVersion: $( {{ toolname }} --version | cut -d' ' -f 2)
echo Call: {{ toolname }} {{ tooloptions }} {{ modelname }}

echo END OF HEADER