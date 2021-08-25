import tkinter as tk
#import cv2
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
