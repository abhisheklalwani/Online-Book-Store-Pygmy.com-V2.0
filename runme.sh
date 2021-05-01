
myip="$(dig +short myip.opendns.com @resolver1.opendns.com)"
source env.cfg

#Function to copy the repository from local to remote servers
copy_repo()
{
	if [[ $2 == $myip ]];
	then
		echo "pygmy repo already present locally."
	else
		echo "###### Copying the pygmy repo to the machine $2 to run $1 server ######"
		scp -i ${pem_file} -r ../pygmy ubuntu@$2:.
	fi
}

#Function to copy the log files from different servers
get_log_files()
{ 
	if [[ $2 == $myip ]]; then
		echo "Copying $1.log"
		sudo docker cp $1:/app/$1.log logs/
		if [[ "$1" == "frontend" ]]; then
			echo "Copying heartbeat.log"
			sudo docker cp $1:/app/heartbeat.log logs/
		fi
	else
		ip=$2
		echo "Copying $1.log"
		ssh -i ${pem_file} ubuntu@${ip} sudo docker cp $1:/app/$1.log .
		scp -i ${pem_file} ubuntu@${ip}:$1.log logs/
		if [[ "$1" == "frontend" ]]; then
			echo "Copying heartbeat.log"
			ssh -i ${pem_file} ubuntu@${ip} sudo docker cp $1:/app/heartbeat.log .
			scp -i ${pem_file} ubuntu@${ip}:heartbeat.log logs/
		fi
	fi

}

#Function to deploy container servers
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
		ssh -i ${pem_file} ubuntu@${ip} "cd pygmy && chmod +x ${run_server_file}" 
		ssh -i ${pem_file} ubuntu@${ip} "cd pygmy && . ./${run_server_file}"
	fi

}

#Copying the Source files to different servers
echo "###### Copying the Source files to different server. ######"
copy_repo orderA ${orderA_ip}
copy_repo orderB ${orderB_ip}
copy_repo catalogA ${catalogA_ip}
copy_repo catalogB ${catalogB_ip}
copy_repo frontend ${frontend_ip}

#Deploying the container servers
echo "###### Deploying the container servers. ######"
deploy_server orderA ${orderA_ip} run_orderA_server.sh
deploy_server orderB ${orderB_ip} run_orderB_server.sh
deploy_server catalogA ${catalogA_ip} run_catalogA_server.sh
deploy_server catalogB ${catalogB_ip} run_catalogB_server.sh
deploy_server frontend ${frontend_ip} run_frontend_server.sh

echo "###### Starting the Client Process. ######"
sleep 2
python client.py "http://${frontend_ip}" ${frontend_port} 2

#Copying log files locally to the folder ./logs/
echo "###### Copying log files locally to the folder ./logs/. ######"
get_log_files orderA ${orderA_ip}
get_log_files orderB ${orderB_ip}
get_log_files catalogA ${catalogA_ip}
get_log_files catalogB ${catalogB_ip}
get_log_files frontend ${frontend_ip}




