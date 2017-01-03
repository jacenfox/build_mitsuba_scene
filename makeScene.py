from xml.dom import minidom
import sys
# TODO: read general scene config file
# Issue: the emitter must be hemi, point do not have 'transform'


def makeScene(inputXML, outputXML, envmapFilename, matXval):
    print 'input scene: ' + inputXML + '\n\toutput scene: ' + outputXML
    xmlfname = inputXML
    xmlfname_new = outputXML
    xmldoc = minidom.parse(xmlfname)
    sceneItem = xmldoc.getElementsByTagName('scene')[0]
    setMitsuba_film(sceneItem)
    setMitsuba_integrator(sceneItem)
    # setMitsuba_config(sceneItem)
    # setMitsuba_emitter(sceneItem, envmapFilename, matXval)
    # write back the xml
    xmldocHandle = open(xmlfname_new, 'w')
    xmldoc.writexml(xmldocHandle)
    xmldocHandle.close()


def setMitsuba_integrator(sceneItem):
    integratorItem = sceneItem.getElementsByTagName('integrator')[0]
    integratorItem.setAttribute('type', 'path')
    string = minidom.Element('integer')
    string.setAttribute('name', 'maxDepth')
    string.setAttribute('value', '1')
    integratorItem.appendChild(string)

    pass


def setMitsuba_emitter(sceneItem, envmapFilename, matXval):
    # DO NOT CHANGE THESE PARAMETERS. THEY ARE ALL ADJUSTED FOR OUT SKY DATA.
    emitterItem = sceneItem.getElementsByTagName('emitter')[0]
    emitterItem.setAttribute('type', 'envmap')
    string = minidom.Element('string')
    string.setAttribute('name', 'filename')
    string.setAttribute('value', envmapFilename)
    emitterItem.appendChild(string)
    transfrom = emitterItem.getElementsByTagName('transform')[0]
    transfrom.setAttribute('name', 'toWorld')
    rotate = minidom.Element('rotate')
    rotate.setAttribute('y', '1')
    rotate.setAttribute('angle', '180')
    transfrom.appendChild(rotate)
    matrix = emitterItem.getElementsByTagName('matrix')[0]
    matrix.setAttribute('value', "{} 0 0 0\n 0 1 0 0\n 0 0 1 0\n 0 0 0 1".format(matXval))
    pass


def setMitsuba_config(sceneItem):
    setMitsuba_film(sceneItem)
    setMitsuba_sampler(sceneItem)


def setMitsuba_sampler(sceneItem):
    # setup scene:sensor:sampler
    sensorItem = sceneItem.getElementsByTagName('sampler')[0]
    samplerItem = sensorItem.getElementsByTagName('integer')[0]
    samplerItem.setAttribute('value', '20')


def setMitsuba_film(sceneItem):
    # setup scene:sensor:film
    sensorItem = sceneItem.getElementsByTagName('sensor')[0]
    filmItem = sensorItem.getElementsByTagName('film')[0]
    filmItem.setAttribute('type', 'ldrfilm')

    # booleans = filmItem.getElementsByTagName('boolean')
    # banner = [item for item in booleans if item.getAttribute(
    #     'name') == 'banner']
    # banner = banner[0]
    # banner.setAttribute('value', 'false')

    # strings = filmItem.getElementsByTagName('string')
    # label = [item for item in strings if item.getAttribute(
    #     'name') == 'label[10,10]']
    # label = label[0]
    # label.setAttribute('value', '')

    strings = filmItem.getElementsByTagName('string')
    itm = [item for item in strings if item.getAttribute(
        'name') == 'fileFormat']
    itm = itm[0]
    itm.setAttribute('value', 'jpg')

# def setMitsuba_integrator(sceneItem):
    # setup scene:integrator
    # integratorItem = sceneItem.getElementsByTagName('integrator')[0]
    # pass

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage:\n\tpython makeScene.py *original_scene*.xml *outputXML*.xml envmapFilename\n'
        exit()
    inputXML, outputXML, envmapFilename = sys.argv[1:4]
    matXval = 1
    if len(sys.argv) == 5:
        matXval = sys.argv[4]
    makeScene(inputXML, outputXML, envmapFilename, matXval)
