myip="$(dig +short myip.opendns.com @resolver1.opendns.com)"
source env.cfg

get_log_files()
{ 
	if [[ $2 == $myip ]]; then
		sudo docker cp $1:/app/$1.log .
	else
		ip=$2
		ssh -i ${pem_file} ubuntu@${ip} sudo docker cp $1:/app/$1.log .
		scp -i ${pem_file} ubuntu@${ip}:$1.log .
	fi

}

deploy_server()
{
	run_server_file=$3
	if [[ $2 == $myip ]]; then
		echo "###### Deploying $1 server locally. ######"
		sleep 2
		. ./${run_server_file}
	else
		echo "###### Deploying $1 server on the server with public IP: $2 ######"
		sleep 2
		ip=$2
		scp -i ${pem_file} env.cfg ubuntu@${ip}:/home/ubuntu/
		scp -i ${pem_file} ${run_server_file} ubuntu@${ip}:/home/ubuntu/
		ssh -i ${pem_file} ubuntu@${ip} chmod +x ${run_server_file} 
		ssh -i ${pem_file} ubuntu@${ip} . ./${run_server_file}
	fi

}
deploy_server orderA ${orderA_ip} run_orderA_server.sh
deploy_server orderB ${orderB_ip} run_orderB_server.sh
deploy_server catalogA ${catalogA_ip} run_catalogA_server.sh
deploy_server catalogB ${catalogB_ip} run_catalogB_server.sh
deploy_server frontend ${frontend_ip} run_frontend_server.sh

echo "###### Starting the Client Process. ######"
sleep 2
python client.py "http://${frontend_ip}" ${frontend_port} 5

get_log_files orderA ${orderA_ip}
get_log_files orderB ${orderB_ip}
get_log_files catalogA ${catalogA_ip}
get_log_files catalogB ${catalogB_ip}
get_log_files frontend ${frontend_ip}


