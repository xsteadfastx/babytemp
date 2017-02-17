import time

import am2320

from config import MQTT_SERVER, NETWORK_PASSWORD, NETWORK_SSID

import machine

from umqtt.robust import MQTTClient


I2C = machine.I2C(scl=machine.Pin(14), sda=machine.Pin(2))
SENSOR = am2320.AM2320(I2C)


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(NETWORK_SSID, NETWORK_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

    return sta_if


def main():

    # connect to wifi
    do_connect()

    # connect to mqtt server
    mqtt_client = MQTTClient('babytemp', MQTT_SERVER)
    mqtt_client.connect()

    while True:

        # getting temp
        SENSOR.measure()
        temperature = SENSOR.temperature()
        humidity = SENSOR.humidity()

        # send to mqtt
        mqtt_client.publish(b'/babytemp/temperature', str(temperature))
        mqtt_client.publish(b'/babytemp/humidity', str(humidity))

        time.sleep(1)

    mqtt_client.disconnect()


if __name__ == '__main__':
    main()
