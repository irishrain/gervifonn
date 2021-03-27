#!/usr/bin/env python3

# Copyright (C) 2020 Fabian Jansen

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

import RPi.GPIO as GPIO
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from mpd import MPDClient
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import tflite_runtime.interpreter as tflite
import asyncio
import snapcast.control
import os
import argparse


class album:
    def __init__(self, artist, albumtitle, imagefile, music, musicdirectory):
        self.artist = artist
        self.album = albumtitle
        self.imagefile = imagefile
        self.image = False
        if os.path.islink('/'.join((musicdirectory, artist, albumtitle, 'next'))):
            target = os.readlink('/'.join((musicdirectory, artist, albumtitle, 'next'))).split('/')[1]
            music[(artist, albumtitle)] = album(artist, target, imagefile, music, musicdirectory)

    def get_image(self):
        if not self.image:
            im = Image.open(self.imagefile)
            im.thumbnail((200, 200))
            self.image = ImageTk.PhotoImage(im)
        return self.image


class gervifonn:
    def __init__(self, musicdirectory, datadirectory, mpdserver, snapcastserver,  snapcastclient):
        self.musicdirectory = musicdirectory
        self.datadirectory = datadirectory
        self.state = 'default'
        self.initgpio()
        self.inittk()
        self.inittf()
        self.initcamera()
        self.artist = ''
        self.album = ''
        self.title = ''
        self.initmusic()
        self.initwidgets()
        self.initmpc(mpdserver)
        self.initsnapcast(snapcastserver, snapcastclient)
        self.showdefaultwindow()
        self.update(False)
        self.root.after(1000, self.update)
        self.root.mainloop()

    def initsnapcast(self, snapcastserver, snapcastclient):
        self.snaploop = asyncio.get_event_loop()
        self.snapserver = self.snaploop.run_until_complete(snapcast.control.create_server(self.snaploop,  snapcastserver))
        for client in self.snapserver.clients:
            if client.friendly_name == snapcastclient:
                self.snapclientid = client.identifier
        self.volupdate = 0

    def inittf(self):
        print('init tf')
        self.imgsize = 224
        self.interpreter = tflite.Interpreter(model_path=self.datadirectory+"/gervifonn.tflite")
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def initcamera(self):
        print('init camera')
        self.camera = PiCamera()
        self.camera.resolution = (self.imgsize, self.imgsize)

    def initmpc(self, server):
        print('init mpd')
        self.mpc = MPDClient()
        self.mpc.connect(server, 6600)
        self.timeupdate = 0

    def initmusic(self):
        print('init music')
        self.music = {}
        for row in open(self.datadirectory+"/labels.txt"):
            # unpack the row and update the labels dictionary
            (classID, label) = row.strip().split(maxsplit=1)
            tartist, talbum = label.strip().split('/')
            self.music[int(classID)] = album(tartist, talbum, '/'.join((self.musicdirectory, tartist, talbum, 'cover.png')), self.music,  self.musicdirectory)

    def inittk(self):
        print('init tk')
        self.root = Tk()
        self.style = ttk.Style()
        self.style.configure('TButton', background='white')
        self.style.configure('TLabel', background='white')
        self.style.configure('TFrame', background='white')
        self.root.attributes("-fullscreen", True)
        self.content = ttk.Frame(self.root)
        self.coverimage = ImageTk.PhotoImage(Image.new("RGB", (20, 20), "white"))

    def initwidgets(self):
        print('init widgets')
        self.covercanvas = Canvas(self.content, width=460, height=270, background="white")
        self.canvascoverimage = self.covercanvas.create_image(0, 0, image=self.coverimage, anchor='center')
        self.canvasartist = self.covercanvas.create_text(0, 0, text=self.artist, anchor='center', font='TkMenuFont', fill='black')
        self.canvasalbum = self.covercanvas.create_text(0, 0, text=self.album, anchor='center', font='TkMenuFont', fill='black')
        self.canvastitle = self.covercanvas.create_text(0, 0, text=self.title, anchor='center', font='TkMenuFont', fill='black')
        self.timescale = ttk.Scale(self.content, orient=HORIZONTAL, length=460, from_=0.0, to=100.0, command=self.settime)
        self.volumescale = ttk.Scale(self.content, orient=VERTICAL, length=285, from_=100.0, to=0.0, command=self.setvol)
        self.previmage = PhotoImage(file=self.datadirectory+'/prev.png')
        self.prevbutton = ttk.Button(self.content, image=self.previmage, command=self.leftbutton)
        self.prevbutton.image = self.previmage
        self.playpauseimage = PhotoImage(file=self.datadirectory+'/playpause.png')
        self.playpausebutton = ttk.Button(self.content, image=self.playpauseimage, command=self.middlebutton)
        self.playpausebutton.image = self.playpauseimage
        self.nextimage = PhotoImage(file=self.datadirectory+'/next.png')
        self.nextbutton = ttk.Button(self.content, image=self.nextimage, command=self.rightbutton)
        self.nextbutton.image = self.nextimage

        self.rotateimage = PhotoImage(file=self.datadirectory+'/rotate.png')
        self.volbutton = ttk.Button(self.content, text='Volume', image=self.rotateimage, compound='left', width=7)
        self.volbutton.image = self.rotateimage
        self.pushimage = PhotoImage(file=self.datadirectory+'/push.png')
        self.newbutton = ttk.Button(self.content, text='New CD', image=self.pushimage, compound='left', width=7, command=self.wheelclick)
        self.newbutton.image = self.pushimage
        self.backimage = PhotoImage(file=self.datadirectory+'/back.png')
        self.backbutton = ttk.Button(self.content, image=self.backimage, command=self.leftbutton)
        self.backbutton.image = self.backimage
        self.playimage = PhotoImage(file=self.datadirectory+'/play.png')
        self.playbutton = ttk.Button(self.content, image=self.playimage, command=self.middlebutton)
        self.playbutton.image = self.playimage
        self.wrongimage = PhotoImage(file=self.datadirectory+'/wrong.png')
        self.wrongbutton = ttk.Button(self.content, image=self.wrongimage, command=self.rightbutton)
        self.wrongbutton.image = self.wrongimage

        self.albumtree = ttk.Treeview(self.content, columns=('Album'), height=14, show="tree", selectmode="browse")
        self.albumtree.column("#0", width=int(460/2), stretch=NO)
        self.albumtree.column("Album", width=int(460/2), stretch=NO)
        _, talbums = zip(*sorted(self.music.items(), key=lambda x: (x[1].artist, x[1].album)))
        for talbum in talbums:
            self.albumtree.insert('', 'end', text=talbum.artist, values=(talbum.album, ))
        self.scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=self.albumtree.yview)
        self.albumtree.configure(yscrollcommand=self.scrollbar.set)
        self.selectbutton = ttk.Button(self.content, text='select', image=self.rotateimage, compound='left', width=7)
        self.selectbutton.image = self.rotateimage
        self.confirmbutton = ttk.Button(self.content, text='confirm', image=self.pushimage, compound='left', width=7, command=self.wheelclick)
        self.confirmbutton.image = self.pushimage
        self.content.grid(column=0, row=0)

    def showdefaultwindow(self):
        cw = 460
        ch = 270
        self.covercanvas['width'] = cw
        self.covercanvas['height'] = ch
        self.covercanvas.coords(self.canvascoverimage, cw/2, 100)
        self.covercanvas.coords(self.canvasartist, cw/2, ch*13/16)
        self.covercanvas.coords(self.canvasalbum, cw/2, ch*14/16)
        self.covercanvas.coords(self.canvastitle, cw/2, ch*15/16)
        self.covercanvas.itemconfigure(self.canvascoverimage, state='normal')
        self.covercanvas.itemconfigure(self.canvasartist, state='normal')
        self.covercanvas.itemconfigure(self.canvasalbum, state='normal')
        self.covercanvas.itemconfigure(self.canvastitle, state='normal')
        self.covercanvas.grid(column=0, row=0, columnspan=7, rowspan=3)
        self.timescale.grid(column=0, row=3, columnspan=7, sticky=(S))
        self.volumescale.grid(column=7, row=0, rowspan=4, sticky=(E))
        self.prevbutton.grid(column=0, row=4, sticky=(N, S, E, W))
        self.playpausebutton.grid(column=1, row=4, sticky=(N, S, E, W))
        self.nextbutton.grid(column=2, row=4, sticky=(N, S, E, W))
        self.volbutton.grid(column=4, row=4, columnspan=2, sticky=(N, S, E, W))
        self.newbutton.grid(column=6, row=4, columnspan=2, sticky=(N, S, E, W))

    def hidedefaultwindow(self):
        self.covercanvas.itemconfigure(self.canvascoverimage, state='hidden')
        self.covercanvas.itemconfigure(self.canvasartist, state='hidden')
        self.covercanvas.itemconfigure(self.canvasalbum, state='hidden')
        self.covercanvas.itemconfigure(self.canvastitle, state='hidden')
        self.covercanvas.grid_forget()
        self.timescale.grid_forget()
        self.volumescale.grid_forget()
        self.prevbutton.grid_forget()
        self.playpausebutton.grid_forget()
        self.nextbutton.grid_forget()
        self.volbutton.grid_forget()
        self.newbutton.grid_forget()

    def showvalidatewindow(self):
        cw = 475
        ch = 285
        self.covercanvas['width'] = cw
        self.covercanvas['height'] = ch
        self.covercanvas.coords(self.canvascoverimage, cw/2, 100)
        self.covercanvas.coords(self.canvasartist, cw/2, ch*14/16)
        self.covercanvas.coords(self.canvasalbum, cw/2, ch*15/16)
        self.covercanvas.itemconfigure(self.canvascoverimage, state='normal')
        self.covercanvas.itemconfigure(self.canvasartist, state='normal')
        self.covercanvas.itemconfigure(self.canvasalbum, state='normal')
        self.covercanvas.grid(column=0, row=0, columnspan=8, rowspan=3)
        self.backbutton.grid(column=0, row=4, sticky=(N, S, E, W))
        self.playbutton.grid(column=1, row=4, sticky=(N, S, E, W))
        self.wrongbutton.grid(column=2, row=4, sticky=(N, S, E, W))

    def hidevalidatewindow(self):
        self.covercanvas.itemconfigure(self.canvascoverimage, state='hidden')
        self.covercanvas.itemconfigure(self.canvasartist, state='hidden')
        self.covercanvas.itemconfigure(self.canvasalbum, state='hidden')
        self.covercanvas.grid_forget()

        self.backbutton.grid_forget()
        self.playbutton.grid_forget()
        self.wrongbutton.grid_forget()

    def showselectwindow(self):
        cid = self.albumtree.get_children()[0]
        self.albumtree.focus(cid)
        self.albumtree.selection_set(cid)
        self.albumtree.grid(column=0, row=0, columnspan=7, rowspan=3)
        self.scrollbar.grid(column=7, row=0, rowspan=4, sticky=(N, S, E))

        self.backbutton.grid(column=0, row=4, sticky=(N, S, E, W))

        self.selectbutton.grid(column=4, row=4, columnspan=2, sticky=(N, S, E, W))
        self.confirmbutton.grid(column=6, row=4, columnspan=2, sticky=(N, S, E, W))

    def hideselectwindow(self):
        self.albumtree.grid_forget()
        self.scrollbar.grid_forget()

        self.backbutton.grid_forget()

        self.selectbutton.grid_forget()
        self.confirmbutton.grid_forget()

    def settime(self, perc):
        status = self.mpc.status()
        if status['state'] in ['pause', 'play']:
            newtime = float(status['duration'])*float(perc)/100
            if self.timeupdate == 0:
                print('seek to', newtime)
                self.mpc.seekcur(newtime)
            else:
                self.timeupdate = 0

    def setvol(self, perc):
        if self.volupdate == 0:
            self.volume = float(perc)
            self.snaploop.run_until_complete(self.snapserver.client_volume(self.snapclientid, {'percent': self.volume, 'muted': False}))
        else:
            self.volupdate = 0

    def update(self, *args):
        status = self.mpc.status()
        if status['state'] in ['pause', 'play']:
            self.timeupdate = 1
            self.timescale.set(100*float(status['elapsed'])/float(status['duration']))
            song = self.mpc.currentsong()
            self.artist = song['artist']
            self.album = song['album']
            self.title = song['title']
            talbum = self.getalbum(self.artist, self.album)
            if talbum >= 0:
                self.coverimage = self.music[talbum].get_image()
            else:
                self.coverimage = ImageTk.PhotoImage(Image.new("RGB", (20, 20), "white"))
        else:
            self.timescale.set(0)
            self.artist = ''
            self.album = ''
            self.title = ''
            self.coverimage = ImageTk.PhotoImage(Image.new("RGB", (20, 20), "white"))
        self.volume = self.snaploop.run_until_complete(self.snapserver.client_status(self.snapclientid))['config']['volume']['percent']
        self.volupdate = 1
        self.volumescale.set(self.volume)
        if self.state == 'default':
            self.covercanvas.itemconfigure(self.canvascoverimage, image=self.coverimage)
            self.covercanvas.itemconfigure(self.canvasartist, text=self.artist)
            self.covercanvas.itemconfigure(self.canvasalbum, text=self.album)
            self.covercanvas.itemconfigure(self.canvastitle, text=self.title)
        if not (len(args) == 1 and args[0] is False):
            self.root.after(1000, self.update)

    def getalbum(self, artist, album):
        matches = [talbum for talbum in self.music if self.music[talbum].artist == artist and self.music[talbum].album == album]
        if len(matches) > 0:
            return matches[0]
        else:
            matches = [talbum for talbum in self.music if self.music[talbum].artist == 'Various' and self.music[talbum].album == album]
            if len(matches) > 0:
                return matches[0]
            else:
                return -1

    def initgpio(self):
        print('init gpio')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(26, GPIO.HIGH)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(6, GPIO.FALLING, callback=self.wheelcallback, bouncetime=200)
        GPIO.add_event_detect(19, GPIO.FALLING, callback=self.wheelclick, bouncetime=400)
        GPIO.add_event_detect(16, GPIO.FALLING, callback=self.rightbutton, bouncetime=400)
        GPIO.add_event_detect(20, GPIO.FALLING, callback=self.middlebutton, bouncetime=400)
        GPIO.add_event_detect(21, GPIO.FALLING, callback=self.leftbutton, bouncetime=400)

    def wheelcallback(self, *args):
        if GPIO.input(6) == 0:
            self.wheelturn(GPIO.input(13))

    def leftbutton(self, *args):
        print('left')
        if self.state == 'default':
            self.mpc.previous()
        elif self.state == 'validate':
            self.state = 'busy'
            self.hidevalidatewindow()
            self.showdefaultwindow()
            self.state = 'default'
        elif self.state == 'select':
            self.state = 'busy'
            self.hideselectwindow()
            self.showvalidatewindow()
            self.state = 'validate'

    def middlebutton(self, *args):
        print('middle')
        if self.state == 'default':
            self.mpc.pause()
        elif self.state == 'validate':
            self.state = 'busy'
            self.hidevalidatewindow()
            self.mpc.clear()
            artist = self.recognized.artist
            album = self.recognized.album
            self.mpc.searchadd("file", "{}/{}/".format(artist, album))
            while (artist, album) in self.music:
                nalbum = self.music[(artist, album)]
                artist = nalbum.artist
                album = nalbum.album
                self.mpc.searchadd("file", "{}/{}/".format(artist, album))
            self.mpc.play()
            filename = '/'.join((self.musicdirectory, self.recognized.artist, self.recognized.album, 'gervifonn', str(time.time())+'.png'))
            self.videoimage.save(filename)
            self.state = 'default'
            self.update()
            self.showdefaultwindow()

    def rightbutton(self, *args):
        print('right')
        if self.state == 'default':
            self.mpc.next()
        elif self.state == 'validate':
            self.state = 'busy'
            self.hidevalidatewindow()
            self.showselectwindow()
            self.state = 'select'

    def wheelclick(self, *args):
        print('click')
        if self.state == 'default':
            self.state = 'busy'
            self.hidedefaultwindow()
            rawCapture = PiRGBArray(self.camera)
            self.camera.capture(rawCapture, format="rgb")
            self.videoimage = Image.fromarray(rawCapture.array)
            self.capturedimage = self.videoimage.resize((200, 200))
            self.capturedimage = ImageTk.PhotoImage(self.capturedimage)
            self.covercanvas.itemconfigure(self.canvascoverimage, image=self.capturedimage)
            self.covercanvas.itemconfigure(self.canvasartist, text='Identifying CD,')
            self.covercanvas.itemconfigure(self.canvasalbum, text='please wait!')
            self.showvalidatewindow()

            videoframe = np.asarray(rawCapture.array[:self.imgsize, :self.imgsize, :], dtype=np.float32)
            videoframe = np.expand_dims(videoframe, axis=0)
            self.interpreter.set_tensor(self.input_details[0]['index'], videoframe)
            self.interpreter.invoke()
            preds = self.interpreter.get_tensor(self.output_details[0]['index'])
            scores = []
            for (i, pred) in enumerate(preds[0, :]):
                scores.append([self.music[i], pred])
            scores.sort(key=lambda tup: -tup[1])
            self.recognized = scores[0][0]
            self.covercanvas.itemconfigure(self.canvascoverimage, image=self.recognized.get_image())
            self.covercanvas.itemconfigure(self.canvasartist, text=self.recognized.artist)
            self.covercanvas.itemconfigure(self.canvasalbum, text=self.recognized.album)
            self.state = 'validate'
        elif self.state == 'select':
            self.state = 'busy'
            ciid = self.albumtree.focus()
            selected = self.albumtree.item(ciid)
            artist = selected['text']
            album = selected['values'][0]
            self.hideselectwindow()
            self.mpc.clear()
            self.mpc.searchadd("file", "{}/{}/".format(artist, album))
            while (artist, album) in self.music:
                nalbum = self.music[(artist, album)]
                artist = nalbum.artist
                album = nalbum.album
                self.mpc.searchadd("file", "{}/{}/".format(artist, album))
            self.mpc.play()
            filename = '/'.join((self.musicdirectory, artist, album, 'gervifonn', str(time.time())+'.png'))
            self.videoimage.save(filename)
            self.state = 'default'
            self.update(False)
            self.showdefaultwindow()

    def wheelturn(self, direct):
        if direct == 0:
            print('leftturn')
            if self.state == 'default':
                self.setvol(max(self.volume-5, 0))
            elif self.state == 'select':
                ciid = self.albumtree.focus()
                previd = self.albumtree.prev(ciid)
                if not previd == '':
                    self.albumtree.focus(previd)
                    self.albumtree.selection_set(previd)
                    self.albumtree.see(previd)
        else:
            print('rightturn')
            if self.state == 'default':
                self.setvol(min(self.volume+5, 100))
            elif self.state == 'select':
                ciid = self.albumtree.focus()
                nextid = self.albumtree.next(ciid)
                if not nextid == '':
                    self.albumtree.focus(nextid)
                    self.albumtree.selection_set(nextid)
                    self.albumtree.see(nextid)

    def __del__(self):
        self.mpc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gervifonn GUI')
    parser.add_argument('-m', '--musicfolder',  required=True,  help='Path to the music library')
    parser.add_argument('-n', '--mpdserver', required=True, help='Hostname of the MPD server')
    parser.add_argument('-s', '--snapcastserver', required=True, help='Hostname of the snapcast server')
    parser.add_argument('-c', '--snapcastclient', required=True, help='Name of the snapcast client')
    args=parser.parse_args()
    GF = gervifonn(args.musicfolder, os.path.dirname(__file__), args.mpdserver, args.snapcastserver,args.snapcastclient)
