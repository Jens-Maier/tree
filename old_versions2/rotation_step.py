class rotationStep():
    def __init__(self, RotationPoint, Curvature, CurveAxis, IsLast):
       self.rotationPoint = RotationPoint
       self.curvature = Curvature
       self.curveAxis = CurveAxis
       self.isLast = IsLast
       
        
    def register():
        print("in rotationStep: register")
    
    def unregister():
        print("in rotationStep: unregister")
        
        
        
def register():
    print("register rotationStep")
    rotationStep.register()
    
def unregister():
    rotationStep.unregister()
    print("unregister rotationStep")
