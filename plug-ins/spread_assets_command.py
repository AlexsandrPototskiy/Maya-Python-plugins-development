import maya.api.OpenMaya as om


# tell maya to use New API 2.0
def maya_useNewAPI():
    pass


class SpreadAssetsCommand(om.MPxCommand):
    
    """
    Spead command is responsible to take selected object and spread them in the world by given offset;
    I has an undo/redo support
    """       
    
    COMMAND_NAME = "spread_assets"
    
    SELECTION_FLAG = ["-sl", "-selections", om.MSyntax.kSelectionList]
    OFFSET_FLAG = ["-of", "-offset", om.MSyntax.kDouble]
    DEFAULT_OFFSET = 2
    
    def __init__(self):
        super(SpreadAssetsCommand, self).__init__()
        self.original_tranlation = {}
        self.new_tranlation = {}
    
    def doIt(self, arg_list):
        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list)
        except:
            raise RuntimeError("[SpreadAssetsCommand] Error when parsing arguments: {0}".format(arg_list))
        
        try:
            self.current_selection = arg_db.getObjectList()        
        except:
            raise RuntimeError("[SpreadAssetsCommand] SELECTION AGRUMENT ERROR")
        
        self.offset = SpreadAssetsCommand.DEFAULT_OFFSET
        # get offset from flag if isFlag set True
        if arg_db.isFlagSet(SpreadAssetsCommand.OFFSET_FLAG[0]):
            self.offset = arg_db.flagArgumentDouble(SpreadAssetsCommand.OFFSET_FLAG[0], 0)
        
        self.doSpreading(self.current_selection, self.offset)
    
    def doSpreading(self, selection_list, offset):
        self.displayInfo("OFFSET AGRUMENT = {0}".format(offset))
        
        position = 0.0
        for i in range(selection_list.length()):
            mObject = selection_list.getDependNode(i)
            dep_node = om.MFnDependencyNode(mObject)
            
            if mObject.hasFn(om.MFn.kTransform):
                
                transfrom_fn = om.MFnTransform(mObject)
                
                # save initial translation
                self.original_tranlation[dep_node.name()] = transfrom_fn.translation(om.MSpace.kTransform)
                
                # move object
                transfrom_fn = om.MFnTransform(mObject)
                vector = om.MVector(position, 0, 0)
                position += offset
                transfrom_fn.setTranslation(vector, om.MSpace.kTransform)
                
                # store new transaltion
                self.new_tranlation[dep_node.name()] = transfrom_fn.translation(om.MSpace.kTransform)
                
            else:
                raise RuntimeError("[SpreadAssetsCommand] Objects in selection must be Transform Node Type, current type {0}".
                                   format(dep_node.typeName))
        
        self.displayInfo("Original Saved info:")
        self.displayInfo(str(self.original_tranlation))
        
        self.displayInfo("New Saved info:")
        self.displayInfo(str(self.new_tranlation))        
        
    
    def undoIt(self):
        self.displayInfo("undoIt was called")
        selection_list = om.MSelectionList()
        
        for key in self.original_tranlation.keys():
            selection_list.add(key)
        
        for i in range(selection_list.length()):
            mObject = selection_list.getDependNode(i)
            depend_node = om.MFnDependencyNode(mObject)
            transfrom_fn = om.MFnTransform(mObject)
            transfrom_fn.setTranslation(self.original_tranlation[depend_node.name()], om.MSpace.kTransform)
   
    
    def redoIt(self):
        self.displayInfo("redoIt was called")
        selection_list = om.MSelectionList()
        
        for key in self.original_tranlation.keys():
            selection_list.add(key)
        
        for i in range(selection_list.length()):
            mObject = selection_list.getDependNode(i)
            depend_node = om.MFnDependencyNode(mObject)
            transfrom_fn = om.MFnTransform(mObject)
            transfrom_fn.setTranslation(self.new_tranlation[depend_node.name()], om.MSpace.kTransform)        
    
    def isUndoable(self):
        return True
    
    @classmethod
    def creator(cls):
        return SpreadAssetsCommand()
    
    @classmethod
    def syntax_initializer(cls):
        syntax = om.MSyntax()
        
        syntax.setObjectType(om.MSyntax.kSelectionList)        
        
        syntax.addFlag(SpreadAssetsCommand.OFFSET_FLAG[0], 
                       SpreadAssetsCommand.OFFSET_FLAG[1],
                       om.MSyntax.kDouble)
        
        return syntax


# initialize plugin
def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
        plugin_fn.registerCommand(SpreadAssetsCommand.COMMAND_NAME,
                                  SpreadAssetsCommand.creator,
                                  SpreadAssetsCommand.syntax_initializer)
        om.MGlobal.displayInfo("initialized")
    except:
        om.MGlobal.displayError("[SpreadAssetsCommand] Failed to register command: {0}".format(SpreadAssetsCommand.COMMAND_NAME))


# uninitialize plugin
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
        plugin_fn.deregisterCommand(SpreadAssetsCommand.COMMAND_NAME)
        om.MGlobal.displayInfo("uninitialized")
    except:
        om.MGlobal.displayError("[SpreadAssetsCommand] Failed to deregister command: {0}".format(SpreadAssetsCommand.COMMAND_NAME))