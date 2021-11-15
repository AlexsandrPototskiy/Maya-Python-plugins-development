cmds.file(new=True,force=True)

display_radius = 5
base_distance = 15

suffix = "_JNT"
palm_name = "palm"
fingers_names = ["thumb", "index", "middle", "ring", "pinky"]


def create_palm(palm_name, fingers_names):
	
	cmds.select(clear=True)
	
	#create base palm joint
	base_joint = cmds.joint(name = palm_name + suffix, radius = display_radius)
	
	# create base fingers
	for finger in fingers_names:
		cmds.select(clear=True)
		cmds.select(base_joint)
		cmds.joint(name = finger + suffix, radius = display_radius, p = (0, base_distance, 0))
	

create_palm(palm_name, fingers_names)
