import maya.api.OpenMaya as om


# tell Maya use API 2.0
def maya_useNewAPI():
    pass


class MultiplyNode(om.MPxNode):
    
    TYPE_NAME = "multiplynode"
    TYPE_ID = om.MTypeId(0x0007f7f8)
    
    multiplier_object = None
    multiplicant_object = None
    product_object = None
    
    def __init__(self):
        super(MultiplyNode, self).__init__()
        
    def compute(self, plug, data):
        if not plug == MultiplyNode.product_object: 
            return
        
        a = data.inputValue(MultiplyNode.multiplier_object).asInt()
        b = data.inputValue(MultiplyNode.multiplicant_object).asDouble()
        result = a * b
        product_data = data.outputValue(MultiplyNode.product_object)
        product_data.setDouble(result)
        
        data.setClean(plug)
    
    @classmethod
    def creator(cls):
        return MultiplyNode()
    
    @classmethod
    def initialize(cls):
        numberic_fn = om.MFnNumericAttribute()
        
        # create a value input
        cls.multiplier_object = numberic_fn.create("multiplier", "mul",
                                                   om.MFnNumericData.kInt, 2)
        numberic_fn.keyable = True # make atr appear in channel box and node editor
        numberic_fn.readable = False # disable output for this attr
        
        # create b value input
        cls.multiplicant_object = numberic_fn.create("multiplicant", "mulc", 
                                                     om.MFnNumericData.kDouble, 0.0)
        numberic_fn.keyable = True # make atr appear in channel box and node editor
        numberic_fn.readable = False # disable output for this attr
        
        # create result value output
        cls.product_object = numberic_fn.create("product", "prd", 
                                                om.MFnNumericData.kDouble, 0.0)
        numberic_fn.writable = False # make product read only
        
        # add attributes to node
        cls.addAttribute(cls.multiplier_object)
        cls.addAttribute(cls.multiplicant_object)
        cls.addAttribute(cls.product_object)
        
        # tell maya what attributes will affected if value will be changed
        cls.attributeAffects(cls.multiplier_object, cls.product_object)
        cls.attributeAffects(cls.multiplicant_object, cls.product_object)



# initialize plugin
def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerNode(MultiplyNode.TYPE_NAME, MultiplyNode.TYPE_ID, 
                               MultiplyNode.creator, MultiplyNode.initialize,
                               om.MPxNode.kDependNode)
    
        print("Math Plugin was inititalized")
    except:
        print("Fail To initialize Node {0}: with ID {1}".format(MultiplyNode.TYPE_NAME,
                                                                MultiplyNode.TYPE_ID))

    
# uninitialize plugin
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
        plugin_fn.deregisterNode(MultiplyNode.TYPE_ID)
        
        print("Math Plugin was uninititalized")
    except:
        print("Fail To uninitialize Node {0}: with ID {1}".format(MultiplyNode.TYPE_NAME,
                                                                  MultiplyNode.TYPE_ID))
