from MitsubaRender import MitsubaRender
from MitsubaConditionParser import ConditionParser
import argparse
import os
import time
import math

from mitsuba.core import *
from mitsuba.render import *


class MBR(MitsubaRender):

    def genNewScene(self, paras):
        cameraOrigin = map(float, paras['cameraOrigin'].split())
        cameraTarget = map(float, paras['cameraTarget'].split())
        emitterFname = paras['lightFile']
        emitterScale = float(paras['emitterScale'])
        emitterRotate = float(paras['emitterRotateY'])

        # will replace the whole sensor
        SENSOR_TYPE = 'spherical'
        FILM_TYPE = 'ldrfilm'  # hdr
        FILM_FILE_FORMAT = 'png'
        FILM_WIDTH = 512
        FILM_HEIGHT = 256
        SAMPLER_SAMPLE_COUNT = 64
        newScene = Scene(self.scene)

        pmgr = PluginManager.getInstance()
        sensor = pmgr.create({'type': SENSOR_TYPE,
                              'toWorld': Transform.lookAt(Point(cameraOrigin[0], cameraOrigin[1], cameraOrigin[2]),
                                                          Point(cameraTarget[0], cameraTarget[1], cameraTarget[2]), Vector(0, 1, 0)),
                              'film': {'type': FILM_TYPE, 'fileFormat': FILM_FILE_FORMAT,
                                       'width': FILM_WIDTH, 'height': FILM_HEIGHT, 'banner': False, 'componentFormat': 'float32',
                                       'rfilter': {'type': 'tent', 'radius': 1.0}},
                              'sampler': {'type': 'ldsampler', 'sampleCount': SAMPLER_SAMPLE_COUNT},
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


def main(inputXML, conditionFile, outputPath, poolNum, skipExist, scenePATH):
    mcp = ConditionParser()
    mcp.load(conditionFile)

    mbr = MBR(logLevel='error', cpus=3)

    start_time = time.time()
    mbr.loadScene(inputXML, scenePath=scenePATH)
    print('loading time: %.2f' % (time.time() - start_time))

    # render all
    start_time = time.time()
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    # TODO: loop all
    loggerFile = open('mitsuba_logger.log', 'a')
    conditions = mcp.conditions[0:15]

    for idx, condition in enumerate(conditions):
        # test if render exist
        destination = os.path.join(outputPath, condition['imageName'])
        if os.path.isfile(destination) is True and skipExist is True:
            continue

        # render
        try:
            newScene = mbr.genNewScene(condition)
            newScene.setDestinationFile(destination)
            mbr.render(newScene)
        except:
            loggerFile.write("%s\n" % destination)

        # estimate time
        n = 10
        if idx % n == n - 1:
            remaining = len(conditions) - idx
            time_elapsed = time.time() - start_time
            time_left = time_elapsed * (remaining / float(len(conditions) - remaining + 1))
            m_elapsed, s_elapsed = divmod(time_elapsed, 60)
            h_elapsed, m_elapsed = divmod(m_elapsed, 60)
            m_left, s_left = divmod(time_left, 60)
            h_left, m_left = divmod(m_left, 60)
            print("\nTask %d\\%d.\tTime start: %s\telapsed: %d:%02d:%02d\tleft: %d:%02d:%02d\n" %
                  (remaining, len(conditions), start_time_str,
                   h_elapsed, m_elapsed, s_elapsed, h_left, m_left, s_left))
    # done
    loggerFile.close()
    print('done with %d!' % len(conditions))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch render with mitsuba')

    parser.add_argument('-i', '--input', help="input xml", required=True)
    parser.add_argument('-c', '--conditionFile', help="*conditionFile*.txt", required=True)
    parser.add_argument('-o', '--output', help="output image path", required=True)
    parser.add_argument('-j', '--jobs', help="pool size", required=False)
    parser.add_argument('-s', '--skip', help="skip exist, -s 1 skip if .jpg[.png.pfm] exist", required=False)
    parser.add_argument('-a', '--addPATH', help="-a additional path for scene file", required=False)

    args = parser.parse_args()

    inputXML = args.input
    outputPath = args.output
    conditionFile = args.conditionFile

    if os.path.isdir(outputPath) is False:
        print('no such output dir: %s' % (outputPath))
        exit()

    poolNum = 1
    if args.jobs is not None:
        poolNum = int(args.jobs)
        print('using pool ' + str(poolNum))

    skipExist = False
    if args.skip is not None:
        skip01 = args.skip
        if skip01 == '1':
            skipExist = True
            print('will skip the existing image files.')
        elif skip01 == '0':
            skipExist = False
            print('will replace the existing image files.')
        else:
            print('-s only supports 0 or 1')
            exit()
    scenePATH = './'
    if args.addPATH is not None:
        scenePATH = args.addPATH

    main(inputXML, conditionFile, outputPath, poolNum, skipExist, scenePATH)
