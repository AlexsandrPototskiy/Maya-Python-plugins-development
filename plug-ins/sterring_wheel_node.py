import maya.api.OpenMaya as om
from math import *

def maya_useNewAPI():
    pass


class SterringWheelNode(om.MPxNode):
    
    NAME = "sterring_wheel_node"
    ID = om.MTypeId(0x0007f7f9)
    
    rotation_attr = None
    min_attr = None
    max_attr = None
    wheel_angle_attr = None
    result_rotation_attr = None
    
    def __init__(self):
        super(SterringWheelNode, self).__init__()
        
    def compute(self, plug, data):
        if not plug == SterringWheelNode.result_rotation_attr:
            return
        
        minR = data.inputValue(self.min_attr).asFloat()
        maxR = data.inputValue(self.max_attr).asFloat()
        
        currentRotation = data.inputValue(self.rotation_attr).asFloat()
        
        s = copysign(1.0, currentRotation)
        
        max_angle = 360.0
                
        if currentRotation >= max_angle:
            currentRotation = max_angle
        
        if currentRotation <= -max_angle:
            currentRotation = -max_angle
        
        set_max = data.outputValue(self.rotation_attr)
        set_max.setFloat(currentRotation)
        
        t = fabs(currentRotation) / max_angle 
        
        #  linear interpolation: a + (b - a) * t
        rot = 0.0 + (maxR - 0.0) * t
        
        rot = rot * s
        
        output = data.outputValue(self.result_rotation_attr)
        output.setFloat(rot)
        
        data.setClean(plug)
    
    @classmethod
    def creator(cls):
        return SterringWheelNode()
    
    @classmethod
    def initializer(cls):
        numeric_fn = om.MFnNumericAttribute()
        
        cls.rotation_attr = numeric_fn.create("input_rotation", 
                                              "inrot", 
                                              om.MFnNumericData.kFloat,
                                              0.0)
        numeric_fn.keyable = True
        numeric_fn.readable = False
        
        cls.min_attr = numeric_fn.create("minAngle", 
                                         "minA", 
                                         om.MFnNumericData.kFloat,
                                         -30.0)
        numeric_fn.keyable = True
        numeric_fn.readable = False
        
        cls.max_attr = numeric_fn.create("maxAngle", 
                                         "maxA", 
                                         om.MFnNumericData.kFloat,
                                         30.0)
        numeric_fn.keyable = True
        numeric_fn.readable = False        
        
        cls.result_rotation_attr = numeric_fn.create("wheelrotation",
                                                     "wheelrot",
                                                     om.MFnNumericData.kFloat,
                                                     0.0)
        numeric_fn.writable = False
        
        cls.addAttribute(cls.rotation_attr)
        cls.addAttribute(cls.min_attr)
        cls.addAttribute(cls.max_attr)
        cls.addAttribute(cls.result_rotation_attr)
        
        cls.attributeAffects(cls.rotation_attr, cls.result_rotation_attr)
        cls.attributeAffects(cls.min_attr, cls.result_rotation_attr)
        cls.attributeAffects(cls.max_attr, cls.result_rotation_attr)
   

def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    
    plugin_fn.registerNode(SterringWheelNode.NAME, SterringWheelNode.ID,
                           SterringWheelNode.creator, SterringWheelNode.initializer,
                           om.MPxNode.kDependNode)
    
    print("Init Sterring Wheel Node")


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    plugin_fn.deregisterNode(SterringWheelNode.ID)
    print("Uninit Sterring Wheel Node")
