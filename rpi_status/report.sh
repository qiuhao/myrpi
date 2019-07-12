ETH0_IP=`/sbin/ifconfig eth0 | sed -n "2,2p" | awk '{print substr($2,1)}'`
HOST=`hostname`
MEM=`cat /proc/meminfo | grep MemTotal | awk '{print substr($2,1)}'`
MEMA=`cat /proc/meminfo | grep MemAvailable | awk '{print substr($2,1)}'`
MEMF=`cat /proc/meminfo | grep MemFree | awk '{print substr($2,1)}'`
MODEL=`cat /proc/device-tree/model`
CPU=`cat /proc/cpuinfo | grep Hardware | awk '{print substr($3,1)}'`
CPU_CORE=`cat /proc/cpuinfo | grep processor | wc -l`
CPU_ARCH=`cat /proc/cpuinfo | grep "model name" | sort -n | tail -1 | cut -b 14-`
CPU_TEMP=`vcgencmd measure_temp | cut -b 6-`
curl -X POST --data "{\"host\":\"$HOST\",\"ip\":\"$ETH0_IP\",\"temperature\":\"$CPU_TEMP\",\"cpu\":\"$CPU\",\"core\":\"$CPU_CORE\",\"arch\":\"$CPU_ARCH\",\"model\":\"$MODEL\",\"mem\":\"$MEM\",\"mema\":\"$MEMA\",\"memf\":\"$MEMF\"}" http://test.qiuhao.online/rpi_status/
