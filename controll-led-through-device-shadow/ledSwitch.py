import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json

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

LED_PIN_NUM = 18 # GPIO Number of Led long pin. Change to yours.
deviceShadowHandler = None
#initialize GOPI
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_NUM, GPIO.OUT)


def customShadowCallback_Delta(payload, responseStatus, token):
    # payload is a JSON string which will be parsed by jason lib
    print(responseStatus)
    print(payload)
    payloadDict = json.loads(payload)
    print("++++++++ Get DELTA data +++++++++++")
    desiredStatus = str(payloadDict["state"]["light"])
    print("desired status: " + desiredStatus)
    print("version: " + str(payloadDict["version"]))
    
    #get device current status
    currentStatus = getDeviceStatus()
    print("Device current status is " + currentStatus)
    #udpate device current status
    if (currentStatus != desiredStatus):
        # update device status as desired
        updateDeviceStatus(desiredStatus)
        # send current status to IoT service
        sendCurrentState2AWSIoT()
    print("+++++++++++++++++++++++++++\n")


    
def updateDeviceStatus(status):
    print("=============================")
    print("Set device status to " + status)
    if (status == "on"):
        turnLedOn(LED_PIN_NUM)
    else:
        turnLedOff(LED_PIN_NUM)
    print("=============================\n")

def getDeviceStatus():
    return getLedStatus(LED_PIN_NUM)

def turnLedOn(gpionum):
    GPIO.output(gpionum, GPIO.HIGH)

def turnLedOff(gpionum):
    GPIO.output(gpionum, GPIO.LOW)

def getLedStatus(gpionum):
    outputFlag = GPIO.input(gpionum)
    print("outputFlag is " + str(outputFlag))
    if outputFlag:
        return "on"
    else:
        return "off"    

def sendCurrentState2AWSIoT():
    #check current status of device
    currentStatus = getDeviceStatus()
    print("Device current status is " + currentStatus)
    print("Sending reported status to MQTT...")
    jsonPayload = '{"state":{"reported":{"light":"' + currentStatus + '"}}}'
    print("Payload is: " + jsonPayload + "\n")
    deviceShadowHandler.shadowUpdate(jsonPayload, customShadowCallback_upate, 50)
 
def customShadowCallback_upate(payload, responseStatus, token):
    # payload is a JSON string which will be parsed by jason lib
    if responseStatus == "timeout":
        print("Update request with " + token + " time out!")
    if responseStatus == "accepted":
        playloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(payload)
        print("Update request with token: " + token + " accepted!")
        print("light: " + str(playloadDict["state"]["reported"]["light"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customShadowCallback_Get(payload, responseStatus, token):
    print("responseStatus: " + responseStatus)
    print("payload: " + payload)
    payloadDict = json.loads(payload)
    # {"state":{"desired":{"light":37},"delta":{"light":37}},"metadata":{"desired":{"light":{"timestamp":1533888405}}},"version":54
    stateStr = "" 
    try:
        stateStr = stateStr + "Desired: " + str(payloadDict["state"]["desired"]["light"]) + ", "
    except Exception:
        print("No desired state")

    try:
        stateStr = stateStr + "Delta: " + str(payloadDict["state"]["delta"]["light"]) + ", "
    except Exception:
        print("No delta state")

    try:
        stateStr = stateStr + "Reported: " + str(payloadDict["state"]["reported"]["light"]) + ", "
    except Exception:
        print("No reported state") 
    
    print(stateStr + ", Version: " + str(payloadDict["version"]))

def printDeviceStatus():
    print("=========================")
    status = getDeviceStatus()
    print(" Current status: " + str(status))
    print("=========================\n\n")

# Cofigure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

#Change AWS IoT service endpoint and port to yours
awsiotHost = "*******.iot.ap-southeast-1.amazonaws.com"
awsiotPort = 8883;
rootCAPath = "/home/pi/awsiot/VeriSign-Class3-Public-Primary-Certification-Authority-G5.pem"
privateKeyPath = "/home/pi/awsiot/aec2731afd-private.pem.key"
certificatePath = "/home/pi/awsiot/aec2731afd-certificate.pem.crt"
myAWSIoTMQTTShadowClient = None;
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("RaspberryLedSwitch")
myAWSIoTMQTTShadowClient.configureEndpoint(awsiotHost, awsiotPort)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(60) # 10sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(30) #5sec

#connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

#create a devcie Shadow with persistent subscription
#change thing name to yours
thingName = "homepi"
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

#listen on deleta
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)

#print the intital status
printDeviceStatus()

#send initial status to IoT service
sendCurrentState2AWSIoT()

#get the shadow after started
deviceShadowHandler.shadowGet(customShadowCallback_Get, 60)

#update shadow in a loop
loopCount = 0
while True:
    time.sleep(1)
