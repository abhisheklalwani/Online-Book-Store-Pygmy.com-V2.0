
source env.cfg

sleep 2
#Spawing orderA container
docker pull himgupta1996/pygmy:order
echo host=0.0.0.0 > orderA-env.txt
echo port=${orderA_port} >> orderA-env.txt
echo replica=${orderB} >> orderA-env.txt
echo catalog=${catalogA} >> orderA-env.txt
sleep 2
docker run --env-file orderA-env.txt -d -p ${orderA_port}:${orderA_port} himgupta1996/pygmy:order

#Spawing orderB container
docker pull himgupta1996/pygmy:order
echo host=0.0.0.0 > orderB-env.txt
echo port=${orderB_port} >> orderB-env.txt
echo replica=${orderA} >> orderB-env.txt
echo catalog=${catalogB} >> orderB-env.txt
sleep 2
docker run --env-file orderB-env.txt -d -p ${orderB_port}:${orderB_port} himgupta1996/pygmy:order

#Spawing catalogA container
docker pull himgupta1996/pygmy:catalog
echo host=0.0.0.0 > catalogA-env.txt
echo port=${catalogA_port} >> catalogA-env.txt
echo replica=${catalogB} >> catalogA-env.txt
sleep 2
docker run --env-file catalogA-env.txt -d -p ${catalogA_port}:${catalogA_port} himgupta1996/pygmy:catalog

#Spawing catalogB container
docker pull himgupta1996/pygmy:catalog
echo host=0.0.0.0 > catalogB-env.txt
echo port=${catalogB_port} >> catalogB-env.txt
echo replica=${catalogA} >> catalogB-env.txt
sleep 2
docker run --env-file catalogB-env.txt -d -p ${catalogB_port}:${catalogB_port} himgupta1996/pygmy:catalog

#Spawing frontend container
docker pull himgupta1996/pygmy:frontend
echo host=0.0.0.0 > frontend-env.txt
echo port=${frontend_port} >> frontend-env.txt
echo catalogA=${catalogA} >> frontend-env.txt
echo catalogB=${catalogB} >> frontend-env.txt
echo orderA=${orderA} >> frontend-env.txt
echo orderB=${orderB} >> frontend-env.txt
sleep 2
docker run --env-file frontend-env.txt -d -p ${frontend_port}:${frontend_port} himgupta1996/pygmy:frontend
