import maya.cmds as cmds

# patterns loaded from Json
match_obj = ["Intern", "Break", "Apple"]

# get current scene objects
current_scene_objects = cmds.ls(geometry=True)

# shape_suffix to remove from shape node
shape_suffix = "Shape"

# current geometry list
current_geometry = []

# removing suffix
for scene_object in current_scene_objects:
	current_geometry.append(scene_object.replace(shape_suffix, ''))

print current_geometry
