import bpy

#https://blender.stackexchange.com/questions/61618/add-a-custom-curve-mapping-property-for-an-add-on/61829#61829

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0)
    
def myNodeTree():
    if 'TestCurveData' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('TestCurveData', 'ShaderNodeTree')
    #bpy.data.node_groups['TestCurveData'].nodes[0].mapping.curves[3].points[0].location = 1.0
    #bpy.data.node_groups['TestCurveData'].nodes[0].mapping.curves[3].points[1].location = 0.0
    
    return bpy.data.node_groups['TestCurveData'].nodes

curve_node_mapping = {}

def myCurveData(curve_name):
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        curve_node_mapping[curve_name] = cn.name
        
    #return myNodeTree()[curve_node_mapping[curve_name]]
    nodeTree = myNodeTree()[curve_node_mapping[curve_name]]
    
    
    return nodeTree

def drawDebugPoint(pos, name="debugPoint"):
        bpy.ops.object.empty_add(type='SPHERE', location=pos)
        bpy.context.active_object.empty_display_size = 0.1
        bpy.context.active_object.name=name
    

class initButton(bpy.types.Operator):
    bl_idname="scene.init_button"
    bl_label="initialise"
        
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('TestCurveData')
        nrCurves = len(nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves)
        self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves[3] 
        
        #initialise values (funkt!)
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                self.report({'INFO'}, "removing point")
        nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.update()
        return {'FINISHED'}

class evaluateButton(bpy.types.Operator):
    bl_idname="scene.evaluate_button"
    bl_label="evaluate"
    
    x: bpy.props.FloatProperty()
    
    def lerp(self, a, b, t):
        return (a + (b - 1) * t)
    
    def f0(self, t):
        return (2.0 - t) * (2.0 - t) * (1.0 - t) / 2.0
    def f1(self, t):
        return (2.0 - t) * (2.0 - t) * t + (t - 1.0) * (3.0 - t) * (2.0 - t) / 2.0
    def f2(self, t):
        return (2.0 - t) * (t - 1.0) * t / 2.0 + (3.0 - t) * (t - 1.0) * (t - 1.0)
    def f3(self, t):
        return (t - 1.0) * (t - 1.0) * (t - 2.0) / 2.0
    
    def sampleSpline(self, p0, p1, p2, p3, t):
        return self.f0(t + 1.0) * p0 + self.f1(t + 1.0) * p1 + self.f2(t + 1.0) * p2 + self.f3(t + 1.0) * p3
        
        #a0 = self.lerp(p0, p1, t - 1.0)
        #a1 = self.lerp(p1, p2, t - 1.0)
        #a2 = self.lerp(p2, p3, t - 1.0)
        #b0 = self.lerp(a0, a1, t - 1.0)
        #b1 = self.lerp(a1, a2, t - 1.0)
        #return self.lerp(b0, b1, t - 1.0)
            
    
    
    
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('TestCurveData')
        curveElement = nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves[3] 
        y = 0.0
        nrSamplePoints = 32
        self.report({'INFO'}, f"length: {len(curveElement.points)}")
        
        #bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
        #bpy.context.active_object.empty_display_size = 0.05
        
        for i in range(0, nrSamplePoints):  
            self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                self.report({'INFO'}, f"begin of loop: n = {n}")
                #bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
                #bpy.context.active_object.empty_display_size = 0.05
                
                # -> do all with bezier: p0, p1, p2, p3!
                
                #first segment
                if n == 0:
                    if curveElement.points[1].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = 0, linear") 
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                        self.report({'INFO'}, f"n = 0, linear: p0: {p0}, p1: {p1}, p2: {p2}, p3: {p3}")
                    else:
                        if curveElement.points[0].handle_type == "AUTO":
                            self.report({'INFO'}, "n = 0, n -> reflected")
                            p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                            p1 = curveElement.points[0].location
                        else:
                            self.report({'INFO'}, "n = 0, slope") #s. Block...
            
                #last segment
                if n == len(curveElement.points) - 2:
                    if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = last, linear")
                        p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 1].location)
                        
                        #p0 = curveElement.points[len(curveElement.points) - 2].location
                        #p1 = curveElement.points[len(curveElement.points) - 2].location + (1.0 / 3.0) * (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        #p2 = curveElement.points[len(curveElement.points) - 2].location + (2.0 / 3.0) * (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        #p3 = curveElement.points[len(curveElement.points) - 1].location
                    else:
                        if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO":
                            self.report({'INFO'}, "n = last, n + 1-> reflected")
                            p2 = curveElement.points[len(curveElement.points) - 1].location
                            p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        else:
                            self.report({'INFO'}, "n = last, slope")
            
                #middle segments
                if n > 0 and n < len(curveElement.points) - 2:
                    if curveElement.points[n].handle_type == "AUTO" or curveElement.points[n].handle_type == "AUTO_CLAMPED":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            self.report({'INFO'}, "n = middle, n + 1 -> reflected")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            self.report({'INFO'}, "n = middle, (cubic (clamped)) -> spline!")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                        
                    if curveElement.points[n].handle_type == "VECTOR":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            self.report({'INFO'}, "linear")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                            
                            #p0 = curveElement.points[n].location
                            #p1 = curveElement.points[n].location + (1.0 / 3.0) * (curveElement.points[n + 1].location - curveElement.points[0].location)
                            #p2 = curveElement.points[n].location + (2.0 / 3.0) * (curveElement.points[n + 1].location - curveElement.points[0].location)
                            #p3 = curveElement.points[n + 1].location
                            
                        else:
                            self.report({'INFO'}, "n = middle, n -> reflected")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
            
                # test which segment the sample point falls into
                if n >= 0:
                    #if p1.x <= x and p2.x >= x: # x in [0, 1] for EACH sample point !!!
                    self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, x: {x}")
                    px = self.sampleSpline(p0.x, p1.x, p2.x, p3.x, x)
                    py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, x)
                        
                    bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
                    bpy.context.active_object.empty_display_size = 0.01
                    #else:
                    #    self.report({'INFO'}, f"x = {x}: not in segment {n}")
                        
                    # x in [0, 1] for EACH sample point !!!
                        
                    break
                
            
        
            #bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
            #bpy.context.active_object.empty_display_size = 0.05
        
        return {'FINISHED'} 
    
    
        #for n in range(0, len(curveElement.points) - 1):
        #    for i in range(0, nrSamplePoints):  
        #        x = i / nrSamplePoints
        #        x0 = 0.0
        #        y0 = 0.0
        #        x1 = 0.0
        #        y1 = 0.0
        #        x2 = 0.0
        #        y2 = 0.0
        #        x3 = 0.0
        #        y3 = 0.0
        #        if n == 0:
        #            if x >= curveElement.points[n].location.x and x < curveElement.points[n + 1].location.x:
        #                if curveElement.points[1].handle_type == "VECTOR":
        #                    #linear
        #                    x0 = curveElement.points[n].location.x
        #                    x1 = curveElement.points[n + 1].location.x
        #                        
        #                    y0 = curveElement.points[n].location.y
        #                    y1 = curveElement.points[n + 1].location.y
        #                    px = x0 + (x1 - x0) * (x) #/ (x1 - x0)
        #                    py = y0 + (y1 - y0) * (x) #/ (x1 - x0)
        #                
        #                    x2 = 1.0 # TODO
        #                    y2 = 1.0 # TODO
        #                    bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
        #                    bpy.context.active_object.empty_display_size = 0.01
        #                    self.report({'INFO'}, "adding point, n = 0")
        ##                    
         #               else: # [1] auto / auto clamped
        #                    if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
        #                        self.report({'INFO'}, "AUTO handle n = 0")
        #                        
        #                        # n0 reflectd (n == 0)
        #                        point_n0 = curveElement.points[n].location - (curveElement.points[n + 1].location -  curveElement.points[n].location)
        #                        x0 = point_n0.x
        #                        y0 = point_n0.y
        #                        x1 = curveElement.points[n].location.x # points[0]
        #                        y1 = curveElement.points[n].location.y
        #                        x2 = curveElement.points[n + 1].location.x
        #                        y2 = curveElement.points[n + 1].location.y
        #                            
        #                        self.report({'INFO'}, f"x0: {x0}, x1: {x1}, x2: {x2}") #OK
        #                        self.report({'INFO'}, f"y0: {y0}, y1: {y1}, y2: {y2}") #OK
        #                        
        #                    if curveElement.points[1].handle_type == "AUTO" or curveElement.points[1].handle_type == "AUTO_CLAMPED":
        #                        if len(curveElement.points) == 2:
        #                            x0 = point_n0.x
        #                            y0 = point_n0.y
        #                            x1 = curveElement.points[n].location.x # points[0]
        #                            y1 = curveElement.points[n].location.y
        #                            x2 = curveElement.points[n + 1].location.x
        #                            y2 = curveElement.points[n + 1].location.y
        #                            # n3 reflected
        #                            point_n3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
        #                            x3 = point_n3.x
        #                            y3 = point_n3.y
        #                            
        #                    self.report({'INFO'}, f"x1: {x1}, x2: {x2}")
        #                    if x1 == x2:
        #                        self.report({'ERROR'}, "x1 == x2 : divide by 0 (set to 1)")
        #                    t = (x - x1) / (x2 - x1)
         ##                   if t < 0 or t > 1:
        #                        self.report({'ERROR'}, f"t = {t} out of bounds: ")
        #                        self.report({'ERROR'}, f"x1: {x1}, x2: {x2}, x: {x}") # x ???
        #                    px = self.sampleSpline(x0, x1, x2, x3, t)
        #                    py = self.sampleSpline(y0, y1, y2, y3, t)
        #                    bpy.ops.object.empty_add(type='SPHERE', location=(px, 0.0, py))
        #                    bpy.context.active_object.empty_display_size = 0.01
        #                        
        #        else: #n > 0
        #            if x >= curveElement.points[n].location.x and x < curveElement.points[n + 1].location.x:
        #                if curveElement.points[n].handle_type == "VECTOR" and curveElement.points[n + 1].handle_type == "VECTOR":
        #                    #linear
        #                    x0 = curveElement.points[n].location.x
        #                    x1 = curveElement.points[n + 1].location.x
        #                    
        #                    y0 = curveElement.points[n].location.y
        #                    y1 = curveElement.points[n + 1].location.y
        #                    
        #                    px = x0 + x * (x1 - x0)
        #                    py = y0 + x * (y1 - y0)
        #                    #px = x0 + (x1 - x0) * (x) / (x1 - x0)
        #                    #py = y0 + (y1 - y0) * (x) / (x1 - x0)
        #                
        #                    
        #                    bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
        #                    bpy.context.active_object.empty_display_size = 0.01
        #                    self.report({'INFO'}, f"adding point, n = {n}")
        #                
        #                else:
        #                    if curveElement.points[n].handle_type == "VECTOR" and (curveElement.points[n + 1].handle_type == "AUTO" or curveElement.points[n + 1].handle_type == "AUTO_CLAMPED") and n < len(curveElement.points) - 2:
        #                    
        #                        # n0 = (index=n - 1) reflected
        #                        point_n0 = curveElement.points[n - 1].location - (curveElement.points[n].location -  curveEle#ment.points[n - 1].location)
        #                        x0 = point_n0.x
        #                        y0 = point_n0.y
        #                        x1 = curveElement.points[n].location.x
        #                        y1 = curveElement.points[n].location.y
        #                        x2 = curveElement.points[n + 1].location.x
        #                        y2 = curveElement.points[n + 1].location.y
        #                        x3 = curveElement.points[n + 2].location.x
        #                        y3 = curveElement.points[n + 2].location.y #TODO...
        #                        
        #                        bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
        #                        bpy.context.active_object.empty_display_size = 0.01
        #                        self.report({'INFO'}, f"adding point, n = {n}")
        #                        
        #                        
        #                    if (curveElement.points[n].handle_type == "AUTO" or curveElement.points[n].handle_type == "AUTO_CL#AMPED") and n < (len(curveElement.points) - 2):
        #                        self.report({'INFO'}, f"AUTO handle n = {n}")
        #                        # n-1 ok
        #                        # n ok
        #                        self.report({'INFO'}, f"len(curveElement.points) - 2: {len(curveElement.points) - 2}, n: {n}")
        #                        x1 = curveElement.points[n].location.x
        #                        y1 = curveElement.points[n].location.y
        #                        x2 = curveElement.points[n + 1].location.x
        #                        y2 = curveElement.points[n + 1].location.y
        #                        x3 = curveElement.points[n + 2].location.x
        #                        y3 = curveElement.points[n + 2].location.y
        #                        
        #                        
        #                        px = self.sampleSpline(x0, x1, x2, x3, x)
        #                        py = self.sampleSpline(y0, y1, y2, y3, x)
        #                        
        #                        bpy.ops.object.empty_add(type='SPHERE', location=(px,0.0,py))
        #                        bpy.context.active_object.empty_display_size = 0.01
        #                        self.report({'INFO'}, f"adding point, n = {n}")
        #
        #return {'FINISHED'}  
    
    
    
    
    
     
                
                # 
                # point_n1 = curveElement.points[n].location
                # point_n2 = curveElement.points[n + 1].location
                # 
                # point_n3 = point_n2 + (point_n2 - point_n1)
                # if n < len(curveElement.points) - 2:
                #     point_n3 = curveElement.points[n + 2].location
                # 
                # self.report({'INFO'}, f"element.point_n0.location: {point_n0}")
                # self.report({'INFO'}, f"element.point_n1.location: {point_n1}")
                # self.report({'INFO'}, f"element.point_n2.location: {point_n2}")
                # self.report({'INFO'}, f"element.point_n3.location: {point_n3}")
                # 
                # if curveElement.points[n].handle_type == "VECTOR":
                #     y = point_n1 + (point_n2 - point_n1) * self.x #TODO: Test!
                #     self.report({'INFO'}, f"VECTOR: in samplePoint: y: {y}")
                #     break
                # if curveElement.points[n].handle_type == "AUTO":
                #     t = point_n1.x + (point_n2.x - point_n1.x) * self.x
                #     y = self.sampleSpline(point_n0.y, point_n1.y, point_n2.y, point_n3.y, t)
                #     self.report({'INFO'}, f"AUTO: in samplePoint: y: {y}")
                #     break
                # if curveElement.points[n].handle_type == "AUTO_CLAMPED":
                #     y = 0.0
                #     #TODO
                #     self.report({'INFO'}, f"AUTO_CLAMPED: in samplePoint: y: {y}")
                #     break
        #return y
        #return {'FINISHED'}      
                #                    pn2     pn3
                #  0     1     2      n-2     n-1
                #n=5
                
                # p_n2
                # n + 1 <= len-2
                # n <= len-3
                # n < len-2
                
                # p_n3
                # n + 2 <= len-1
                # n <= len-3
                #n < len-2
        
        
    
class CurvyPanel(bpy.types.Panel):
    bl_label = "Test curve mapping"
    bl_idname = "PT_curveMapping"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'curveMapping'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.template_curve_mapping(myCurveData('TestOne'), "mapping")
        
class EvalPanel(bpy.types.Panel):
    bl_label = "Evaluate"
    bl_idname = "PT_evaluate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'curveMapping'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "evaluate", slider=True)
        layout.operator("scene.evaluate_button", text="Evaluate").x = context.scene.evaluate
        layout.operator("scene.init_button", text="Initialise")

def register():
    #bpy.utils.register_class(floatProp)
    bpy.utils.register_class(CurvyPanel)
    bpy.utils.register_class(EvalPanel)
    bpy.utils.register_class(evaluateButton)
    bpy.utils.register_class(initButton)
    
    bpy.utils.register_class(floatProp)
    
    bpy.types.Scene.evaluate = bpy.props.FloatProperty(
        name = "evaluate at",
        default = 0.0,
        min = 0.0, 
        max = 1.0
    )
    
    bpy.types.Scene.my_curve_mapping : bpy.props.CurveMappingProperty(
        name="My Curve Mapping", 
        min=0.0, 
        max=1.0,
        subtype='VALUE' # or 'XYZ', 'HSV', 'CRGB'
    )

def unregister():
    bpy.utils.unregister_class(CurvyPanel)
    bpy.utils.unregister_class(EvalPanel)
    bpy.utils.unregister_class(evaluateButton)
    bpy.utils.unregister_class(initButton)
    bpy.utils.unregister_class(floatProp)
    del bpy.types.Scene.evaluate
    del bpy.types.Scene.my_curve_mapping
    
if __name__ == "__main__":
    register();