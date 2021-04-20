source env.cfg
#Spawing frontend container
sudo docker pull himgupta1996/pygmy:frontend
echo host=0.0.0.0 > frontend-env.txt
echo port=${frontend_port} >> frontend-env.txt
echo catalogA="http://${catalogA_ip}:${catalogA_port}" >> frontend-env.txt
echo catalogB="http://${catalogB_ip}:${catalogB_port}" >> frontend-env.txt
echo orderA="http://${orderA_ip}:${orderA_port}" >> frontend-env.txt
echo orderB="http://${orderB_ip}:${orderB_port}" >> frontend-env.txt
sleep 2
sudo docker run --name frontend --env-file frontend-env.txt -d -p ${frontend_port}:${frontend_port} himgupta1996/pygmy:frontend

