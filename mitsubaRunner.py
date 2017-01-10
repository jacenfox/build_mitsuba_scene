from MitsubaRender import MitsubaRender
from MitsubaConditionParser import ConditionParser


class MBR(MitsubaRender):

    def genNewScene(self, paras):
        cameraOrigin = paras['cameraOrigin']
        cameraTarget = paras['cameraTarget']
        emitterFname = paras['emitterFname']
        emitterScale = paras['emitterScale']
        emitterRotate = paras['emitterRotate']

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
    mcp = ConditionParser()
    mcp.load('/home-local/jizha16.extra.nobkp/data/3Dmodels/urban/condTest.txt')

    mbr = MBR()
    mbr.setLogger('EWarn')
    mbr.loadScene("/home-local2/jizha16.extra.nobkp/data/3Dmodels/render_models_with_ldr2hdr/bunny.xml")

    for condition in mcp.conditions[0:5:
        newScene = mbr.genNewScene(conditions)
        destination = 'scene_' + condition['imageName']
        newScene.setDestinationFile(destination)
        mbr.render(newScene)

if __name__ == '__main__':
    main()
