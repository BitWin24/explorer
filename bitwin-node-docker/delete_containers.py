import os

# stop node1 container
os.system("sudo docker stop bitwin-node1")
os.system("sudo docker stop bitwin-node2")

# remove node1 container
os.system("sudo docker rm bitwin-node1")
os.system("sudo docker rm bitwin-node2")

# ps
os.system("sudo docker ps -a")

print("===== Continers deleted =====")
