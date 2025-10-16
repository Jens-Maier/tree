import bpy
import mathutils
from mathutils import Vector
import math

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0)
    
def myNodeTree():
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['CurveNodeGroup'].nodes

curve_node_mapping = {}

def myCurveData(curve_name):
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        curve_node_mapping[curve_name] = cn.name
    nodeTree = myNodeTree()[curve_node_mapping[curve_name]]
    return nodeTree

def ensure_branch_curve_node(idx):
    curve_name = f"BranchCluster_{idx}"
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        #cn.label = curve_name
        curve_node_mapping[curve_name] = cn.name
    return curve_name

def drawDebugPoint(pos, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = 0.1
    bpy.context.active_object.name=name

class AddBranchClusterButton(bpy.types.Operator):
    bl_idname = "scene.add_branch_cluster"
    bl_label = "Add Branch Cluster"

    def execute(self, context):
        context.scene.nrBranchClusters += 1
        idx = context.scene.nrBranchClusters - 1
        ensure_branch_curve_node(idx)
        self.report({'INFO'}, f"Added branch cluster {idx}")
        return {'FINISHED'}

class BranchClusterResetButton(bpy.types.Operator):
    bl_idname = "scene.reset_branch_cluster"
    bl_label = "Reset Branch Cluster"
    
    idx: bpy.props.IntProperty()
    
    def execute(self, context):
        curve_name = ensure_branch_curve_node(self.idx)
        self.report({'INFO'}, f"curve_name: {curve_name}")
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveNodeMapping = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping
        curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        
        self.report({'INFO'}, f"in reset: length: {len(curveElement.points)}")
        
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                
        curveNodeMapping.update()
        
        return {'FINISHED'}



class BranchClusterEvaluateButton(bpy.types.Operator):
    bl_idname = "scene.evaluate_branch_cluster"
    bl_label = "Evaluate Branch Cluster"
    
    idx: bpy.props.IntProperty()
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
    
    def f0b(self, t):
        return (-0.5*t*t*t + t*t - 0.5*t)
    def f1b(self, t):
        return (1.5*t*t*t - 2.5*t*t + 1.0)
    def f2b(self, t):
        return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
    def f3b(self, t):
        return (0.5*t*t*t - 0.5*t*t)
    
    def sampleSplineB(self, p0, p1, p2, p3, t):
        return self.f0b(t) * p0 + self.f1b(t) * p1 + self.f2b(t) * p2 + self.f3b(t) * p3

    def execute(self, context):
        curve_name = ensure_branch_curve_node(self.idx)
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        y = 0.0
        nrSamplePoints = 20
        self.report({'INFO'}, f"length: {len(curveElement.points)}")
        for i in range(0, nrSamplePoints):  
            self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                self.report({'INFO'}, f"begin of loop: n = {n}")
                
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
                        
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                self.report({'INFO'}, f"n = 0, n -> 2 * slope2: {slope2}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p1: {p1}, p2: {p2}")
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                            else: #only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                                self.report({'INFO'}, f"in n = 0: only 2 points -> linear, p0.x: {p0.x}, p0.y: {p0.y}")
                                                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                                
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                            self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                        else:
                            self.report({'INFO'}, "n = 0, reflected == 1 * slope")
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            self.report({'INFO'}, f"n = 0, n -> 2 * slope1: {slope1}")
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope2 * (p2.x - p1.x)))
                            # [0] -> reflected
                            if len(curveElement.points) > 2:
                                # cubic
                                p3 = curveElement.points[2].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p3 = p2 + (p2 - p1)
            
                #last segment
                if n == len(curveElement.points) - 2:
                    if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = last, linear")
                        p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                    else:
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO" or curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO_CLAMPED":
                            p0 = curveElement.points[len(curveElement.points) - 3].location
                            self.report({'INFO'}, "n = last, n -> 2 * slope")
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))
                            else:
                                p3 = p2 + (p2 - p1)
                        else:
                            self.report({'INFO'}, "n = last, slope")
                            if len(curveElement.points) > 2:
                                # cubic
                                p0 = curveElement.points[0].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # liear
                                p0 = p1 - (p2 - p1)
            
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
                        else:
                            self.report({'INFO'}, "n = middle, n -> reflected")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
            
                if p1.x <= x and p2.x >= x:
                    self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, x: {x}")
                    
                    
                    
                
                    #  x: [0..1]
                    # tx: [p1.x...p2.x]
                    #tx = p1.x + x * (p2.x - p1.x)
                    
                    tx = (x - p1.x) / (p2.x - p1.x)  #AI
                    
                    self.report({'INFO'}, f"tx: {tx}")
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    px = self.sampleSplineB(p0.x, p1.x, p2.x, p3.x, tx) # tx (not x) (AI)
                    py = self.sampleSplineB(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, x)
                    
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p0.x, 0.0, p0.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p1.x, 0.0, p1.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p2.x, 0.0, p2.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p3.x, 0.0, p3.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    
                    bpy.ops.object.empty_add(type='SPHERE', location= (x,0.0,py))
                
                    bpy.context.active_object.empty_display_size = 0.01
        return {'FINISHED'}

class BranchSettings(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_branchSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'curveMapping'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "nrBranchClusters")
        layout.operator("scene.add_branch_cluster", text="Add Branch Cluster")
        for i in range(0, context.scene.nrBranchClusters):
            curve_name = ensure_branch_curve_node(i)
            box = layout.box()
            box.label(text=f"Branch Cluster {i}")
            curve_node = myCurveData(curve_name)
            box.template_curve_mapping(curve_node, "mapping")
            op = box.operator("scene.evaluate_branch_cluster", text="Evaluate")
            op.idx = i
            reset = box.operator("scene.reset_branch_cluster", text="Reset")
            reset.idx = i

class initButton(bpy.types.Operator):
    bl_idname="scene.init_button"
    bl_label="initialise"
        
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        nrCurves = len(nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves)
        self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves[3] 
        
        #initialise values
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
    
    def f0b(self, t):
        return (-0.5*t*t*t + t*t - 0.5*t)
    def f1b(self, t):
        return (1.5*t*t*t - 2.5*t*t + 1.0)
    def f2b(self, t):
        return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
    def f3b(self, t):
        return (0.5*t*t*t - 0.5*t*t)
    
    def sampleSplineB(self, p0, p1, p2, p3, t):
        return self.f0b(t) * p0 + self.f1b(t) * p1 + self.f2b(t) * p2 + self.f3b(t) * p3
        
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[curve_node_mapping['TestOne']].mapping.curves[3] 
        y = 0.0
        nrSamplePoints = 20
        self.report({'INFO'}, f"length: {len(curveElement.points)}")
        
        for i in range(0, nrSamplePoints):  
            self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                self.report({'INFO'}, f"begin of loop: n = {n}")
                
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
                        
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                self.report({'INFO'}, f"n = 0, n -> 2 * slope2: {slope2}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p1: {p1}, p2: {p2}")
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                            else: #only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                                self.report({'INFO'}, f"in n = 0: only 2 points -> linear, p0.x: {p0.x}, p0.y: {p0.y}")
                                                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                                
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                            self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                        else:
                            self.report({'INFO'}, "n = 0, reflected == 1 * slope")
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            self.report({'INFO'}, f"n = 0, n -> 2 * slope1: {slope1}")
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope2 * (p2.x - p1.x)))
                            # [0] -> reflected
                            if len(curveElement.points) > 2:
                                # cubic
                                p3 = curveElement.points[2].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p3 = p2 + (p2 - p1)
            
                #last segment
                if n == len(curveElement.points) - 2:
                    if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = last, linear")
                        p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                    else:
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO" or curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO_CLAMPED":
                            p0 = curveElement.points[len(curveElement.points) - 3].location
                            self.report({'INFO'}, "n = last, n -> 2 * slope")
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))
                            else:
                                p3 = p2 + (p2 - p1)
                        else:
                            self.report({'INFO'}, "n = last, slope")
                            if len(curveElement.points) > 2:
                                # cubic
                                p0 = curveElement.points[0].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # liear
                                p0 = p1 - (p2 - p1)
            
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
                        else:
                            self.report({'INFO'}, "n = middle, n -> reflected")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
            
                if p1.x <= x and p2.x >= x:
                    self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, x: {x}")
                    
                    
                    
                
                    #  x: [0..1]
                    # tx: [p1.x...p2.x]
                    #tx = p1.x + x * (p2.x - p1.x)
                    
                    tx = (x - p1.x) / (p2.x - p1.x)  #AI
                    
                    self.report({'INFO'}, f"tx: {tx}")
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    px = self.sampleSplineB(p0.x, p1.x, p2.x, p3.x, tx) # tx (not x) (AI)
                    py = self.sampleSplineB(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, x)
                    
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p0.x, 0.0, p0.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p1.x, 0.0, p1.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p2.x, 0.0, p2.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p3.x, 0.0, p3.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    
                    bpy.ops.object.empty_add(type='SPHERE', location= (x,0.0,py))
                
                    bpy.context.active_object.empty_display_size = 0.01
        return {'FINISHED'} 
        
    
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

class updateButton(bpy.types.Operator):
    bl_idname="scene.update"
    bl_label="Update"
    
    def execute(self, context):
        nodes = []
        angles = []
        n = 6
        for i in range(0, n):
            nodes.append(Vector((i, 0.0, 0.0)))
            angles.append(0.0)
            bpy.ops.object.empty_add(type='SPHERE', location= nodes[i])
            bpy.context.active_object.empty_display_size = 0.02
        
        iterations = 80
        
        fixPoint = Vector((-1.0,0.0,0.0))
        
        for i in range(iterations):
            self.report({'INFO'}, f"iteration: {i}")
            forces = []
            for j in range(0, n):
                gravity = 0.1
                if j <= 1:
                    Fgrav = Vector((0.0,0.0,-1.0)) * gravity / 5
                    Fspring = (((nodes[j + 1] - nodes[j]).length - 1.0) * (nodes[j + 1] - nodes[j]) / (nodes[j + 1] - nodes[j]).length) * 0.8
                    forces.append(Fgrav + Fspring)
                    #TODO: length constratint!
                else:
                    
                    if j == n - 1:
                        Fgrav = Vector((0.0,0.0,-1.0)) * gravity #* (nodes[j] - nodes[j - 1]).dot(Vector((0.0,0.0,-1.0)))
                        
                        Fspring = (((nodes[j - 1] - nodes[j]).length - 1.0) * (nodes[j - 1] - nodes[j]) / (nodes[j - 1] - nodes[j]).length)
                    else:
                        Fgrav = Vector((0.0,0.0,-1.0)) * gravity
                        Fspring = (((nodes[j + 1] - nodes[j]).length - 1.0) * (nodes[j + 1] - nodes[j]) / (nodes[j + 1] - nodes[j]).length + 
                                   ((nodes[j - 1] - nodes[j]).length - 1.0) * (nodes[j - 1] - nodes[j]) / (nodes[j - 1] - nodes[j]).length) * 0.2
                        #Fspring = ((nodes[j + 1] - nodes[j]) + (nodes[j - 1] - nodes[j])) * 0.2
                        if j == 3:
                            drawArrow(nodes[j], nodes[j + 1])
                            drawArrow(nodes[j], nodes[j - 1])
                        
                        #self.report({'INFO'}, f"Fgrav: {Fgrav}")
                        self.report({'INFO'}, f"Fspring: {Fspring}")
                    
                    
                    if Fgrav.z > 0.0:
                        self.report({'ERROR'}, f"Fgrav: {Fgrav}")
                    F = Fgrav + Fspring
                    #drawArrow(nodes[j], nodes[j] + F)
                    drawArrow(nodes[j], nodes[j] + Fspring)
                    #drawArrow(nodes[j], nodes[j] + Fgrav)
                    #nodes[j] += F
                    
                    forces.append(F)
                    #TODO: length constratint!
                    
            for j in range(0, n):
                #apply forces
                nodes[j] += forces[j]
            
            for j in range(0, n - 1):
                #TODO: length constratint!
                stretch = (nodes[n - j - 1] - nodes[n - j - 2]).length - 1.0
                for k in range(n - j + 1, n):
                    nodes[k] -= stretch * (nodes[k] - nodes[k - 1])
                
        for j in range(0, n):
            p = nodes[j]
            self.report({'INFO'}, f"p: {p}")
            bpy.ops.object.empty_add(type='SPHERE', location = p)
            bpy.context.active_object.empty_display_size = 0.01
            #if j < n - 1:
            #    drawArrow(nodes[j], nodes[j + 1])
        
        return {'FINISHED'} 
    
def drawArrow(a, b):
    # Step 1: Create the empty at the position of point A with type 'SINGLE_ARROW'
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=a)
    empty = bpy.context.object  # Get the newly created empty
    
    # Step 2: Calculate the direction vector from A to B
    direction = b - a
    
    # Step 3: Calculate the rotation to point from A to B
    # Create a rotation matrix that makes the Z-axis of the empty point towards point B
    rotation = direction.to_track_quat('Z', 'Y')  # 'Z' axis points towards B, 'Y' is up
    
    # Apply the rotation to the empty
    empty.rotation_euler = rotation.to_euler()

    # Step 4: Scale the empty based on the distance from A to B
    distance = direction.length
    empty.scale = (distance, distance, distance)  # Scale uniformly along all axes
    
    return empty
        
class bendBranchesPanel(bpy.types.Panel):
    bl_label = "bend Branches"
    bl_idname = "PT_bend_Branches"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'bendBranches'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("scene.update", text="Update")

def register():
    bpy.utils.register_class(CurvyPanel)
    bpy.utils.register_class(EvalPanel)
    bpy.utils.register_class(BranchSettings)
    bpy.utils.register_class(evaluateButton)
    bpy.utils.register_class(initButton)
    bpy.utils.register_class(bendBranchesPanel)
    bpy.utils.register_class(updateButton)
    bpy.utils.register_class(AddBranchClusterButton)
    bpy.utils.register_class(BranchClusterEvaluateButton)
    bpy.utils.register_class(BranchClusterResetButton)
    
    bpy.utils.register_class(floatProp)
    
    bpy.types.Scene.evaluate = bpy.props.FloatProperty(
        name = "evaluate at",
        default = 0.0,
        min = 0.0, 
        max = 1.0
    )
    
    bpy.types.Scene.nrBranchClusters = bpy.props.IntProperty(
        name = "nr branch clusters",
        default = 0,
        min = 0
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
    bpy.utils.unregister_class(BranchSettings)
    bpy.utils.unregister_class(bendBranchesPanel)
    bpy.utils.unregister_class(evaluateButton)
    bpy.utils.unregister_class(updateButton)
    bpy.utils.unregister_class(AddBranchClusterButton)
    bpy.utils.unregister_class(BranchClusterEvaluateButton)
    bpy.utils.unregister_class(BranchClusterResetButton)
    
    bpy.utils.unregister_class(initButton)
    bpy.utils.unregister_class(floatProp)
    del bpy.types.Scene.evaluate
    del bpy.types.Scene.my_curve_mapping
    del bpy.types.Scene.nrBranchClusters
    
if __name__ == "__main__":
    register()
