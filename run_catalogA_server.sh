source env.cfg

#Building catalog image
cd catalog/
sudo docker build -t himgupta1996/pygmy:catalog .
cd ../

#Spawing catalogA container
#sudo docker pull himgupta1996/pygmy:catalog
echo host=0.0.0.0 > catalogA-env.txt
echo port=${catalogA_port} >> catalogA-env.txt
echo replica="http://${catalogB_ip}:${catalogB_port}" >> catalogA-env.txt
echo tag=catalogA >> catalogA-env.txt
sleep 2
sudo docker run --name catalogA --env-file catalogA-env.txt -d -p ${catalogA_port}:${catalogA_port} himgupta1996/pygmy:catalog

