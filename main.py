import network
import esp
import machine
import usocket as _socket
import ussl as ssl
import https_client

SSID = ""
PASS = ""

esp.osdebug(True)

sta_if = network.WLAN(network.STA_IF)

sta_if.active(True) 

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID,PASS)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


do_connect()


print(https_client.request("https://www.google.com/"))
print(https_client.request("https://www.google.com/",cert="google.pem"))

try: 
    print(https_client.request("https://www.yahoo.com/",cert="google.pem"))
    print("This should not work")
except OSError:
    print("Works")

