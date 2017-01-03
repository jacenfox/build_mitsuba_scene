==============
Render
==============
Make and render mitsuba scenes.
You may need to install mitsuba, and source the setpath.sh. Same as python.

Coordinates:
<pre>
Blender:
^z    ^	y  
|    /  
|  /  
|/  
-----------> x  
Mitsuba:
^y    ^	(-z)
|    /
|  / 	
|/
-----------> x
</pre>
Our envmap input should be:  
<pre>
zenith    zenith    zenith  
|-----------------------|+Y 
|	-X	-Z		+X		|		west  
|	image in latlong	|+Z		west  
|		south			|		west  
|-----------------------|-Y  
Nadir		Nadir		Nadir

Mitsuba envmap coordiantes, used to warp to sphere
|-----------------------|+Y 
|	+X	+Z		-X		|
|						|-Z
|						|
|-----------------------|-Y
TODO:update this
They may warp in different way, neet to rotate emitter <rotate angle="180" y="1"/></transform>
</pre>

--------------
Usage:
--------------
1. Model scene in Blender  
	* export as mitsuba scene file (need mitsuba add-ons for Blender)  
	* save as *scene*.xml  

    All the scene parameters are in *scene*.xml  
	
2. Generate new mitsuba scene files:   
	use the mapping and condition file:  
		`python makeScenes.py *scene*.xml *mapping*.txt *conditions*.txt *PATH_out_xmls*`  

	or directly change the parameters in *scene*.xml file.
	
	this will generate a bunch of scenes with the condition file, very useful for rendering with different parameters.  
	*PATH_out_xmls* contains the new scene .xml file for mitsuba render.  
	 
3. Render the scene:  
		`mitsuba *outputScene* -o ldr.png`  

    or use the batch render:  
		`python batchRender.py *PATH_out_xmls* *PATH_output_render_result*`  



--------------
SAMPLE CONDITION FILE
--------------
Example:
```
	imageName	lightFile	variable2
	BumpySphere_HDR		/gel/usr/hdr.hdr	value	
	BumpySphere_LDR		/gel/usr/hdrTmo.hdr	value
	%BumpySphere_AkyuzEO	AkyuzEO.hdr	value
```
* Notes
	* each row corresponds a new scene
	* first row are variables, see also mapping file
	* imageName is name of the new scene .xml file, also the rendered image
	* first column is always `imageName`, other cols are the variables in mapping file
	* seperate each column with `tab` not `space`, `\t` in matlab
	* use `%` to comment a line

--------------
SAMPLE MAPPING FILE
--------------
Format:  
	`node1:node2.attribute1|attribute2|attribute3 = value1|value2|(variable_in_condition_file)`  
Example
```
	scene:sensor:film.name|type = film|ldrfilm
	scene:sensor:film:boolean.name|value = banner|false
	% tricky to hide mitsuba label
	scene:sensor:film:string.name|value = label[10,10]|'labeltag'
	scene:sensor:film:string.name|value = labeltag|label[-100,-100]

	% emitter
	scene:emitter.type = 'envmap'
	% require sensor looks at +z, south
	scene:emitter:transform:matrix.value = 1 0 0 0, 0 1 0 0, 0 0 1 0, 0 0 0 1
	scene:emitter:transform:rotate.angle|y = 0|1
	% rotate, flip, the envmap
	% prefer without rotation
	%	scene:emitter:transform:matrix.value = -1 0 0 0, 0 1 0 0, 0 0 -1 0, 0 0 0 1
	%	scene:emitter:transform:rotate.angle|y = 0|1
	
		scene:emitter:string.name|value = filename|(lightFile)
```
* Notes
	* Use `%` to comment a line
	* Follow the order to create new nodes
		1. create parentNode  
		`scene:parentNode.attribute = 'parent'`
		2. create childNode for the parentNode  
		`scene:parentNode.childNode1.attribute|value = 'child'|'abc'`  
		cannot create childNode before parentNode exist
		
	* Add an `attribute` with `value`  
			`scene:node1:node2.attribute1 = 'value1'`  
			`scene:node1:node2.attribute1|attribute2 = 'value1'|'value2'`  

	* Modify `attribute1` while keep other attributes  
		`scene:node1:node2.attribute1|attribute2 = 'value1'|'value2'`  
		use the first attribute on the right hand to locate the node  

	* Use `variable` to generate multiple scenes  
		`scene:node1:node2.attribute1 = (variable)`  
		Mark the right-hand value with `'('` , `')'`  
		`value` of the `variable` should be specified in condition file
```
