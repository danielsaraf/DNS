import socket
import sys

# extract parent ip and port
serverIp = sys.argv[1]
try:
    serverPort = int(sys.argv[2])
except:
    print("non integer port, please enter valid port")
    exit(1)

while True:
    # get address from user and send to server to get the ip
    sAddress = input("")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.sendto(str.encode(sAddress), (serverIp, serverPort))
    data, addr = clientSocket.recvfrom(1024)
    print(data.decode("utf-8").split(",")[1])
    clientSocket.close()
