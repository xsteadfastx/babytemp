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


P1 = figure(
    title='Temperature',
    tools='pan',
    plot_width=600,
    plot_height=400,
    x_axis_type='datetime'
)

P2 = figure(
    title='Humidity',
    tools='pan',
    plot_width=600,
    plot_height=400,
    x_axis_type='datetime'
)

# data store
TEMP_SOURCE = ColumnDataSource(data=dict(x=[], y=[]))
HUMI_SOURCE = ColumnDataSource(data=dict(x=[], y=[]))

# sensor values
TEMP = None
HUMI = None

# define plots
TEMP_GRAPH = P1.line(x='x', y='y', source=TEMP_SOURCE, color="navy", alpha=0.5)
HUMI_GRAPH = P2.line(x='x', y='y', source=HUMI_SOURCE, color="red", alpha=0.5)

# This is important! Save curdoc() to make sure all threads
# see then same document.
DOC = curdoc()


def on_connect(client, userdata, flags, rc):
    client.subscribe('/babytemp/#')


def on_message(client, userdata, msg):
    global TEMP
    global HUMI

    if msg.topic == '/babytemp/temperature':
        TEMP = float(msg.payload)

    if msg.topic == '/babytemp/humidity':
        HUMI = float(msg.payload)


MQTT_CLIENT = mqtt.Client()
MQTT_CLIENT.on_connect = on_connect
MQTT_CLIENT.on_message = on_message
MQTT_CLIENT.connect(MQTT_SERVER, 1883, 60)


def mqtt_loop():
    while True:
        time.sleep(0.1)
        MQTT_CLIENT.loop()
        DOC.add_next_tick_callback(partial(update))


@gen.coroutine
def update():
    if not TEMP or not HUMI:
        return

    now = datetime.now()

    if now.hour == 0 and now.second == 0:

        TEMP_SOURCE.data = {
            'x': [],
            'y': []
        }

        HUMI_SOURCE.data = {
            'x': [],
            'y': []
        }

    else:

        TEMP_SOURCE.stream(
            {
                'x': [now],
                'y': [TEMP]
            }
        )

        HUMI_SOURCE.stream(
            {
                'x': [now],
                'y': [HUMI]
            }
        )


P = gridplot([P1], [P2], sizing_mode='stretch_both')

DOC.add_root(P)

thread = Thread(target=mqtt_loop)
thread.start()
