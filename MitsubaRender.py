import sys
import os
import time

import mitsuba
from mitsuba.core import *
from mitsuba.render import *
import multiprocessing
import abc


class MitsubaBatchRender():

    def __init__(self):
        self.scene = None
        self.setLogger()
        self.setScheduler()
        self.queue = RenderQueue()
        pass

    def setLogger(self):
        logger = mitsuba.core.Thread.getThread().getLogger()
        logger.setLogLevel(EWarn)  # EWarn, EError, EInfo, EDebug,

    def setScheduler(self):
        scheduler = Scheduler.getInstance()
        for i in range(0, multiprocessing.cpu_count() / 3):  # half power
            scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
        scheduler.start()

    def loadScene(self, fnameXML, addPath='./'):
        # load .xml
        fileResolver = Thread.getThread().getFileResolver()
        fileResolver.appendPath(addPath)
        print('Loading Scene')
        self.scene = SceneHandler.loadScene(fileResolver.resolve(fnameXML))
        print('Scene Loaded')

    def render(self, scene):
        print('starting RenderJob')
        job = RenderJob('myRenderJob', scene, self.queue)  # shouldn't use sceneResID
        job.start()
        self.queue.waitLeft(0)
        self.queue.join()

    # Function to add the range sensor to the scene
    @abc.abstractmethod
    def modifyScene(self, scene, paras):
        # newScene = scene
        newScene = Scene(scene)
        newScene.setDestinationFile(destination)
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
    mbr = MitsubaBatchRender()
    mbr.loadScene("/home-local2/jizha16.extra.nobkp/data/3Dmodels/render_models_with_ldr2hdr/bunny.xml")
    for i in range(0, 3):
        destination = 'scene_' + str(i)
        print(destination)
        newScene = mbr.modifyScene(newScene, i)
        mbr.render(newScene)


if __name__ == '__main__':
    main()
