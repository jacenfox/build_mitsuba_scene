import os
import sys
import time
from os import listdir
from multiprocessing import Pool
from os.path import isfile, join

global DEBUG
global outputformat
DEBUG = 0
outputformat = 'anyFormat'


def parseRenderCmds(PATH_xml, PATH_png, skipExist):
    # PATH_xml = './'
    # PATH_png = '/gel/usr/jizha16/laval/results/'
    xmlfiles = [f for f in listdir(PATH_xml) if isfile(join(PATH_xml, f)) and f.endswith('.xml')]
    # xmlfiles = sorted(xmlfiles)
    renderCmds = []
    for xmlfile in xmlfiles:
        xmlfullfile = join(PATH_xml, xmlfile)
        outfullfile = join(PATH_png, xmlfile)
        outfullfile = outfullfile.replace('.xml', '.' + outputformat)  # does not matter
        if isfile(outfullfile) is True and skipExist is True:
            print('skip ' + outfullfile)
            continue
        renderCmds.append("mitsuba -q -p 2 " + xmlfullfile + " -o " + outfullfile)
    return renderCmds


def render(params):
    renderCmd = params
    try:
        print('rendering: ' + renderCmd)
        os.system(renderCmd)
    except:
        print('render failed: ' + renderCmd)


def printHelp():
    print('usage:\n\tpython batchRender.py *inputXMLs_path*.xml *outputImg_path* '
          '-j4 [-sjpg]\n\t-j4 pool size 4\n\t-sjpg[png] skip if .jpg[.png] exist')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        printHelp()
        exit()
    PATH_xml = sys.argv[1]
    PATH_img = sys.argv[2]
    poolNum = 1
    # print sys.argv, first one is the name of this script
    if len(sys.argv) >= 4 and '-j' in sys.argv[3]:
        poolNum = int(sys.argv[3][2:])
        print('using pool ' + str(poolNum))

    skipExist = False
    if len(sys.argv) >= 5 and '-s' in sys.argv[4]:
        outputformat = sys.argv[4][2:]
        skipExist = True
        print('will skip the existing .' + outputformat)

    renderCmds = parseRenderCmds(PATH_xml, PATH_img, skipExist)

    params = renderCmds
    NUM_COUNT_ALL = len(params)
    print('wait')
    time.sleep(5)
    start_time = time.time()
    _debug = DEBUG
    if _debug:
        render(params[0])
    else:
        pool = Pool(processes=poolNum)
        chunksize = 10
        rs = pool.map_async(render, params, chunksize)
        pool.close()

    while (True):
        if (rs.ready()):
            break
        remaining = rs._number_left
        time_elapsed = time.time() - start_time
        time_left = time_elapsed * (remaining / (int(NUM_COUNT_ALL) - remaining))
        print("Task %d\\%d.\tTime start %.2f\telapsed%.2f\tleft%.2f\n" %
              (remaining * chunksize, int(NUM_COUNT_ALL + 1), start_time, time_elapsed, time_left))
        time.sleep(10)

    print(str(NUM_COUNT_ALL) + ' scenes done!')
