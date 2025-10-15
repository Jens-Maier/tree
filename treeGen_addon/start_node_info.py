class startNodeInfo:
    def __init__(self, StartNode, NextIndex, StartTval, EndTval, StartTvalGlobal, EndTvalGlobal):
        self.startNode = StartNode
        self.nextIndex = NextIndex
        self.startTval = StartTval
        self.endTval = EndTval
        self.startTvalGlobal = StartTvalGlobal
        self.endTvalGlobal = EndTvalGlobal
        
    def register():
        print("in startNodeInfo: register")
    
    def unregister():
        print("in startNodeInfo: unregister")
        
        
        
def register():
    print("register startNodeInfo")
    startNodeInfo.register()
    
def unregister():
    startNodeInfo.unregister()
    print("unregister startNodeInfo")
