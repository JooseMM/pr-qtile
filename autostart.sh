#!/bin/sh
xrandr --output HDMI-A-0 --left-of DisplayPort-0
xrandr --output HDMI-A-0 --primary
xrandr --output HDMI-A-0 --mode 1920x1080
nitrogen --restore 
