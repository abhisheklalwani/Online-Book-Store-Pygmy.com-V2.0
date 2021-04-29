myip="$(dig +short myip.opendns.com @resolver1.opendns.com)"
source env.cfg

echo "###### Testing fault tolerance of the system ######"
echo "Calling the shutdown API to stop the catalogA server"
curl http://${catalogA_ip}:${catalogA_port}/shutdown
echo "Successfully crashed the catalogA server"
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
start_server()
{
	if [[ $2 == $myip ]]; then
		sudo docker start $1
	else
		ip=$2
		echo "Starting the $1 server"
		ssh -i ${pem_file} ubuntu@${ip} sudo docker start $1

	fi
}
echo "Invoking client.py to start the traffic and test the system."
echo "Check the client.log to check fault tolerance of the system"
sleep 2
python client.py "http://${frontend_ip}" ${frontend_port} 2

sleep 2
echo "Now starting the catalogA server and see if it is able to recover properly after the crash."
start_server catalogA ${catalogA_ip}
echo "Successfully started the catalogA server"

echo "Invoking test_server_recovery.py to check the recovery of the system."
echo "Check the test_server_recovery.log for the result"
sleep 2
python test_server_recovery.py "http://${catalogA_ip}" ${catalogA_port} "http://${catalogB_ip}" ${catalogB_port}

echo "Copying Log Files"
get_log_files orderA ${orderA_ip}
get_log_files orderB ${orderB_ip}
get_log_files catalogA ${catalogA_ip}
get_log_files catalogB ${catalogB_ip}
get_log_files frontend ${frontend_ip}
