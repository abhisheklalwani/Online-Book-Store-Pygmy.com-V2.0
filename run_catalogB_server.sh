source env.cfg

#Builing catalog image
cd catalog/
sudo docker build -t himgupta1996/pygmy:catalog .
cd ../

#Spawing catalogB container
#sudo docker pull himgupta1996/pygmy:catalog
echo host=0.0.0.0 > catalogB-env.txt
echo port=${catalogB_port} >> catalogB-env.txt
echo replica="http://${catalogA_ip}:${catalogA_port}" >> catalogB-env.txt
echo tag=catalogB >> catalogB-env.txt
sleep 2
sudo docker run --name catalogB --env-file catalogB-env.txt -d -p ${catalogB_port}:${catalogB_port} himgupta1996/pygmy:catalog

