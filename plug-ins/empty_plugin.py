import maya.cmds as cmds
import maya.api.OpenMaya as om


# use new API 2.0
def maya_useNewAPI():
    pass


# initialize current plugin
def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    om.MFnPlugin(plugin, vendor, version)

    print("Hello Maya from empty plugin")


# uninilialize current plugin
def uninitializePlugin(plugin):
    print("Hello Node uninitializePlugin")


# just for development to speed up development process
if __name__ == "__main__":
    plugin_name = "empty_plugin.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
