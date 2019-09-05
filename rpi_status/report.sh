#!/bin/sh
SCRIPTVER=2
CPUUSAGE="`/usr/bin/top -b -n1 | awk '/Cpu\(s\):/ {print $2}'`"
echo "USAGE: "$CPUUSAGE
HOST=`hostname`
echo "HOST: "$HOST
ETH0IP=`/sbin/ifconfig eth0 | grep 'inet ' | awk '{print substr($2,1)}'`
echo "IP:   "$ETH0IP
ETH0IP6=`/sbin/ifconfig eth0 | grep 'inet6' | awk '{print substr($2,1)}'`
echo "IPv6: "$ETH0IP6
WLANIP=`/sbin/ifconfig wlan0 | grep 'inet ' | awk '{print substr($2,1)}'`
echo "WIP:  "$WLANIP
WLANIP6=`/sbin/ifconfig wlan0 | grep 'inet6' | awk '{print substr($2,1)}'`
echo "WIPv6: "$WLANIP6
CPUNAME=`cat /proc/cpuinfo | grep Hardware | awk '{print substr($3,1)}'`
echo "NAME: "$CPUNAME
CPUCORE=`cat /proc/cpuinfo | grep processor | sed -n '/^processor/p' | wc -l`
echo "CORE: "$CPUCORE
CPUARCH="`cat /proc/cpuinfo | grep "model name" | sort -n | tail -1 | cut -b 14-`"
echo "ARCH: "$CPUARCH
CPUTEMP=`vcgencmd measure_temp | cut -b 6-`
echo "FREQ: "$CPUTEMP
CPUFREQ=`vcgencmd measure_clock arm | cut -b 15-`
echo "TEMP: "$CPUFREQ
MEMT=`cat /proc/meminfo | grep MemTotal | awk '{print substr($2,1)}'`
echo "TOTAL:"$MEMT
MEMF=`cat /proc/meminfo | grep MemFree | awk '{print substr($2,1)}'`
echo "FREE: "$MEMF
MODEL=`cat /proc/device-tree/model`
echo "MODEL:"$MODEL
echo "====================================="
JSON=`jo -p host="$HOST" ip="$ETH0IP" ipv6="$ETH0IP6" wip="$WLANIP" wipv6="$WLANIP6" cpu="$CPUNAME" core="$CPUCORE" arch="$CPUARCH" temperature="$CPUTEMP" freq="$CPUFREQ" model="$MODEL" mem="$MEMT" memf="$MEMF" usage="$CPUUSAGE" scriptver="$SCRIPTVER"`
if [ $? -ne 0 ]; then 
echo "jo not installed"
JSON=`printf '{"%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":%s,"%s":%s,"%s":%s,"%s":%s,"%s":%s,"%s":%s}' "host" "$HOST" "ip" "$ETH0IP" "ipv6" "$ETH0IP6" "wip" "$WLANIP" "wipv6" "$WLANIP6" "cpu" "$CPUNAME" "arch" "$CPUARCH" "temperature" "$CPUTEMP" "model" "$MODEL" "usage" "$CPUUSAGE" "core" "$CPUCORE" "mem" "$MEMT" "memf" "$MEMF" "freq" "0" "scriptver" "$SCRIPTVER"`
fi
echo $JSON
curl -X POST --data "`echo -n $JSON | sed 's/"/\\"/g; s/\\r//g'`" http://test.qiuhao.online:8081/rpi_status/
