from os import listdir
from os.path import isfile, join
from makeScene import *
inPath = 'xmls'
outPath = 'xmlsMask'
files = listdir(inPath)
# files = files[0:10]
inFiles = [join(inPath, f) for f in files if isfile(join(inPath, f))]
outFiles = [join(outPath, f) for f in files if isfile(join(inPath, f))]
print inFiles, outFiles
for i in range(len(inFiles)):
	makeScene(inFiles[i], outFiles[i], 'envmapFilename', 1)
	print i, inFiles[i]
# os.system("~/laval/ulaval/mycode/render/makeScene/modifyScenes.py")
