from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from blinkstick import blinkstick
import json
import time

topic1 = "sdk/test/Python"
topic2 = "test1/*"
topic3 = "test1/sausages"

def customOnMessage(message):
    print("***********************************")     
    print("Received a new message on topic " )
    print("Message:")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("***********************************\n\n")

def customSubackCallback1(mid, data):
    print("--------------")     
    print("Received a new message on topic "+ topic1 )
    print("Message:")
    print(mid)
    print("received QOS: ")
    print(data)
    print("--------------\n\n")

def customSubackCallback2(mid, data):
    print("--------------")     
    print("Received a new message on topic "+ topic2 )
    print("Message:")
    print(mid)
    print("received QOS: ")
    print(data)
    print("--------------\n\n")

def customSubackCallback3(mid, data):
    print("--------------")     
    print("Received a new message on topic "+ topic3 )
    print("Message:")
    print(mid)
    print("received QOS: ")
    print(data)
    print("--------------\n\n")                

  

# Puback callback
def customPubackCallback(mid):
    print("++++++++++++++")   
    print("Received PUBACK packet id: ")
    print(mid)
    print("++++++++++++++\n\n")

myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient("someTestID")
myAWSIoTMQTTClient.configureEndpoint("a2t9vffvaeksf7-ats.iot.ap-southeast-2.amazonaws.com", 8883)
myAWSIoTMQTTClient.configureCredentials("root-CA.crt", "TestWindowsPythonThing1.private.key", "TestWindowsPythonThing1.cert.pem")

myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.onMessage = customOnMessage

myAWSIoTMQTTClient.connect()


myAWSIoTMQTTClient.subscribeAsync(topic1, 1, ackCallback=customSubackCallback1)
myAWSIoTMQTTClient.subscribeAsync(topic2, 1, ackCallback=customSubackCallback2)
myAWSIoTMQTTClient.subscribeAsync(topic3, 1, ackCallback=customSubackCallback3)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    myAWSIoTMQTTClient.publishAsync(topic1, "New Message " + str(loopCount), 1, ackCallback=customPubackCallback)
    loopCount += 1
    time.sleep(5)