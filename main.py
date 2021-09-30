from machine import Pin, ADC
from time import sleep
import urequests
import ujson
#import network
import wifimgr

#wlan = network.WLAN(network.STA_IF)

# connect to wifi
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        allAPByte = wlan.scan()
        allAP = list(allAPByte)
        print(allAP)
        #APBool = 'realme5' in allAP
        APBool = any("realme5" in s for s in allAP)
        print(APBool)
        #wlan.connect('realme5', 'tysonchamp')
        #while not wlan.isconnected():
            #print('Wifi Not Available. Will try after 30 sec..')
            #sleep(30)
            #wlan.connect('realme5', 'tysonchamp')
    #print('network config:', wlan.ifconfig())


# switch Toogle Function
def toogleSwitch(gpioPin, status):
    if status == '0':
        gpioPin.value(0)
        print("turned Off!")
    else:
        gpioPin.value(1)
        print("turned On!")


# check if internet is connected or not
def connect(host='http://www.google.com'):
    #if wlan.isconnected():
    print('Trying to Connect....')
    try:
        urequests.get(host)  # Python 3.x
        return True
    except:
        return False
    #else:
    #    return False


# fetch API Data function
def fetchAPIData(deviceid):
    response = urequests.get(
            "http://homeautoci.erisetechnology.com/api/devices/devicelists/"+deviceid)
    return response.text


# toogle status
def toogle_status(status):
    if status == 0:
        return '1'
    else:
        return '0'

# ESP32 Signal Output
light1 = Pin(25, Pin.OUT)
light2 = Pin(26, Pin.OUT)
plug = Pin(27, Pin.OUT)


# ESP32 Signal input
light1in = Pin(33, Pin.IN, Pin.PULL_UP)
light1in_status = 0

light2in = ADC(Pin(35))
plugin = Pin(36, Pin.IN)
light2in.atten(ADC.ATTN_11DB)

#############################################MAIN PROGRAMME#############################################

# device id
deviceid = "jsdukjfnxvzxcxjhzxjgha"
headers = {'Content-Type': 'application/json'}

# connect to wifi
#do_connect()

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# main programme
while True:
    apiData = fetchAPIData(deviceid)
    apiArray = ujson.loads(apiData)
    # device toogle system
    if apiArray["success"]:
        for i in apiArray["devices"]:
                if i["type"] != "fan":
                    print(i["name"])
                    if i["nickname"] == '25':
                        toogleSwitch(light1, i["status"])
                    elif i["nickname"] == '26':
                        toogleSwitch(light2, i["status"])
                    elif i["nickname"] == '27':
                        toogleSwitch(plug, i["status"])
                    else:
                        print("Do Nothing")
                else:
                    print(i["name"])
                    fanSwitch(i["status"])
    else:
        print("Nothing To Do!")
        # wait for 1 sec
        
    light1in_state = light1in.value()
    
    
    if light1in_status != light1in_state:
        url = "http://homeautoci.erisetechnology.com/api/device/toogle_device_from_esp/22/"+str(light1in_state)
        responce = urequests.get(url)
        print(responce.text)
        light1in_status = light1in_state
        for i in apiArray["devices"]:
            if i["nickname"] == '25':
                if i["status"] != light1in_state:
                    print("Light 1 IN Status 1: " + str(light1in_state) + " : " + str(light1in_status) + " : " + str(i["status"]))
                    toogleSwitch(light1, toogle_status(i["status"]))
                elif i["status"] == light1in_state:
                    toogleSwitch(light1, toogle_status(i["status"]))
                    print("Light 1 IN Status 2: " + str(light1in_state) + " : " + str(light1in_status) + " : " + str(i["status"]))
    #else:
    #    for i in apiArray["devices"]:
    #        if i["nickname"] == '25':
    #            if i["status"] == light1in_state:
    #                toogleSwitch(light1, toogle_status(i["status"]))
        
    light2in_state = light2in.read()
    print("Light 2 IN Status: " + str(light2in_state))
        
    #sleep(1)
