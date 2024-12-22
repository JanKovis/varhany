import kredence

import socket
import network
from machine import Pin
from time import sleep
import re
import select


def send_impulses_on_pin(
    impulse_count: int, pin: Pin, pulse_duration: float = 0.1
) -> None:
    # print("Impulses: ", impulse_count)
    pin.off()  # turn off light in every case
    if impulse_count < 1:
        return

    sleep(pulse_duration)

    for i in range(impulse_count):
        # print("I> ", i)
        pin.on()
        sleep(pulse_duration)
        pin.off()
        sleep(pulse_duration)


def number_in_message(msg: bytes) -> int:
    """Try to extract a number on the end of message following the text number=
    returns None if number is not present"""
    if msg is None:
        return None
    msg = msg.decode().strip()
    match = re.search(r"number\s*=\s*(\d+)$", msg)
    if not match:
        print("Number to be set not found in the request")
        return None
    return int(match.group(1))


boardLED = Pin("LED", Pin.OUT, value=1)  # signalize the power presence

with open("web.html", "r") as f:
    input_webpage = f.read()

ap = network.WLAN(network.AP_IF)
ap.config(essid=kredence.ssid, key=kredence.password, pm=network.WLAN.PM_NONE)
ap.active(True)

while ap.active == False:
    pass

print("Access point active")
print(ap.ifconfig())

# Set up the TCP server
port = 80
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))  # Listen on all available interfaces
server_socket.listen(5)  # Allow only few connections at a time

print(f"Server listening on port {port}")

# assign the right relay GPIO
onesPin = Pin(18, Pin.OUT, value=0)  # ~relay 1
tensPin = Pin(19, Pin.OUT, value=0)  # ~relay 2
hundredsPin = Pin(20, Pin.OUT, value=0)  # ~relay 3

numbers_to_set = []

poller = select.poll()
poller.register(server_socket, select.POLLIN)

while True:
    something_has_been_done = False
    ready = poller.poll(-1)  # no timeout on polling

    if len(ready) > 0:
        something_has_been_done = True
        for poller_record in ready:
            socket_with_data = poller_record[0]
            if socket_with_data is server_socket:
                new_connection_socket, new_connection_address = server_socket.accept()
                print(f"Incoming connection from {new_connection_address}")
                poller.register(new_connection_socket, select.POLLIN)
            else:
                try:
                    data = socket_with_data.recv(1024)
                except OSError as e:
                    poller.unregister(socket_with_data)
                    continue
                    
                print("Received: ", data)
                
                if len(data) == 0:
                    poller.unregister(socket_with_data)
                    continue

                if b"GET" in data:
                    socket_with_data.send(input_webpage)
                    socket_with_data.close()
                    poller.unregister(socket_with_data)
                    continue

                nr = number_in_message(data)
                if nr is not None:
                    numbers_to_set.append(nr)
                    print(f"Enqueued number {nr}")
                    socket_with_data.send(f"<html><body>Nastavuje se cislo {nr}</body></html>")
                    sleep(0.01)
                    socket_with_data.close()
                    poller.unregister(socket_with_data)

    if len(numbers_to_set):
        something_has_been_done = True

        nr = numbers_to_set.pop()
        print("setting NR> ", nr)

        hundreds = nr // 100
        send_impulses_on_pin(hundreds, hundredsPin)
        nr -= hundreds * 100

        tens = nr // 10
        send_impulses_on_pin(tens, tensPin)
        nr -= tens * 10

        send_impulses_on_pin(nr, onesPin)

    if not something_has_been_done:
        sleep(0.5)
