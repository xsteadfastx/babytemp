BABYTEMP
========

![nodemcu v3](nodemcuv3.jpg)

![babytemp interface](interface.png)

1. `$ docker run -it --rm -p 1883:1883 -p 9001:9001 eclipse-mosquitto`
2. Create `config.py`
3. `make flash`
4. `$ bokeh serve --show interface.py`
