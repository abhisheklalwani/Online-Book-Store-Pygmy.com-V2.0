#Spawing orderA container
source env.cfg
sudo docker pull himgupta1996/pygmy:order
echo host=0.0.0.0 > orderA-env.txt
echo port=${orderA_port} >> orderA-env.txt
echo replica="http://${orderB_ip}:${orderB_port}" >> orderA-env.txt
echo catalog="http://${catalogA_ip}:${catalogA_port}" >> orderA-env.txt
sleep 2
sudo docker run --env-file orderA-env.txt -d -p ${orderA_port}:${orderA_port} himgupta1996/pygmy:order
