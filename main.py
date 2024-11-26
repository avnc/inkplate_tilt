import binascii
import gc
import time
from time import sleep
import network
import ntptime
import bluetooth
import machine
import ujson
import ure
from micropython import const
from inkplate5 import Inkplate

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

def connect_and_get_time():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.active(True)
        wlan.connect(config_data["network_name"], config_data["network_password"])
        while not wlan.isconnected():
            print("connecting")
            pass
    print("network config:", wlan.ifconfig())
    # set time to value from ntp
    print("getting ntptime")
    ntptime.settime()
    wlan.disconnect()
    wlan.active(False)

def fix_dump(data, is_request=False):
    data_to_dump = {}
    for k, v in data.items():
        if is_request:
            if len(v) > 0:
                data_to_dump[k] = v[0]
            else:
                data_to_dump[k] = v
        else:
            data_to_dump[k] = v
        if k == 'network_name' and len(data_to_dump[k]) == 0:
            data_to_dump[k] = 'changeme'

    return data_to_dump

def dump_and_write(filename, data, is_request=False):
    data_to_dump = fix_dump(data, is_request)
    print(f"Writing configuration data: {ujson.dumps(data_to_dump)}")
    f = open("config.json", "w")
    f.write(ujson.dumps(data_to_dump))
    f.close()
    return data_to_dump

config_data = {
    'network_name': '',
    'network_password': '',
    'utc_offset': '',
    'blue': '',
    'black': '',
}

try:
    f = open("config.json", "r")
    config_data = ujson.loads(f.read())
    f.close()
except:
    dump_and_write('config.json', config_data)


TILT_DEVICES = {
    'a495bb30c5b14b44b5121370f02d74de': 'black',
    'a495bb60c5b14b44b5121370f02d74de': 'blue',
    'a495bb20c5b14b44b5121370f02d74de': 'green',
    'a495bb50c5b14b44b5121370f02d74de': 'orange',
    'a495bb80c5b14b44b5121370f02d74de': 'pink',
    'a495bb40c5b14b44b5121370f02d74de': 'purple',
    'a495bb10c5b14b44b5121370f02d74de': 'red',
    'a495bb70c5b14b44b5121370f02d74de': 'yellow',
    'a495bb90c5b14b44b5121370f02d74de': 'brown',
}

# only have two of these, a blue and a black, modify to fit your need
tilt_data = {"blue_temp": "",
             "blue_grav": "",
             "black_temp": "",
             "black_grav": ""
}

ble = bluetooth.BLE()
ble.active(True)

display = Inkplate(Inkplate.INKPLATE_1BIT)
display.begin()

# Clear the frame buffer
display.clearDisplay()
display.setTextSize(4)

# connects to configured wifi, sets time from ntp server and then disconnects
connect_and_get_time()
(year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()
hour = hour + int(config_data["utc_offset"])
print(f"Current time: {hour}:{minute:02}:{second:02}")

# set rtc with our values from ntp
display.rtcSetDate(weekday, mday, month, year)
display.rtcSetTime(hour, minute, second)

# get names of current beers
blue_beer = config_data["blue"]
black_beer = config_data["black"]

# used to parse out the bluetooth data, with tilt major is temp, minor is SG
def parse_data(addr, adv_data):
    mac_raw = binascii.hexlify(addr).decode('utf-8')
    raw_data = binascii.hexlify(bytes(adv_data)).decode('ascii')
    return {
        'mac': ':'.join(mac_raw[i:i+2] for i in range(0,12,2)),
        'uuid': raw_data[18:50],
        'major': raw_data[50:54],
        'minor': raw_data[54:58],
    }

def bt_irq_nothing(event, data):
    pass

# bluetooth irq event handler
def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:      
        addr_type, addr, connectable, rssi, adv_data = data
        parsed_data = parse_data(addr, adv_data)
        print(parsed_data)
        if parsed_data['uuid'] in TILT_DEVICES:
            grav = (int(parsed_data['minor'], 16)) / 1000
            temp = round((int(parsed_data['major'], 16) - 32) / 1.8, 1)
            temp = (temp * 1.8) + 32            
            tilt = TILT_DEVICES[parsed_data['uuid']]
            tilt_data[f"{tilt}_temp"] = temp
            tilt_data[f"{tilt}_grav"] = grav

    elif event == _IRQ_SCAN_DONE:
        print("Scan complete")
        display.clearDisplay()   
        display.setTextSize(5)
        display.printText(80, 50, blue_beer)
        display.setTextSize(4)
        display.printText(80, 100, f"Temperature: {tilt_data["blue_temp"]}")
        display.printText(80, 150, f"Specific Gravity: {tilt_data["blue_grav"]}")
        display.setTextSize(5)
        display.printText(80, 250, black_beer)
        display.setTextSize(4)
        display.printText(80, 300, f"Temperature: {tilt_data["black_temp"]}")
        display.printText(80, 350, f"Specific Gravity: {tilt_data["black_grav"]}")            
        display.drawFastHLine(100, 225, 400, display.BLACK)
        battery = str(display.readBattery())
        display.setTextSize(2)
        time_date = display.rtcGetData()
        display.printText(80, 500, f"Battery voltage: {battery}V, Updated: {time_date["hour"]}:{time_date["minute"]:02}")       
        display.partialUpdate()
        
    

# start looking for tilts
try:
    display.clearDisplay()
    display.printText(100, 100, "Starting Scan...")
    display.display()
    
    while True:
        # look for bluetooth devices for 15 secs, may need to modify if farther away (or more devices)
        scan = ble.gap_scan(15000, 30000, 10000)
        ble.irq(bt_irq)
        sleep(3600)
except OSError as e:
    pass
