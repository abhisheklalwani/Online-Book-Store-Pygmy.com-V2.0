# Book-Store

This repository contains implementation of the Lab 2 Project of COMPSCI 677 course at UMass Amherst. <br>
Contributors - <br>
Abhishek Lalwani (alalwani@umass.edu) <br>
Himanshu Gupta (hgupta@umass.edu) <br>
Kunal Chakrabarty (kchakrabarty@umass.edu) <br>

# System requirement

Local machine (Windows),  
Ec2 servers (Linux)  
Python module dependencies that we used: Details in `requirements.txt`

# Source File Descriptions
1. `catalog/catalog.py` implements the catalog server with the relevant GET and PUT methods.
2. `frontend/frontend.py` implements the front end server with the buy, search and lookup methods.
3. `order/order.py` implements the order server with the buy method. 
4. `Docs` contains the design documentation and the test case documentation.
5. `requirements.txt` contains the python libraries required.
6. `runme.py` is a single script to automatically deploy servers and run frontend APIs.
7. `const.py` contains information about the type, IP and Port for all the servers. Change the IP and port of the servers as per requirement.


Please find the instructions below for testing the implementation.

# Instructions 

### To run the server locally

1. Define the ip and ports of order, catalog and front end server by editing the `const.py` file. For running locally make the IPs for the server as `http://12.0.0.1`.
2. Run `python runme.py -n <number of iterations>`. For example, if you want the service to run for 20 iterations (where each iteration contains one frontend API of each search,lookup and buy) you use `python client.py -n 20`. Default value is 5 iterations. Please note that the servers keep running after the completion of all iterations and have to be stopped manually by the user.
3. You can observe the results of this run in the log files. `client.log` will contain the logs of `runme.py` script. For server specific logs, you can refer to the logs inside the specific server folders named order, catalog and frontend.

### To run servers remotely 

1. Use the custom public AMI: `ami-07f5352ed5fd844e3` to deploy instances. The image contains all the library and source code for the respective flask servers to run. If you want to use another image, you have to follow the commands written in the `remote setup` section.
2. Create EC2 instances with key pair value, and get the private .pem file.
3. Edit the security group to ensure that the ports required by the peers to communicate are open.
3. Set up password-less ssh from the local machine to the ec2 servers by running the following command from the local terminal:
    `ssh -i <pem_file_path> ec2-user@<ec2_public_ip>` with the private pem file and the public IP address of the EC2 instance that has been set up. (This will add the ec2 server to the known_host file so that you can ssh from the script without the need of a password).
4. Copy the public IP of the instances and add them to the `const.py` file. Change the port IDs of the servers as pleased.
5. Now, on your local machine, run the `runme.py` file which will ssh on the remote machine and start the flask servers. It will then trigger frontend APIs to test the functionalities. USAGE: `python runme.py -pem <pem file used to ssh to all the machines> -n <number of iterations>`. The argument -pem is compulsory in the case the servers are running in remote environment/machines.
6. You can observe the results of this run in different log files. `client.log` will contain the logs of `runme.py` script. For server specific logs, you can refer to the logs inside the specific server folders in remote machines. The location for the same will be: `/home/ec2-user/src/<servername>/<servername>.log`

# Remote setup

sudo yum install python3  
curl -O https://bootstrap.pypa.io/get-pip.py  
python3 get-pip.py --user  
pip install flask  
pip install gunicorn  
gunicorn -b 0.0.0.0:8010 frontend:app  
pip install requests  
