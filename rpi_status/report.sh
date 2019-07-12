ETH0_IP=`/sbin/ifconfig eth0 | sed -n "2,2p" | awk '{print substr($2,1)}'` 
HOST=`hostname` 
curl -X POST --data "{\"host\":\"$HOST\",\"ip\":\"$ETH0_IP\"}" http://test.qiuhao.online/rpi_status/
