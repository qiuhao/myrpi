#!/bin/sh
CPUUSAGE="`/usr/bin/top -b -n1 | awk '/Cpu\(s\):/ {print $2}'`"
echo "USAGE: "$CPUUSAGE
HOST=`hostname`
echo "HOST: "$HOST
ETH0IP=`/sbin/ifconfig eth0 | sed -n "2,2p" | awk '{print substr($2,1)}'`
echo "IP:   "$ETH0IP
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
JSON=`jo -p host="$HOST" ip="$ETH0IP" cpu="$CPUNAME" core="$CPUCORE" arch="$CPUARCH" temperature="$CPUTEMP" freq="$CPUFREQ" model="$MODEL" mem="$MEMT" memf="$MEMF" usage="$CPUUSAGE"`
if [ $? -ne 0 ]; then 
echo "jo not installed"
JSON=`printf '{"%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":"%s","%s":%s,"%s":%s,"%s":%s,"%s":%s,"%s":%s}' "host" "$HOST" "ip" "$ETH0IP" "cpu" "$CPUNAME" "arch" "$CPUARCH" "temperature" "$CPUTEMP" "model" "$MODEL" "usage" "$CPUUSAGE" "core" "$CPUCORE" "mem" "$MEMT" "memf" "$MEMF" "freq" "0"`
fi
echo $JSON
curl -X POST --data "`echo -n $JSON | sed 's/"/\\"/g; s/\\r//g'`" http://test.qiuhao.online:8081/rpi_status/
