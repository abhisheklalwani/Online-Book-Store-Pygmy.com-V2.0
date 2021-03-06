source env.cfg

#Builing order image
cd order/
sudo docker build -t himgupta1996/pygmy:order .
cd ../

#Spawing orderB container
#sudo docker pull himgupta1996/pygmy:order
echo host=0.0.0.0 > orderB-env.txt
echo port=${orderB_port} >> orderB-env.txt
echo replica="http://${orderA_ip}:${orderA_port}" >> orderB-env.txt
echo catalog="http://${catalogB_ip}:${catalogB_port}" >> orderB-env.txt
echo catalog_replica="http://${catalogA_ip}:${catalogA_port}" >> orderB-env.txt
echo tag=orderB >> orderB-env.txt
sleep 2
sudo docker run --name orderB --env-file orderB-env.txt -d -p ${orderB_port}:${orderB_port} himgupta1996/pygmy:order

