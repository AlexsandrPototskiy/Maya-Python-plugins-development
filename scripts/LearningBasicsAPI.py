import maya.cmds as cmds

cmds.file(new=True, force=True)

plugin_name = "sterring_wheel_node.py"

print("-----------------------")

if cmds.pluginInfo(plugin_name, q = True, loaded = True):
    print("Plugin is loaded, do unload")
    cmds.unloadPlugin(plugin_name)
    
if not cmds.pluginInfo(plugin_name, q = True, loaded = True):
    print("Load plugin")
    cmds.loadPlugin(plugin_name)

cmds.createNode("sterring_wheel_node")
print("Node Was created")
print("-----------------------")