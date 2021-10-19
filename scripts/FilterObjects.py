import pymel.core as pm
# get current scene objects
current_scene_objects = pm.ls(transforms=True)

ignorable_types = ["camera"]

filtred_objects = []

# filtering maya scene objects
for scene_object in current_scene_objects:
	first_relative = pm.listRelatives(scene_object, ad = True)[0]
	if pm.nodeType(first_relative, q=True) not in ignorable_types:
		filtred_objects.append(scene_object)
        
print(filtred_objects)