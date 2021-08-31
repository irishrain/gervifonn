#!/usr/bin/env python3

# Copyright (C) 2021 Fabian Jansen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tkinter as tk
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from PIL import Image, ImageTk
import RPi.GPIO as GPIO

imgsize = 224


def take_picture():
    global window
    global camera
    global imagelabel

    if GPIO.input(21) == 0:
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format="rgb")

        videoimage = Image.fromarray(rawCapture.array)
        videotkimage = ImageTk.PhotoImage(videoimage)
        imagelabel.configure(image=videotkimage)
        imagelabel.image = videotkimage
        videoimage.save(str(time.time())+'.png')
        print('saved')

    window.after(50, take_picture)

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

camera = PiCamera()
camera.resolution = (imgsize, imgsize)

window = tk.Tk()
window.attributes("-fullscreen", True)
frame = tk.Frame(window)
imagelabel = tk.Label(frame)
imagelabel.pack()
frame.pack()

window.after(50, take_picture)

window.mainloop()
