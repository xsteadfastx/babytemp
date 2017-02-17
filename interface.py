from datetime import datetime

from bokeh.client import push_session
from bokeh.layouts import gridplot
from bokeh.plotting import curdoc, figure

from config import MQTT_SERVER

import paho.mqtt.client as mqtt


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

x = []
y = []

temp = None
humi = None
temp_graph = p1.line(x, y, color="navy", alpha=0.5)
humi_graph = p2.line(x, y, color="red", alpha=0.5)

# This is important! Save curdoc() to make sure all threads
# see then same document.
doc = curdoc()

# open a session to keep our local document in sync with server
session = push_session(doc)


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

mqtt_client.loop_start()


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

doc.add_periodic_callback(update, 50)

session.show(p)  # open the document in a browser
session.loop_until_closed()  # run forever
