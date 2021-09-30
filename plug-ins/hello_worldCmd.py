import maya.cmds as cmds
import maya.api.OpenMaya as om


# use new API 2.0
def maya_useNewAPI():
    pass


# create new command
class HelloWorldCommand(om.MPxCommand):
    COMMAND_NAME = "HelloWorld"

    def __init__(self):
        super(HelloWorldCommand, self).__init__()

    def doIt(self, args):
        print("Hello World!")

    @classmethod
    def creator(cls):
        return HelloWorldCommand()


# initialize current plugin
def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerCommand(HelloWorldCommand.COMMAND_NAME, HelloWorldCommand.creator)
    except:
        om.MGlobal.displayError("Fail to register command {0}".format(HelloWorldCommand.COMMAND_NAME))


# uninilialize current plugin
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(HelloWorldCommand.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Fail to deregister command {0}".format(HelloWorldCommand.COMMAND_NAME))


# just for development to speed up development process
if __name__ == "__main__":
    plugin_name = "hello_worldCmd.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
