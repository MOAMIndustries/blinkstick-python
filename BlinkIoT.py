from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from blinkstick import blinkstick
import json
import time

topic1 = "test1/"
topic2 = "test2/"
topic3 = "test3/"



def customOnMessage(message):
    print("$$$$$$$$$$$$")     
    print("Default Callback" )
    print("Message:")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("$$$$$$$$$$$$$\n\n")

def customSubCallback1(client, userdata, message):
    print("------SUB 1--------")     
    print("Received a new message on topic "+ topic1 )
    print("cleint:")
    print(client)
    print("user Data: ")
    print(userdata)
    print("message")
    print(message.payload)
    j = json.loads(message.payload)
    print("INDEX= {}, RED= {}, GREEN= {}, BLUE= {}".format(j['index'],j['red'], j['green'], j["blue"]))
    stick.set_color(channel=0, index=j['index'],red=j['red'],green=j['green'],blue=j['blue'])
    print("--------------\n\n")

def customSubCallback2(client, userdata, message):
    print("------ SUB 2--------")     
    print("Received a new message on topic "+ topic2 )
    print("cleint:")
    print(client)
    print("user Data: ")
    print(userdata)
    print("message")
    print(message.payload)
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


myAWSIoTMQTTClient.subscribeAsync(topic1, 1, messageCallback=customSubCallback1)
myAWSIoTMQTTClient.subscribeAsync(topic2, 1, messageCallback=customSubCallback2)
myAWSIoTMQTTClient.subscribeAsync(topic3, 1, ackCallback=customSubackCallback3)
time.sleep(2)

blinkstick
stick = .find_first()
print ("Found device:")
print ("    Manufacturer:  " + stick.get_manufacturer())
print ("    Description:   " + stick.get_description())
print ("    Serial:        " + stick.get_serial())
print ("    Current Color: " + stick.get_color(color_format="hex"))
print ("    Info Block 1:  " + stick.get_info_block1())
print ("    Info Block 2:  " + stick.get_info_block2())
print ("    Mode: {}".format(stick.get_mode()))

for i in range(1,5):
    stick.set_color(channel=0, index=i, red=0,green=0,blue=0)


# Publish to the same topic in a loop forever
loopCount = 0
while True:
    #myAWSIoTMQTTClient.publishAsync(topic1, "New Message " + str(loopCount), 1, ackCallback=customPubackCallback)
    loopCount += 1
    time.sleep(5)