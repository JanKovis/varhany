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
ap.config(essid=kredence.ssid, key=kredence.password)
ap.active(True)

while ap.active == False:
    pass

print("Access point active")
print(ap.ifconfig())

# Set up the TCP server
port = 80
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))  # Listen on all available interfaces
server_socket.listen(4)  # Allow only one connection at a time

print(f"Server listening on port {port}")

# assign the right relay GPIO
onesPin = Pin(18, Pin.OUT, value=0)  # ~relay 1
tensPin = Pin(19, Pin.OUT, value=0)  # ~relay 2
hundredsPin = Pin(20, Pin.OUT, value=0)  # ~relay 3

while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print("Connection from", client_address)

    # Receive and print data from the client
    data = client_socket.recv(1024)
    print("Received: ", data)

    if b"GET" in data:
        client_socket.send(input_webpage)
        client_socket.close()
        continue

    nr = number_in_message(data)
    if (
        nr is None
    ):  # iPhone Safari browser has nasty habbit to send POST contents a bit later
        poller = select.poll()
        poller.register(client_socket, select.POLLIN)
        poll_result = poller.poll(300)
        print("PR: ", poll_result)
        if not poll_result:  # timed out
            client_socket.close()
            continue
        for _, event in poll_result:
            if event & select.POLLIN:
                data = client_socket.recv(1024)
                nr = number_in_message(data)
                if nr is not None:
                    break

    if nr is None:
        client_socket.close()
        continue

    print("NR> ", nr)

    client_socket.send(f"<html><body>Nastavuje se cislo {nr}</body></html>")
    client_socket.close()

    hundreds = nr // 100
    send_impulses_on_pin(hundreds, hundredsPin)
    nr -= hundreds * 100

    # just to visually divide
    # sleep(1)

    tens = nr // 10
    send_impulses_on_pin(tens, tensPin)
    nr -= tens * 10

    # just to visually divide
    # sleep(1)

    send_impulses_on_pin(nr, onesPin)
