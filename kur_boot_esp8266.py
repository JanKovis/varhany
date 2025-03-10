# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import os, machine

# os.dupterm(None, 1) # disable REPL on UART(0)
import gc
import network

# import webrepl
# webrepl.start()


def configure_wifi():
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    wlan.disconnect()  # Disconnect from any network
    wlan.config(reconnect=False)  # Disable auto-reconnect
    print("WiFi auto-connect disabled.")


gc.collect()
configure_wifi()
