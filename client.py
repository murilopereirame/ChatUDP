import socket
import threading
import random
import json
import sys

class Client:
    SERVER_UDP_IP_ADDRESS = "127.0.0.1"
    SERVER_UDP_PORT_NO = 6789
    user = ""
    room = "geral"
    clientSock = None
    
    def __init__(self, ip):
        self.SERVER_UDP_IP_ADDRESS = ip

    def autenticate(self):
        usr = input('Insira seu nickname: ')
        if(usr == ''):
            usr = 'Visitante'+str(random.randint(1000,2000))
        self.user = usr
        print("Autenticado como " + self.user) 
    
    def sendMessage(self, message):
        messagePackage = {'user':self.user, 'room':self.room, 'message':message}
        self.clientSock.sendto(json.dumps(messagePackage).encode('utf-8'), (self.SERVER_UDP_IP_ADDRESS, self.SERVER_UDP_PORT_NO))
    
    def changeRoom(self, room):
        self.room = room

    def connectToServer(self):
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        messagePackage = {'user':self.user, 'room':self.room, 'message':'connecting'}
        self.clientSock.sendto(json.dumps(messagePackage).encode('utf-8'), (self.SERVER_UDP_IP_ADDRESS, self.SERVER_UDP_PORT_NO))

    def listenMessages(self):
        while True:
            data, addr = self.clientSock.recvfrom(1024)
            incoming = json.loads(data.decode('utf-8'))
            if(incoming['user'] == self.SERVER_UDP_IP_ADDRESS+str(self.SERVER_UDP_PORT_NO)):
                if(incoming['message'][0:5].strip() == 'nick'):
                    newUser = incoming['message'][5:]
                    self.user = newUser
                    print('[SERVER] -> Nome de usuario em uso! Seu novo nome e ' + newUser)
                elif(incoming['message'][0:5].strip() == 'room'):
                    newRoom = incoming['message'][5:]
                    self.room = newRoom
                    print('[SERVER] -> Sala alterada para ' + newRoom)
            else:
                print ('['+incoming['user']+'] -> ' + incoming['message'])

    def chat(self):
        while True:
            data = input("[" + self.user + "]: ")
            if data == 'croom':
                sys.stdout.write("\033[F")
                newRoom = input("Digite a nova sala: ")
                self.room = newRoom
                self.sendMessage('croom ' + newRoom)
                continue
            elif data=='':
                continue
            elif data=='disconnect':
                self.sendMessage(data)
                print('Desconectado do servidor')
                break
            sys.stdout.write("\033[F")
            print('['+self.user+'] -> ' + data)
            self.sendMessage(data)                    
        self.clientSock.close()
    
    def initClient(self):
        self.autenticate()
        self.connectToServer()
        threading.Thread(target=self.listenMessages).start()
        threading.Thread(target=self.chat).start()

if len(sys.argv)==1:
    print('Para iniciar -> client.py server-ip')
elif len(sys.argv)==2:
    client = Client(sys.argv[1])
    client.initClient()

