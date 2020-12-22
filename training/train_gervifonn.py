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

from sklearn.metrics import classification_report
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.utils import Sequence
from keras.utils import to_categorical
from keras.preprocessing.image import load_img
from imutils import paths
import numpy as np
from scipy import ndimage
import random
import os
import sys
from keras.applications import DenseNet121
import tensorflow as tf

gpu = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpu[0], True)

batchsize = 2
numepochs = 48
imgsize = 224
factor = 8


class gervifonntrainingdatagenerator(Sequence):
    def __init__(self, musicfolder, bgfolder, mode):
        self.mode = mode
        if self.mode == 'train':
            self.factor = factor
        else:
            self.factor = 1
        imagePaths = list(paths.list_images(musicfolder))
        self.data = []
        self.labels = []
        self.classes = dict()
        self.bgs = []
        self.names = []
        for imagePath in imagePaths:
            if imagePath.endswith('cover.png'):
                label = os.path.sep.join(imagePath.split(os.path.sep)[-3:-1])
                if self.mode == 'train':
                    image = load_img(imagePath, target_size=(imgsize, imgsize))
                    image = np.asarray(image)
                    self.data.append(image)
                if label not in self.classes:
                    self.classes[label] = len(self.classes)
                    self.names.append(label)
                if self.mode == 'train':
                    self.labels.append(self.classes[label])
        for imagePath in imagePaths:
            if (not imagePath.endswith('cover.png')) and ('gervifonn' in imagePath):
                label = os.path.sep.join(imagePath.split(os.path.sep)[-4:-2])
                if label in self.classes:
                    image = load_img(imagePath, target_size=(imgsize, imgsize))
                    image = np.asarray(image)
                    self.data.append(image)
                    self.labels.append(self.classes[label])
        if self.mode == 'train':
            imagePaths = list(paths.list_images(bgfolder))
            for imagePath in imagePaths:
                image = load_img(imagePath, target_size=(imgsize, imgsize))
                image = np.asarray(image)
                self.bgs.append(image)
        self.data = np.array(self.data, dtype="uint8")
        self.numclasses = len(self.classes)
        self.labels = to_categorical(self.labels)
        self.indexes = np.arange(len(self.data)*self.factor)
        if self.mode == 'train':
            np.random.shuffle(self.indexes)
        self.datagen = ImageDataGenerator()

    def __len__(self):
        return int(np.floor(len(self.data)*self.factor / batchsize))

    def __getitem__(self, index):
        return self.__getbatch__(index, batchsize)

    def __getbatch__(self, index, bs):
        indexes = self.indexes[index * bs:(index + 1) * bs]
        batch_x = []
        batch_y = []
        for ind in indexes:
            batch_y.append(self.labels[ind//self.factor])
            image = np.copy(self.data[ind//self.factor])
            if self.mode == 'train':
                if random.random() < 0.9:
                    bg = np.copy(random.choice(self.bgs))
                    scalefact = 0.8 + (0.2*random.random())
                    image = ndimage.zoom(image, (scalefact, scalefact, 1))
                    scaledsize = image.shape[0]
                    offs = (imgsize-scaledsize)//2
                    bg[offs:offs+scaledsize, offs:offs+scaledsize, :] = bg[offs:offs+scaledsize, offs:offs+scaledsize, :]*0.2+0.8*image
                    image = bg
                image[:, :, 0] = (0.7+(0.3*random.random()))*image[:, :, 0]
                image[:, :, 1] = (0.7+(0.3*random.random()))*image[:, :, 1]
                image[:, :, 2] = (0.7+(0.3*random.random()))*image[:, :, 2]
                if random.random() < 0.3:
                    bg = np.copy(random.choice(self.bgs))
                    bg = self.datagen.apply_transform(x=bg,
                        transform_parameters={"theta": -20+(40*random.random()),
                            "tx": (imgsize*((random.random()-0.5)*0.1)),
                            "ty": (imgsize*((random.random()-0.5)*0.1)),
                            "shar": -20+(40*random.random()),
                            "zx": min(1, 0.5+random.random()),
                            "zy": min(1, 0.5+random.random())})
                    image[:, :, :] = 0.8*image[:, :, :]+0.2*bg[:, :, :]
                image = self.datagen.apply_transform(x=image,
                    transform_parameters={"theta": -20+(40*random.random()),
                        "tx": (imgsize*((random.random()-0.5)*0.1)),
                        "ty": (imgsize*((random.random()-0.5)*0.1)),
                        "shar": -20+(40*random.random()),
                        "zx": min(1, 0.5+random.random()),
                        "zy": min(1, 0.5+random.random())})
                if random.random() < 0.3:
                    bg = np.copy(random.choice(self.bgs))
                    bg = self.datagen.apply_transform(x=bg,
                        transform_parameters={"theta": -20+(40*random.random()),
                            "tx": (imgsize*((random.random()-0.5)*0.1)),
                            "ty":  (imgsize*((random.random()-0.5)*0.1)),
                            "shar": -20+(40*random.random()),
                            "zx": min(1, 0.5+random.random()),
                            "zy": min(1, 0.5+random.random())})
                    image[:, :, :] = 0.8*image[:, :, :]+0.2*bg[:, :, :]
                if random.random() < 0.3:
                    bg = np.copy(random.choice(self.data))
                    bg = self.datagen.apply_transform(x=bg,
                        transform_parameters={"theta": -20+(40*random.random()),
                            "tx": (imgsize*((random.random()-0.5)*0.1)),
                            "ty": (imgsize*((random.random()-0.5)*0.1)),
                            "shar": -20+(40*random.random()),
                            "zx": min(1, 0.5+random.random()),
                            "zy": min(1, 0.5+random.random())})
                    image[:, :, :] = 0.8*image[:, :, :]+0.2*bg[:, :, :]
            batch_x.append(image)
        return np.array(batch_x), np.array(batch_y)

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.data)*self.factor)
        np.random.shuffle(self.indexes)


if __name__ == "__main__":
    musicfolder = sys.argv[1]
    bgfolder = sys.argv[2]
    generator = gervifonntrainingdatagenerator(musicfolder, bgfolder, 'train')
    valgenerator = gervifonntrainingdatagenerator(musicfolder, bgfolder, 'val')
    model = DenseNet121(input_shape=(imgsize, imgsize, 3), weights=None, classes=generator.numclasses)
    opt = Adam()
    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
    H = model.fit_generator(
        generator, validation_data=valgenerator,
        steps_per_epoch=len(generator.data)*generator.factor//batchsize,
        validation_steps=len(valgenerator.data)*generator.factor//batchsize,
        epochs=numepochs)
    model.save("gervifonn.model")
    f = open("labels.txt", "w")
    for key in generator.classes.keys():
        f.write("{} {}\n".format(generator.classes[key], key))
    f.close()
    generator.on_epoch_end()
    batch_x, batch_y = generator.__getbatch__(0, len(generator.data)*min(generator.factor, 10))
    predIdxs = model.predict(batch_x)
    predIdxs = np.argmax(predIdxs, axis=1)
    print(classification_report(np.argmax(batch_y, axis=1),
                                predIdxs,
                                labels=range(len(generator.data)),
                                target_names=generator.names))
