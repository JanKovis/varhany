import kredence

import network
import socket
import time
from machine import Pin

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def connect_wifi():
    # Connect to WLAN
    wlan.connect(kredence.ssid, kredence.password)
    while wlan.isconnected() == False:
        print("Waiting for connection...")
        time.sleep(0.5)
    ip = wlan.ifconfig()[0]
    print("Connected to " + kredence.ssid + ". " + "Device IP: " + ip)
    return ip


def send_message(msg: str):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("192.168.1.31", 80))
    # client_socket.connect(("192.168.4.1", 80))
    client_socket.sendall(msg.encode())
    client_socket.close()


def check_button(button_pin: Pin, indicator_pin: Pin, msg: str) -> None:
    if button_pin.value() == 1:
        send_message(msg)
        indicator_pin.on()
        time.sleep(0.05)
        indicator_pin.off()


wlan_indicator = Pin(26, Pin.OUT, value=0)
power_indicator = Pin(22, Pin.OUT, value=1)

hundreds_indicator = Pin(21, Pin.OUT, value=0)
tens_indicator = Pin(19, Pin.OUT, value=0)
ones_indicator = Pin(17, Pin.OUT, value=0)

hundreds_button = Pin(10, Pin.IN)
tens_button = Pin(12, Pin.IN)
ones_button = Pin(14, Pin.IN)

while True:
    print(wlan, wlan.isconnected())
    if not wlan.isconnected():
        wlan_indicator.off()
        connect_wifi()

    wlan_indicator.on()

    check_button(hundreds_button, hundreds_indicator, "=100")
    check_button(tens_button, tens_indicator, "=10")
    check_button(ones_button, ones_indicator, "=1")
