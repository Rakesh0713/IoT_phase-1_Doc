import network
import usocket as socket
import ujson
import machine
import time
from machine import I2C, Pin
import ssd1306

# Define pin numbers
sensorPin = 0

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Rakesh_0213', '$aran0213')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
do_connect()    
    
def measure_noise():
   adc = machine.ADC(machine.Pin(sensorPin))
   noise_level = adc.read()
   return noise_level
   
def web_socket_handler():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 81))
    s.listen(5)
    
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)
        ws = websocket.WebSocket(sock=conn)
        
        while True:
            noise_level = measure_noise()
            data = {'noise_level': noise_level}
            ws.send(ujson.dumps(data))
            time.sleep(1)

web_socket_handler()

# Constants
num_Measure = 128
soundlow = 40
soundmedium = 500
error = 33

# OLED display configuration
i2c = I2C(sda=Pin(4), scl=Pin(5))  # Adjust the pins for your setup
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

while True:
    sum_value = 0
    # Perform 128 signal readings
    for i in range(num_Measure):
        Sound_signal = measure_noise()
        sum_value += Sound_signal

    level = sum_value / num_Measure  # Calculate the average value

    # Display Sound Level on OLED
    oled.fill(0)  # Clear the display
    oled.text("Sound Level:", 0, 0)
    oled.text("{:.2f} dB".format(level - error), 0, 20)

    if level - error < soundlow:
        intensity = "Intensity=Low"
    elif soundlow <= level - error < soundmedium:
        intensity = "Intensity=Medium"
    else:
        intensity = "Intensity=High"

    oled.text(intensity, 0, 40)
    oled.show()

    print("Sound Level:", level - error)
    print(intensity)

    sum_value = 0  

    time.sleep(1)  
