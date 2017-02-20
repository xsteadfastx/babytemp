import time

from datetime import datetime

from functools import partial

from threading import Thread

from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
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

# data store
temp_source = ColumnDataSource(data=dict(x=[], y=[]))
humi_source = ColumnDataSource(data=dict(x=[], y=[]))

# sensor values
temp = None
humi = None

# define plots
temp_graph = p1.line(x='x', y='y', source=temp_source, color="navy", alpha=0.5)
humi_graph = p2.line(x='x', y='y', source=humi_source, color="red", alpha=0.5)

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
    if not temp or not humi:
        return

    now = datetime.now()

    temp_source.stream(
        {
            'x': [now],
            'y': [temp]
        }
    )

    humi_source.stream(
        {
            'x': [now],
            'y': [humi]
        }
    )


p = gridplot([p1], [p2], sizing_mode='stretch_both')

doc.add_root(p)

thread = Thread(target=mqtt_loop)
thread.start()
