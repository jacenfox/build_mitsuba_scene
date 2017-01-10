from mitsuba.core import *
from mitsuba.render import Scene
from mitsuba.render import SceneHandler

from mitsuba.render import RenderQueue, RenderJob
import multiprocessing
print('start')

fileResolver = Thread.getThread().getFileResolver()
fileResolver.appendPath('scene_251')
# load scene to memory
scene = SceneHandler.loadScene(fileResolver.resolve("/home-local2/jizha16.extra.nobkp/data/3Dmodels/render_models_with_ldr2hdr/bunny.xml"))

pmgr = PluginManager.getInstance()

scheduler = Scheduler.getInstance()
for i in range(0, multiprocessing.cpu_count()):
    scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
scheduler.start()
sceneResID = scheduler.registerResource(scene)

queue = RenderQueue()
print('starting')
for i in range(2):
    # render different scenes
    destination = 'scene%02d' % i
    print(destination)
    newScene = Scene(scene)
    # sensor = pmgr.create({'type': 'spherical',
    #                       'toWorld': Transform.lookAt(Point(0, i, 1), Point(0, i, 0), Vector(0, 1, 0)),
    #                       'film': {'type': 'ldrfilm', 'width': 512, 'height': 256}
    #                       })
    # newScene.addChild(sensor)
    newScene.configure()
    newScene.initialize()
    print('rendering')
    newScene.setDestinationFile(destination)
    print('rendering job')
    job = RenderJob('test', newScene, queue, sceneResID)
    print('rendering start')
    job.start()
    print('rendering done')
    import time
    time.sleep(3)