import network, time, ubinascii, json, bluetooth, machine, gc
from machine import Pin, WDT
from umqtt.simple import MQTTClient
from micropython import const

# ==========================================
#          DYNAMIC CONFIGURATION
# ==========================================
ROOM_NAME = "living_room"  # Change this for each new Pico! (e.g. "garage", "bedroom")

# Network Settings
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
MQTT_SERVER = "192.168.X.X"

# Target Device (BLE Beacon/Collar)
TARGET_MAC = "XX:XX:XX:XX:XX:XX"

# Automatically generates unique IDs to prevent Broker conflicts
CLIENT_ID = "PicoNode_" + ROOM_NAME
MAC_CLEAN = TARGET_MAC.replace(':', '').upper()
TOPIC_STR = "pico/proximity/" + ROOM_NAME + "/" + MAC_CLEAN
TOPIC = TOPIC_STR.encode('utf-8')

# ==========================================
#             SYSTEM GLOBALS
# ==========================================
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6) 
last_rssi = None
scan_in_progress = False
led = Pin("LED", Pin.OUT)

def bt_irq(event, data):
    global last_rssi, scan_in_progress
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        mac = ubinascii.hexlify(addr, ':').decode()
        if mac.lower() == TARGET_MAC.lower():
            last_rssi = rssi
    elif event == _IRQ_SCAN_DONE:
        scan_in_progress = False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            led.toggle()
            time.sleep(0.5)
            timeout -= 1
    return wlan.isconnected()

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=60)
    client.connect()
    return client

# ==========================================
#                  SETUP
# ==========================================
if not connect_wifi(): 
    machine.reset()

ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)

try:
    mqtt_client = connect_mqtt()
    print("✅ " + ROOM_NAME + " Pico Ready")
except Exception as e:
    time.sleep(2)
    machine.reset()

# Hardware Watchdog (8.3s max for Pico)
wdt = WDT(timeout=8388) 

# ==========================================
#                MAIN RUN
# ==========================================
while True:
    try:
        wdt.feed()   
        gc.collect() 

        last_rssi = None
        scan_in_progress = True
        
        ble.gap_scan(4000, 30000, 30000)
        
        scan_timeout = 10 
        while scan_in_progress and scan_timeout > 0:
            time.sleep(0.5)
            wdt.feed()
            scan_timeout -= 1

        status = "online" if last_rssi is not None else "offline"
        rssi_val = last_rssi if last_rssi is not None else -100
        
        if last_rssi: 
            led.on()
        else: 
            led.off()

        payload = json.dumps({"mac": TARGET_MAC, "rssi": rssi_val, "status": status})

        # Soft WiFi connection check
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            connect_wifi()
            mqtt_client = connect_mqtt() 

        mqtt_client.publish(TOPIC, payload.encode('utf-8'))
        print("Sent: " + status + " (" + str(rssi_val) + "dBm)")
        
        wdt.feed()
        time.sleep(2)

    except OSError: 
        time.sleep(1)
        machine.reset() 
    except Exception: 
        time.sleep(1)
        machine.reset()
