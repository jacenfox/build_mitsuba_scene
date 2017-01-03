from astropy.io import ascii
from xml.dom import minidom
from multiprocessing import Pool
from os.path import join
import sys
import time
import re
import copy
# from makeScene import makeScene
# Issue:
# TODO: done, sensor label cannot hide
global xmldoc_global
global DEBUG
DEBUG = 0
NUM_COUNT = 0


def parseConditionFile(conditionFile):
    # ASCII txt file, each row will be a new scene
    data = ascii.read(conditionFile)
    nrows = len(data)

    commentPattern = '%'
    names = data.colnames
    values = []
    for i_row in range(0, nrows):
        rowdata = data[i_row]

        imageName = str(rowdata['imageName'])  # TODO
        if imageName.find(commentPattern) == 0:
            continue

        values.append(rowdata)

    return names, values


def parseMappingFile(mappingFile):
    lines = [line for line in open(mappingFile, "r").read().splitlines() if line]

    commentPattern = '%'
    elements = []
    attributes = []
    rights = []
    for line in lines:
        if line.strip()[0] == commentPattern:
            continue

        left, right = line.split('=')
        left = left.strip().translate(None, '\"\'')
        right = right.strip().translate(None, '\"\'')

        element, attribute = left.split('.')
        element = element.split(':')

        elements.append(element)
        attributes.append(attribute)
        rights.append(right)

    return elements, attributes, rights


def connectConditionMapping(condition_names, condition_values, mapping_elements, mapping_attributes, mapping_rights):
    NSCENE = len(condition_values)

    # find the (*) replace for each scene
    regexp = re.compile(r'\(*\)')

    # check if the mapping file contains condition variables
    rightsIndName = []
    for ind in range(0, len(mapping_rights)):
        right = mapping_rights[ind]
        # check if the right hand value has a condition
        hasCondition = bool(re.search(regexp, right))
        if hasCondition is True:

            name = right.translate(None, '()')

            # check if the condition name is defined in the condition file
            name = [name_tmp for name_tmp in condition_names if name_tmp in name]
            if len(name) == 1:
                name = name[0]
                rightsIndName.append([ind, name])
            else:
                print 'Condition file does not have: ' + name \
                    + ' check both condition and mapping file'

    SCENE_MAP = []
    for i_c in range(0, NSCENE):

        rights = copy.deepcopy(mapping_rights)

        # replace all the conditions
        for rightIndName in rightsIndName:
            ind, name = rightIndName
            repstr = '(' + name + ')'
            rights[ind] = rights[ind].replace(repstr, str(condition_values[i_c][name]))

        scene_map = [mapping_elements, mapping_attributes, rights]
        SCENE_MAP.append(scene_map)

    # SCENE_MAP contains how to change the scene for each condition
    return SCENE_MAP


def reachtoDocument(node):
    while not isinstance(node, xmldoc_global.__class__):
        node = node.parentNode
    return node


def reachtoLeafNode(rootNode, childNodeNames):
    # if childNodeNames[-1] exist, return this node,
    # if not, return its parent node
    # may exist more than one leaf nodes
    nodeType = ''
    for indName, childNodeName in enumerate(childNodeNames):

        if indName == 0:
            childNodes = rootNode.childNodes
        else:
            childNodes = []
            for indNodeParent, parentNode in enumerate(parentNodes):
                childNodes += parentNode.childNodes

        foundNodes = []
        for indNodeChild, childNode in enumerate(childNodes):
            if childNode.nodeName == childNodeName:
                foundNodes += [childNode]
                parentNodes = foundNodes

            elif len(foundNodes) == 0 and indNodeChild == len(childNodes) - 1:
                if indName == len(childNodeNames) - 1:
                    nodeType = 'parent'
                    return parentNodes, nodeType
                else:
                    print 'Couldn''t reach to the leaf Node, create mapping in order'
                    print childNodeNames
                    sys.exit('in reachtoLeafNode')   # err
    nodeType = 'leaf'
    return parentNodes, nodeType


def makeScene(xmldoc, elements, attribute, value):
    attributes = attribute.split('|')
    values = value.split('|')
    leafs, nodeType = reachtoLeafNode(xmldoc, elements)

    if nodeType == 'parent':
        addElement(leafs[-1], elements[-1], attributes, values)

    elif nodeType == 'leaf':
        indMOD = 0
        for ind_leaf, leaf in enumerate(leafs):  # enable to modify the existing node
            if len(attributes) > 1:
                if leaf.getAttribute(attributes[0]) == values[0]:
                    modifyElement(leaf, attributes, values)  # modify any match
                    indMOD += 1
                else:
                    pass
            else:
                modifyElement(leaf, attributes, values)  # modify all match

        if indMOD == 0 and len(leafs) > 1:  # no match and multi-leaf
            addElement(leaf.parentNode, elements[-1], attributes, values)

    # write back the xml
    return xmldoc


def modifyElement(elementItem, attribute_names, attribute_values):
    # Modify an existing element, with attributes and values
    assert type(attribute_names) == list
    assert type(attribute_values) == list
    try:
        for i_att in range(0, len(attribute_names)):
            elementItem.setAttribute(attribute_names[i_att], attribute_values[i_att])
    except:
        print 'cannot modify element '
        return ''
    return elementItem


def addElement(item_parent, element_name, attribute_names, attribute_values):
    # add one element, with attributes and values
    assert type(attribute_names) == list
    assert type(attribute_values) == list
    try:
        # create an Item
        item = reachtoDocument(item_parent).createElement(element_name)
        # item = minidom.Element(element_name)
        modifyElement(item, attribute_names, attribute_values)
        # for i_att in range(0, len(attribute_names)):
        #     item.setAttribute(attribute_names[i_att], attribute_values[i_att])
        item_parent.appendChild(item)  # append new child, return new child
    except:
        print 'cannot create element: '
        print element_name
        return ''  # error
    return item_parent


def makeScenes(params):
    try:
        outputXML, SCENE_MAP = params
        elements, attributes, values = SCENE_MAP

        print 'make scene: ' + outputXML
        xmldoc = xmldoc_global.cloneNode(True)

        for i_s in range(0, len(values)):
            try:
                xmldoc = makeScene(xmldoc, elements[i_s], attributes[i_s], values[i_s])
            except:
                print 'makeScene error\nelements: attributes: values'
                print elements[i_s]
                print attributes[i_s]
                print values[i_s]
                break
        # write back the xml
        xmldocHandle = open(outputXML, 'w')
        xmldoc.writexml(xmldocHandle)
        xmldocHandle.close()

    except:
        print 'make scene ' + outputXML + ' failed'

if __name__ == '__main__':
    if len(sys.argv) < 4:
        helpmsg = 'usage:\n\tpython makeScenes.py *original_scene*.xml '\
                  '*mappingFile*.txt ' '*conditionsFile*.txt ' \
                  'output_path -j4\n\t-j4 pool size 4'
        print helpmsg
        exit()

    inputXML = sys.argv[1]
    mappingFile = sys.argv[2]
    conditionFile = sys.argv[3]
    output_path = sys.argv[4]

    if len(sys.argv) == 6 and '-j' in sys.argv[5]:
        poolNum = int(sys.argv[5][2:])
        print 'using pool ' + str(poolNum)
    else:
        poolNum = 1

    xmldoc_global = minidom.parse(inputXML)
    try:
        names, values = parseConditionFile(conditionFile)
    except:
        print 'error: read ConditionFile: ' + conditionFile
        sys.exit()

    elements, attributes, rights = parseMappingFile(mappingFile)
    SCENE_MAPs = connectConditionMapping(names, values, elements, attributes, rights)

    outputXMLs = []
    for i in range(0, len(values)):
        outputXML = join(output_path, str(values[i]['imageName']) + '.xml')
        outputXMLs.append(outputXML)

    params = zip(outputXMLs, SCENE_MAPs)
    NUM_COUNT_ALL = len(params)

    _debug = DEBUG
    if _debug:
        makeScenes(params[0])
    else:
        pool = Pool(processes=poolNum)
        chunksize = 1
        rs = pool.map_async(makeScenes, params, chunksize)
        pool.close()

    while (True):
        if (rs.ready()):
            break
        remaining = rs._number_left
        print "\nWaiting for", remaining, "tasks to complete in %d\n" % (int(NUM_COUNT_ALL / chunksize + 1))
        time.sleep(5)

    print str(NUM_COUNT_ALL) + ' scenes done!'
