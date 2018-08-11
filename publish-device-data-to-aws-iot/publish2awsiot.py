import RPi.GPIO as GPIO
import Adafruit_DHT as dht
#import dht11
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from datetime import date, datetime
 
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
 
# AWS IoT certificate based connection
# Client UUID, you can update if needed
myMQTTClient = AWSIoTMQTTClient("123afhlss411")
# AWS IoT Core endpoint. Need change to yours.
myMQTTClient.configureEndpoint("********.iot.ap-southeast-1.amazonaws.com", 8883)
# Thing certification files. Need change to yours.
myMQTTClient.configureCredentials("/home/pi/awsiot/VeriSign-Class3-Public-Primary-Certification-Authority-G5.pem", "/home/pi/awsiot/aec2731afd-private.pem.key", "/home/pi/awsiot/aec2731afd-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
 
#connect and publish
myMQTTClient.connect()
# The MQTT topic to which messages will be published. Change if needed.
myMQTTClient.publish("homepi/dht22", "connected", 0)
 
#loop and publish sensor reading
while 1:
    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ') #e.g. 2016-04-18T06:12:25.877Z
    #instance = dht11.DHT11(pin = 4) #BCM GPIO04
    #result = instance.read()
    h,t = dht.read_retry(dht.DHT22, 4)
    print 'Temp = %.1f"C, Humidity = %.1f%%RH' % (t, h)
    #if result.is_valid():
    payload = '{ "timestamp": "' + now_str + '","temperature": ' + "{:.2f}".format(t)+ ',"humidity": '+ "{:.2f}".format(h) + ' }'
    print payload
    myMQTTClient.publish("homepi/dht22", payload, 0)
    sleep(10)
    #else:
    #    print (".")
    #    sleep(1)
