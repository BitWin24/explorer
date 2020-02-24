# you need to set 5454 (5555) rpcport in explorer settings.json file
import json
import subprocess
import os
import time
import pprint
import pymongo
from pymongo import MongoClient

# mongo
client = MongoClient('localhost', 27017)
db = client["explorerdb"]
collection = db["txes"]

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
    
def create_new_containers():
    notify("Create new containers for nodes", 1)
    
    # run containers
    notify("Create new containers", 2)
    execute_command("sudo docker run -p " + container1_rpc_ports + " -p " + container1_ports + " --name " + container1_name + " -dit " + docker_image, "", "create node1 container", 3)
    execute_command("sudo docker run -p " + container2_rpc_ports + " -p " + container2_ports + " --name " + container2_name + " -dit " + docker_image, "", "create node2 container", 3)

    notify("wait 1.5sec", 2)
    time.sleep(1.5)
    
    notify("", 5)

def start_containers():
    notify("Start containers", 1)
    
    # start containers
    notify("Start containers", 2)
    execute_command("sudo docker start " + container1_name, "", "start node 1 container", 3)
    execute_command("sudo docker start " + container2_name, "", "start node 2 container", 3)

    notify("wait 1.5sec", 2)
    time.sleep(1.5)
    
    notify("", 5)







def run_node(number):

    # run node
    notify("Run node " + str(number), 2)
    if number == 1:
        execute_command("sudo docker exec -dit " + container1_name + " ./bitwin24-node/src/bitwin24d -txindex=1 -connect=" + ip + container2_ports[:4] + " -daemon=1 -masternode=1 -masternodeprivkey=" + node1_privk + " -listen=1 -rpcallowip=::/0 -server=1 -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container1_rpc_ports[:4] + " -port=" + container1_ports[:4], "", "", 0)
    elif number == 2:
        execute_command("sudo docker exec -dit " + container2_name + " ./bitwin24-node/src/bitwin24d -txindex=1 -connect=" + ip + container1_ports[:4] + " -daemon=1 -masternode=1 -masternodeprivkey=" + node2_privk + " -listen=1 -rpcallowip=::/0 -server=1 -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container2_rpc_ports[:4] + " -port=" + container2_ports[:4], "", "", 0)

    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

def rpc(command, msg, size, number, print_command=2):

    # rpc command
    notify(msg, size)
    if number == 1:
        return execute_command("sudo docker exec -it " + container1_name + " ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container1_rpc_ports[:4] + " " + command, "", "", print_command)
    elif number == 2:
        return execute_command("sudo docker exec -it " + container2_name + " ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container2_rpc_ports[:4] + " " + command, "", "", print_command)

def drop_mongo():
    execute_command("mongo explorerdb --eval \"db.dropDatabase()\"", "", "Drop database", 0, 1)

def create_mongo():
    execute_command("mongo explorerdb --eval \"db.createUser( { user: \"iquidus\", pwd: \"3xp!0reR\", roles: [ \"readWrite\" ] } )\"", "", "Load new database", 0, 1)
    execute_command("mongo explorerdb --eval \"use explorerdb\"", "", "", 0, 1)

def stop_explorer():
    pid = execute_command("ps -ef | grep 'node --stack-size' | awk '{print $2}'", "", "", 0, 0)
    pid_array = pid.split('\n')
    for i in pid_array[:-1]:
        execute_command("sudo kill " + i, "", "Process " + i + " terminating", 3, 0)

def run_explorer():
    execute_command("npm run start", "", "", 0, 1)


def run_sync_script():
    execute_command("rm -rf tmp/index.pid", "", "", 1, 0)
    execute_command("node scripts/sync.js index update", "", "", 1, 0)

def get_explorer_txs():
    txs = collection.find({}).sort("blockindex")
    last_tx = {}
    for tx in txs:
        # pprint.pprint(tx)
        last_tx = tx
    return last_tx

notify("Explorer setup", 1)
drop_mongo()
create_mongo()
stop_explorer()
run_explorer()

delete_old_containers()
create_new_containers()
start_containers()

run_node(1)

rpc("getinfo", "Getinfo node 1", 2, 1)

rpc("setgenerate true 100", "Start mining node1", 2, 1)
    
notify("wait 10sec\n", 2)
time.sleep(10)

rpc("setgenerate false", "Stop mining node1", 2, 1)

notify("wait 1.5sec\n", 2)
time.sleep(1.5)

rpc("getinfo", "Getinfo node 1", 2, 1)

rpc("getbalance", "Node 1 balance", 2, 1)

run_sync_script()

notify("wait 5sec\n", 2)
time.sleep(5)

def print_explorer_blocks(last_block):
    txs = collection.find({}).sort("blockindex")
    last_tx = {}
    for tx in txs:
        print("\n\n INDEX: " + str(tx["blockindex"]))
        print("=======> Node blockhash: " + rpc("getblockhash " + str(tx["blockindex"]), "", 0, 1, 0))
        print("=======> Expl blockhash: " + tx["blockhash"])

def fork_type1():
    notify("Fork type 1", 1)
    last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)
    last_explorer_tx = get_explorer_txs()

    print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[:-2])
    if last_explorer_tx["blockhash"] != last_node_block[:-2]:
        notify("Not synced", 2)
    else:
        notify("Synced", 2)

    # delete block
    rpc("invalidateblock " + last_node_block, "Delete block", 2, 1)

    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

    last_explorer_tx = get_explorer_txs()
    last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)

    print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[-2])
    if last_explorer_tx["blockhash"] != last_node_block[:-2]:
        notify("Not synced", 2)
    else:
        notify("Synced", 2)


def fork_type2():
    notify("Fork type 2", 1)
    last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)
    last_explorer_tx = get_explorer_txs()
    fork_block_index = last_explorer_tx["blockindex"] // 2
    fork_block_hash = rpc("getblockhash " + str(fork_block_index), "", 0, 1)

    print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[:-2])
    if last_explorer_tx["blockhash"] != last_node_block[:-2]:
        notify("Not synced", 2)
    else:
        notify("Synced", 2)
    
    notify("Create fork on block " + str(fork_block_index) + " : " + fork_block_hash, 1)

    # delete block
    rpc("invalidateblock " + fork_block_hash, "Delete block", 2, 1)

    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

    # get current block on node
    fresh_block = rpc("getbestblockhash", "Fork block hash node1", 2, 1)
    
    # get fresh block
    fork_block = json.loads(rpc("getblock " + fresh_block, "Fork block node1", 2, 1))
    print(fork_block, type(fork_block))

    last_explorer_tx = get_explorer_txs()
    last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)

    print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[-2])
    if last_explorer_tx["blockhash"] != last_node_block[:-2]:
        notify("Not synced", 2)
    else:
        notify("Synced", 2)

    rpc("getinfo", "Getinfo node 1", 2, 1)

    rpc("setgenerate true 100", "Start mining node1", 2, 1)
        
    notify("wait 10sec\n", 2)
    time.sleep(10)

    rpc("setgenerate false", "Stop mining node1", 2, 1)

    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

    rpc("getinfo", "Getinfo node 1", 2, 1)

    rpc("getbalance", "Node 1 balance", 2, 1)

    run_sync_script()

    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

    # get fork block hash
    best_hash = rpc("getbestblockhash", "Fork block hash node1", 2, 1)

    # get fork block
    best_block = json.loads(rpc("getblock " + best_hash, "Fork block node1", 2, 1))

    print_explorer_blocks(best_block["height"])

    run_sync_script()



# fork_type1()
fork_type2()

# # get fork block hash
# fork_block_hash = rpc("getbestblockhash", "Fork block hash node1", 2, 1)

# # get fork block
# fork_block = json.loads(rpc("getblock " + fork_block_hash, "Fork block node1", 2, 1))
# print(fork_block, type(fork_block))

# # get tx from block
# tx = json.loads(rpc("gettransaction " + fork_block["tx"][0], "Get tx info", 2, 1))["details"][0]

# # get transfer info
# receiver = tx["address"]
# notify(json.dumps(receiver), 3)

# # check account balance
# rpc("getbalance " + receiver, "Balance before block delete", 2, 1)

# notify("wait 1.5sec\n", 2)
# time.sleep(1.5)

# # delete block
# rpc("invalidateblock " + fork_block_hash, "Delete block", 2, 1)

# # check account balance
# rpc("getbalance " + receiver, "Balance after block delete", 2, 1)


# rpc("getbalance", "Node 1 balance", 2, 1)


# # get fork block hash
# fork_block_hash = rpc("getbestblockhash", "Fork block hash node1", 2, 1)

# # get fork block
# fork_block = json.loads(rpc("getblock " + fork_block_hash, "Fork block node1", 2, 1))

# notify("Please turn off the SCRIPT.sh. You have 20sec\n", 2)
# time.sleep(20)

# # get fork block hash
# fork_block_hash = rpc("getbestblockhash", "Fork block hash node1", 2, 1)

# # get fork block
# fork_block = json.loads(rpc("getblock " + fork_block_hash, "Fork block node1", 2, 1))

# rpc("setgenerate true 1", "Start mining node1", 2, 1)
# rpc("setgenerate false", "Stop mining node1", 2, 1)




"""

#invalidateblock
print("=============================> get top block hash node1")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getblock $(sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash)")

print("=============================> invalidateblock")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 invalidateblock $(sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash)")

print("=============================> get top block hash node1")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getblock $(sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash)")


os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getblock $(sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbestblockhash) | grep -oP '(?<=height:)[\d.]+'")
"""

"""
print("=============================> start mining node1")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 setgenerate true 1")
print("=============================> start mining node2")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 setgenerate true 1")

print("=============================> wait 5sec...")
time.sleep(5)

print("=============================> stop mining node1")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 setgenerate false")
print("=============================> stop mining node2")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 setgenerate false")

print("=============================> run get node1 info before start")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getinfo")
print("=============================> run get node2 info before start")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getinfo")

print("=============================> node1 getbalance")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbalance")
print("=============================> node2 getbalance")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getbalance")





print("get top block hash node2")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getbalance")


print("=============================> node1 stop")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 stop")
print("=============================> start mining node2")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 setgenerate true 1")

print("=============================> wait 5sec...")
time.sleep(5)

print("=============================> stop mining node2")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 setgenerate false")

print("=============================> run get node2 info before start")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getinfo")

print("=============================> run node1 in container")
os.system("sudo docker exec -dit bitwin-node1 ./bitwin24-node/src/bitwin24d -keypool=1 -connect=192.168.88.204:5556 -daemon=1 -masternode=1 -masternodeprivkey=5mTsKPvyeZvMmXHqsB679GnM6Nv2uTKqfG4uACqTrqnQVD99iBp -listen=1 -rpcallowip=::/0 -server=1 -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 -port=5455")

print("=============================> run get node1 info before start")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getinfo")
print("=============================> run get node2 info before start")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getinfo")

print("=============================> wait 5sec...")
time.sleep(5)

print("=============================> run get node1 info before start")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getinfo")
print("=============================> run get node2 info before start")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getinfo")

print("=============================> node1 getbalance")
os.system("sudo docker exec -it bitwin-node1 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5454 getbalance")
print("=============================> node2 getbalance")
os.system("sudo docker exec -it bitwin-node2 ./bitwin24-node/src/bitwin24-cli -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=5555 getbalance")

print("================================= END ====================================")

"""
