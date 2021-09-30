import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass



class BasicMoveCommand(om.MPxCommand):
    
    COMMAND_NAME = "basicmovecommad"
       
    def __init__(self):
        super(BasicMoveCommand, self).__init__()
    
    def doIt(self, arg_list):
        try:
            arg_database = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.displayError("Erro by parsing arguments: {0}".format(arg_list))
            raise
        
        name = arg_database.commandArgumentString(0)
        self.displayInfo("Hello from command {0}".format(name))

        
    def undoIt(self):
        pass  
    
    def redoIt(self):
        pass    
    
    def isUndoable(self):
        return True
    
    @classmethod
    def creator(cls):
        return BasicMoveCommand()
    
    @classmethod
    def create_syntax(cls):
        syntax = om.MSyntax()       
        syntax.addArg(om.MSyntax.kString)
        return syntax

def initializePlugin(plugin):
    vendor = "Alex3D"
    version = "1.0.0"
    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    
    plugin_fn.registerCommand(BasicMoveCommand.COMMAND_NAME,
                              BasicMoveCommand.creator,
                              BasicMoveCommand.create_syntax)
    
    print("Custom Command initialization")


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    plugin_fn.deregisterCommand(BasicMoveCommand.COMMAND_NAME)
    
    print("Custom Command uninitialization")