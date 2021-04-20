myip="$(dig +short myip.opendns.com @resolver1.opendns.com)"
source env.cfg

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
deploy_server order ${orderA_ip} run_orderA_server.sh
deploy_server order ${orderB_ip} run_orderB_server.sh
deploy_server catalog ${catalogA_ip} run_catalogA_server.sh
deploy_server catalog ${catalogB_ip} run_catalogB_server.sh
deploy_server frontend ${frontend_ip} run_frontend_server.sh
#Deploying the orderA server

string='My long string'
#if [[ $orderA_ip == $myip ]]; then
#	  echo "It's there!"
#else
#	echo "Not there"
#	ip=${orderA_ip}
#	run_server_file="run_orderA_server.sh"
#	scp -i ${pem_file} env.cfg ubuntu@${ip}:/home/ubuntu/
#	scp -i ${pem_file} run_orderA_server.sh ubuntu@${ip}:/home/ubuntu/
#	ssh -i ${pem_file} ubuntu@${ip} chmod +x ${run_server_file} 
#	ssh -i ${pem_file} ubuntu@${ip} . ./${run_server_file}
#fi
