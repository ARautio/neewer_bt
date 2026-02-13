# Homeassistant integration for Neewer Bluetooth Light TL40

This is a simple Home Assistant integration for Neewer TL40 Bluetooth light. It supports turning the light on/off, brightness, and color temperature control.

# Installation

I highly suggest ot use HACS for installing this. See [Custom repository documentation from HACS](https://www.hacs.xyz/docs/faq/custom_repositories/) for more info.

# Testing

You can run the local unit tests with:

`python3 -m unittest tests/test_neewer_bt.py`

# Expectations for the future

This is very much proof of concept right now since I haven't done integrations before for home assistant. Right now it connects to the light everytime before changing the state so it's a bit slow.

The current version works well for my use case. The light supports additional controls and this integration now includes brightness and color temperature in CCT mode.


# Credits

[NeewerLite-Python](https://github.com/taburineagle/NeewerLite-Python/tree/main) has been a huge help to figure out how the light works.
