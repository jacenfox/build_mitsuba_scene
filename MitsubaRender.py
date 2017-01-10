import sys
import random
import os
import math
import time

import mitsuba
from mitsuba.core import *
from mitsuba.render import *
import multiprocessing

from os import listdir
from os.path import join


# Function to add the range sensor to the scene
def modifyScene(scene, i):
    # newScene = Scene(scene)
    newScene = scene
    pmgr = PluginManager.getInstance()
    sensor = pmgr.create({'type': 'spherical',
                          'toWorld': Transform.lookAt(Point(0, i * 5, 1), Point(0, i * 5, i * 5), Vector(0, 1, 0)),
                          'film': {'type': 'ldrfilm', 'fileFormat': 'png', 'width': 512, 'height': 256},
                          'sampler': {'type': 'ldsampler', 'sampleCount': 32},
                          })
    # newScene.addSensor(sensor)
    newScene.setSensor(sensor)
    fname_envmap = '/gel/usr/jizha16/laval/data/3Dmodels/render_models_with_ldr2hdr/140305/hdr.exr'

    emitter = pmgr.create({'type': "envmap",
                           "filename": fname_envmap,
                           "scale": 1.0,
                           "toWorld": Transform.rotate(Vector(0, 1, 0), 0.0)
                           })
    # emitter.configure()
    newScene.addChild('emitter', emitter)
    newScene.configure()
    newScene.initialize()  # init envmap BSphere

    # print newScene
    return newScene


def main():
    logger = mitsuba.core.Thread.getThread().getLogger()
    logger.setLogLevel(EWarn)  # EWarn, EError, EInfo, EDebug,

    scheduler = Scheduler.getInstance()
    for i in range(0, multiprocessing.cpu_count() / 3):  # half power
        scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
    scheduler.start()

    # load .xml
    fileResolver = Thread.getThread().getFileResolver()
    fileResolver.appendPath('additional_path')

    scene = SceneHandler.loadScene(fileResolver.resolve("/home-local2/jizha16.extra.nobkp/data/3Dmodels/render_models_with_ldr2hdr/bunny.xml"))
    # scene.initialize()

    # make new scenes, add to a queue
    queue = RenderQueue()
    for i in range(0, 3):
        destination = 'scene_' + str(i)
        print(destination)
        # copy the scene
        newScene = Scene(scene)
        newScene.setDestinationFile(destination)
        newScene = modifyScene(newScene, i)
        newScene.configure()

        # scene resource ID provide to avoid multiple copy, create job insert to queue
        print('starting RenderJob')
        job = RenderJob('myRenderJob' + str(i), newScene, queue)  # shouldn't use sceneResID
        job.start()
        print('queue waitLeft')
        queue.waitLeft(0)
        queue.join()


if __name__ == '__main__':
    main()
