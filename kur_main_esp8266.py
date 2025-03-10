import kredence

import network
import socket
import time
from machine import Pin

wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
print("Active? ", wlan.active())

wifis = wlan.scan()
for a_wifi in wifis:
    print("WLAN: ", a_wifi)


def connect_wifi() -> str:
    # Connect to WLAN
    wlan.connect(kredence.ssid, kredence.password)
    status_texts = {
        network.STAT_IDLE: "idle",
        network.STAT_CONNECTING: "connecting",
        network.STAT_WRONG_PASSWORD: "wrong password",
        network.STAT_NO_AP_FOUND: "no AP found",
        network.STAT_CONNECT_FAIL: "other failure",
        network.STAT_GOT_IP: "Connected",
    }
    while wlan.isconnected() == False:
        print(
            f"Waiting for connection... {wlan.status()} {status_texts.get(wlan.status(), '???')})"
        )
        time.sleep(0.5)
    print("IF: ", wlan.ifconfig())
    ip = wlan.ifconfig()[2]
    print("Connected to " + kredence.ssid + ". " + "Gateway IP: " + ip)
    return ip

# the stuff is inverted with ESP8266
CIRCUIT_TRUE = 0
CIRCUIT_FALSE = 1

class ButtonHandler:
    class ButtonEntry:
        def __init__(self, button_pin: Pin, indicator_pin: Pin):
            self.button_pin = button_pin
            self.indicator_pin = indicator_pin
            # debouncing time record
            self.sent_recently_timestamp = 0

        def indicate(self):
            if self.indicator_pin:
                self.indicator_pin.value(CIRCUIT_TRUE)

        def stop_indication(self):
            if self.indicator_pin:
                self.indicator_pin.value(CIRCUIT_FALSE)

    def __init__(self):
        self.target_ip = "???"
        self.buttons = {}

    def check(self):
        for number, button_entry in self.buttons.items():
            now = time.ticks_ms()
            diff = time.ticks_diff(now, button_entry.sent_recently_timestamp)
            if diff < 300:  # do not send more often than that many ms
                continue

            if button_entry.button_pin.value() == CIRCUIT_TRUE:
                print(f"Button {number} start")
                self._send_message(number)
                button_entry.indicate()
                button_entry.sent_recently_timestamp = now
            else:
                button_entry.stop_indication()
                
            time.sleep(0.1)

    def _send_message(self, msg: int):
        ButtonHandler.send_message(self.target_ip, msg)

    @staticmethod
    def send_message(target_ip: str, msg: int):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting {target_ip}")
            client_socket.connect((target_ip, 80))
            sent_text = f"number={msg}"
            print("Sending", sent_text)
            client_socket.sendall(sent_text.encode())
            client_socket.close()
        except OSError as e:
            print("Message not sent: ", e)


handler = ButtonHandler()
handler.buttons[1] = ButtonHandler.ButtonEntry(
    Pin(5, Pin.IN, pull=Pin.PULL_UP, value=CIRCUIT_TRUE), None
)
handler.buttons[10] = ButtonHandler.ButtonEntry(
   Pin(4, Pin.IN, pull=Pin.PULL_UP), None
)
handler.buttons[100] = ButtonHandler.ButtonEntry(
   Pin(0, Pin.IN, pull=Pin.PULL_UP), None
)

# wlan_indicator = Pin(26, Pin.OUT, value=0)
ONBOARD_LED_ID = 2
power_indicator = Pin(15, Pin.OUT, value=CIRCUIT_TRUE)
wlan_indicator = Pin(16, Pin.OUT, value=CIRCUIT_FALSE)
# 2 = onboard LED
# pinz = {}
# for pinnr in [2, 3, 4, 10, 12, 13, 14, 15, 16]: #(2, 3, 4, 5, 10, 12, 13, 14, 15, 16): 
#     print(f"Instantiate pin {pinnr}")
#     pinz[pinnr] = Pin(pinnr, Pin.OUT, value=0)

while True:
    #print(wlan, wlan.isconnected())
    if not wlan.isconnected():
        print("No WLAN")
        wlan_indicator.value(CIRCUIT_FALSE)
        target_ip = connect_wifi()
        handler.target_ip = connect_wifi()
        wlan_indicator.value(CIRCUIT_TRUE)

    handler.check()
