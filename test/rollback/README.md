Rollback test
================

Checking resynchronization of the explorer database in the event of a longer chain in the network that differs from the explorer chain.
This test launches bitwin node in the docker container, generates a chain of blocks and synchronizes the explorer database with the network. Then a fork is generated in the middle of the chain, the test generates an alternative chain, starts the synchronization of the explorer and checks its correctness
### Requires


* All requirements from explorer README
* Builded explorer
* Docker
* Python3
* Pymongo module for python

### Set parameters

In order for everything to work correctly, you need to configure the test. Open `explorer_test_run.py` and set parameters:


    # please, set 5454 rpcport in explorer settings.json file

    # mongo
    # set your port
    client = MongoClient('localhost', 27017)
    db = client["explorerdb"]
    tx_collection = db["txes"]
    address_collection = db["addresses"]

    # docker ip addresses
    # enter in command line: hostname -I (copy first ip and paste here)
    ip = "192.168.88.204"

    # docker image id (paste id of pulled image)
    docker_image = "54c602564d7f"


### Get docker image with node

Enter in command line:

    $ docker pull opanini/bitwin-node


### Run test

Go to the root folder of the project and enter:

    python3 test/rollback/explorer_fix_run.py

If the test passes successfully, you will see such an inscription:

    ======================> Test passed!

### Stop explorer and containers 

After the test is over, you have the opportunity to use the explorer and the network node, if you no longer need this, enter:

    python3 test/rollback/explorer_fix_stop.py

Then you can delte docker image by entering:

    docker image rm IMAGE_ID