#!/bin/sh
ps -ef | grep rpi_status_svr.py | grep -v grep 
if [ $? -ne 0 ] 
then 
echo "starting rpi_status service" 
python3 /root/rpi_status/rpi_status_svr.py > /root/rpi_status/log.log 2>&1 &
else 
echo "rpi_status service is running" 
fi
