import maya.cmds as cmds

# read external configuration file
def read_config_file():
	return ["Intern", "Break", "Apple"]

def validate_scene_objects():
	# reading configuration 
	configuration = read_config_file()
		
	# get current scene objects
	current_scene_objects = cmds.ls(geometry=True)
	
	# shape_suffix to remove from shape node
	shape_suffix = "Shape"
	
	# current geometry list
	filtred_objects = []
	
	# removing suffix
	for scene_object in current_scene_objects:
		filtred_objects.append(scene_object.replace(shape_suffix, ''))
	
	# validating
	validate(filtred_objects, configuration)


def validate(scene_objects, configuration):
	not_founded_objects = []
	
	for c in configuration:
		if c not in scene_objects:
			not_founded_objects.append(c)
	
	if len(not_founded_objects) > 0:
		print "Not Founded Objects in scene"
		for n in not_founded_objects:
			print n
			
			
validate_scene_objects()
