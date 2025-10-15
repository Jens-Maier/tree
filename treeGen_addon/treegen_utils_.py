import bpy
from . import property_groups
from mathutils import Vector


class treegen_utils():
    
    @staticmethod
    def _get_curve_element(mapping_dict, curve_name):
        """Helper to safely retrieve the curve element from the node group."""
        try:
            node_name = mapping_dict[curve_name]
            # Access the curve element (assuming index 3, the B channel)
            curveElement = myNodeTree()[node_name].mapping.curves[3] 
            return curveElement
        except KeyError:
            print(f"Error: Curve mapping for '{curve_name}' not found.")
            return None
        except Exception as e:
            print(f"Error accessing curve node '{node_name}': {e}")
            return None
    
    def sampleSplineC(controlPt0, controlPt1, controlPt2, controlPt3, t):
        return (1.0 - t)**3.0 * controlPt0 + 3.0 * (1.0 - t)**2.0 * t * controlPt1 + 3.0 * (1.0 - t) * t**2.0 * controlPt2 + t**3.0 * controlPt3
    
    def sampleSplineT(start, end, startTangent, endTangent, t):
        controlPt1 = start + startTangent.normalized() * (end - start).length / 3.0
        controlPt2 = end - endTangent.normalized() * (end - start).length / 3.0
        return (1.0 - t)**3.0 * start + 3.0 * (1.0 - t)**2.0 * t * controlPt1 + 3.0 * (1.0 - t) * t**2.0 * controlPt2 + t**3.0 * end
    
    def sampleSplineTangentC(controlPt0, controlPt1, controlPt2, controlPt3, t):
        return (-3.0 * (1.0 - t)**2.0 * controlPt0 + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * controlPt3).normalized()
    
    def sampleSplineTangentT(start, end, startTangent, endTangent, t):
        controlPt1 = start + startTangent.normalized() * (end - start).length / 3.0
        controlPt2 = end - endTangent.normalized() * (end - start).length / 3.0
        return (-3.0 * (1.0 - t)**2.0 * start + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * end).normalized()
    
    def lerp(a, b, t):
        return a + (b - a) * t
    
    #nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
    #curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves#!!!!!!!!!!!!!!!!!!!!
    
    
    def sampleCurveStem(treeGeneratorInstance, x):
        curve_name = "Stem"
        mapping_dict = property_groups.curve_node_mapping
        curveElement = property_groups.curve_node_mapping 
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
        nrCurves = len(nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves)#!!!!!!!!!!!!!!!!!!!!
        
        treegen_utils.ensure_stem_curve_node()
        
        def lerp(self, a, b, t):
            return (a + (b - 1) * t)    
        def f0(t):
            return (-0.5*t*t*t + t*t - 0.5*t)
        def f1(t):
            return (1.5*t*t*t - 2.5*t*t + 1.0)
        def f2(t):
            return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
        def f3(t):
            return (0.5*t*t*t - 0.5*t*t)
        
        def sampleSpline(p0, p1, p2, p3, t):
            return f0(t) * p0 + f1(t) * p1 + f2(t) * p2 + f3(t) * p3
        
        treegen_utils.ensure_stem_curve_node()
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3]#!!!!!!!!!!!!!!!!!!!!
        
        
        #nodeGroups = bpy.data.node_groups.get('CurveNodeGroup') #taperNodeGroup')
        #curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] #'Stem'
        
        #for p in curveElement.points:
        #    self.report({'INFO'}, f"stem: point: {p.location}")
            
        y = 0.0
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
                            p0 = Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
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
                        p0 = Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
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
                            p3 = Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))  
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
                
                px = sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
                py = sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                
                #self.report({'INFO'}, f"stem: sample point: x: {x}, y: {y}, px: {px}, py: {py}")
                return py
        self.report({'ERROR'}, f"segment not found!, x: {x}")
        return 0.0
    
    def sampleCurveBranch(self, x, clusterIndex):
        
        def lerp(self, a, b, t):
            return (a + (b - 1) * t)    
        def f0(t):
            return (-0.5*t*t*t + t*t - 0.5*t)
        def f1(t):
            return (1.5*t*t*t - 2.5*t*t + 1.0)
        def f2(t):
            return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
        def f3(t):
            return (0.5*t*t*t - 0.5*t*t)
        
        def sampleSpline(p0, p1, p2, p3, t):
            return f0(t) * p0 + f1(t) * p1 + f2(t) * p2 + f3(t) * p3
        
        curve_name = treegen_utils.ensure_branch_curve_node(clusterIndex)
        
        #nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        #curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
        curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves[3]#!!!!!!!!!!!!!!!!!!!!
        
        
        y = 0.0
        
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
                            p0 = Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                        else: # only 2 points -> linear
                            p0 = curveElement.points[0].location - (curveElement.points[1].location -   curveElement.points[0].location)
                        
                        if len(curveElement.points) > 2:                            
                            p3 = curveElement.points[2].location
                        else: # linear when only 2 points
                            p3 = p2 + (p2 - p1)
                            p0 = p1 - (p2 - p1)
                    else:
                        #n = 0, reflected == 1 * slope
                        slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                        p0 = Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
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
                            p3 = Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))  
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
                        p0 = curveElement.points[n].location - (curveElement.points[n + 1].location -   curveElement.points[n].location)
                        p1 = curveElement.points[n].location
                        p2 = curveElement.points[n + 1].location
                        p3 = curveElement.points[n + 2].location
            
            if p1.x <= x and (p2.x > x or p2.x == 1.0):
                
                tx = (x - p1.x) / (p2.x - p1.x)
                
                px = sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
                py = sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                
                return py
                    
        return 0.0
    
    # in tree_generator.py: 
    # 
    # class treeGenerator:
    # def __init__():
    #     curve_node_mapping = {}
    #     taper_node_mapping = {}
    
    #nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
    #curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves#!!!!!!!!!!!!!!!!!!!!
        
    
    def ensure_stem_curve_node():
        curve_name = "Stem"
        if 'CurveNodeGroup' not in bpy.data.node_groups:
            bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
        if curve_name not in property_groups.curve_node_mapping:
            cn = myNodeTree().new('ShaderNodeRGBCurve')
            property_groups.curve_node_mapping[curve_name] = cn.name
        return curve_name
    
    #nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')#!!!!!!!!!!!!!!!!!!!!
    #curveElement = nodeGroups.nodes[property_groups.curve_node_mapping['Stem']].mapping.curves#!!!!!!!!!!!!!!!!!!!!
    
    def ensure_branch_curve_node(idx):
        curve_name = f"BranchCluster_{idx}"
        if 'CurveNodeGroup' not in bpy.data.node_groups:
            bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
        if curve_name not in property_groups.curve_node_mapping:
            cn = myNodeTree().new('ShaderNodeRGBCurve')
            #cn.label = curve_name
            property_groups.curve_node_mapping[curve_name] = cn.name
        return curve_name
    
    def register():
        print("in treegen_utils: register")

    def unregister():
        print("in treegen_utils: unregister")
    
    
def myNodeTree():
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['CurveNodeGroup'].nodes


def register():
    print("register node")
    treegen_utils.register()
    
def unregister():
    treegen_utils.unregister()
    print("unregister node")
