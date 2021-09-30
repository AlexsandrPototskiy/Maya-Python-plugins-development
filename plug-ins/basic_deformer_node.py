# basic deformer node writing case study
# using Maya API1.0 since deformer node not implemented in API2.0
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import maya.cmds as cmds


class BasicDeformerNode(mpx.MPxDeformerNode):
    
    TYPE_NAME = "basic_deformer_node"
    TYPE_ID = om.MTypeId(0x0007F7F7FC)
    
    def __init__(self):
        super(BasicDeformerNode, self).__init__()
        
    def deform(self, data_block, geo_iter, matrix, multi_index):
        envelop = data_block.inputValue(self.envelope).asFloat()
        
        if envelop == 0:
            return
        
        geo_iter.reset()
        while not geo_iter.isDone():
            if geo_iter.index() % 2 == 0:
                pt = geo_iter.position()
                pt.y += (100 * envelop)
                geo_iter.setPosition(pt)
            
            geo_iter.next()

    @classmethod
    def creator(cls):
        return BasicDeformerNode()
    
    @classmethod
    def initialize(cls):
        pass



# plugin initialization
def initializePlugin(plugin):
    print("Basic Deformer Node Intitialization")
    version = "0.0.1"
    vendor = "Alex3D"
    plugin_fn = mpx.MFnPlugin(plugin, vendor, version)  
    plugin_fn.registerNode(BasicDeformerNode.TYPE_NAME,
                           BasicDeformerNode.TYPE_ID,
                           BasicDeformerNode.creator,
                           BasicDeformerNode.initialize,
                           mpx.MPxNode.kDeformerNode)


# plugin uninitialization
def uninitializePlugin(plugin):
    print("Basic Deformer Node Untitialization")
    plugin_fn = mpx.MFnPlugin(plugin)
    plugin_fn.deregisterNode(BasicDeformerNode.TYPE_ID)
    

if __name__ == "__main__":
    # just development code for quick load and unload plugin
    # reloading scene and so on
    # not used in production
    
    # creation new file to get rid of dependencies for current plugin
    cmds.file(new=True, force=True)
    
    # load and then unload plugin
    plugin_name = "basic_deformer_node.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
    
    # load test scene, select nurbPlane1 and add basic_deformer_node to object
    cmds.evalDeferred('cmds.file("C:/Users/intel/Documents/maya/2019/basic_deformer_test.ma", open=True, force=True)')
    cmds.evalDeferred('cmds.select("nurbsPlane1"); cmds.deformer(type="{0}")'.format(BasicDeformerNode.TYPE_NAME))