offset_between = 100

suffix = "_JNT"


def create_palm(fingers_amount, falangs_amount, base_distance, display_radius, falang_distance):
	
	selection = cmds.ls(selection = True)
	
	if len(selection) < 1:
		base_joint = cmds.joint(radius = display_radius)
	else:
		base_joint = selection[0]
		print("attaching to selected")
	
	joints = []
	
	joints.append(base_joint)
	
	offset = offset_between / 2
 	distance = offset_between / len(fingers_names)
	current_offset = offset
	
	# create base fingers
	for finger in range(0, fingers_amount):
		
		cmds.select(clear=True)
		cmds.select(base_joint)
		
		finger_bones = []
		
		j = cmds.joint(radius = display_radius)
		cmds.setAttr(str(j)+'.translate',current_offset, 0, -base_distance)
		
		finger_bones.append(j)
		
		# create falangs
		for i in range(0, falangs_amount):
			f = cmds.joint(radius = display_radius)
			cmds.setAttr(str(f)+'.translate', 0, 0, -falang_distance)
			
			finger_bones.append(f)
		
		joints.append(finger_bones)
					
		current_offset -= distance
	
	cmds.select(clear=True)
	return joints


#UI
class HandBonesCreator():
	
	def __init__(self):
		
		self.joints = []
		
		win = cmds.window(title='Hand Bones Creator', widthHeight = (300,200), sizeable = False, toolbox = True)
		column = cmds.columnLayout()
		
		#fingers layout
		self.fingers_amount = 5
		cmds.rowLayout(p = column, nc = 3)
		cmds.text(label="Fingers:")
		self.fingers_slider = cmds.intSlider(step = 1, w = 200, value = self.fingers_amount, min = 2, max = 10, dc = self.__change_fingers)
		self.finger_text = cmds.text(w = 25, label = str(self.fingers_amount))
		
		# bones layout
		self.bones_amount = 3
		cmds.rowLayout(p = column, nc = 3)
		cmds.text(label="Bones:  ")
		self.bones_slider = cmds.intSlider(step = 1, w = 200, value = self.bones_amount, min = 1, max = 10, dc = self.__change_bones)
		self.bones_text = cmds.text(w = 25, label = str(self.bones_amount))
		
		cmds.rowLayout(p = column, nc = 1)
		cmds.button(label="Create Bones", w = 295, c = self.__create_rig)
		
		#distance layout
		self.palm_lengh = 35
		cmds.rowLayout(p = column, nc = 3)
		cmds.text(label="Palm Lengh:")
		self.palm_lengh_slider = cmds.floatSlider(w = 190, value = self.palm_lengh, min = 0.01, max = 80, dc = self.__update_bones_distance)
		self.palm_lengh_text = cmds.text(w = 35, label = str(self.palm_lengh))
		
		#falang distance
		self.falang_distance = 20
		cmds.rowLayout(p = column, nc = 3)
		cmds.text(label="Falang Distance:")
		self.falang_distance_slider = cmds.floatSlider(w = 150, value = self.falang_distance, min = 0.01, max = 80, dc = self.__update_falang_distance)
		self.falang_distance_text = cmds.text(w = 35, label = str(self.falang_distance))
		
		#radius
		self.radius = 5
		cmds.rowLayout(p = column, nc = 3)
		cmds.text(label="Display radius:")
		self.radius_slider = cmds.floatSlider(w = 190, value = self.radius, min = 0.01, max = 80, dc = self.__update_radius)
		self.radius_text = cmds.text(w = 35, label = str(self.radius))
		
		cmds.showWindow(win)
	
	def __change_fingers(self, *args):
		value = cmds.intSlider(self.fingers_slider, q = True, v = True)
		cmds.text(self.finger_text, edit = True, label = str(value))
		self.fingers_amount = value
		
	def __change_bones(self, *args):
		value = cmds.intSlider(self.bones_slider, q = True, v = True)
		cmds.text(self.bones_text, edit = True, label = str(value))
		self.bones_amount = value
	
	def __create_rig(self, *args):
		self.joints = create_palm(self.fingers_amount, self.bones_amount, self.palm_lengh, self.radius, self.falang_distance)
		print(self.joints)
		print('creating rig: fingers {0}. bones {1}'.format(self.fingers_amount, self.bones_amount))
	
	def __update_bones_distance(self, *args):
		value = cmds.floatSlider(self.palm_lengh_slider, q = True, v = True)
		cmds.text(self.palm_lengh_text, edit = True, label = '% 6.2f' % value)
		self.palm_lengh = value
		
		if len(self.joints) < 1:
			return
			
		for i in range(1, len(self.joints)):
			fingers = self.joints[i]
			x = cmds.getAttr(str(fingers[0])+'.translateX')
			y = cmds.getAttr(str(fingers[0])+'.translateY')
			cmds.setAttr(str(fingers[0])+'.translate',x, y, -self.palm_lengh)
			
	def __update_falang_distance(self, *args):
		value = cmds.floatSlider(self.falang_distance_slider, q = True, v = True)
		cmds.text(self.falang_distance_text, edit = True, label = '% 6.2f' % value)
		self.falang_distance = value
		
		if len(self.joints) < 1:
			return
				
		for i in range(1, len(self.joints)):
			fingers = self.joints[i]
			for j in range(1,len(fingers)):
				x = cmds.getAttr(str(fingers[j])+'.translateX')
				y = cmds.getAttr(str(fingers[j])+'.translateY')
				cmds.setAttr(str(fingers[j])+'.translate',x, y, -self.falang_distance)
				
				
	def __update_radius(self, *args):
		value = cmds.floatSlider(self.radius_slider, q = True, v = True)
		cmds.text(self.radius_text, edit = True, label = '% 6.2f' % value)
		self.radius = value
		
		if len(self.joints) < 1:
			return
		
		cmds.setAttr(str(self.joints[0])+'.radius', self.radius)
		for i in range(1, len(self.joints)):
			fingers = self.joints[i]
			for f in fingers:
				cmds.setAttr(str(f)+'.radius', self.radius)
	
		
HandBonesCreator()


