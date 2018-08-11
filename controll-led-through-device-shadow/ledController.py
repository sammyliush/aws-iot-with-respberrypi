
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import threading

# Led shadow JSON Schema
#
# 
# Name: Led
# {
#     "state: {
#               "desired": {
#                          "light": <on|off>
#                }
#      }
#}

deviceShadowHandler = None

def getDeviceStatus():
    while True:
        print("Getting device status...\n")
        deviceShadowHandler.shadowGet(customShadowCallback_get, 50)
        time.sleep(60)    

def customShadowCallback_get(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Get request with token " + token + " time out!")
    if responseStatus == "accepted":
        print("========== Printing Device Current Status =========")
        print(payload)
        payloadDict = json.loads(payload)
        #{"state":{"desired":{"light":0},"reported":{"light":100}
        try:
            desired = payloadDict["state"]["desired"]["light"]
            desiredTime = payloadDict["metadata"]["desired"]["light"]["timestamp"]
        except Exception:
            print("Failed to get desired state and timestamp.")
        else:
            print("Desired status: " + str(desired) + " @ " + time.ctime(int(desiredTime)))

        try:
            reported = payloadDict["state"]["reported"]["light"]
            #"metadata":{"desired":{"light":{"timestamp":1533893848}},"reported":{"light":{"timestamp":1533893853}}}
            reportedTime = payloadDict["metadata"]["reported"]["light"]["timestamp"]
        except Exception:
            print("Failed to get reported time or timestamp")
        else:
            print("Reported status: " + str(reported) + " @ " + time.ctime(int(reportedTime)))
        
        print("=======================================\n\n")
    if responseStatus == "rejected":
        print("Get request with token " + token + " rejected!")

def customShadowCallback_upate(payload, responseStatus, token):
    # payload is a JSON string which will be parsed by jason lib
    if responseStatus == "timeout":
        print("Update request with " + token + " time out!")
    if responseStatus == "accepted":
        playloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("light: " + str(playloadDict["state"]["desired"]["light"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


def customShadowCallback_delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")
    if responseStatus == "accepted":
        print("Delete request with token " + token + " accepted!")
    if responseStatus == "rejected":
        print("Delete request with token " + token + " rejected!")

# Cofigure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# AWS IoT Core endpoint and port. Need change to yours.
awsiotHost = "*********.iot.ap-southeast-1.amazonaws.com"
awsiotPort = 8883;
# AWS IoT Root Certificate. Needn't change.
rootCAPath = "/home/pi/awsiot/VeriSign-Class3-Public-Primary-Certification-Authority-G5.pem"
# Device private key. Need change to yours.
privateKeyPath = "/home/pi/awsiot/aec2731afd-private.pem.key"
# Device certificate. Need change to yours.
certificatePath = "/home/pi/awsiot/aec2731afd-certificate.pem.crt"
myAWSIoTMQTTShadowClient = None;
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("RaspberryLedController")
myAWSIoTMQTTShadowClient.configureEndpoint(awsiotHost, awsiotPort)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(60) # 10sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(50) #5sec

#connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

#create a devcie Shadow with persistent subscription
# change thing name to yours
thingName = "homepi"
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

#Delete shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_delete, 50)


#start a thread to loop device status every 5 seconds
statusLoopThread = threading.Thread(target=getDeviceStatus)
statusLoopThread.start()

#update shadow in a loop
loopCount = 0
while True:
    desiredState = "off"
    if (loopCount % 2 == 0):
        desiredState = "on"
    print("To change Led desired status to \"" + desiredState + "\" ...\n")
    jsonPayload = '{"state":{"desired":{"light":"' + desiredState + '"}}}'
    print("payload is: " + jsonPayload + "\n")
    deviceShadowHandler.shadowUpdate(jsonPayload, customShadowCallback_upate, 60)
    loopCount += 1
    time.sleep(60)

