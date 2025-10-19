import bpy.types
import os
import json

from . import panels
from . import property_groups
from . import tree_generator

class OBJECT_OT_generateTree(bpy.types.Operator):
    bl_label = "generateTree"
    bl_idname = "object.generate_tree"
    
    def execute(self, context):
        #delete all existing empties
        if context.active_object is not None and context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY':
                    obj.select_set(True)
            bpy.ops.object.delete()
        #self.report({'INFO'}, "deleted all empties")
        tree_generator.treeGenerator.generate_tree(self, context)
        
        bpy.context.view_layer.objects.active = bpy.data.objects["tree"]
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class OBJECT_OT_packUVs(bpy.types.Operator):
    bl_label = "packUVs"
    bl_idname = "object.pack_uvs"
    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=False, correct_aspect=True, use_subsurf_data=False, margin=0.1, no_flip=False, iterations=5, use_weights=True, weight_group="uv_importance", weight_factor=1)
    
        bpy.ops.uv.pack_islands(shape_method='CONVEX', scale=True, rotate=True, rotate_method='AXIS_ALIGNED', margin_method='FRACTION', margin=context.scene.treeSettings.uvMargin, pin=False, merge_overlap=False, udim_source='CLOSEST_UDIM')
    
        bpy.ops.object.editmode_toggle()
        print(f"uv margin: {context.scene.treeSettings.uvMargin}")
        
        # Check UV bounds after packing
        if checkUVbounds():
            self.report({'WARNING'}, "Warning: UVs out of bounds! Reduce UV margin.")
        
        return {'FINISHED'}
    
def checkUVbounds():
    obj = bpy.context.active_object
    uv_layer = obj.data.uv_layers.active.data
    
    outOfBounds = False
    for loop in obj.data.loops:
        uv = uv_layer[loop.index].uv
        if uv.x < 0.0 or uv.x > 1.0 or uv.y < 0.0 or uv.y > 1.0:
            outOfBounds = True
            break
    
    return outOfBounds
            
    
    

class SCENE_OT_BranchClusterResetButton(bpy.types.Operator):
    bl_idname = "scene.reset_branch_cluster_curve"
    bl_label = "Reset Branch Cluster"
    
    idx: bpy.props.IntProperty()
    
    def execute(self, context):
        curve_name = panels.ensure_branch_curve_node(tree_generator, self.idx)
        #self.report({'INFO'}, f"curve_name: {curve_name}")
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveNodeMapping = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.curves[3]
        
        #self.report({'INFO'}, f"in reset: length: {len(curveElement.points)}")
        
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                
        curveNodeMapping.update()
        
        return {'FINISHED'}

class SCENE_OT_BranchClusterEvaluateButton(bpy.types.Operator):
    bl_idname = "scene.evaluate_branch_cluster"
    bl_label = "Evaluate Branch Cluster"
    
    idx: bpy.props.IntProperty
    x: bpy.props.FloatProperty
    
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
        curve_name = panels.ensure_branch_curve_node(tree_generator, self.idx)
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.curves[3]
        y = 0.0
        nrSamplePoints = 20
        #self.report({'INFO'}, f"length: {len(curveElement.points)}")
        for i in range(0, nrSamplePoints):  
            #self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                
                #first segment
                if n == 0:
                    if curveElement.points[1].handle_type == "VECTOR":
                        #linear
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                    else:
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                #n = 0, n -> 2 * slope
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                            else: # only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                        else:
                            #n = 0, reflected == 1 * slope
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
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
                        #n = last, linear
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
                            #n = last, n -> 2 * slope
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))  
                            else:
                                p3 = p2 + (p2 - p1)
                                #n = last, p3: mirror
                        else:
                            #n = last, slope
                            if len(curveElement.points) > 2:
                                # cubic
                                p0 = curveElement.points[0].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p0 = p1 - (p2 - p1)
                    
                #middle segments
                if n > 0 and n < len(curveElement.points) - 2:
                    if curveElement.points[n].handle_type == "AUTO" or curveElement.points[n].handle_type == "AUTO_CLAMPED":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            #n = middle, n + 1 -> reflected
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #n = middle, (cubic (clamped)) -> spline!
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                                    
                    if curveElement.points[n].handle_type == "VECTOR":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            #linear
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #n = middle, n -> reflected
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                
                if p1.x <= x and (p2.x > x or p2.x == 1.0):
                    
                    tx = (x - p1.x) / (p2.x - p1.x)
                    
                    px = self.sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
                    py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                            
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

class SCENE_OT_initButton(bpy.types.Operator):
    bl_idname="scene.init_button"
    bl_label="Reset"
        
    def execute(self, context):
        panels.ensure_stem_curve_node(tree_generator)
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        nrCurves = len(nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves)
        #self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3] 
        
        #initialise values
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                #self.report({'INFO'}, "removing point")
        nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.update()
        return {'FINISHED'}
    
    
class SCENE_OT_evaluateButton(bpy.types.Operator):
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
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3] 
        y = 0.0
        nrSamplePoints = 20
        #self.report({'INFO'}, f"length: {len(curveElement.points)}")
        
        for i in range(0, nrSamplePoints):  
            #self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                #self.report({'INFO'}, f"begin of loop: n = {n}")
                
                #first segment
                if n == 0:
                    if curveElement.points[1].handle_type == "VECTOR":
                        #self.report({'INFO'}, "n = 0, linear") 
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                        #self.report({'INFO'}, f"n = 0, linear: p0: {p0}, p1: {p1}, p2: {p2}, p3: {p3}")
                    else:
                        
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                #self.report({'INFO'}, f"n = 0, n -> 2 * slope2: {slope2}")
                                #self.report({'INFO'}, f"in n = 0, AUTO: p1: {p1}, p2: {p2}")
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                                #self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                            else: #only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                                #self.report({'INFO'}, f"in n = 0: only 2 points -> linear, p0.x: {p0.x}, p0.y: {p0.y}")
                                                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                                
                                #self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                                #self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                            #self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                        else:
                            #self.report({'INFO'}, "n = 0, reflected == 1 * slope")
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            #self.report({'INFO'}, f"n = 0, n -> 2 * slope1: {slope1}")
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
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
                        #self.report({'INFO'}, "n = last, linear")
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
                            #self.report({'INFO'}, "n = last, n -> 2 * slope")
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))
                            else:
                                p3 = p2 + (p2 - p1)
                        else:
                            #self.report({'INFO'}, "n = last, slope")
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
                            #self.report({'INFO'}, "n = middle, n + 1 -> reflected")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #self.report({'INFO'}, "n = middle, (cubic (clamped)) -> spline!")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                            
                    if curveElement.points[n].handle_type == "VECTOR":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            #self.report({'INFO'}, "linear")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #self.report({'INFO'}, "n = middle, n -> reflected")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
            
                if p1.x <= x and p2.x >= x:
                    #self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, x: {x}")
                    
                    
                    
                
                    #  x: [0..1]
                    # tx: [p1.x...p2.x]
                    #tx = p1.x + x * (p2.x - p1.x)
                    
                    tx = (x - p1.x) / (p2.x - p1.x)  #AI
                    
                    #self.report({'INFO'}, f"tx: {tx}")
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

class SCENE_OT_addBranchCluster(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_branch_cluster"
    bl_label = "Add Branch Cluster"
    def execute(self, context):
                
        context.scene.treeSettings.branchClusters += 1
        branchSettings = context.scene.branchClusterSettingsList.add()
        
        bpy.ops.scene.reset_branch_cluster_curve(idx = context.scene.treeSettings.branchClusters - 1)
        
        parentClusterBoolListList = context.scene.treeSettings.parentClusterBoolListList.add()
        for b in range(0, context.scene.treeSettings.branchClusters):
            parentClusterBoolListList.value.add()
        parentClusterBoolListList.value[0].value = True
        
        branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
        
        while context.scene.treeSettings.branchClusters - 20 < len(context.scene.branchSplitHeightInLevelListList) and len(context.scene.branchSplitHeightInLevelListList) > 0:
            context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
        
        while context.scene.treeSettings.branchClusters - 20 > len(context.scene.branchSplitHeightInLevelListList):
            context.scene.branchSplitHeightInLevelListList.add()
        
        taperFactorItem = context.scene.taperFactorList.add()
        taperFactorItem.taperFactor = 1.0
        
        for leafParentClusterList in context.scene.treeSettings.leafParentClusterBoolListList:
            leafParentClusterList.value.add()
        
        return {'FINISHED'}
    
class SCENE_OT_removeBranchCluster(bpy.types.Operator):
    bl_idname = "scene.remove_branch_cluster"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        if len(context.scene.branchClusterSettingsList) > 0:
            context.scene.treeSettings.branchClusters -= 1
            context.scene.branchClusterSettingsList.remove(len(context.scene.branchClusterSettingsList) - 1)
        
        #TEMP
        #context.scene.treeSettings.branchClusters = 0
        #while len(context.scene.treeSettings.parentClusterBoolListList) > 0:
        #    self.report({'INFO'}, "removing item")
        #    listItem = context.scene.treeSettings.parentClusterBoolListList[0].value
        #    while len(listItem) > 0:
        #        listItem.remove(len(listItem) - 1)
        #        self.report({'INFO'}, "removing list item")
        #    context.scene.treeSettings.parentClusterBoolListList.remove(len(context.scene.treeSettings.parentClusterBoolListList) - 1)
        
        if len(context.scene.treeSettings.parentClusterBoolListList) > 0:
            listToClear = context.scene.treeSettings.parentClusterBoolListList[len(context.scene.treeSettings.parentClusterBoolListList) - 1].value
            lenToClear = len(listToClear)
            
            for i in range(0, lenToClear):
                listToClear.remove(len(listToClear) - 1)
                
            context.scene.treeSettings.parentClusterBoolListList.remove(len(context.scene.treeSettings.parentClusterBoolListList) - 1)
            
        if len(context.scene.branchSplitHeightInLevelListList) > 0 and context.scene.treeSettings.branchClusters > 5:
            context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
            
        if len(context.scene.taperFactorList) > 0:
            context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
          
        for leafParentClusterList in context.scene.treeSettings.leafParentClusterBoolListList:
            if len(leafParentClusterList.value) > 1:
                leafParentClusterList.value.remove(len(leafParentClusterList.value) - 1)
                
                allFalse = True
                for b in leafParentClusterList.value:
                    if b.value == True:
                        allFalse = False
                if allFalse == True:
                    leafParentClusterList.value[0].value = True
            
        return {'FINISHED'}
    
class SCENE_OT_addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_cluster"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.treeSettings.leafClusters += 1
        context.scene.leafClusterSettingsList.add()
        
        leafParentClusterBoolListList = context.scene.treeSettings.leafParentClusterBoolListList.add()
        stemBool = context.scene.treeSettings.leafParentClusterBoolListList[len(context.scene.treeSettings.leafParentClusterBoolListList) - 1].value.add()
        stemBool = True
                
        for b in range(0, len(context.scene.branchClusterSettingsList)):
            context.scene.treeSettings.leafParentClusterBoolListList[len(context.scene.treeSettings.leafParentClusterBoolListList) - 1].value.add()
        
        leafParentClusterBoolListList.value[0].value = True
        return {'FINISHED'}
    
class SCENE_OT_removeLeafItem(bpy.types.Operator):
    bl_idname = "scene.remove_leaf_cluster"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        if context.scene.treeSettings.leafClusters > 0:
            context.scene.treeSettings.leafClusters -= 1
        if len(context.scene.leafClusterSettingsList) > 0:
            context.scene.leafClusterSettingsList.remove(len(context.scene.leafClusterSettingsList) - 1)
        if len(context.scene.treeSettings.leafParentClusterBoolListList) > 0:
            context.scene.treeSettings.leafParentClusterBoolListList.remove(len(context.scene.treeSettings.leafParentClusterBoolListList) - 1)
       
        return {'FINISHED'}

    
class SCENE_OT_toggleBool(bpy.types.Operator):
    bl_idname = "scene.toggle_bool"
    bl_label = "Toggle Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.treeSettings.parentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'}

class SCENE_OT_toggleLeafBool(bpy.types.Operator):
    bl_idname = "scene.toggle_leaf_bool"
    bl_label = "Toggle Leaf Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.treeSettings.leafParentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'}

class SCENE_OT_toggleUseTaperCurveOperator(bpy.types.Operator):
    bl_idname = "scene.toggle_use_taper_curve"
    bl_label = "Use Taper Curve"
    bl_description = "resets taper curve"
    
    idx: bpy.props.IntProperty()
    
    def execute(self, context):
        settings = context.scene.branchClusterSettingsList[self.idx]
        wasEnabled = settings.useTaperCurve
        settings.useTaperCurve = not wasEnabled
        if wasEnabled:
            bpy.ops.scene.reset_branch_cluster_curve(idx = self.idx)
            
        return {'FINISHED'}
    

class SCENE_OT_addStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_stem_split_level"
    bl_label = "Add split level"
    
    def execute(self, context):
        context.scene.treeSettings.showStemSplitHeights = True
        newSplitHeight = context.scene.treeSettings.stemSplitHeightInLevelList.add()
        newSplitHeight.value = 0.5
        context.scene.treeSettings.stemSplitHeightInLevelListIndex = len(context.scene.treeSettings.stemSplitHeightInLevelList) - 1
        return {'FINISHED'}
    
class SCENE_OT_removeStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_stem_split_level"
    bl_label = "Remove split level"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.treeSettings.showStemSplitHeights = True
        if len(context.scene.treeSettings.stemSplitHeightInLevelList) > 0:
            context.scene.treeSettings.stemSplitHeightInLevelList.remove(len(context.scene.treeSettings.stemSplitHeightInLevelList) - 1)
        return {'FINISHED'}
    
class SCENE_OT_addBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_branch_split_level"
    bl_label = "Add split level"
    level: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.branchClusterSettingsList[self.level].showBranchSplitHeights = True
        
        if self.level == 0:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_0.add()
            newSplitHeight.value = 0.5
        if self.level == 1:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_1.add()
            newSplitHeight.value = 0.5
        if self.level == 2:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_2.add()
            newSplitHeight.value = 0.5
        if self.level == 3:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_3.add()
            newSplitHeight.value = 0.5
        if self.level == 4:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_4.add()
            newSplitHeight.value = 0.5
        if self.level == 5:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_5.add()
            newSplitHeight.value = 0.5
        if self.level == 6:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_6.add()
            newSplitHeight.value = 0.5
        if self.level == 7:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_7.add()
            newSplitHeight.value = 0.5
        if self.level == 8:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_8.add()
            newSplitHeight.value = 0.5
        if self.level == 9:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_9.add()
            newSplitHeight.value = 0.5
        if self.level == 10:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_10.add()
            newSplitHeight.value = 0.5
        if self.level == 11:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_11.add()
            newSplitHeight.value = 0.5
        if self.level == 12:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_12.add()
            newSplitHeight.value = 0.5
        if self.level == 13:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_13.add()
            newSplitHeight.value = 0.5
        if self.level == 14:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_14.add()
            newSplitHeight.value = 0.5
        if self.level == 15:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_15.add()
            newSplitHeight.value = 0.5
        if self.level == 16:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_16.add()
            newSplitHeight.value = 0.5
        if self.level == 17:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_17.add()
            newSplitHeight.value = 0.5
        if self.level == 18:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_18.add()
            newSplitHeight.value = 0.5
        if self.level == 19:
            newSplitHeight = context.scene.treeSettings.branchSplitHeightInLevelList_19.add()
            newSplitHeight.value = 0.5
        
        if self.level > 19:
            splitHeightList = context.scene.treeSettings.branchSplitHeightInLevelListList[self.level - 20].value
            newSplitHeight = splitHeightList.add()
            newSplitHeight.value = 0.5
            return {'FINISHED'}
        
        return {'FINISHED'}
    
class SCENE_OT_removeBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_branch_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        context.scene.branchClusterSettingsList[self.level].showBranchSplitHeights = True
        if self.level == 0:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_0) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_0.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_0) - 1)
        if self.level == 1:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_1) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_1.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_1) - 1)
        if self.level == 2:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_2) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_2.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_2) - 1)
        if self.level == 3:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_3) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_3.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_3) - 1)
        if self.level == 4:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_4) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_4.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_4) - 1)
        if self.level == 5:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_5) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_5.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_5) - 1)
        if self.level == 6:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_6) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_6.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_6) - 1)
        if self.level == 7:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_7) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_7.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_7) - 1)
        if self.level == 8:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_8) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_8.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_8) - 1)
        if self.level == 9:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_9) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_9.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_9) - 1)
        if self.level == 10:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_10) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_10.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_10) - 1)
        if self.level == 11:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_11) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_11.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_11) - 1)
        if self.level == 12:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_12) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_12.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_12) - 1)
        if self.level == 13:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_13) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_13.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_13) - 1)
        if self.level == 14:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_14) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_14.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_14) - 1)
        if self.level == 15:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_15) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_15.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_15) - 1)
        if self.level == 16:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_16) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_16.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_16) - 1)
        if self.level == 17:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_17) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_17.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_17) - 1)
        if self.level == 18:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_18) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_18.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_18) - 1)
        if self.level == 19:
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_19) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_19.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_19) - 1)
        
        if self.level > 19:
            context.scene.treeSettings.branchSplitHeightInLevelListList[self.level - 20].value.remove(len(context.scene.treeSettings.branchSplitHeightInLevelListList[self.level - 20].value) - 1)
        
        return {'FINISHED'}
    
class EXPORT_OT_exportProperties(bpy.types.Operator):
    bl_idname = "export.save_properties_file"
    bl_label = "Save Properties"
    
    def execute(self, context):
        props = context.scene  
        
        filename = props.file_name + ".json"  # Automatically append .json  
        
        filepath = os.path.join(props.folder_path, filename)
        
        props = bpy.context.scene
    
        controlPts = []
        handleTypes = []
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3]
        
        for n in range(0, len(curveElement.points)):
            controlPts.append(list(curveElement.points[n].location))
            handleTypes.append(curveElement.points[n].handle_type)
        
        nestedBranchList = []
        for cluster in props.treeSettings.parentClusterBoolListList:
            innerList = []
            for boolProp in cluster.value:
                innerList.append(boolProp.value)
            nestedBranchList.append(innerList)
            
        nestedLeafList = []
        for cluster in props.treeSettings.leafParentClusterBoolListList:
            innerLeafList = []
            for boolProp in cluster.value:
                innerLeafList.append(boolProp.value)
            nestedLeafList.append(innerLeafList)
            
        nestedBranchSplitHeightInLevelList = []
        for item in props.branchSplitHeightInLevelListList:
            innerHeightList = []
            for height in item.value:
                innerHeightList.append(height.value)
            nestedBranchSplitHeightInLevelList.append(innerHeightList)
        
        storeSplitHeights_0 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 0:
            if bpy.context.scene.branchClusterSettingsList[0].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_0):
                storeSplitHeights_0 = [props.treeSettings.branchSplitHeightInLevelList_0[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 0:
                    storeSplitHeights_0 = props.treeSettings.branchSplitHeightInLevelList_0
            
        storeSplitHeights_1 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 1:
            if bpy.context.scene.branchClusterSettingsList[1].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_1):
                storeSplitHeights_1 = [props.treeSettings.branchSplitHeightInLevelList_1[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 1:
                    storeSplitHeights_1 = props.treeSettings.branchSplitHeightInLevelList_1
                
        storeSplitHeights_2 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 2:
            if bpy.context.scene.branchClusterSettingsList[2].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_2):
                storeSplitHeights_2 = [props.treeSettings.branchSplitHeightInLevelList_2[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 2:
                    storeSplitHeights_2 = props.treeSettings.branchSplitHeightInLevelList_2
            
        storeSplitHeights_3 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 3:
            if bpy.context.scene.branchClusterSettingsList[3].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_3):
                storeSplitHeights_3 = [props.treeSettings.branchSplitHeightInLevelList_3[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 3:
                    storeSplitHeights_3 = props.treeSettings.branchSplitHeightInLevelList_3
            
        storeSplitHeights_4 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 4:
            if bpy.context.scene.branchClusterSettingsList[4].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_4):
                storeSplitHeights_4 = [props.treeSettings.branchSplitHeightInLevelList_4[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 4:
                    storeSplitHeights_4 = props.treeSettings.branchSplitHeightInLevelList_4
            
        storeSplitHeights_5 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 5:
            if bpy.context.scene.branchClusterSettingsList[5].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_5):
                storeSplitHeights_5 = [props.treeSettings.branchSplitHeightInLevelList_5[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 5:
                    storeSplitHeights_5 = props.treeSettings.branchSplitHeightInLevelList_5
        
        storeSplitHeights_6 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 6:
            if bpy.context.scene.branchClusterSettingsList[6].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_6):
                storeSplitHeights_6 = [props.treeSettings.branchSplitHeightInLevelList_6[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 6:
                    storeSplitHeights_6 = props.treeSettings.branchSplitHeightInLevelList_6
        
        storeSplitHeights_7 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 7:
            if bpy.context.scene.branchClusterSettingsList[7].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_7):
                storeSplitHeights_7 = [props.treeSettings.branchSplitHeightInLevelList_7[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 7:
                    storeSplitHeights_7 = props.treeSettings.branchSplitHeightInLevelList_7
        
        storeSplitHeights_8 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 8:
            if bpy.context.scene.branchClusterSettingsList[8].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_8):
                storeSplitHeights_8 = [props.treeSettings.branchSplitHeightInLevelList_8[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 8:
                    storeSplitHeights_5 = props.treeSettings.branchSplitHeightInLevelList_8
        
        storeSplitHeights_9 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 9:
            if bpy.context.scene.branchClusterSettingsList[9].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_9):
                storeSplitHeights_9 = [props.treeSettings.branchSplitHeightInLevelList_9[i].value for i in range(0,     bpy.context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 9:
                    storeSplitHeights_9 = props.treeSettings.branchSplitHeightInLevelList_9
    
        storeSplitHeights_10 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 10:
            if bpy.context.scene.branchClusterSettingsList[10].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_10):
                storeSplitHeights_10 = [props.treeSettings.branchSplitHeightInLevelList_10[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 10:
                    storeSplitHeights_10 = props.treeSettings.branchSplitHeightInLevelList_10
        
        storeSplitHeights_11 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 11:
            if bpy.context.scene.branchClusterSettingsList[11].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_11):
                storeSplitHeights_11 = [props.treeSettings.branchSplitHeightInLevelList_11[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 11:
                    storeSplitHeights_11 = props.treeSettings.branchSplitHeightInLevelList_11
        
        storeSplitHeights_12 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 12:
            if bpy.context.scene.branchClusterSettingsList[12].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_12):
                storeSplitHeights_12 = [props.treeSettings.branchSplitHeightInLevelList_12[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 12:
                    storeSplitHeights_12 = props.treeSettings.branchSplitHeightInLevelList_12
        
        storeSplitHeights_13 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 13:
            if bpy.context.scene.branchClusterSettingsList[13].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_13):
                storeSplitHeights_13 = [props.treeSettings.branchSplitHeightInLevelList_13[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 13:
                    storeSplitHeights_13 = props.treeSettings.branchSplitHeightInLevelList_13
        
        storeSplitHeights_14 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 14:
            if bpy.context.scene.branchClusterSettingsList[14].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_14):
                storeSplitHeights_14 = [props.treeSettings.branchSplitHeightInLevelList_14[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 14:
                    storeSplitHeights_14 = props.treeSettings.branchSplitHeightInLevelList_14
        
        storeSplitHeights_15 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 15:
            if bpy.context.scene.branchClusterSettingsList[15].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_15):
                storeSplitHeights_15 = [props.treeSettings.branchSplitHeightInLevelList_15[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 15:
                    storeSplitHeights_15 = props.treeSettings.branchSplitHeightInLevelList_15
        
        storeSplitHeights_16 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 16:
            if bpy.context.scene.branchClusterSettingsList[16].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_16):
                storeSplitHeights_16 = [props.treeSettings.branchSplitHeightInLevelList_16[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 16:
                    storeSplitHeights_16 = props.treeSettings.branchSplitHeightInLevelList_16
        
        storeSplitHeights_17 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 17:
            if bpy.context.scene.branchClusterSettingsList[17].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_17):
                storeSplitHeights_17 = [props.treeSettings.branchSplitHeightInLevelList_17[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 17:
                    storeSplitHeights_17 = props.treeSettings.branchSplitHeightInLevelList_17
        
        storeSplitHeights_18 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 18:
            if bpy.context.scene.branchClusterSettingsList[18].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_18):
                storeSplitHeights_18 = [props.treeSettings.branchSplitHeightInLevelList_18[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 18:
                    storeSplitHeights_18 = props.treeSettings.branchSplitHeightInLevelList_18
        
        storeSplitHeights_19 = []
        if len(bpy.context.scene.branchClusterSettingsList) > 19:
            if bpy.context.scene.branchClusterSettingsList[19].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_19):
                storeSplitHeights_19 = [props.treeSettings.branchSplitHeightInLevelList_19[i].value for i in range(0,   bpy.context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1)]
            else:
                if len(props.branchClusterSettingsList) > 19:
                    storeSplitHeights_19 = props.treeSettings.branchSplitHeightInLevelList_19
        
        clusterTaperControlPts = []
        clusterTaperCurveHandleTypes = []
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
            
        for clusterIndex in range(props.treeSettings.branchClusters):
            curve_name = panels.ensure_branch_curve_node(tree_generator, clusterIndex)
            curveElement = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.curves[3]
            clusterTaperControlPts.append([])
            clusterTaperCurveHandleTypes.append([])
            for i in range(0, len(curveElement.points)):
                clusterTaperControlPts[clusterIndex].append(curveElement.points[i].location)
                clusterTaperCurveHandleTypes[clusterIndex].append(curveElement.points[i].handle_type)
        
        data = {
            "treeHeight": props.treeSettings.treeHeight,
            "treeGrowDir": list(props.treeSettings.treeGrowDir),
            "taper": props.treeSettings.taper,
            
            "taperCurvePoints": [list(pt.location) for pt in nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3].points],
            "taperCurveHandleTypes": [pt.handle_type for pt in nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3].points],
            
            "clusterTaperCurvePoints": [list(list(pt) for pt in clusterTaperPoints) for clusterTaperPoints in clusterTaperControlPts],
            "clusterTaperCurveHandleTypes": [list(clusterTaperHandles) for clusterTaperHandles in clusterTaperCurveHandleTypes],
            
            "branchTipRadius": props.treeSettings.branchTipRadius,
            "ringSpacing": props.treeSettings.ringSpacing,
            "stemRingResolution": props.treeSettings.stemRingResolution,
            "resampleDistance": props.treeSettings.resampleDistance,
            
            "noiseAmplitudeVertical": props.treeSettings.noiseAmplitudeVertical,
            "noiseAmplitudeHorizontal": props.treeSettings.noiseAmplitudeHorizontal,
            "noiseAmplitudeGradient": props.treeSettings.noiseAmplitudeGradient,
            "noiseAmplitudeExponent": props.treeSettings.noiseAmplitudeExponent,
            "noiseScale": props.treeSettings.noiseScale,
            "seed": props.treeSettings.seed,
            
            "curvatureStart": props.treeSettings.curvatureStart,
            "curvatureEnd": props.treeSettings.curvatureEnd,
            
            "nrSplits": props.treeSettings.nrSplits,
            "variance": props.treeSettings.variance,
            "stemSplitMode": props.treeSettings.stemSplitMode,
            "stemSplitRotateAngle": props.treeSettings.stemSplitRotateAngle,
            "curvOffsetStrength": props.treeSettings.curvOffsetStrength,
            
            "stemSplitHeightInLevelList": [item.value for item in props.treeSettings.stemSplitHeightInLevelList],
            "stemSplitHeightInLevelListIndex": props.treeSettings.stemSplitHeightInLevelListIndex,
            
            "splitHeightVariation": props.treeSettings.splitHeightVariation,
            "splitLengthVariation": props.treeSettings.splitLengthVariation,
            "stemSplitAngle": props.treeSettings.stemSplitAngle,
            "stemSplitPointAngle": props.treeSettings.stemSplitPointAngle,
            
            "branchClusters": props.treeSettings.branchClusters,
            "showBranchClusterList": [props.branchClusterBoolListList[i].show_branch_cluster for i in range(props.treeSettings.branchClusters)],
            "showParentClusterList": [props.treeSettings.parentClusterBoolListList[i].show_cluster for i in range(props.treeSettings.branchClusters)],
            
            "parentClusterBoolListList": nestedBranchList,
            
            "nrBranchesList": [props.branchClusterSettingsList[i].nrBranches for i in range(props.treeSettings.branchClusters)],
            "treeShapeList": [props.branchClusterSettingsList[i].treeShape.value for i in range(props.treeSettings.branchClusters)],
            "branchShapeList": [props.branchClusterSettingsList[i].branchShape.value for i in range(props.treeSettings.branchClusters)],
            "branchTypeList": [props.branchClusterSettingsList[i].branchType.value for i in range(props.treeSettings.branchClusters)],
            "branchWhorlCountStartList": [props.branchClusterSettingsList[i].branchWhorlCountStart for i in range(props.treeSettings.branchClusters)],
            "branchWhorlCountEndList": [props.branchClusterSettingsList[i].branchWhorlCountEnd for i in range(props.treeSettings.branchClusters)],
            "relBranchLengthList": [props.branchClusterSettingsList[i].relBranchLength for i in range(props.treeSettings.branchClusters)],
            "relBranchLengthVariationList": [props.branchClusterSettingsList[i].relBranchLengthVariation for i in range(props.treeSettings.branchClusters)],
            "taperFactorList": [props.taperFactorList[i].taperFactor for i in range(props.treeSettings.branchClusters)],
            "useTaperCurveList": [props.branchClusterSettingsList[i].useTaperCurve for i in range(props.treeSettings.branchClusters)],
            "ringResolutionList": [props.branchClusterSettingsList[i].ringResolution for i in range(props.treeSettings.branchClusters)],
            "branchesStartHeightGlobalList": [props.branchClusterSettingsList[i].branchesStartHeightGlobal for i in range(props.treeSettings.branchClusters)],
            "branchesEndHeightGlobalList": [props.branchClusterSettingsList[i].branchesEndHeightGlobal for i in range(props.treeSettings.branchClusters)],
            "branchesStartHeightClusterList": [props.branchClusterSettingsList[i].branchesStartHeightCluster for i in range(props.treeSettings.branchClusters)],
            "branchesEndHeightClusterList": [props.branchClusterSettingsList[i].branchesEndHeightCluster for i in range(props.treeSettings.branchClusters)],
            "branchesStartPointVariationList": [props.branchClusterSettingsList[i].branchesStartPointVariation for i in range(props.treeSettings.branchClusters)],
            
            "showNoiseSettingsList": [props.branchClusterSettingsList[i].showNoiseSettings for i in range(props.treeSettings.branchClusters)],
            
            "noiseAmplitudeHorizontalList": [props.branchClusterSettingsList[i].noiseAmplitudeHorizontalBranch for i in range(props.treeSettings.branchClusters)],
            "noiseAmplitudeVerticalList": [props.branchClusterSettingsList[i].noiseAmplitudeVerticalBranch for i in range(props.treeSettings.branchClusters)],
            "noiseAmplitudeGradientList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchGradient for i in range(props.treeSettings.branchClusters)],
            "noiseAmplitudeExponentList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchExponent for i in range(props.treeSettings.branchClusters)],
            "noiseScaleList": [props.branchClusterSettingsList[i].noiseScale for i in range(props.treeSettings.branchClusters)],
            
            "showAngleSettingsList": [props.branchClusterSettingsList[i].showAngleSettings for i in range(props.treeSettings.branchClusters)],
            
            "verticalAngleCrownStartList": [props.branchClusterSettingsList[i].verticalAngleCrownStart for i in range(props.treeSettings.branchClusters)],
            "verticalAngleCrownEndList": [props.branchClusterSettingsList[i].verticalAngleCrownEnd for i in range(props.treeSettings.branchClusters)],
            "verticalAngleBranchStartList": [props.branchClusterSettingsList[i].verticalAngleBranchStart for i in range(props.treeSettings.branchClusters)],
            "verticalAngleBranchEndList": [props.branchClusterSettingsList[i].verticalAngleBranchEnd for i in range(props.treeSettings.branchClusters)],
            "branchAngleModeList": [props.branchClusterSettingsList[i].branchAngleMode.value for i in range(props.treeSettings.branchClusters)],
            "useFibonacciAnglesList": [props.branchClusterSettingsList[i].useFibonacciAngles for i in range(props.treeSettings.branchClusters)],
            "fibonacciNr": [props.branchClusterSettingsList[i].fibonacciNr.fibonacci_nr for i in range(props.treeSettings.branchClusters)],
            "rotateAngleRangeList": [props.branchClusterSettingsList[i].rotateAngleRange for i in range(props.treeSettings.branchClusters)],
            "rotateAngleOffsetList": [props.branchClusterSettingsList[i].rotateAngleOffset for i in range(props.treeSettings.branchClusters)],
            
            "rotateAngleCrownStartList": [props.branchClusterSettingsList[i].rotateAngleCrownStart for i in range(props.treeSettings.branchClusters)],
            "rotateAngleCrownEndList": [props.branchClusterSettingsList[i].rotateAngleCrownEnd for i in range(props.treeSettings.branchClusters)],
            "rotateAngleBranchStartList": [props.branchClusterSettingsList[i].rotateAngleBranchStart for i in range(props.treeSettings.branchClusters)],
            "rotateAngleBranchEndList": [props.branchClusterSettingsList[i].rotateAngleBranchEnd for i in range(props.treeSettings.branchClusters)],
            "rotateAngleRangeFactorList": [props.branchClusterSettingsList[i].rotateAngleRangeFactor for i in range(props.treeSettings.branchClusters)],
            
            "reducedCurveStepCutoffList": [props.branchClusterSettingsList[i].reducedCurveStepCutoff for i in range(props.treeSettings.branchClusters)],
            "reducedCurveStepFactorList": [props.branchClusterSettingsList[i].reducedCurveStepFactor for i in range(props.treeSettings.branchClusters)],
            
            "branchGlobalCurvatureStartList": [props.branchClusterSettingsList[i].branchGlobalCurvatureStart for i in range(props.treeSettings.branchClusters)],
            "branchGlobalCurvatureEndList": [props.branchClusterSettingsList[i].branchGlobalCurvatureEnd for i in range(props.treeSettings.branchClusters)],
            "branchCurvatureStartList": [props.branchClusterSettingsList[i].branchCurvatureStart for i in range(props.treeSettings.branchClusters)],
            "branchCurvatureEndList": [props.branchClusterSettingsList[i].branchCurvatureEnd for i in range(props.treeSettings.branchClusters)],
            "branchCurvatureOffsetStrengthList": [props.branchClusterSettingsList[i].branchCurvatureOffsetStrength for i in     range(props.treeSettings.branchClusters)],
            
            "showSplitSettingsList": [props.branchClusterSettingsList[i].showSplitSettings for i in range(props.treeSettings.branchClusters)],
            
            "nrSplitsPerBranchList": [props.branchClusterSettingsList[i].nrSplitsPerBranch for i in range(props.treeSettings.branchClusters)],
            "branchSplitModeList": [props.branchClusterSettingsList[i].branchSplitMode.value for i in range(props.treeSettings.branchClusters)],
            "branchSplitRotateAngleList": [props.branchClusterSettingsList[i].branchSplitRotateAngle for i in range(props.treeSettings.branchClusters)],
            "branchSplitAxisVariationList": [props.branchClusterSettingsList[i].branchSplitAxisVariation for i in range(props.treeSettings.branchClusters)],
            
            "branchSplitAngleList": [props.branchClusterSettingsList[i].branchSplitAngle for i in range(props.treeSettings.branchClusters)],
            "branchSplitPointAngleList": [props.branchClusterSettingsList[i].branchSplitPointAngle for i in range(props.treeSettings.branchClusters)],
            
            "splitsPerBranchVariationList": [props.branchClusterSettingsList[i].splitsPerBranchVariation for i in range(props.treeSettings.branchClusters)],
            "branchVarianceList": [props.branchClusterSettingsList[i].branchVariance for i in range(props.treeSettings.branchClusters)],
            "outwardAttractionList": [props.branchClusterSettingsList[i].outwardAttraction for i in range(props.treeSettings.branchClusters)],
            "branchSplitHeightVariationList": [props.branchClusterSettingsList[i].branchSplitHeightVariation for i in range(props.treeSettings.branchClusters)],
            "branchSplitLengthVariationList": [props.branchClusterSettingsList[i].branchSplitLengthVariation for i in range(props.treeSettings.branchClusters)],
            
            "showBranchSplitHeights": [props.branchClusterSettingsList[i].showBranchSplitHeights for i in range(props.treeSettings.branchClusters)],
            
            "branchSplitHeightInLevelListIndex": props.treeSettings.branchSplitHeightInLevelListIndex,
            #------
            "branchSplitHeightInLevelList_0": storeSplitHeights_0,
            "branchSplitHeightInLevelListIndex_0": props.treeSettings.branchSplitHeightInLevelListIndex_0,
            
            "branchSplitHeightInLevelList_1": storeSplitHeights_1,
            "branchSplitHeightInLevelListIndex_1": props.treeSettings.branchSplitHeightInLevelListIndex_1,
            
            "branchSplitHeightInLevelList_2": storeSplitHeights_2,
            "branchSplitHeightInLevelListIndex_2": props.treeSettings.branchSplitHeightInLevelListIndex_2,
            
            "branchSplitHeightInLevelList_3": storeSplitHeights_3,
            "branchSplitHeightInLevelListIndex_3": props.treeSettings.branchSplitHeightInLevelListIndex_3,
            
            "branchSplitHeightInLevelList_4": storeSplitHeights_4,
            "branchSplitHeightInLevelListIndex_4": props.treeSettings.branchSplitHeightInLevelListIndex_4,
            
            "branchSplitHeightInLevelList_5": storeSplitHeights_5,
            "branchSplitHeightInLevelListIndex_5": props.treeSettings.branchSplitHeightInLevelListIndex_5,
            
            "branchSplitHeightInLevelList_6": storeSplitHeights_6,
            "branchSplitHeightInLevelListIndex_6": props.treeSettings.branchSplitHeightInLevelListIndex_6,
            
            "branchSplitHeightInLevelList_7": storeSplitHeights_7,
            "branchSplitHeightInLevelListIndex_7": props.treeSettings.branchSplitHeightInLevelListIndex_7,
            
            "branchSplitHeightInLevelList_8": storeSplitHeights_8,
            "branchSplitHeightInLevelListIndex_8": props.treeSettings.branchSplitHeightInLevelListIndex_8,
            
            "branchSplitHeightInLevelList_9": storeSplitHeights_5,
            "branchSplitHeightInLevelListIndex_9": props.treeSettings.branchSplitHeightInLevelListIndex_9,
            
            "branchSplitHeightInLevelList_10": storeSplitHeights_10,
            "branchSplitHeightInLevelListIndex_10": props.treeSettings.branchSplitHeightInLevelListIndex_10,
            
            "branchSplitHeightInLevelList_11": storeSplitHeights_11,
            "branchSplitHeightInLevelListIndex_11": props.treeSettings.branchSplitHeightInLevelListIndex_11,
            
            "branchSplitHeightInLevelList_12": storeSplitHeights_12,
            "branchSplitHeightInLevelListIndex_12": props.treeSettings.branchSplitHeightInLevelListIndex_12,
            
            "branchSplitHeightInLevelList_13": storeSplitHeights_13,
            "branchSplitHeightInLevelListIndex_13": props.treeSettings.branchSplitHeightInLevelListIndex_13,
            
            "branchSplitHeightInLevelList_14": storeSplitHeights_14,
            "branchSplitHeightInLevelListIndex_14": props.treeSettings.branchSplitHeightInLevelListIndex_14,
            
            "branchSplitHeightInLevelList_15": storeSplitHeights_15,
            "branchSplitHeightInLevelListIndex_15": props.treeSettings.branchSplitHeightInLevelListIndex_15,
            
            "branchSplitHeightInLevelList_16": storeSplitHeights_16,
            "branchSplitHeightInLevelListIndex_16": props.treeSettings.branchSplitHeightInLevelListIndex_16,
            
            "branchSplitHeightInLevelList_17": storeSplitHeights_17,
            "branchSplitHeightInLevelListIndex_17": props.treeSettings.branchSplitHeightInLevelListIndex_17,
            
            "branchSplitHeightInLevelList_18": storeSplitHeights_18,
            "branchSplitHeightInLevelListIndex_18": props.treeSettings.branchSplitHeightInLevelListIndex_18,
            
            "branchSplitHeightInLevelList_19": storeSplitHeights_19,
            "branchSplitHeightInLevelListIndex_19": props.treeSettings.branchSplitHeightInLevelListIndex_19,
            
            "branchSplitHeightInLevelListList": nestedBranchSplitHeightInLevelList,
            
            "showLeafSettings": [props.leafClusterSettingsList[i].showLeafSettings for i in range(props.treeSettings.leafClusters)],
            #------------
            "leavesDensityList": [props.leafClusterSettingsList[i].leavesDensity for i in range(props.treeSettings.leafClusters)],
            "leafSizeList": [props.leafClusterSettingsList[i].leafSize for i in range(props.treeSettings.leafClusters)],
            "leafAspectRatioList": [props.leafClusterSettingsList[i].leafAspectRatio for i in range(props.treeSettings.leafClusters)],
            "leafStartHeightGlobalList": [props.leafClusterSettingsList[i].leafStartHeightGlobal for i in range(props.treeSettings.leafClusters)],
            "leafEndHeightGlobalList": [props.leafClusterSettingsList[i].leafEndHeightGlobal for i in range(props.treeSettings.leafClusters)],
            "leafStartHeightClusterList": [props.leafClusterSettingsList[i].leafStartHeightCluster for i in range(props.treeSettings.leafClusters)],
            "leafEndHeightClusterList": [props.leafClusterSettingsList[i].leafEndHeightCluster for i in range(props.treeSettings.leafClusters)],
            "leafTypeList": [props.leafClusterSettingsList[i].leafType.value for i in range(props.treeSettings.leafClusters)],
            "leafWhorlCountList": [props.leafClusterSettingsList[i].leafWhorlCount for i in range(props.treeSettings.leafClusters)],
            "leafAngleModeList": [props.leafClusterSettingsList[i].leafAngleMode.value for i in range(props.treeSettings.leafClusters)],
            
            "leafVerticalAngleBranchStartList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchStart for i in range(props.treeSettings.leafClusters)],
            "leafVerticalAngleBranchEndList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
            "leafRotateAngleBranchStartList": [props.leafClusterSettingsList[i].leafRotateAngleBranchStart for i in range(props.treeSettings.leafClusters)],
            "leafRotateAngleBranchEndList": [props.leafClusterSettingsList[i].leafRotateAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
            "leafTiltAngleBranchStartList": [props.leafClusterSettingsList[i].leafTiltAngleBranchStart for i in range(props.treeSettings.leafClusters)],
            "leafTiltAngleBranchEndList": [props.leafClusterSettingsList[i].leafTiltAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
            
            "showLeafClusterList": [props.treeSettings.leafParentClusterBoolListList[i].show_leaf_cluster for  i in range(len(props.treeSettings.leafParentClusterBoolListList))],
            "leafParentClusterBoolListList": nestedLeafList
        }

        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        #self.report({'INFO'}, f'Saved properties to {filepath}')
        return {'FINISHED'}
    
class EXPORT_OT_importProperties(bpy.types.Operator):
    bl_idname = "export.load_properties_file"
    bl_label = "Load Properties"
    
    def execute(self, context):
        scene = context.scene
        filename = scene.file_name + ".json"  # Automatically append .json  
        
        filepath = os.path.join(scene.folder_path, filename)
        
        while len(scene.branchClusterSettingsList) > 0:
            bpy.ops.scene.remove_branch_cluster()
        while len(scene.leafClusterSettingsList) > 0:
            bpy.ops.scene.remove_leaf_cluster()
            self.report({'INFO'}, f"after scene.remove_leaf_cluster(), llen(scene.leafClusterSettingsList): {len(scene.leafClusterSettingsList)}")

        scene.treeSettings.leafParentClusterBoolListList.clear() # TEST

        self.report({'INFO'}, f"in importProperties (before init_properties): nrLeafClusters: {len(scene.leafClusterSettingsList)}") # 0 (OK)
        with open(filepath, 'r') as f:
            data = json.load(f)
            scene = context.scene
            init_properties(data, scene, self)

            # synchronise leafParentClusterBoolListList
            

            leafParentClusterListLength = len(scene.treeSettings.leafParentClusterBoolListList)
            self.report({'INFO'}, f"in importProperties: len(scene.treeSettings.leafParentClusterBoolListList: {leafParentClusterListLength})") # 1 (OK)

            nrLeafClusters = len(scene.leafClusterSettingsList)
            self.report({'INFO'}, f"in importProperties (after init_properties): nrLeafClusters: {nrLeafClusters}") # 2 # ERROR HERE !!!

            while len(scene.treeSettings.leafParentClusterBoolListList) < nrLeafClusters:
                bpy.ops.scene.add_leaf_cluster()
            
            while len(scene.leafClusterSettingsList) < len(scene.treeSettings.leafParentClusterBoolListList):
                scene.leafParentClusterBoolListList.remove(scene.treeSettings.leafParentClusterBoolListList[len(scene.treeSettings.leafParentClusterBoolListList) - 1])

            scene.treeSettings.leafClusters = 0#len(scene.treeSettings.leafParentClusterBoolListList)

            # Synchronize the parent bool list with the number of leaf clusters
            while len(scene.treeSettings.leafParentClusterBoolListList) < nrLeafClusters:
                # Add a new collection item directly
                scene.treeSettings.leafParentClusterBoolListList.add()

            # Optional: If you need to remove extra entries (for robust loading)
            while len(scene.treeSettings.leafParentClusterBoolListList) > nrLeafClusters:
                # Remove the last item in the collection
                scene.treeSettings.leafParentClusterBoolListList.remove(len(scene.treeSettings.leafParentClusterBoolListList) - 1)

        return {'FINISHED'}

        
        
class EXPORT_OT_loadPreset(bpy.types.Operator):
    bl_idname = "export.load_preset"
    bl_label = "Load Preset"
    
    def execute(self, context):
        scene = context.scene
        #self.report({'INFO'}, "in operator loadPreset")
        
        scene.branchClusterSettingsList.clear() 
        scene.treeSettings.branchClusterSettingsListIndex = 0 

        scene.leafClusterSettingsList.clear()
        scene.treeSettings.leafClusterSettingsListIndex = 0

        load_preset(scene.treeSettings.treePreset.value, context, self)

        return {'FINISHED'}
    
def load_preset(preset, context, self):
    #self.report({'INFO'}, f"in load_preset(): preset: {preset}")
    if preset == 'TREE1':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.14000000059604645, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"], ["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 1.2300000190734863, "noiseAmplitudeHorizontal": 1.2000000476837158, "noiseAmplitudeGradient": 0.35999998450279236, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 0.3100000321865082, "seed": 1484, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 1, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125], "stemSplitHeightInLevelListIndex": 0, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.07000000029802322, "stemSplitPointAngle": 0.25999999046325684, "branchClusters": 2, "showBranchClusterList": [true, true], "showParentClusterList": [true, true], "parentClusterBoolListList": [[true], [false, true]], "nrBranchesList": [37, 68], "treeShapeList": ["INVERSE_HEMISPHERICAL", "INVERSE_HEMISPHERICAL"], "branchShapeList": ["CYLINDRICAL", "CYLINDRICAL"], "branchTypeList": ["SINGLE", "SINGLE"], "branchWhorlCountStartList": [12, 3], "branchWhorlCountEndList": [3, 3], "relBranchLengthList": [0.5138890147209167, 0.2569444477558136], "relBranchLengthVariationList": [0.0694444477558136, 0.0], "taperFactorList": [0.8402778506278992, 0.8402777910232544], "useTaperCurveList": [false, false], "ringResolutionList": [6, 5], "branchesStartHeightGlobalList": [0.1666666716337204, 0.0], "branchesEndHeightGlobalList": [0.9166666865348816, 1.0], "branchesStartHeightClusterList": [0.0, 0.0416666679084301], "branchesEndHeightClusterList": [0.875, 0.340277761220932], "branchesStartPointVariationList": [0.0, 0.0], "showNoiseSettingsList": [true, true], "noiseAmplitudeHorizontalList": [0.0, 0.0], "noiseAmplitudeVerticalList": [0.0, 0.0], "noiseAmplitudeGradientList": [0.0, 0.0], "noiseAmplitudeExponentList": [1.0, 1.0], "noiseScaleList": [1.0, 1.0], "showAngleSettingsList": [true, true], "verticalAngleCrownStartList": [1.2400000095367432, 0.7850000262260437], "verticalAngleCrownEndList": [0.44999998807907104, 0.7850000262260437], "verticalAngleBranchStartList": [0.0, 0.0], "verticalAngleBranchEndList": [0.0, 0.0], "branchAngleModeList": ["WINDING", "SYMMETRIC"], "useFibonacciAnglesList": [false, true], "fibonacciNr": [40, 5], "rotateAngleRangeList": [6.2831854820251465, 3.140000104904175], "rotateAngleOffsetList": [1.5700000524520874, 0.0], "rotateAngleCrownStartList": [2.480001211166382, -0.17000000178813934], "rotateAngleCrownEndList": [2.480001211166382, -0.23999999463558197], "rotateAngleBranchStartList": [0.0, 0.0], "rotateAngleBranchEndList": [0.0, 0.0], "rotateAngleRangeFactorList": [1.0, 1.0], "reducedCurveStepCutoffList": [0.0, 0.0], "reducedCurveStepFactorList": [0.0, 0.0], "branchGlobalCurvatureStartList": [0.0, 0.0], "branchGlobalCurvatureEndList": [0.0, 0.0], "branchCurvatureStartList": [-0.057999998331069946, 0.012000000104308128], "branchCurvatureEndList": [0.03999999910593033, 0.024000000208616257], "branchCurvatureOffsetStrengthList": [0.0, 0.0], "showSplitSettingsList": [true, true], "nrSplitsPerBranchList": [7.980000019073486, 2.369999885559082], "branchSplitModeList": ["HORIZONTAL", "HORIZONTAL"], "branchSplitRotateAngleList": [0.0, 0.0], "branchSplitAxisVariationList": [0.5399997234344482, 0.44999998807907104], "branchSplitAngleList": [0.25999999046325684, 0.27000001072883606], "branchSplitPointAngleList": [0.17000000178813934, 0.17000000178813934], "splitsPerBranchVariationList": [0.0, 0.0], "branchVarianceList": [0.0, 0.0], "outwardAttractionList": [0.0, 0.0], "branchSplitHeightVariationList": [0.38129496574401855, 0.0], "branchSplitLengthVariationList": [0.1366906315088272, 0.0], "showBranchSplitHeights": [false, true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.2371794879436493, 0.2756410241127014, 0.3333333134651184, 0.5], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [0.5458715558052063, 0.3205128014087677, 0.23076921701431274], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props, self)
        
    if preset == 'TREE2':
        f = '{"treeHeight": 5.0, "treeGrowDir": [0.0, 0.0, 1.0], "taper": 0.15000000596046448, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 0.0], [1.0, 1.0]]], "clusterTaperCurveHandleTypes": [["AUTO", "AUTO"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 0.10000000149011612, "stemRingResolution": 16, "resampleDistance": 0.4599999785423279, "noiseAmplitudeVertical": 0.0, "noiseAmplitudeHorizontal": 0.0, "noiseAmplitudeGradient": 0.7799999713897705, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 1.0, "seed": 832, "curvatureStart": 0.0, "curvatureEnd": 0.03400000184774399, "nrSplits": 3, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5], "stemSplitHeightInLevelListIndex": 0, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.33000001311302185, "stemSplitPointAngle": 0.25999999046325684, "branchClusters": 1, "showBranchClusterList": [true], "showParentClusterList": [true], "parentClusterBoolListList": [[true]], "nrBranchesList": [30], "treeShapeList": ["CONICAL"], "branchShapeList": ["INVERSE_CONICAL"], "branchTypeList": ["SINGLE"], "branchWhorlCountStartList": [3], "branchWhorlCountEndList": [3], "relBranchLengthList": [1.0], "relBranchLengthVariationList": [0.0], "taperFactorList": [0.7361111044883728], "useTaperCurveList": [false], "ringResolutionList": [6], "branchesStartHeightGlobalList": [0.4652777314186096], "branchesEndHeightGlobalList": [0.8680555820465088], "branchesStartHeightClusterList": [0.0], "branchesEndHeightClusterList": [1.0], "branchesStartPointVariationList": [0.0], "showNoiseSettingsList": [true], "noiseAmplitudeHorizontalList": [0.0], "noiseAmplitudeVerticalList": [0.0], "noiseAmplitudeGradientList": [0.0], "noiseAmplitudeExponentList": [1.0], "noiseScaleList": [1.0], "showAngleSettingsList": [true], "verticalAngleCrownStartList": [-0.7699999809265137], "verticalAngleCrownEndList": [-0.6800000071525574], "verticalAngleBranchStartList": [0.0], "verticalAngleBranchEndList": [0.0], "branchAngleModeList": ["WINDING"], "useFibonacciAnglesList": [false], "fibonacciNr": [3], "rotateAngleRangeList": [3.6600000858306885], "rotateAngleOffsetList": [-1.5700000524520874], "rotateAngleCrownStartList": [4.429999828338623], "rotateAngleCrownEndList": [5.300000190734863], "rotateAngleBranchStartList": [0.0], "rotateAngleBranchEndList": [0.0], "rotateAngleRangeFactorList": [1.0], "reducedCurveStepCutoffList": [0.0], "reducedCurveStepFactorList": [0.0], "branchGlobalCurvatureStartList": [0.0], "branchGlobalCurvatureEndList": [0.0], "branchCurvatureStartList": [0.0], "branchCurvatureEndList": [-0.061000000685453415], "branchCurvatureOffsetStrengthList": [0.0], "showSplitSettingsList": [true], "nrSplitsPerBranchList": [1.0], "branchSplitModeList": ["HORIZONTAL"], "branchSplitRotateAngleList": [0.0], "branchSplitAxisVariationList": [0.0], "branchSplitAngleList": [0.4359999895095825], "branchSplitPointAngleList": [0.4359999895095825], "splitsPerBranchVariationList": [0.0], "branchVarianceList": [0.0], "outwardAttractionList": [0.11510791629552841], "branchSplitHeightVariationList": [0.0], "branchSplitLengthVariationList": [0.17266187071800232], "showBranchSplitHeights": [true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true]]}'
        data = json.loads(f)
        #self.report({'INFO'}, f"in load_preset(): TREE2: data.treeHeight: {data.treeHeight}")
        props = context.scene
        init_properties(data, props, self)
        
    if preset == 'MAPLE':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.14000000059604645, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"], ["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 1.2300000190734863, "noiseAmplitudeHorizontal": 1.2000000476837158, "noiseAmplitudeGradient": 0.35999998450279236, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 0.3100000321865082, "seed": 1567, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 2, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.4143102467060089, 0.14462800323963165], "stemSplitHeightInLevelListIndex": 1, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.07119999825954437, "stemSplitPointAngle": 0.27379998564720154, "branchClusters": 2, "showBranchClusterList": [true, true], "showParentClusterList": [true, true], "parentClusterBoolListList": [[true], [false, true]], "nrBranchesList": [37, 68], "treeShapeList": ["INVERSE_HEMISPHERICAL", "INVERSE_HEMISPHERICAL"], "branchShapeList": ["CYLINDRICAL", "CYLINDRICAL"], "branchTypeList": ["SINGLE", "SINGLE"], "branchWhorlCountStartList": [12, 3], "branchWhorlCountEndList": [3, 3], "relBranchLengthList": [0.5138890147209167, 0.2569444477558136], "relBranchLengthVariationList": [0.0694444477558136, 0.0], "taperFactorList": [0.8402778506278992, 0.8402777910232544], "useTaperCurveList": [true, false], "ringResolutionList": [6, 5], "branchesStartHeightGlobalList": [0.19351230561733246, 0.0], "branchesEndHeightGlobalList": [0.9166666865348816, 1.0], "branchesStartHeightClusterList": [0.0, 0.05508948862552643], "branchesEndHeightClusterList": [0.875, 0.340277761220932], "branchesStartPointVariationList": [0.0, 0.0], "showNoiseSettingsList": [true, true], "noiseAmplitudeHorizontalList": [0.0, 0.0], "noiseAmplitudeVerticalList": [0.0, 0.0], "noiseAmplitudeGradientList": [0.0, 0.0], "noiseAmplitudeExponentList": [1.0, 1.0], "noiseScaleList": [1.0, 1.0], "showAngleSettingsList": [true, true], "verticalAngleCrownStartList": [0.879800021648407, 0.7850000262260437], "verticalAngleCrownEndList": [0.5440000295639038, 0.7850000262260437], "verticalAngleBranchStartList": [0.0, 0.0], "verticalAngleBranchEndList": [0.0, 0.0], "branchAngleModeList": ["ADAPTIVE", "SYMMETRIC"], "useFibonacciAnglesList": [false, true], "fibonacciNr": [40, 5], "rotateAngleRangeList": [6.28000020980835, 6.28000020980835], "rotateAngleOffsetList": [1.5700000524520874, 0.0], "rotateAngleCrownStartList": [1.2209999561309814, -0.1745000034570694], "rotateAngleCrownEndList": [1.2389999628067017, -0.22599999606609344], "rotateAngleBranchStartList": [0.0, 0.0], "rotateAngleBranchEndList": [0.0, 0.0], "rotateAngleRangeFactorList": [1.0, 1.0], "reducedCurveStepCutoffList": [0.010000020265579224, 0.0], "reducedCurveStepFactorList": [0.0, 0.0], "branchGlobalCurvatureStartList": [0.0, 0.0], "branchGlobalCurvatureEndList": [0.0, 0.0], "branchCurvatureStartList": [-0.05700000002980232, 0.011300000362098217], "branchCurvatureEndList": [0.040800001472234726, 0.026100000366568565], "branchCurvatureOffsetStrengthList": [0.0, 0.0], "showSplitSettingsList": [true, true], "nrSplitsPerBranchList": [7.980000019073486, 2.369999885559082], "branchSplitModeList": ["HORIZONTAL", "HORIZONTAL"], "branchSplitRotateAngleList": [0.0, 0.0], "branchSplitAxisVariationList": [0.5399997234344482, 0.44999998807907104], "branchSplitAngleList": [0.2660999894142151, 0.2661600112915039], "branchSplitPointAngleList": [0.17880000174045563, 0.17890000343322754], "splitsPerBranchVariationList": [0.0, 0.0], "branchVarianceList": [0.0, 0.0], "outwardAttractionList": [0.0, 0.0], "branchSplitHeightVariationList": [0.38129496574401855, 0.0], "branchSplitLengthVariationList": [0.1366906315088272, 0.0], "showBranchSplitHeights": [true, true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.4166666567325592, 0.4166666567325592, 0.2300613522529602, 0.4166666567325592], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [0.4082568883895874, 0.3205128014087677, 0.23076921701431274], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props, self)
        
    if preset == 'SILVER_BIRCH':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.11999999731779099, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 0.0, "noiseAmplitudeHorizontal": 0.0, "noiseAmplitudeGradient": 0.0, "noiseAmplitudeExponent": 0.0, "noiseScale": 1.0, "seed": 1787, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 0, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5], "stemSplitHeightInLevelListIndex": 5, "splitHeightVariation": 0.11999999731779099, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.29580000042915344, "stemSplitPointAngle": 0.27379998564720154, "branchClusters": 1, "showBranchClusterList": [true], "showParentClusterList": [true], "parentClusterBoolListList": [[true]], "nrBranchesList": [24], "treeShapeList": ["INVERSE_CONICAL"], "branchShapeList": ["CYLINDRICAL"], "branchTypeList": ["SINGLE"], "branchWhorlCountStartList": [3], "branchWhorlCountEndList": [3], "relBranchLengthList": [0.5838925838470459], "relBranchLengthVariationList": [0.0], "taperFactorList": [0.8120805621147156], "useTaperCurveList": [false], "ringResolutionList": [6], "branchesStartHeightGlobalList": [0.24161073565483093], "branchesEndHeightGlobalList": [0.9127516746520996], "branchesStartHeightClusterList": [0.0], "branchesEndHeightClusterList": [1.0], "branchesStartPointVariationList": [0.0], "showNoiseSettingsList": [true], "noiseAmplitudeHorizontalList": [0.0], "noiseAmplitudeVerticalList": [0.0], "noiseAmplitudeGradientList": [0.0], "noiseAmplitudeExponentList": [1.0], "noiseScaleList": [1.0], "showAngleSettingsList": [true], "verticalAngleCrownStartList": [1.417330026626587], "verticalAngleCrownEndList": [-0.09004999697208405], "verticalAngleBranchStartList": [0.0], "verticalAngleBranchEndList": [0.0], "branchAngleModeList": ["WINDING"], "useFibonacciAnglesList": [true], "fibonacciNr": [6], "rotateAngleRangeList": [3.1415927410125732], "rotateAngleOffsetList": [0.0], "rotateAngleCrownStartList": [0.0], "rotateAngleCrownEndList": [0.0], "rotateAngleBranchStartList": [0.0], "rotateAngleBranchEndList": [0.0], "rotateAngleRangeFactorList": [1.0], "reducedCurveStepCutoffList": [0.0], "reducedCurveStepFactorList": [0.0], "branchGlobalCurvatureStartList": [0.10000000149011612], "branchGlobalCurvatureEndList": [-0.10599999874830246], "branchCurvatureStartList": [0.0], "branchCurvatureEndList": [0.0], "branchCurvatureOffsetStrengthList": [0.0], "showSplitSettingsList": [true], "nrSplitsPerBranchList": [1.5], "branchSplitModeList": ["HORIZONTAL"], "branchSplitRotateAngleList": [0.0], "branchSplitAxisVariationList": [0.23999999463558197], "branchSplitAngleList": [0.26179999113082886], "branchSplitPointAngleList": [0.26179999113082886], "splitsPerBranchVariationList": [0.0], "branchVarianceList": [0.0], "outwardAttractionList": [0.0], "branchSplitHeightVariationList": [0.2569444477558136], "branchSplitLengthVariationList": [0.2013888955116272], "showBranchSplitHeights": [true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.2300613522529602], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props, self)


def init_properties(data, props, operator): # props = context.scene
        #operator.report({'INFO'}, "in init_properties()")
        
        #operator.report({'INFO'}, f"treeHeight before loading: {props.treeSettings.treeHeight}")
        dataTreeHeight = 0.0
        dataTreeHeight = data.get("treeHeight", dataTreeHeight)
        #operator.report({'INFO'}, f"data.treeHeight: {dataTreeHeight}")
        
        props.treeSettings.treeHeight = data.get("treeHeight", props.treeSettings.treeHeight)
        
        #operator.report({'INFO'}, f"treeHeight after loading: {props.treeSettings.treeHeight}")
        
        
        treeGrowDir = data.get("treeGrowDir", props.treeSettings.treeGrowDir)
        if isinstance(treeGrowDir, list) and len(treeGrowDir) == 3:
            props.treeSettings.treeGrowDir = treeGrowDir
        props.treeSettings.taper = data.get("taper", props.treeSettings.taper)
        
        controlPts = []
        controlPts = data.get("taperCurvePoints", controlPts)
        handleTypes = []
        handleTypes = data.get("taperCurveHandleTypes", handleTypes)
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
                
        panels.ensure_stem_curve_node(tree_generator)
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup') #taperNodeGroup')
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3]
    
        
                
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
        curveElement.points[0].location = controlPts[0]
        curveElement.points[0].handle_type = handleTypes[0]
        curveElement.points[1].location = controlPts[1]
        curveElement.points[1].handle_type = handleTypes[1]
        
        if len(controlPts) > 2:
            for i in range(2, len(controlPts)):
                curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                curveElement.points[len(curveElement.points) - 1].location.x = controlPts[i][0]
                curveElement.points[len(curveElement.points) - 1].location.y = controlPts[i][1]
                
                curveElement.points[len(curveElement.points) - 1].handle_type = handleTypes[i]
                
        nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.update()
        
        props.treeSettings.branchTipRadius = data.get("branchTipRadius", props.treeSettings.branchTipRadius)
        props.treeSettings.ringSpacing = data.get("ringSpacing", props.treeSettings.ringSpacing)
        props.treeSettings.stemRingResolution = data.get("stemRingResolution", props.treeSettings.stemRingResolution)
        props.treeSettings.resampleDistance = data.get("resampleDistance", props.treeSettings.resampleDistance)
        
        props.treeSettings.noiseAmplitudeVertical = data.get("noiseAmplitudeVertical", props.treeSettings.noiseAmplitudeVertical)
        props.treeSettings.noiseAmplitudeHorizontal = data.get("noiseAmplitudeHorizontal", props.treeSettings.noiseAmplitudeHorizontal)
        props.treeSettings.noiseAmplitudeGradient = data.get("noiseAmplitudeGradient", props.treeSettings.noiseAmplitudeGradient)
        props.treeSettings.noiseAmplitudeExponent = data.get("noiseAmplitudeExponent", props.treeSettings.noiseAmplitudeExponent)
        props.treeSettings.noiseScale = data.get("noiseScale", props.treeSettings.noiseScale)
        props.treeSettings.seed = data.get("seed", props.treeSettings.seed)
        
        props.treeSettings.curvatureStart = data.get("curvatureStart", props.treeSettings.curvatureStart)
        props.treeSettings.curvatureEnd = data.get("curvatureEnd", props.treeSettings.curvatureEnd)
        
        props.treeSettings.nrSplits = data.get("nrSplits", props.treeSettings.nrSplits)
        props.treeSettings.variance = data.get("variance", props.treeSettings.variance)
        props.treeSettings.stemSplitMode = data.get("stemSplitMode", props.treeSettings.stemSplitMode)
        props.treeSettings.stemSplitRotateAngle = data.get("stemSplitRotateAngle", props.treeSettings.stemSplitRotateAngle)
        props.treeSettings.curvOffsetStrength = data.get("curvOffsetStrength", props.treeSettings.curvOffsetStrength)
        
        for value in data.get("stemSplitHeightInLevelList", []):
            item = props.treeSettings.stemSplitHeightInLevelList.add()
            item.value = value
        props.treeSettings.stemSplitHeightInLevelListIndex = data.get("stemSplitHeightInLevelListIndex", props.treeSettings.stemSplitHeightInLevelListIndex)
                
        props.treeSettings.splitHeightVariation = data.get("splitHeightVariation", props.treeSettings.splitHeightVariation)
        props.treeSettings.splitLengthVariation = data.get("splitLengthVariation", props.treeSettings.splitLengthVariation)
        props.treeSettings.stemSplitAngle = data.get("stemSplitAngle", props.treeSettings.stemSplitAngle)
        props.treeSettings.stemSplitPointAngle = data.get("stemSplitPointAngle", props.treeSettings.stemSplitPointAngle)
        
        for outerList in props.treeSettings.parentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.treeSettings.parentClusterBoolListList.clear()
        
        
        nrBranchClusters = data.get("branchClusters", props.treeSettings.branchClusters)
        props.treeSettings.branchClusters = 0 # gets incremented by add_branch_cluster()


        # nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        #
        # for clusterIndex in range(props.branchClusters):
        #   curve_name = panels.ensure_branch_curve_node(clusterIndex)
        #   curveElement = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.curves[3]
        #   clusterTaperControlPts.append([])
        #   clusterTaperCurveHandleTypes.append([])
        #   for i in range(0, len(curveElement.points)):
        #     clusterTaperControlPts[clusterIndex].append(curveElement.points[i].location)
        #     clusterTaperCurveHandleTypes[clusterIndex].append(curveElement.points[i].handle_type)
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        
        clusterControlPts = []
        clusterControlPts = data.get("clusterTaperControlPts", controlPts)
        clusterHandleTypes = []
        clusterHandleTypes = data.get("clusterTaperCurveHandleTypes", handleTypes)
        
        for clusterIndex in range(nrBranchClusters):

            bpy.ops.scene.add_branch_cluster()
            
            bpy.ops.scene.reset_branch_cluster_curve(idx = clusterIndex)
            
            
            curve_name = panels.ensure_branch_curve_node(tree_generator, clusterIndex)
            curveElement = nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.curves[3]
            
            
            
            if len(curveElement.points) > 2:
                for i in range(2, len(curveElement.points)):
                    curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                    
                curveElement.points[0].location = controlPts[0]
                curveElement.points[0].handle_type = handleTypes[0]
                curveElement.points[1].location = controlPts[1]
                curveElement.points[1].handle_type = handleTypes[1]
                
                if len(controlPts) > 2:
                    for i in range(2, len(controlPts)):
                        curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                        curveElement.points[len(curveElement.points) - 1].location.x = clusterControlPts[clusterIndex][i][0]
                        curveElement.points[len(curveElement.points) - 1].location.y = clusterControlPts[clusterIndex][i][1]
                
                        curveElement.points[len(curveElement.points) - 1].handle_type = clusterHandleTypes[clusterIndex][i]
            
            nodeGroups.nodes[property_groups.curve_node_mapping[curve_name]].mapping.update()
            
        props.treeSettings.parentClusterBoolListList.clear()
        operator.report({'INFO'}, f"in init_properties(): after parentClusterBoolListList.clear(): len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") #0
        nestedList = []
        nestedList = data.get("parentClusterBoolListList", nestedList)
        for n in range(0, props.treeSettings.branchClusters):
            innerList = nestedList[n]
            item = props.treeSettings.parentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            boolList = props.treeSettings.parentClusterBoolListList[n].value
            for b in innerList:
                boolItem = boolList.add()
                boolItem.value = b
        
        operator.report({'INFO'}, f"in init_properties(): after adding parent clusters from json: len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") # 2

        nrLeafClusters = len(bpy.context.scene.leafClusterSettingsList)
        operator.report({'INFO'}, f"in init_properties() (before adding leaf clusters): nrLeafClusters: {nrLeafClusters}") # 0
        
        for outerList in props.treeSettings.leafParentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.treeSettings.leafParentClusterBoolListList.clear()
        operator.report({'INFO'}, f"in init_properties(): after leafParentClusterBoolListList.clear(): len(leafParentClusterBoolListList): {len(props.treeSettings.leafParentClusterBoolListList)}") # 0
        nestedLeafList = []
        nestedLeafList = data.get("leafParentClusterBoolListList", nestedLeafList)
        for n in range(0, len(nestedLeafList)):
            innerLeafList = nestedLeafList[n]
            item = props.treeSettings.leafParentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            boolList = props.treeSettings.leafParentClusterBoolListList[n].value
            for b in innerLeafList:
                boolItem = boolList.add()
                boolItem = b

        operator.report({'INFO'}, f"in init_properties(): after adding leaf parent clusters from json: len(leafParentClusterBoolListList): {len(props.treeSettings.leafParentClusterBoolListList)}") # 1

        props.branchClusterSettingsList.clear()
        
        for i in range(0, props.treeSettings.branchClusters):
            props.branchClusterSettingsList.add()
        
        for i, value in enumerate(data.get("nrBranchesList", [])):
            props.branchClusterSettingsList[i].nrBranches = value
        
        for i, value in enumerate(data.get("treeShapeList", [])):
            props.branchClusterSettingsList[i].treeShape.value = value
        
        for i, value in enumerate(data.get("branchShapeList", [])):
            props.branchClusterSettingsList[i].branchShape.value = value
            
        for i, value in enumerate(data.get("branchTypeList", [])):
            props.branchClusterSettingsList[i].branchType.value = value
            
        for i, value in enumerate(data.get("branchWhorlCountStartList", [])):
            props.branchClusterSettingsList[i].branchWhorlCountStart = value
            
        for i, value in enumerate(data.get("branchWhorlCountEndList", [])):
            props.branchClusterSettingsList[i].branchWhorlCountEndStart = value
            
        for i, value in enumerate(data.get("relBranchLengthList", [])):
            props.branchClusterSettingsList[i].relBranchLength = value
            
        for i, value in enumerate(data.get("relBranchLengthVariationList", [])):
            props.branchClusterSettingsList[i].relBranchLengthVariation = value
        
        props.taperFactorList.clear()
        while len(props.taperFactorList) < props.treeSettings.branchClusters:
            props.taperFactorList.add()
        for i, value in enumerate(data.get("taperFactorList", [])):
            props.taperFactorList[i].taperFactor = value
        
        for i, value in enumerate(data.get("useTaperCurveList", [])):
            props.branchClusterSettingsList[i].useTaperCurve = value
            
        for i, value in enumerate(data.get("ringResolutionList", [])):
            props.branchClusterSettingsList[i].ringResolution = value
        
        for i, value in enumerate(data.get("branchesStartHeightGlobalList", [])):
            props.branchClusterSettingsList[i].branchesStartHeightGlobal = value
            
        for i, value in enumerate(data.get("branchesEndHeightGlobalList", [])):
            props.branchClusterSettingsList[i].branchesEndHeightGlobal = value
        
        for i, value in enumerate(data.get("branchesStartHeightClusterList", [])):
            props.branchClusterSettingsList[i].branchesStartHeightCluster = value
        
        for i, value in enumerate(data.get("branchesEndHeightClusterList", [])):
            props.branchClusterSettingsList[i].branchesEndHeightCluster = value
            
        for i, value in enumerate(data.get("branchesStartPointVariationList", [])):
            props.branchClusterSettingsList[i].branchesStartPointVariation = value
        
        for i, value in enumerate(data.get("noiseAmplitudeHorizontalBranchList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeHorizontalBranch = value
        
        for i, value in enumerate(data.get("noiseAmplitudeVerticalBranchList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeVerticalBranch = value
        
        for i, value in enumerate(data.get("noiseAmplitudeBranchGradientList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeBranchGradient = value
            
        for i, value in enumerate(data.get("noiseAmplitudeBranchExponentList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudBranchExponent = value
            
        for i, value in enumerate(data.get("noiseScaleList", [])):
            props.branchClusterSettingsList[i].noiseScale = value
            
        
        for i, value in enumerate(data.get("verticalAngleCrownStartList", [])):
            props.branchClusterSettingsList[i].verticalAngleCrownStart = value
            
        for i, value in enumerate(data.get("verticalAngleCrownEndList", [])):
            props.branchClusterSettingsList[i].verticalAngleCrownEnd = value
            
        for i, value in enumerate(data.get("verticalAngleBranchStartList", [])):
            props.branchClusterSettingsList[i].verticalAngleBranchStart = value
            
        for i, value in enumerate(data.get("verticalAngleBranchEndList", [])):
            props.branchClusterSettingsList[i].verticalAngleBranchEnd = value
        
        
        for i, value in enumerate(data.get("branchAngleModeList", [])):
            props.branchClusterSettingsList[i].branchAngleMode.value = value
            
        for i, value in enumerate(data.get("useFibonacciAnglesList", [])):
            props.branchClusterSettingsList[i].useFibonacciAngles = value
            
        for i, value in enumerate(data.get("fibonacciNr", [])):
            props.branchClusterSettingsList[i].fibonacciNr.fibonacci_nr = value
        
        for i, value in enumerate(data.get("rotateAngleRangeList", [])):
            props.branchClusterSettingsList[i].rotateAngleRange = value
            
        for i, value in enumerate(data.get("rotateAngleOffsetList", [])):
            props.branchClusterSettingsList[i].rotateAngleOffset = value
        
        
        for i, value in enumerate(data.get("rotateAngleCrownStartList", [])):
            props.branchClusterSettingsList[i].rotateAngleCrownStart = value
            
        for i, value in enumerate(data.get("rotateAngleCrownEndList", [])):
            props.branchClusterSettingsList[i].rotateAngleCrownEnd = value
            
        for i, value in enumerate(data.get("rotateAngleBranchStartList", [])):
            props.branchClusterSettingsList[i].rotateAngleBranchStart = value
            
        for i, value in enumerate(data.get("rotateAngleBranchEndList", [])):
            props.branchClusterSettingsList[i].rotateAngleBranchEnd = value
        
        for i, value in enumerate(data.get("rotateAngleRangeFactorList", [])):
            props.branchClusterSettingsList[i].rotateAngleRangeFactor = value
            
            
        for i, value in enumerate(data.get("reducedCurveStepCutoffList", [])):
            props.branchClusterSettingsList[i].reducedCurveStepCutoff = value
            
        for i, value in enumerate(data.get("reducedCurveStepFactorList", [])):
            props.branchClusterSettingsList[i].reducedCurveStepFactor = value
        
        for i, value in enumerate(data.get("branchGlobalCurvatureStartList", [])):
            props.branchClusterSettingsList[i].branchGlobalCurvatureStart = value
            
        for i, value in enumerate(data.get("branchGlobalCurvatureEndList", [])):
            props.branchClusterSettingsList[i].branchGlobalCurvatureEnd = value
        
        for i, value in enumerate(data.get("branchCurvatureStartList", [])):
            props.branchClusterSettingsList[i].branchCurvatureStart = value
           
        for i, value in enumerate(data.get("branchCurvatureEndList", [])):
            props.branchClusterSettingsList[i].branchCurvatureEnd = value
        
        for i, value in enumerate(data.get("branchCurvatureOffsetStrengthList", [])):
            props.branchClusterSettingsList[i].branchCurvatureOffsetStrength = value
        
        
        for i, value in enumerate(data.get("nrSplitsPerBranchList", [])):
            props.branchClusterSettingsList[i].nrSplitsPerBranch = value
            
        for i, value in enumerate(data.get("branchSplitModeList", [])):
            props.branchClusterSettingsList[i].branchSplitMode.value = value
            
        for i, value in enumerate(data.get("branchSplitRotateAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitRotateAngle = value
            
        for i, value in enumerate(data.get("branchSplitAxisVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitAxisVariation = value
            
        
        for i, value in enumerate(data.get("branchSplitAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitAngle = value
            
        for i, value in enumerate(data.get("branchSplitPointAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitPointAngle = value
            
        
        for i, value in enumerate(data.get("splitsPerBranchVariationList", [])):
            props.branchClusterSettingsList[i].splitsPerBranchVariation = value
            
        for i, value in enumerate(data.get("branchVarianceList", [])):
            props.branchClusterSettingsList[i].branchVariance = value
            
        for i, value in enumerate(data.get("outwardAttractionList", [])):
            props.branchClusterSettingsList[i].outwardAttraction = value
        
        for i, value in enumerate(data.get("branchSplitHeightVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitHeightVariation = value
        
        for i, value in enumerate(data.get("branchSplitLengthVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitLengthVariation = value
        
        props.treeSettings.branchSplitHeightInLevelListList.clear()
        nestedBranchSplitHeightInLevelList = []
        nestedBranchSplitHeightInLevelList = data.get("branchSplitHeightInLevelListList", nestedBranchSplitHeightInLevelList)
        for n in range(0, len(nestedBranchSplitHeightInLevelList)):
            innerList = nestedBranchSplitHeightInLevelList[n]
            item = props.treeSettings.branchSplitHeightInLevelListList.add()
            for n in item.value:
                item.remove(n)
            for h in innerList:
                i = item.value.add()
                i.value = h
            
        props.branchSplitHeightInLevelListIndex = data.get("branchSplitHeightInLevelListIndex", props.branchSplitHeightInLevelListIndex)
            
        for value in data.get("branchSplitHeightInLevelList_0", []):
            item = props.treeSettings.branchSplitHeightInLevelList_0.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_0 = data.get("branchSplitHeightInLevelListIndex_0", props.treeSettings.branchSplitHeightInLevelListIndex_0)
        
        for value in data.get("branchSplitHeightInLevelList_1", []):
            item = props.treeSettings.branchSplitHeightInLevelList_1.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_1 = data.get("branchSplitHeightInLevelListIndex_1", props.treeSettings.branchSplitHeightInLevelListIndex_1)
        
        for value in data.get("branchSplitHeightInLevelList_2", []):
            item = props.treeSettings.branchSplitHeightInLevelList_2.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_2 = data.get("branchSplitHeightInLevelListIndex_2", props.treeSettings.branchSplitHeightInLevelListIndex_2)
        
        for value in data.get("branchSplitHeightInLevelList_3", []):
            item = props.treeSettings.branchSplitHeightInLevelList_3.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_3 = data.get("branchSplitHeightInLevelListIndex_3", props.treeSettings.branchSplitHeightInLevelListIndex_3)
        
        for value in data.get("branchSplitHeightInLevelList_4", []):
            item = props.treeSettings.branchSplitHeightInLevelList_4.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_4 = data.get("branchSplitHeightInLevelListIndex_4", props.treeSettings.branchSplitHeightInLevelListIndex_4)
        
        for value in data.get("branchSplitHeightInLevelList_5", []):
            item = props.treeSettings.branchSplitHeightInLevelList_5.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_5 = data.get("branchSplitHeightInLevelListIndex_5", props.treeSettings.branchSplitHeightInLevelListIndex_5)
        
        for value in data.get("branchSplitHeightInLevelList_6", []):
            item = props.treeSettings.branchSplitHeightInLevelList_6.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_6 = data.get("branchSplitHeightInLevelListIndex_6", props.treeSettings.branchSplitHeightInLevelListIndex_6)
        
        for value in data.get("branchSplitHeightInLevelList_7", []):
            item = props.treeSettings.branchSplitHeightInLevelList_7.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_7 = data.get("branchSplitHeightInLevelListIndex_7", props.treeSettings.branchSplitHeightInLevelListIndex_7)
        
        for value in data.get("branchSplitHeightInLevelList_8", []):
            item = props.treeSettings.branchSplitHeightInLevelList_8.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_8 = data.get("branchSplitHeightInLevelListIndex_8", props.treeSettings.branchSplitHeightInLevelListIndex_8)
        
        for value in data.get("branchSplitHeightInLevelList_9", []):
            item = props.treeSettings.branchSplitHeightInLevelList_9.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_9 = data.get("branchSplitHeightInLevelListIndex_9", props.treeSettings.branchSplitHeightInLevelListIndex_9)
        
        for value in data.get("branchSplitHeightInLevelList_10", []):
            item = props.treeSettings.branchSplitHeightInLevelList_10.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_10 = data.get("branchSplitHeightInLevelListIndex_10", props.treeSettings.branchSplitHeightInLevelListIndex_10)
        
        for value in data.get("branchSplitHeightInLevelList_11", []):
            item = props.treeSettings.branchSplitHeightInLevelList_11.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_11 = data.get("branchSplitHeightInLevelListIndex_11", props.treeSettings.branchSplitHeightInLevelListIndex_11)
        
        for value in data.get("branchSplitHeightInLevelList_12", []):
            item = props.treeSettings.branchSplitHeightInLevelList_12.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_12 = data.get("branchSplitHeightInLevelListIndex_12", props.treeSettings.branchSplitHeightInLevelListIndex_12)
        
        for value in data.get("branchSplitHeightInLevelList_13", []):
            item = props.treeSettings.branchSplitHeightInLevelList_13.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_13 = data.get("branchSplitHeightInLevelListIndex_13", props.treeSettings.branchSplitHeightInLevelListIndex_13)
        
        for value in data.get("branchSplitHeightInLevelList_14", []):
            item = props.treeSettings.branchSplitHeightInLevelList_14.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_14 = data.get("branchSplitHeightInLevelListIndex_14", props.treeSettings.branchSplitHeightInLevelListIndex_14)
        
        for value in data.get("branchSplitHeightInLevelList_15", []):
            item = props.treeSettings.branchSplitHeightInLevelList_15.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_15 = data.get("branchSplitHeightInLevelListIndex_15", props.treeSettings.branchSplitHeightInLevelListIndex_15)
        
        for value in data.get("branchSplitHeightInLevelList_16", []):
            item = props.treeSettings.branchSplitHeightInLevelList_16.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_16 = data.get("branchSplitHeightInLevelListIndex_16", props.treeSettings.branchSplitHeightInLevelListIndex_16)
        
        for value in data.get("branchSplitHeightInLevelList_17", []):
            item = props.treeSettings.branchSplitHeightInLevelList_17.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_17 = data.get("branchSplitHeightInLevelListIndex_17", props.treeSettings.branchSplitHeightInLevelListIndex_17)
        
        for value in data.get("branchSplitHeightInLevelList_18", []):
            item = props.treeSettings.branchSplitHeightInLevelList_18.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_18 = data.get("branchSplitHeightInLevelListIndex_18", props.treeSettings.branchSplitHeightInLevelListIndex_18)
        
        for value in data.get("branchSplitHeightInLevelList_19", []):
            item = props.treeSettings.branchSplitHeightInLevelList_19.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_19 = data.get("branchSplitHeightInLevelListIndex_19", props.treeSettings.branchSplitHeightInLevelListIndex_19)
        
        operator.report({'INFO'}, f"in init_properties() before props.leafClusterSettingsList.clear(), props.treeSettings.leafParentClusterBoolListList.clear") 
        operator.report({'INFO'}, f"in init_properties(): before props.leafClusterSettingsList.clear(): len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") # 2

        nrLeafClusters = len(bpy.context.scene.leafClusterSettingsList)
        operator.report({'INFO'}, f"in init_properties() (before props.leafClusterSettingsList.clear(): nrLeafClusters: {nrLeafClusters}") # 0
        props.leafClusterSettingsList.clear()
        props.treeSettings.leafParentClusterBoolListList.clear()

        operator.report({'INFO'}, f"in init_properties(): after props.leafClusterSettingsList.clear(): len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") # 2

        nrLeafClusters = len(bpy.context.scene.leafClusterSettingsList)
        operator.report({'INFO'}, f"in init_properties() (after props.leafClusterSettingsList.clear(): nrLeafClusters: {nrLeafClusters}") # 0
        
        jsonLeavesDensityList = data.get("leavesDensityList", [])
        operator.report({'INFO'}, f"len(json leaves density list): {len(jsonLeavesDensityList)}")# 1 -> loop over range (0, jsonLeavesDensityList)!


        for n in range(0, len(jsonLeavesDensityList)):
            bpy.ops.scene.add_leaf_cluster()
            
            item.leavesDensity = value
            nrLeafClusters = len(bpy.context.scene.leafClusterSettingsList)
            operator.report({'INFO'}, f"in init_properties() (after for ... props.leafClusterSettingsList.add(): nrLeafClusters: {nrLeafClusters}")
            operator.report({'INFO'}, f"jsonLeafDensity{n}: {jsonLeavesDensityList[n]}")
            bpy.context.scene.leafClusterSettingsList[n].leavesDensity = jsonLeavesDensityList[n]
            operator.report({'INFO'}, f"bpy.context.scene.leafClusterSettingsList[n].leafDensity: {bpy.context.scene.leafClusterSettingsList[n].leavesDensity}")
        
        operator.report({'INFO'}, f"in init_properties(): after for... props.leafClusterSettingsList.add(): len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") # 2

        nrLeafClusters = len(bpy.context.scene.leafClusterSettingsList)
        operator.report({'INFO'}, f"in init_properties() (after for ... props.leafClusterSettingsList.add(): nrLeafClusters: {nrLeafClusters}") 
        
        props = bpy.context.scene
        i = 0
        for value in data.get("leafSizeList", []):
            props.leafClusterSettingsList[i].leafSize = value
            operator.report({'INFO'}, f"in init_properties(): setting leaf size : props . leafSize: {props.leafClusterSettingsList[i].leafSize}")
            i += 1
        i = 0
        for value in data.get("leafAspectRatioList", []):
            props.leafClusterSettingsList[i].leafAspectRatio = value
            i += 1
        i = 0
        for value in data.get("leafStartHeightGlobalList", []):
            props.leafClusterSettingsList[i].leafStartHeightGlobal = value
            i += 1
        i = 0
        for value in data.get("leafEndHeightGlobalList", []):
            props.leafClusterSettingsList[i].leafEndHeightGlobal = value
            i += 1
        i = 0
        for value in data.get("leafStartHeightClusterList", []):
            props.leafClusterSettingsList[i].leafStartHeightCluster = value
            i += 1
        i = 0
        for value in data.get("leafEndHeightClusterList", []):
            props.leafClusterSettingsList[i].leafEndHeightCluster = value
            i += 1
        i = 0
        for value in data.get("leafTypeList", []):
            props.leafClusterSettingsList[i].leafType.value = value
            i += 1
        i = 0
        for value in data.get("leafWhorlCountList", []):
            props.leafClusterSettingsList[i].leafWhorlCount = value
            i += 1
        i = 0
        for value in data.get("leafAngleModeList", []):
            props.leafClusterSettingsList[i].leafAngleMode.value = value
            i += 1
        i = 0
        for value in data.get("leafVerticalAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafVerticalAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafVerticalAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafVerticalAngleBranchEnd = value
            i += 1
        i = 0
        for value in data.get("leafRotateAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafRotateAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafRotateAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafRotateAngleBranchEnd = value
            i += 1
        i = 0
        for value in data.get("leafTiltAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafTiltAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafTiltAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafTiltAngleBranchEnd = value
            i += 1

        operator.report({'INFO'}, f"in init_properties(): (after adding leaf clusters):: len(parentClusterBoolListList): {len(props.treeSettings.parentClusterBoolListList)}") # 

        nrLeafClusters = len(props.leafClusterSettingsList)
        operator.report({'INFO'}, f"in init_properties() (after adding leaf clusters): nrLeafClusters: {nrLeafClusters}") # 2 ERROR HERE !!!
        
        

        
        
def register():
    print("register operators (TODO???)")
    
def unregister():
    print("unregister operators(TODO???)")