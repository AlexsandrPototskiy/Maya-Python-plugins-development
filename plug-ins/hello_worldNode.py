import maya.api.OpenMaya as open_maya
import maya.api.OpenMayaUI as open_maya_ui
import maya.api.OpenMayaRender as open_maya_render

import maya.cmds as maya_commands


def maya_useNewAPI():
    # tell Maya to use API 2.0
    pass


class HelloWorldNode(open_maya_ui.MPxLocatorNode):
    TYPE_NAME = "HelloWorldNode"
    # just developer hex value - in real project use something from Autodesk
    TYPE_ID = open_maya.MTypeId(0x0007f7f7)
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld"
    DRAW_REGISTRANT_ID = "HelloWorldNodeDraw"

    def __init__(self):
        super(HelloWorldNode, self).__init__()

    @classmethod
    def creator(cls):
        return HelloWorldNode()

    @classmethod
    def initialize(cls):
        pass


class HelloWorldNodeDraw(open_maya_render.MPxDrawOverride):
    NAME = "HelloWorldNodeDraw"

    def __init__(self, m_object):
        super(HelloWorldNodeDraw, self).__init__(m_object, None, False)

    def prepareForDraw(self, object_path, cam_path, frame_context, old_data):
        pass

    def supportedDrawAPIs(self):
        return open_maya_render.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, object_path, draw_manager, frame_context, data):
        draw_manager.beginDrawable()
        draw_manager.text2d(open_maya.MPoint(100, 100), "HelloWorld")
        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return HelloWorldNodeDraw(obj)


def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    plugin_fn = open_maya.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(HelloWorldNode.TYPE_NAME,
                               HelloWorldNode.TYPE_ID,
                               HelloWorldNode.creator,
                               HelloWorldNode.initialize,
                               open_maya.MPxNode.kLocatorNode,
                               HelloWorldNode.DRAW_CLASSIFICATION)

        print("Hello Node - initialized")
    except:
        print("Fail to initialize node: {0}".format(HelloWorldNode.TYPE_NAME))

    try:
        open_maya_render.MDrawRegistry.registerDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                                   HelloWorldNode.DRAW_REGISTRANT_ID,
                                                                   HelloWorldNodeDraw.creator)
    except:
        print("Fail to register draw override: {0}".format(HelloWorldNodeDraw.NAME))


def uninitializePlugin(plugin):
    plugin_fn = open_maya.MFnPlugin(plugin)

    try:
        open_maya_render.MDrawRegistry.derigisterDrawOverride(HelloWorldNode.DRAW_CLASSIFICATION,
                                                              HelloWorldNode.DRAW_REGISTRANT_ID)
    except:
        print("Fail to derigister draw override: {0}".format(HelloWorldNodeDraw.NAME))

    try:
        plugin_fn.deregisterNode(HelloWorldNode.TYPE_ID)
        print("Hello Node - uninitialized")
    except:
        print("Fail to uninitialize node: {0}".format(HelloWorldNode.TYPE_NAME))


# just for development to speed up development process
if __name__ == "__main__":
    # just reload scene for development purpose
    maya_commands.file(new=True, force=True)

    plugin_name = "hello_worldNode.py"
    maya_commands.evalDeferred(
        'if maya_commands.pluginInfo("{0}", q=True, loaded=True): maya_commands.unloadPlugin("{0}")'.format(
            plugin_name))
    maya_commands.evalDeferred(
        'if not maya_commands.pluginInfo("{0}", q=True, loaded=True): maya_commands.loadPlugin("{0}")'.format(
            plugin_name))

    maya_commands.evalDeferred('maya_commands.createNode("{0}")'.format(HelloWorldNode.TYPE_NAME))
