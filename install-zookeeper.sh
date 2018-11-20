#######################
# Variable definition #
#######################
ip1="192.168.1.14"
ip2="192.168.1.15"
ip3="192.168.1.16"
myid=1

#Download and unzip zookeeper
echo "
----------------------------------------------
 Downloading Apache Zookeeper from repository
----------------------------------------------"
#    Download
curl http://ftp.cixug.es/apache/zookeeper/stable/zookeeper-3.4.12.tar.gz -o zookeeper-3.4.12.tar.gz
#    Unzip
echo "----------------------------------------------
 Unzipping contents - Be patient
----------------------------------------------"
tar -zxf zookeeper-3.4.12.tar.gz
#    Rename
mv zookeeper-3.4.12 zookeeper
#    Delete zip
rm zookeeper-3.4.12.tar.gz
echo "Unzip OK!"

#Set up config file
echo "----------------------------------------------
 Setting up zookeeper config
----------------------------------------------"

echo "tickTime=2000
initLimit=10
syncLimit=5
dataDir=$PWD/zookeeper/data
clientPort=2181
server.1=$ip1:2888:3888
server.2=$ip2:2888:3888
server.3=$ip3:2888:3888
" > zookeeper/conf/zoo.cfg
#Create data dir
mkdir zookeeper/data
#Set up myid
echo "$myid" > zookeeper/data/myid

echo "Config OK"

#Ensure we have a JDK installed, or install version JDK v7
echo "----------------------------------------------
 Setting up java config
----------------------------------------------"
javac -version || ( yes | sudo apt-get update && yes | sudo apt-get install openjdk-8-jdk )

#Find jdk installation folder, usually /usr/local/jvm/<jdk>
javaout=$(which javac)
javahome=$(sudo readlink -f $javaout | sed -s 's/\/bin\/javac//')

#Ensure no errors during installation or exit
if [ -z $javahome ] ; then
	echo "Unable to find the JDK file in the system. Aborting!"
	exit -1
fi
echo "Java JDK found in $javahome"
echo "Config OK"

#Add JAVA_HOME var to bashrc
echo "----------------------------------------------
 Setting JAVA_HOME in .bashrc
----------------------------------------------"
echo "
JAVA_HOME=\$JAVA_HOME:$javahome
export JAVA_HOME" >> /home/$USER/.bashrc
#Refresh source
source /home/$USER/.bashrc
echo "Java home:
$JAVA_HOME"



echo "cd zookeeper && java -cp zookeeper-3.4.12.jar:lib/slf4j-api-1.7.25.jar:lib/slf4j-log4j12-1.7.25.jar:lib/log4j-1.2.17.jar:lib:conf org.apache.zookeeper.server.quorum.QuorumPeerMain $PWD/zookeeper/conf/zoo.cfg" > $PWD/launch-zookeeper.sh

echo "
#########################
# INSTALLATION FINISHED #
#########################
Launch Apache Zookeeper using the following line:

bash launch-zookeeper.sh"
