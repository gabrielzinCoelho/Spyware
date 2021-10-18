import socket
import messageProtocol


class Server:

    def __init__(self, serverIp, serverPort):
        try:
            self.serverSocket = self.serverListening(serverIp, serverPort)
            self.clientSocket = self.clientConnecting()
        except Exception as error:
            self.serverSocket = None
            self.clientSocket = None
            print("The socket could not be created\n" + str(error))

    def serverListening(self, serverIp, serverPort):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((serverIp, serverPort))
            server.listen(1)
            print("Server listening in " + serverIp + ":" + str(serverPort))
            return server
        except Exception as error:
            return error

    def clientConnecting(self):
        try:
            (client, clientAddress) = self.serverSocket.accept()
            print("Connection received from " + clientAddress[0] + ":" + str(clientAddress[1]))
            return client
        except Exception as error:
            return error

    def startServer(self):
        messageInstance = messageProtocol.MessageProtocol()
        while True:
            try:
                if not self.clientSocket:
                    break
                data = self.clientSocket.recv(4096)
                if not data:
                    continue
                (success, messageData) = messageInstance.receiveMessage(data)
                #if success:
                    #print(messageData)
            except Exception as error:
                print("Server Error\n%s"%str(error))

        self.serverSocket.close()