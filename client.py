import socket
import messageProtocol

class Client:

    def __init__(self, serverIp, serverPort):
        try:
            self.clientSocket = self.clientConnecting(serverIp, serverPort)
            self.messageInstance = messageProtocol.MessageProtocol()
        except Exception as error:
            self.clientSocket = None
            self.messageInstance = None
            print("The socket could not be created\n" + str(error))

    def clientConnecting(self, serverIp, serverPort):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((serverIp, serverPort))
            print("Connection established with " + serverIp + ":" + str(serverPort))
            return client
        except Exception as error:
            return  error

    def sendMessage(self, contentData, contentEncoding, contentType):
        data = self.messageInstance.sendMessage(self.clientSocket, contentData, contentEncoding, contentType)
        return data