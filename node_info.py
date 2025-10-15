class nodeInfo():
    def __init__(self, NodeInLevel, NextIndex, SplitsPerBranch):
        self.nodeInLevel = NodeInLevel
        self.nextIndex = NextIndex
        self.splitsPerBranch = SplitsPerBranch
        
        
        
    def register():
        pass
        #print("in nodeInfo: register")
    
    def unregister():
        pass
        #print("in nodeInfo: unregister")
        
        
        
def register():
    #print("register nodeInfo")
    nodeInfo.register()
    
def unregister():
    nodeInfo.unregister()
    #print("unregister nodeInfo")