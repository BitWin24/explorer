import json
import subprocess
import os
import time
import pymongo
from pymongo import MongoClient

# 5454 rpcport in explorer settings.json file

# mongo
# set your port
db_user="dbuser"
db_pass="dbpassword"
client = MongoClient('localhost', 27017)
db = client["explorerdb"]
tx_collection = db["txes"]
address_collection = db["addresses"]

# docker ip addresses
# enter in command line: hostname -I (copy first ip and paste here)
ip = "192.168.88.204"

# docker image id (paste id of pulled image)
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
    # Delete old containers
    notify("Delete old containers", 2)
    
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
    # run containers
    notify("Create new containers for nodes", 2)
    
    notify("Create new containers", 2)
    execute_command("sudo docker run -p " + container1_rpc_ports + " -p " + container1_ports + " --name " + container1_name + " -dit " + docker_image, "", "create node1 container", 3)
    execute_command("sudo docker run -p " + container2_rpc_ports + " -p " + container2_ports + " --name " + container2_name + " -dit " + docker_image, "", "create node2 container", 3)
    
    notify("wait 1.5sec", 2)
    time.sleep(1.5)
    
    notify("", 5)
def start_containers():
    # start containers
    notify("Start containers", 2)
    
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
        execute_command("sudo docker exec -dit " + container1_name + " ./bitwin24-node/src/bitwin24d -rescan -txindex=1 -connect=" + ip + container2_ports[:4] + " -daemon=1 -masternode=1 -masternodeprivkey=" + node1_privk + " -listen=1 -rpcallowip=::/0 -server=1 -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container1_rpc_ports[:4] + " -port=" + container1_ports[:4], "", "", 0)
    elif number == 2:
        execute_command("sudo docker exec -dit " + container2_name + " ./bitwin24-node/src/bitwin24d -rescan -txindex=1 -connect=" + ip + container1_ports[:4] + " -daemon=1 -masternode=1 -masternodeprivkey=" + node2_privk + " -listen=1 -rpcallowip=::/0 -server=1 -rpcuser=rpcuser -rpcpassword=rpcpassword -rpcport=" + container2_rpc_ports[:4] + " -port=" + container2_ports[:4], "", "", 0)
    
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
    # drop database
    notify("Drop database", 2)
    execute_command("mongo explorerdb --eval \"db.dropDatabase()\"", "", "Drop database", 0, 1)

def create_mongo():
    # create user and database
    notify("Create user and database", 2)
    execute_command("mongo explorerdb --eval \"db.createUser( { user: \"" + db_user + "\", pwd: \"" + db_pass + "\", roles: [ \"readWrite\" ] } )\"", "", "Load new database", 0, 1)
    execute_command("mongo explorerdb --eval \"use explorerdb\"", "", "", 0, 1)
    notify("wait 1.5sec\n", 2)
    time.sleep(1.5)

def stop_explorer():
    # Kill all explorer proccesses
    notify("Kill all explorer proccesses", 2)
    
    pid = execute_command("ps -ef | grep 'node --stack-size' | awk '{print $2}'", "", "", 0, 0)
    pid_array = pid.split('\n')
    for i in pid_array[:-1]:
        execute_command("sudo kill " + i, "", "Process " + i + " terminating", 3, 0)

def run_explorer():
    # Start explorer
    notify("Start explorer", 2)
    
    execute_command("npm run start", "", "", 0, 1)

def run_sync_script():
    execute_command("rm -rf tmp/index.pid", "", "", 1, 0)
    execute_command("node scripts/sync.js index update", "", "", 1, 0)

def get_explorer_txs():
    txs = tx_collection.find({}).sort("blockindex")
    last_tx = {}
    for tx in txs:
        last_tx = tx
    return last_tx

def cmp_balances():
    # Balances cmp
    notify("Blocks cmp ", 2)
    node_balance = float(json.loads(rpc("gettxoutsetinfo", "", 0, 1, 0))["total_amount"])
    
    addresses = list(address_collection.find({"received": {"$gt": 0}}))
    explorer_balance = 0
    
    for i in addresses:
        explorer_balance += (i["received"] / 100000000) - (i["sent"] / 100000000)
    print("Node balance: ", float(node_balance), "Explorer balance: ", float(explorer_balance))
   
    if float(node_balance) != float(explorer_balance):
        notify("Balances are not equal", 3)
        return 1
    else:
        notify("Balances are equal", 3)
        return 0

def cmp_blocks():
    # Blocks cmp
    notify("Blocks cmp ", 2)
    
    explorer_tx_count = 0
    i = 1
    while True:
        block_hash = rpc("getblockhash " + str(i), "", 0, 1, 0)
        block_str = rpc("getblock " + block_hash, "", 0, 1, 0)
        if "error" in block_str:
            return 0
        else:
            block = json.loads(block_str)
            explorer_txs = list(tx_collection.find({"blockindex": {"$eq": i}}))
            node_txs = block["tx"]
            print("BLOCK ====> ", block["height"], " NODE_TXS ====> ", len(node_txs), " EXP_TXS ====> ", len(explorer_txs))
            print("nodehash==> ", block["hash"])
            print("explhash==> ", explorer_txs[0]["blockhash"])
            print("txs:\n")
            if len(node_txs) != len(explorer_txs):
                print("Bad block (wrong txs number)", block["height"], " NOT SYNCED")
                return 0
            for node_tx in node_txs:
                node_tx = json.loads(rpc("gettransaction " + node_tx, "", 0, 1, 0))
                exist = False
                for explorer_tx in explorer_txs:
                    if explorer_tx["txid"] == node_tx["txid"]:
                        exist = True
                if exist:
                    print("Tx found >>>> ", node_tx["txid"])
                else:
                    notify("Bad block ", block["height"], " Blocks are not synced", 3)
                    return 1
            print(">>>>>>>>>>>>>>> Good block\n\n")
        i += 1
    
    notify("Blocks are synced!", 3)
    return 0

def controll_address_check(balance_to_check):
    # Controll address check
    notify("Controll address check ", 2)
    
    current_state = list(address_collection.find({"a_id": {"$eq": balance_to_check["address"]}}))
    if current_state[0]["balance"] != balance_to_check["amount"]:
        notify("Correct address balance", 3)
        return 0
    else:
        notify("Bad address balance", 3)
        return 1

# def fork_type1():
    # notify("Fork type 1", 1)
    # last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)
    # last_explorer_tx = get_explorer_txs()
    # print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[:-2])
    # if last_explorer_tx["blockhash"] != last_node_block[:-2]:
    #     notify("Not synced", 2)
    # else:
    #     notify("Synced", 2)
    # # delete block
    # rpc("invalidateblock " + last_node_block, "Delete block", 2, 1)
    # notify("wait 1.5sec\n", 2)
    # time.sleep(1.5)
    # last_explorer_tx = get_explorer_txs()
    # last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)
    # print("Hash1: ", last_explorer_tx["blockhash"], "Hash2: ", last_node_block[-2])
    # if last_explorer_tx["blockhash"] != last_node_block[:-2]:
    #     notify("Not synced", 2)
    # else:
    #     notify("Synced", 2)

def fork_type2():
    # Fork type 2
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
    
    notify("wait 0.5sec\n", 2)
    time.sleep(0.5)
    
    # get current block on node
    fresh_block = rpc("getbestblockhash", "Fork block hash node1", 2, 1)
    
    # get fresh block
    fork_block = json.loads(rpc("getblock " + fresh_block, "Fork block node1", 2, 1))
    txs = list(tx_collection.find({"blockindex": {"$eq": fork_block["height"]}}).sort("blockindex"))
    balance_to_check = {"address": txs[0]["vout"][0]["addresses"], "amount": txs[0]["vin"][0]["amount"], "block": txs[0]["blockindex"]}
    
    return balance_to_check

def explorer_setup():
    # Setup explorer and database
    notify("Setup explorer and database", 1)
    
    drop_mongo()
    create_mongo()
    stop_explorer()
    run_explorer()
    
    notify("", 5)

def nodes_setup():
    # Setup nodes
    notify("Nodes setup", 1)
    
    delete_old_containers()
    create_new_containers()
    start_containers()
    
    run_node(1)
    rpc("getinfo", "Getinfo node 1", 2, 1)
    
    notify("", 5)

explorer_setup()
nodes_setup()
rpc("setgenerate true 100", "Start mining node1", 2, 1)
    
notify("wait 3sec\n", 2)
time.sleep(3)

rpc("setgenerate false", "Stop mining node1", 2, 1)

notify("wait 0.5sec\n", 2)
time.sleep(0.5)

rpc("getinfo", "Getinfo node 1", 2, 1)

rpc("getbalance", "Node 1 balance", 2, 1)

# Run sync script
run_sync_script()

notify("wait 3sec\n", 2)
time.sleep(3)

if cmp_balances():
    print("Test failed!")
else:
    print("Test passed!")

notify("wait 1sec\n", 2)
time.sleep(1)

# create fork in chain
balance_to_check = fork_type2()
last_explorer_tx = get_explorer_txs()
last_node_block = rpc("getbestblockhash", "Get best block hash", 2, 1)

if last_explorer_tx["blockhash"] != last_node_block[:-2]:
    notify("Not synced", 2)
else:
    notify("Synced", 2)

rpc("getinfo", "Getinfo node 1", 2, 1)
rpc("setgenerate true 100", "Start mining node1", 2, 1)
        
notify("wait 3sec\n", 2)
time.sleep(3)

rpc("setgenerate false", "Stop mining node1", 2, 1)

notify("wait 1sec\n", 2)
time.sleep(1)

rpc("getinfo", "Getinfo node 1", 2, 1)
rpc("getbalance", "Node 1 balance", 2, 1)

notify("wait 1sec\n", 2)
time.sleep(1)

# Run sync script
run_sync_script()

if cmp_balances() or cmp_blocks() or controll_address_check(balance_to_check):
    notify("", 5)
    notify("Test failed!", 1)
else:
    notify("", 5)
    notify("Test passed!", 1)