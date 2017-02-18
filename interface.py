import time

from datetime import datetime

from functools import partial

from threading import Thread

from bokeh.layouts import gridplot
from bokeh.plotting import curdoc, figure

from config import MQTT_SERVER

import paho.mqtt.client as mqtt

from tornado import gen


p1 = figure(
    title='Temperature',
    tools='pan',
    plot_width=600,
    plot_height=400,
    x_axis_type='datetime'
)

p2 = figure(
    title='Humidity',
    tools='pan',
    plot_width=600,
    plot_height=400,
    x_axis_type='datetime'
)

# axes
x = []
y = []

# sensor values
temp = None
humi = None

temp_graph = p1.line(x, y, color="navy", alpha=0.5)
humi_graph = p2.line(x, y, color="red", alpha=0.5)

# This is important! Save curdoc() to make sure all threads
# see then same document.
doc = curdoc()


def on_connect(client, userdata, flags, rc):
    client.subscribe('/babytemp/#')


def on_message(client, userdata, msg):
    global temp
    global humi

    if msg.topic == '/babytemp/temperature':
        temp = float(msg.payload)

    if msg.topic == '/babytemp/humidity':
        humi = float(msg.payload)


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_SERVER, 1883, 60)


def mqtt_loop():
    while True:
        time.sleep(0.1)
        mqtt_client.loop()
        doc.add_next_tick_callback(partial(update))


@gen.coroutine
def update():
    if not temp and not humi:
        return
    now = datetime.now()

    if now.minute == 0 and now.hour == 0:
        temp_new_y = []
        temp_new_x = []

        humi_new_y = []
        humi_new_x = []

    else:
        temp_new_y = list(temp_graph.data_source.data['y'])
        temp_new_y.append(temp)

        temp_new_x = list(temp_graph.data_source.data['x'])
        temp_new_x.append(now)

        humi_new_y = list(humi_graph.data_source.data['y'])
        humi_new_y.append(humi)

        humi_new_x = list(humi_graph.data_source.data['x'])
        humi_new_x.append(now)

    temp_graph.data_source.data['y'] = temp_new_y
    temp_graph.data_source.data['x'] = temp_new_x

    humi_graph.data_source.data['y'] = humi_new_y
    humi_graph.data_source.data['x'] = humi_new_x


p = gridplot([p1], [p2], sizing_mode='stretch_both')

doc.add_root(p)

thread = Thread(target=mqtt_loop)
thread.start()
