

在服务端的nginx配置代理：

​        location /rpi_status/ {

​            rewrite /(.*)$ /$1 break;

​            proxy_redirect off;

​            proxy_pass [http://127.0.0.1:23912;](http://127.0.0.1:23912;/)

​            proxy_set_header Host $host;

​            proxy_set_header X-Real-Ip $remote_addr;

​            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

​            proxy_cache_valid any 0s;

​        }



写个守护进程脚本：

\#!/bin/sh

ps -ef | grep rpi_status_svr.py | grep -v grep

if [ $? -ne 0 ]

then

echo "starting rpi_status service"

python3 /root/rpi_status//rpi_status_svr.py > /root/rpi_status/log.log 2>&1 &

else

echo "rpi_status service is running"

fi



在crontab里加上* * * * * /root/rpi_status/check_rpi_svr.sh > /dev/null 2>&1 &

每分钟检查一下服务状态



客户端上报：

脚本(注意ifconfig要写全路径， 不然拿不到)：

ETH0_IP=`/sbin/ifconfig eth0 | sed -n "2,2p" | awk '{print substr($2,1)}'`

HOST=`hostname`

curl -X POST --data "{\"host\":\"$HOST\",\"ip\":\"$ETH0_IP\"}" <http://<serveraddr:port>>/rpi_status/

启用crontab任务（都加在root下）：

*/5 * * * * sh /home/pi/report.sh > /dev/null 2>&1 &



