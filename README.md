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
Unity(Left handed):
^y    ^	z
|    /
|  / 	
|/
-----------> -x
Mitsuba(Right handed):
^y    ^	z
|    /
|  / 	
|/
-----------> -x
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
They may warp in different way, need to rotate emitter <rotate angle="180" y="1"/></transform>
</pre>

--------------
Usage:
--------------
1. Model scene in Blender
	* export as mitsuba scene file  
	* save as *scene*.xml  

    All the scene parameters are in *scene*.xml  
	
2. Generate new mitsuba scene files:   
	use the mapping and condition file:  
		`python makeScenes.py -i *scene*.xml -m *mapping*.txt -c *conditions*.txt -o *PATH_out_xmls*`  

	or directly change the parameters in *scene*.xml file.
	
	this will generate a bunch of scenes with the condition file, useful for rendering with different parameters.  
	*PATH_out_xmls* contains the new scene .xml file for mitsuba render.  
	 
3. Render the scene:  
		`mitsuba *outputScene* -o ldr.png`  

    or use the batch render:  
		`python batchRender.py -i *PATH_out_xmls* -o *PATH_output_render_result*`  

* Or render with MitsubaRender
	The scene file should be adjusted before rendering.
	todo with the new Demo.xml
For example,
``` 
	1. Integrator should be set up in the .xml
	<integrator type="volpath"> 
		<integer name="maxDepth" value="-1"/>
		<integer name="rrDepth" value="5"/>
		<boolean name="strictNormals" value="false"/>
	</integrator>
	<integrator type="direct"> 
		<integer name="shadingSamples" value="1"/>
		<boolean name="strictNormals" value="false"/>
	</integrator>
	
	2. Add an emitter node, or else, mitsuba API will create an "sky-sun" emitter
	<emitter type="spot">
	    <transform name="toWorld">
	      <lookat origin= "0, -1, 0" target="0, -2, 0"/></transform>
	<float name="samplingWeight" value="0.1"/></emitter>
	
	3. Remove envmap, if exist.

	4. The sensor, film and sampler will be overwritten
```
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
