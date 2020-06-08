import socket
import threading
import json

class Server:
    UDP_IP_ADDRESS = "127.0.0.1"
    UDP_PORT_NO = 6789
    serverSock = None
    clients = []

    def initServer(self):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind((self.UDP_IP_ADDRESS, self.UDP_PORT_NO))
        print("Monitorando o endereço: " + self.UDP_IP_ADDRESS + ":" + str(self.UDP_PORT_NO))
        threading.Thread(target=self.listenMessages).start()

    def listenMessages(self):
        while True:
            data,addr = self.serverSock.recvfrom(1024)
            incoming = json.loads(data.decode('utf-8'))
            if(incoming['message'] == 'connecting' and not self.isConnected(addr)):
                client = Client()
                client.setIpAddr(addr[0])
                client.setPort(addr[1])
                client.setRoom(incoming['room'])
                
                clientNameCount = self.userNameInUse(incoming['user'])
                
                if(clientNameCount > 0):
                    client.setUser(incoming['user'] + "("+str(clientNameCount)+')')
                    clientNameCount = self.userNameInUse(client.getUser())
                    while(clientNameCount > 0):
                        client.setUser(client.getUser() + "("+str(clientNameCount)+')')                        
                        clientNameCount = self.userNameInUse(client.getUser())
                    client.sendMessage(self.serverSock, 'nick ' + client.getUser(), self.UDP_IP_ADDRESS+str(self.UDP_PORT_NO))
                else:
                    client.setUser(incoming['user'])
                self.clients.append(client)
                print(client.getUser() + ' conectado de ' + addr[0] + ":" + str(addr[1]))
            elif(incoming['message'] == 'disconnect' and self.isConnected(addr)):
                self.dropUser(addr)
            elif(incoming['message'][0:5] == 'croom' and self.isConnected(addr)):
                newRoom = incoming['message'].split(" ")[1]
                c = self.changeUserRoom(incoming['user'], newRoom, addr)
                c.sendMessage(self.serverSock, 'room ' + c.getRoom(), self.UDP_IP_ADDRESS+str(self.UDP_PORT_NO))
            else:
                self.sendMessage(incoming['room'], addr, incoming['message'], incoming['user'])

    def changeUserRoom(self, user, room, addr):
        for client in self.clients:
            if(client.getIpAddr() == addr[0] and client.getPort() == addr[1] and client.getUser() == user):
                client.setRoom(room)
                return client

    def userNameInUse(self, user):
        count = 0
        for client in self.clients:
            if(client.getUser() == user):
                count += 1
        return count

    def isConnected(self, addr):
        for client in self.clients:
            if(client.getIpAddr() == addr[0] and client.getPort() == addr[1]):
                return True        
        return False

    def dropUser(self, addr):
         for client in self.clients:
            if(client.getIpAddr() == addr[0] and client.getPort() == addr[1]):
                self.clients.remove(client)
                return

    def sendMessage(self, room, origin, message, user):
        for client in self.clients:
            if((client.getIpAddr() != origin[0] or client.getPort() != origin[1]) and client.getRoom() == room):
                client.sendMessage(self.serverSock, message, user)

class Client:
    user = ''
    room = ''
    ipAddr = ''
    port = 0

    def setUser(self, user):
        self.user = user
    
    def setRoom(self, room):
        self.room = room
    
    def setIpAddr(self, ip):
        self.ipAddr = ip

    def setPort(self, port):
        self.port = port

    def getUser(self):
        return self.user
    
    def getRoom(self):
        return self.room

    def getIpAddr(self):
        return self.ipAddr
    
    def getPort(self):
        return self.port

    def sendMessage(self, socket, message, user):
        x = {"user":user, "message": message}
        socket.sendto(json.dumps(x).encode('utf-8'), (self.ipAddr, self.port))

server = Server()
server.initServer()