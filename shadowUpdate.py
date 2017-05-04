import sys
import logging
import time
import json
import getopt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

# Shadow JSON scheme:
#
# Name: LEDStatus
# {
#   "state": {
#       "desired":{
#           "LED: <INT Value>",
#           "ON/OFF: <String Value>"
#       }
#    }
# }

# Custom Shadow callback
def customShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("LED #: " + str(payloadDict["state"]["desired"]["LED"]))
        print("LED Status: " + str(payloadDict["state"]["desired"]["ON/OFF"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customShadowCallback_Delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " timeout!")
    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")

# AWS Credentials infomation
rootCAPath = "/home/mark/programs/certs/rootCAcert"
privateKeyPath = "/home/mark/programs/certs/0bdff093f1-private.pem.key"
certPath = "/home/mark/programs/certs/0bdff093f1-certificate.pem.crt"
host = "a35dhtz2sdce3t.iot.us-east-1.amazonaws.com"


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIotMQTTShadowClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("basicShadowUpdater")
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certPath)

# AWSIoTMQTTShadowClient config
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
piShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("piShadow", True)

# Delete shadow JSON doc
piShadow.shadowDelete(customShadowCallback_Delete, 5)

# Update shadow in a loop
led = "12"
ledOnOFF = "ON"
ledJSON = {
    "state": {
        "desired": {
            "LED": led,
            "ON/OFF": ledOnOFF
        }
    }
}
while True:
    JSONPayload = json.dumps(ledJSON)
    #JSONPayload = '{"state":{"desired":{"property":' + str(loopCount) + '}}}'
    piShadow.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    if ledOnOFF == "ON":
        ledOnOFF = "OFF"
        ledJSON = {
            "state": {
                "desired": {
                    "LED": led,
                    "ON/OFF": ledOnOFF
                }
            }
        }
    else:
        ledOnOFF = "ON"
        ledJSON = {
            "state": {
                "desired": {
                    "LED": led,
                    "ON/OFF": ledOnOFF
                }
            }
        }
    time.sleep(1) 
