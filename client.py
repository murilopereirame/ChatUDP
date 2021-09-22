import socket
import threading
import random
import json
import sys
from RSA import RSA


class Client:
    SERVER_UDP_IP_ADDRESS = "127.0.0.1"
    SERVER_UDP_PORT_NO = 6789
    user = ""
    room = "geral"
    clientSock = None

    def __init__(self, ip):
        self.SERVER_UDP_IP_ADDRESS = ip
        self.room = 'lobby'

    def autenticate(self):
        usr = input('Insira seu nickname: ')
        if(usr == ''):
            usr = 'Visitante'+str(random.randint(1000, 2000))
        self.user = usr
        print("Autenticado como " + self.user)

    def sendMessage(self, message):
        messagePackage = {'user': self.user, 'room': self.room, 'connecting': False,
                          'message': self.RSA.encryptString(message, self.serverPK)}
        self.clientSock.sendto(json.dumps(messagePackage).encode(
            'utf-8'), (self.SERVER_UDP_IP_ADDRESS, self.SERVER_UDP_PORT_NO))

    def changeRoom(self, room):
        self.room = room

    def connectToServer(self):
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        messagePackage = {'user': self.user, 'room': self.room,
                          'connecting': True, 'message': '', 'key': self.RSA.getPublicKey()}
        self.clientSock.sendto(json.dumps(messagePackage).encode(
            'utf-8'), (self.SERVER_UDP_IP_ADDRESS, self.SERVER_UDP_PORT_NO))

    def listenMessages(self):
        while True:
            data, addr = self.clientSock.recvfrom(1024)
            incoming = json.loads(data.decode('utf-8'))
            
            if('keys' in incoming):
                self.serverPK = incoming['keys']
                continue

            msg = self.RSA.decryptString(
                incoming['message'], self.RSA.getPrivateKey())

            if(incoming['user'] == self.SERVER_UDP_IP_ADDRESS+str(self.SERVER_UDP_PORT_NO)):
                if(msg[0:5].strip() == 'nick'):
                    newUser = msg[5:]
                    self.user = newUser
                    print(
                        '[SERVER] -> Nome de usuario em uso! Seu novo nome e ' + newUser)
                elif(msg[0:5].strip() == 'room'):
                    newRoom = msg[5:]
                    self.room = newRoom
                    print('[SERVER] -> Sala alterada para ' + newRoom)
            else:
                sys.stdout.write('\r'+'['+incoming['user']+'] -> '+msg)                
                sys.stdout.write('\n['+self.user+']: ')

    def chat(self):
        while True:
            data = input("[" + self.user + "]: ")
            if data == 'croom':
                sys.stdout.write("\033[F")
                newRoom = input("Digite a nova sala: ")
                self.room = newRoom
                self.sendMessage('croom ' + newRoom)
                continue
            elif data == '':
                continue
            elif data == 'disconnect':
                self.sendMessage(data)
                print('Desconectado do servidor')
                break
            sys.stdout.write("\033[F")
            print('['+self.user+'] -> ' + data)
            self.sendMessage(data)

    def initClient(self):
        self.RSA = RSA()
        self.autenticate()
        self.connectToServer()
        threading.Thread(target=self.listenMessages).start()
        threading.Thread(target=self.chat).start()


if len(sys.argv) == 1:
    print('Para iniciar -> client.py server-ip')
elif len(sys.argv) == 2:
    client = Client(sys.argv[1])
    client.initClient()
