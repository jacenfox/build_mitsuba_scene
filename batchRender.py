import os
import argparse
import time
import math
from os import listdir
from multiprocessing import Pool
from os.path import isfile, isdir, join

global DEBUG
global outputformat
DEBUG = 0
outputformat = 'anyFormat'


def parseRenderCmds(PATH_xml, PATH_png, skipExist, mitsuba_arg):
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
        renderCmds.append("mitsuba -q " + mitsuba_arg + ' ' + xmlfullfile + " -o " + outfullfile)
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
    # if len(sys.argv) < 3:
    #     printHelp()
    #     exit()

    parser = argparse.ArgumentParser(description='Batch render with mitsuba')

    parser.add_argument('-i', '--input', help="input xml path", required=True)
    parser.add_argument('-o', '--output', help="output image path", required=True)
    parser.add_argument('-j', '--jobs', help="pool size", required=False)
    parser.add_argument('-s', '--skip', help="skip exist, -sjpg[png,pfm] skip if .jpg[.png.pfm] exist", required=False)
    parser.add_argument('-m', '--mitsuba_arg', help="mitsuba args, '-p 2 -a scene_path'", required=False)

    args = parser.parse_args()

    PATH_xml = args.input
    PATH_img = args.output

    if isdir(PATH_img) is False:
        print('no such output dir: %s' % (PATH_img))
        exit()

    poolNum = 1
    if args.jobs is not None:
        poolNum = int(args.jobs)
        print('using pool ' + str(poolNum))

    skipExist = False
    if args.skip is not None:
        outputformat = args.skip
        skipExist = True
        print('will skip the existing .' + outputformat)

    mitsuba_arg = ''
    if args.mitsuba_arg is not None:
        mitsuba_arg = args.mitsuba_arg

    renderCmds = parseRenderCmds(PATH_xml, PATH_img, skipExist, mitsuba_arg)

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

    start_time = time.time()
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    while (True):
        if (rs.ready()):
            break
        remaining = rs._number_left
        time_elapsed = time.time() - start_time
        time_left = time_elapsed * (remaining / float(math.ceil(NUM_COUNT_ALL / float(chunksize)) - remaining + 1))
        m_elapsed, s_elapsed = divmod(time_elapsed, 60)
        h_elapsed, m_elapsed = divmod(m_elapsed, 60)
        m_left, s_left = divmod(time_left, 60)
        h_left, m_left = divmod(m_left, 60)

        print("Task %d\\%d.\tTime start: %s\telapsed: %d:%02d:%02d\tleft: %d:%02d:%02d\n" %
              (remaining * chunksize, int(NUM_COUNT_ALL + 1), start_time_str,
               h_elapsed, m_elapsed, s_elapsed, h_left, m_left, s_left))
        time.sleep(10)

    print(str(NUM_COUNT_ALL) + ' scenes done!')
