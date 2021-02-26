import socket
import sys
import time


# ask the data mapping from parent server
def askFromFatherServer(data):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        clientSocket.sendto(str.encode(data), (fatherServerIp, fatherServerPort))
    except:
        print("fail to connect with father server on ip: " + str(fatherServerIp) + " port: " + str(fatherServerPort))
        exit(1)
    data, addr = clientSocket.recvfrom(1024)
    clientSocket.close()
    return data


# when parent server return a new mapping, write it to file and save it in ipsList
def saveNewEntry(param):
    nowTime = time.time()
    ipsFile = open(ipsFileName, "a")
    ipsFile.write("\n" + param.decode("utf-8") + "," + str(nowTime))
    ipsFile.close()
    lineArr = param.decode("utf-8").split(",")
    ip = [lineArr[0], lineArr[1], lineArr[2], nowTime]
    # print("saving " + str(ip))
    ipsList.append(ip)


# when the file contains a entry that are no longer update (ttl time pass), rewrite all the file with the updated entry
def refreshIpsFile():
    ipsFile = open(ipsFileName, "w")
    for ip in ipsList:
        ipsFile.write("\n" + str(ip[0]) + "," + str(ip[1]) + "," + str(ip[2]) + "," + str(ip[3]))
    ipsFile.close()


# extract ports,parent ip, and ip file from argument
try:
    myPort = int(sys.argv[1])
    fatherServerPort = int(sys.argv[3])
except:
    print("non integer port, please enter valid port")
    exit(1)
fatherServerIp = sys.argv[2]
ipsFileName = sys.argv[4]

try:
    ipsFile = open(ipsFileName, "r+")  # open file
except:
    print("ips file does not exists. creating a new file and start with empty list..")
    ipsFile = open(ipsFileName, "w+")
Lines = ipsFile.readlines()  # read lines
ipsList = []
# print("reading file...")
# for each line, initialize ip array with address ip and ttl and insert to the ipsList
for idx, line in enumerate(Lines):
    line = line.replace("\n", "")
    if line == "":
        continue
    lineArr = line.split(",")
    try:
        if len(lineArr) == 3:
            lineArr.append("-1")
        ip = [lineArr[0], lineArr[1], lineArr[2], lineArr[3]]
        # print("load " + str(ip))
        ipsList.append(ip)
    except:
        print("ips file - row number: " + str(idx + 1) + " invalid row format")
        continue
ipsFile.close()
# open socket and bind ip
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', myPort))

# wait for client requests
while True:
    # print("wait for client requests")
    found = False
    refreshFile = False
    data, addr = serverSocket.recvfrom(1024)
    data = data.decode("utf-8")
    # print("received " + str(data) + " message from " + str(addr))
    # iterate over ipsLists and look for the client requested address
    # in case of finding it - return the ip line, otherwise request it from parent server
    for ip in ipsList:
        if ip[0] == data:
            if (ip[3] == "-1") or (float(ip[3]) + float(ip[2]) >= time.time()):
                serverSocket.sendto(str.encode(str(ip[0]) + "," + str(ip[1]) + "," + str(ip[2])), addr)
                # print("found")
                found = True
                break
            else:
                refreshFile = True
                ipsList.remove(ip)
    if found is True:
        continue
    # if the code reaches here, the address was not found in the ipsList, request it from parent server
    # print("fail to find address, ask from father server...")
    fatherResponse = askFromFatherServer(data)
    # print("father says: " + str(fatherResponse))
    saveNewEntry(fatherResponse)
    serverSocket.sendto(fatherResponse, addr)
    if refreshFile is True:
        refreshIpsFile()
