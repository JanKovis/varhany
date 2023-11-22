import kredence

import socket
import network
from machine import Pin
from time import sleep
import re


def send_impulses_on_pin(impulse_count: int, pin: Pin, pulse_duration: float = 0.1):
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


with open("web.html", "r") as f:
    input_webpage = f.read()

boardLED = Pin("LED", Pin.OUT)

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
hundredsPin = boardLED
tensPin = boardLED
onesPin = boardLED

while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print("Connection from", client_address)

    # Receive and print data from the client
    data = client_socket.recv(1024)
    data_string = data.decode().strip()
    print("Received data:", data_string)

    if "GET" in data_string:
        client_socket.send(input_webpage)
        client_socket.close()
        continue

    # what is not explicit GET is taken as a POST
    match = re.search(r"number\s*=\s*(\d+)$", data_string)
    if not match:
        print("Number to be set not found in the request")
        continue

    nr = int(match.group(1)) % 1000
    print("NR> ", nr)

    client_socket.send(f"<html><body>Nastavuje se cislo {nr}</body></html>")
    client_socket.close()

    hundreds = nr // 100
    send_impulses_on_pin(hundreds, hundredsPin)
    nr -= hundreds * 100

    # just to visually divide
    sleep(1)

    tens = nr // 10
    send_impulses_on_pin(tens, tensPin)
    nr -= tens * 10

    # just to visually divide
    sleep(1)

    send_impulses_on_pin(nr, onesPin)
