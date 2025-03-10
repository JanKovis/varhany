import kredence

import network
import socket
import time
from machine import Pin

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm=network.WLAN.PM_NONE)
print("PowerManagement wanted: ", network.WLAN.PM_NONE, " real ", wlan.config("pm"))


def connect_wifi() -> str:
    # Connect to WLAN
    wlan.connect(kredence.ssid, kredence.password)
    while wlan.isconnected() == False:
        print(f"Waiting for connection... {wlan.status()}")
        time.sleep(0.5)
    print("IF: ", wlan.ifconfig())
    ip = wlan.ifconfig()[2]
    print("Connected to " + kredence.ssid + ". " + "Gateway IP: " + ip)
    return ip


class ButtonHandler:
    class ButtonEntry:
        def __init__(self, button_pin: Pin, indicator_pin: Pin):
            self.button_pin = button_pin
            self.indicator_pin = indicator_pin
            # debouncing time record
            self.sent_recently_timestamp = 0

        def indicate(self):
            if self.indicator_pin:
                self.indicator_pin.on()

        def stop_indication(self):
            if self.indicator_pin:
                self.indicator_pin.off()

    def __init__(self):
        self.target_ip = "???"
        self.buttons = {}

    def check(self):
        for number, button_entry in self.buttons.items():
            now = time.ticks_ms()
            diff = time.ticks_diff(now, button_entry.sent_recently_timestamp)
            if diff < 300:  # do not send more often than 200 ms
                continue

            if button_entry.button_pin.value() == 1:
                print(f"Button {number}")
                self._send_message(number)
                button_entry.indicate()
                button_entry.sent_recently_timestamp = now
            else:
                button_entry.stop_indication()

    def _send_message(self, msg: int):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting {self.target_ip}")
            client_socket.connect((self.target_ip, 80))
            sent_text = f"number={msg}"
            print("Sending", sent_text)
            client_socket.sendall(sent_text.encode())
            client_socket.close()
        except OSError as e:
            print("Message not sent: ", e)


handler = ButtonHandler()
handler.buttons[1] = ButtonHandler.ButtonEntry(
    Pin(14, Pin.IN, pull=Pin.PULL_DOWN), Pin(17, Pin.OUT, value=0)
)
handler.buttons[10] = ButtonHandler.ButtonEntry(
    Pin(12, Pin.IN, pull=Pin.PULL_DOWN), Pin(19, Pin.OUT, value=0)
)
handler.buttons[100] = ButtonHandler.ButtonEntry(
    Pin(10, Pin.IN, pull=Pin.PULL_DOWN), Pin(21, Pin.OUT, value=0)
)

wlan_indicator = Pin(26, Pin.OUT, value=0)
power_indicator = Pin(22, Pin.OUT, value=1)

myLED = Pin("LED", Pin.OUT, value=1)

while True:
    # print(wlan, wlan.isconnected())
    if not wlan.isconnected():
        print("No WLAN")
        wlan_indicator.off()
        handler.target_ip = connect_wifi()

    wlan_indicator.on()

    handler.check()
