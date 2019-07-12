#!/bin/sh
HOST=`hostname`
echo "HOST: "$HOST
ETH0IP=`/sbin/ifconfig eth0 | sed -n "2,2p" | awk '{print substr($2,1)}'`
echo "IP:   "$ETH0IP
CPUNAME=`cat /proc/cpuinfo | grep Hardware | awk '{print substr($3,1)}'`
echo "NAME: "$CPUNAME
CPUCORE=`cat /proc/cpuinfo | grep processor | wc -l`
echo "CORE: "$CPUCORE
CPUARCH="`cat /proc/cpuinfo | grep "model name" | sort -n | tail -1 | cut -b 14-`"
echo "ARCH: "$CPUARCH
CPUTEMP=`vcgencmd measure_temp | cut -b 6-`
echo "TEMP: "$CPUTEMP
MEMT=`cat /proc/meminfo | grep MemTotal | awk '{print substr($2,1)}'`
echo "TOTAL:"$MEMT
MEMF=`cat /proc/meminfo | grep MemFree | awk '{print substr($2,1)}'`
echo "FREE: "$MEMF
MODEL=`cat /proc/device-tree/model`
echo "MODEL:"$MODEL
echo "====================================="
JSON=`jo -p host="$HOST" ip="$ETH0IP" cpu="$CPUNAME" core="$CPUCORE" arch="$CPUARCH" temperature="$CPUTEMP" model="$MODEL" mem="$MEMT" memf="$MEMF"`
curl -X POST --data "`echo -n $JSON | sed 's/"/\\"/g; s/\\r//g'`" http://test.qiuhao.online/rpi_status/