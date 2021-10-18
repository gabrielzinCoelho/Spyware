import convertBytes
import struct
import time
import os

class MessageProtocol:

    def __init__(self):
        self.flagMessage = "H15wM3sK"
        self.flagFailedSend = "2Kjgvcb1"
        self.flagSuccessSend = "U2a5Pl23"
        self.flagFillBytes = "Y19ap2lO"
        self.converterBytes = convertBytes.ConvertBytes()
        self.recvBuffer = []

        self.flagSize = 8
        self.fixedHeaderSize = 2
        self.packetSize = 4096

    def createMessage(self, contentBytes, contentEncoding, contentType):
        estimatedFreeBytes = 4000
        indexBytes = 0
        packetsArray = []
        jsonHeader = {
            "messageId": time.time(),
            "contentType": contentType,
            "contentEncoding": contentEncoding,
            "contentLenth": estimatedFreeBytes,
        }

        jsonHeaderBytes = self.converterBytes.encodeJson(jsonHeader, "utf-8")
        overDataSize = len(jsonHeaderBytes) + self.fixedHeaderSize + 2 * self.flagSize
        if overDataSize > self.packetSize - estimatedFreeBytes:
            jsonHeader["contentLenth"] = 4000 - (len(jsonHeaderBytes) + 10 - 96)
            jsonHeader["contentLenth"] = self.packetSize - overDataSize
            jsonHeaderBytes = self.converterBytes.encodeJson(jsonHeader, "utf-8")

        fixedHeaderBytes = struct.pack(">H", len(jsonHeaderBytes))
        indexBytesEnd = 0
        while indexBytesEnd != len(contentBytes):
            indexBytesStart = indexBytes * jsonHeader["contentLenth"]
            indexBytesEnd = min(indexBytesStart + jsonHeader["contentLenth"], len(contentBytes))
            contentPacketBytes = contentBytes[indexBytesStart:indexBytesEnd]
            packetBytes = bytes(self.flagMessage, 'utf-8') + fixedHeaderBytes + jsonHeaderBytes + contentPacketBytes + bytes(self.flagFillBytes, 'utf-8')
            packetsArray.append(packetBytes)
            indexBytes+=1
        return (packetsArray, jsonHeader["messageId"])

    def createAcknowledgment(self, flag, messageId):
        jsonMessage = {
            "messageId": messageId
        }
        messageBytes = self.converterBytes.encodeJson(jsonMessage, 'utf-8')
        packet = self.fillPackets(bytes(flag, 'utf-8') + messageBytes + bytes(self.flagFillBytes, 'utf-8'))
        return packet

    def fillPackets(self, packet):
        sizeFillBytes = self.packetSize - len(packet)
        bytesFill = os.urandom(sizeFillBytes)
        packet+=bytesFill
        return packet

    def removeFillBytes(self, packet):
        #remove FillBytes and flagFillBytes
        packetByteArray = bytearray(packet)
        indexFlag = packet.find(bytes(self.flagFillBytes, 'utf-8'))
        packet = bytes(packetByteArray[:indexFlag])
        return packet

    def sendMessage(self, clientSocket, contentData, contentEncoding, contentType):
        if contentType == "text/json":
            contentBytes = self.converterBytes.encodeJson(contentData, contentEncoding)
        elif contentType == "image":
            contentBytes = self.converterBytes.encodeImage(contentData)
        else:
            contentBytes = contentData

        (packetsArray, messageId) = self.createMessage(contentBytes, contentEncoding, contentType)

        for packet in packetsArray:
            packet = self.fillPackets(packet)
            data = clientSocket.sendall(packet)
            if not data == None:
                messageAcknowledgment = self.createAcknowledgment(self.flagFailedSend, messageId)
                clientSocket.sendall(messageAcknowledgment)
                return False;
        messageAcknowledgment = self.createAcknowledgment(self.flagSuccessSend, messageId)
        data = clientSocket.sendall(messageAcknowledgment)
        print(data)

    def receiveMessage(self, packetBytes):
        packetBytes = self.removeFillBytes(packetBytes)
        flag = packetBytes[:8]
        flag = flag.decode("utf-8")
        if not flag in [self.flagMessage, self.flagSuccessSend, self.flagFailedSend]:
            return False
        packetBytes = packetBytes[8:]
        if flag == self.flagMessage:
            self.processPacket(packetBytes)
            return (True, None)
        elif flag == self.flagSuccessSend:
            acknowledgmentJson = self.converterBytes.decodeJson(packetBytes, 'utf-8')
            messageId = acknowledgmentJson["messageId"]
            for index, message in enumerate(self.recvBuffer):
                if message[0]["messageId"] == messageId:
                    jsonHeader = message[0]
                    messageBytes = bytes(0)
                    for packet in self.recvBuffer[index]:
                        if(type(packet) == bytes):
                            messageBytes+=packet
                    if jsonHeader["contentType"] == "text/json":
                        contentData = self.converterBytes.decodeJson(messageBytes, jsonHeader["contentEncoding"])
                        print("Message Received: \n" + contentData["data"])
                    elif jsonHeader["contentType"] == "image":
                        path = "/home/kali/Downloads/" + str(time.time()) + ".jpeg"
                        contentData = self.converterBytes.saveImage(messageBytes, path)
                    else:
                        contentData = messageBytes
                    return (True, contentData)
        else:
            acknowledgmentJson = self.converterBytes.decodeJson(packetBytes, 'utf-8')
            messageId = acknowledgmentJson["messageId"]
            for index, message in enumerate(self.recvBuffer):
                if message[0]["messageId"] == messageId:
                    self.recvBuffer.pop(index)
                    return (False, None)

    def processPacket(self, packetBytes):
        (jsonHeaderLength, packetBytes) = self.processFixedHeader(packetBytes)
        self.processJsonHeader(packetBytes, jsonHeaderLength)

    def processFixedHeader(self, packetBytes):
        if len(packetBytes) >= 2:
            jsonHeaderLength = struct.unpack(
                ">H", packetBytes[:2]
            )[0]
            packetBytes = packetBytes[2:]
            return (jsonHeaderLength, packetBytes)

    def processJsonHeader(self, packetBytes, jsonHeaderLength):
        if len(packetBytes) >= jsonHeaderLength:
            jsonHeaderBytes = packetBytes[:jsonHeaderLength]
            jsonHeader = self.converterBytes.decodeJson(jsonHeaderBytes, "utf-8")
            packetBytes = packetBytes[jsonHeaderLength:]
            for index, message in enumerate(self.recvBuffer):
                if message[0]["messageId"] == jsonHeader["messageId"]:
                    self.recvBuffer[index].append(packetBytes)
                    return True
            self.recvBuffer.append([jsonHeader, packetBytes])
            return True

