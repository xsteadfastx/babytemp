.PHONY: flash serve

flash:
	ampy -p /dev/ttyUSB0 put am2320.py
	ampy -p /dev/ttyUSB0 put config.py
	ampy -p /dev/ttyUSB0 put main.py
	ampy -p /dev/ttyUSB0 run -n main.py
	picocom -b 115200 /dev/ttyUSB0

serve:
	bokeh serve --show interface.py
