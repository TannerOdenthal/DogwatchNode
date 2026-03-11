# 📡 Dogwatch Node: BLE Proximity Edge Scanner

**DogwatchNode** is the MicroPython firmware for the edge-scanning devices used in the [Dogwatch IoT System](https://github.com/TannerOdenthal/dogwatch). 

Designed to run on the Raspberry Pi Pico 2W, this script acts as a localized Bluetooth Low Energy (BLE) proximity scanner. It detects the presence and signal strength (RSSI) of a target BLE beacon (such as a T1000-E) and securely publishes that telemetry to a central MQTT broker over Wi-Fi.



## ✨ Architecture & Reliability Features
Because microcontrollers lack an operating system to manage dropped sockets and memory leaks, this firmware is engineered for absolute stability in a "flash-and-forget" deployment:

* **Hardware Watchdog Timer (WDT):** Configured with an 8.3-second failsafe. If the network socket hangs or the MicroPython loop freezes, the hardware physically cuts power and reboots the board.
* **Garbage Collection (GC):** Actively manages RAM during JSON string generation to prevent `MemoryError` crashes over long uptimes.
* **Dynamic Auto-Discovery:** MQTT topics and Client IDs are dynamically generated based on the `ROOM_NAME` variable, allowing infinite nodes to be deployed without broker conflicts.
* **Soft Failovers:** Checks Wi-Fi and MQTT socket health before every publish, attempting graceful reconnections before resorting to hard resets.

## ⚙️ Hardware Requirements
* **Microcontroller:** Raspberry Pi Pico W or Pico 2W.
* **Target Device:** Any standard Bluetooth LE beacon or Meshtastic Node broadcasting a consistent MAC address.

## 🚀 Installation & Setup

### 1. Flash MicroPython
Ensure your Raspberry Pi Pico 2W is flashed with the latest MicroPython firmware.

### 2. Install Dependencies
You must install the `umqtt.simple` library on your Pico. 
If using an IDE like **Thonny**:
1. Go to `Tools > Manage Packages`.
2. Search for `umqtt.simple` and install it directly to the board.

### 3. Configure the Node
Open `main.py` and modify the **Dynamic Configuration** section at the top of the file:
```python
ROOM_NAME = "living_room"          # Set to the room this node will be placed in
WIFI_SSID = "YOUR_WIFI_SSID"       # Your 2.4GHz WiFi Name
WIFI_PASS = "YOUR_WIFI_PASSWORD"   # Your WiFi Password
MQTT_SERVER = "192.168.X.X"        # The IP of your Mosquitto Broker
TARGET_MAC = "XX:XX:XX:XX:XX:XX"   # The MAC address of the BLE tag
