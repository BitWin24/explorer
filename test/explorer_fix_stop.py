# you need to set 5454 (5555) rpcport in explorer settings.json file
import json
import subprocess
import os
import time

# explorer ip
ip = "127.0.0.1:4444"

# hostname -I (first ip)
ip = "192.168.88.204"

# docker image id
docker_image = "54c602564d7f"

# node 1
container1_name = "bitwin-node1"
container1_rpc_ports = "5454:5454"
container1_ports = "5455:5455"
node1_privk = "5mTsKPvyeZvMmXHqsB679GnM6Nv2uTKqfG4uACqTrqnQVD99iBp"

# node 2
container2_name = "bitwin-node2"
container2_rpc_ports = "5555:5555"
container2_ports = "5556:5556"
node2_privk = "5m4rZzkr3TNd5urxKa9ZziSnjC8kzrtHQFRdrAmoLZNDm4uH4Px"

def notify(msg, size):
    if size == 1:
        print("=============================================> " + msg + "")
    elif size == 2:
        print("===========> " + msg)
    elif size == 3:
        print("===> " + msg)
    elif size == 5:
        print("============================================= END\n\n")

def execute_command(command, params, desc, print_it=0, background=0):
    if desc:
        notify(desc, print_it)
    proc = subprocess.Popen([command, params], stdout=subprocess.PIPE, shell=True)
    if not background:
        (out, err) = proc.communicate()
        if print_it:
            print ("out:\n" +  out.decode("utf-8"), end="")
        return out.decode("utf-8") 

def delete_old_containers():
    notify("Delete old containers", 1)

    # stop containers
    notify("Stop containers", 2)
    execute_command("sudo docker stop " + container1_name, "", "stop node1 container", 3)
    execute_command("sudo docker stop " + container2_name, "", "stop node2 container", 3)

    # remove containers
    notify("Remove containers", 2)
    execute_command("sudo docker rm " + container1_name, "", "remove node1 container", 3)
    execute_command("sudo docker rm " + container2_name, "", "remove node2 container", 3)

    notify("", 5)
    
def rpc(command, msg, size, number):

    # rpc command
    notify(msg, size)
    if number == 1:
        return execute_command("sudo docker exec -it " + container1_name + " ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container1_rpc_ports[:4] + " " + command, "", "", 3)
    elif number == 2:
        return execute_command("sudo docker exec -it " + container2_name + " ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container2_rpc_ports[:4] + " " + command, "", "", 3)

def drop_mongo():
    execute_command("mongo explorerdb --eval \"db.dropDatabase()\"", "", "Drop database", 0, 1)
    execute_command("mongo explorerdb --eval \"db.createUser( { user: \"iquidus\", pwd: \"3xp!0reR\", roles: [ \"readWrite\" ] } )\"", "", "Load new database", 0, 1)
    execute_command("mongo explorerdb --eval \"use explorerdb\"", "", "", 0, 1)

def stop_explorer():
    pid = execute_command("ps -ef | grep 'node --stack-size' | awk '{print $2}'", "", "", 0, 0)
    pid_array = pid.split('\n')
    for i in pid_array[:-1]:
        execute_command("sudo kill " + i, "", "Process " + i + " terminating", 3, 0)

def run_sync_script():
    execute_command("rm -rf tmp/index.pid", "", "", 0, 1)
    execute_command("node scripts/sync.js index update", "", "", 0, 1)


notify("Clear everysing", 1)
delete_old_containers()
stop_explorer()
