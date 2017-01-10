import sys
import os
import time

import mitsuba
from mitsuba.core import *
from mitsuba.render import *
import multiprocessing
import abc


class MitsubaRender():

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
    def genNewScene(self, paras):
        cameraOrigin, cameraTarget, emitterFname, emitterScale, emitterRotate = paras

        newScene = Scene(self.scene)

        pmgr = PluginManager.getInstance()
        sensor = pmgr.create({'type': 'spherical',
                              'toWorld': Transform.lookAt(Point(cameraOrigin[0], cameraOrigin[0], cameraOrigin[2]),
                                                          Point(cameraTarget[0], cameraTarget[1], cameraTarget[2]), Vector(0, 1, 0)),
                              'film': {'type': 'ldrfilm', 'fileFormat': 'png', 'width': 512, 'height': 256},
                              'sampler': {'type': 'ldsampler', 'sampleCount': 32},
                              })
        newScene.setSensor(sensor)

        emitter = pmgr.create({'type': "envmap",
                               "filename": emitterFname,
                               "scale": float(emitterScale),
                               "toWorld": Transform.rotate(Vector(0, 1, 0), float(emitterRotate))
                               })
        # emitter.configure()
        newScene.addChild('emitter', emitter)
        newScene.configure()
        newScene.initialize()  # init envmap BSphere
        # print newScene
        return newScene


def main():
    mbr = MitsubaRender()
    mbr.loadScene("/home-local2/jizha16.extra.nobkp/data/3Dmodels/render_models_with_ldr2hdr/bunny.xml")
    for i in range(0, 3):
        cameraOrigin = [0, 1, 0]
        cameraTarget = [0, 1, 1]
        emitterFname = '/gel/usr/jizha16/laval/data/ldr2hdr/sunAligned256_2014/20140924174631.exr'
        emitterScale = 2
        emitterRotate = 0
        paras = (cameraOrigin, cameraTarget, emitterFname, emitterScale, emitterRotate)
        newScene = mbr.genNewScene(paras)
        destination = 'scene_' + str(i)
        newScene.setDestinationFile(destination)
        mbr.render(newScene)


if __name__ == '__main__':
    main()
