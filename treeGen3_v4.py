# SPDX-License-Identifier: GPL-3.0-or-later



import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import json
import os
import bmesh

import importlib.util
import sys
import os

# Add the directory containing treeGen3_v4_utils.py to sys.path

# for testing: 
module_path = "/home/j/Downloads/treeGen3_v4_utils.py"
#module_path = os.path.join(os.path.dirname(__file__), "treeGen3_v4_utils.py")

module_name = "treeGen3_v4_utils"
spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

#startNodeInfo = module.startNodeInfo
#nodeInfo = module.nodeInfo
#startPointData = module.startPointData
#dummyStartPointData = module.dummyStartPointData
#rotationStep = module.rotationStep
#node = module.node
#segment = module.segment
#splitMode = module.splitMode


test_instance = module.testClass() # -> register dynamically!

# TESTstartNodeInfo = module.startNodeInfo(None, 0, 0.0, 1.0, 0.0, 0.5)

#script_dir = os.path.dirname(os.path.realpath(__file__))
#if script_dir not in sys.path:
#    sys.path.append(script_dir)
#
#from treeGen3_v4_utils import startNodeInfo, nodeInfo, startPointData, dummyStartPointData, rotationStep, node



class fibonacciProps(bpy.types.PropertyGroup):
    fibonacci_nr: bpy.props.IntProperty(name = "fibonacciNr", default=3, min=3, 
        update = lambda self, context:update_fibonacci_numbers(self))
        
    fibonacci_angle: bpy.props.FloatProperty(name="", default=2.0 * math.pi / 3.0, options={'HIDDEN'})
    
    use_fibonacci: bpy.props.BoolProperty(name = "useFibonacci", default=False,
        update = lambda self, context:update_fibonacci_numbers(self))

def update_fibonacci_numbers(self):
    fn0 = 1.0
    fn1 = 1.0
    self.rotate_angle_range = 2.0 * math.pi
    if self.fibonacci_nr > 2:
        for n in range(2, self.fibonacci_nr + 1):
            temp = fn0 + fn1
            fn0 = fn1
            fn1 = temp
    self.fibonacci_angle = 2.0 * math.pi * (1.0 - fn0 / fn1)

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

class initButton(bpy.types.Operator):
    bl_idname="scene.init_button"
    bl_label="Reset"
        
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        nrCurves = len(nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves)
        self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] 
        
        #initialise values
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                self.report({'INFO'}, "removing point")
        nodeGroups.nodes[curve_node_mapping['Stem']].mapping.update()
        return {'FINISHED'}

class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=10)
    
class intPropL(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=200)

class posIntProp3(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "posIntProp3", default=3, min=3, soft_max=12)

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0)
    
class posFloatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0, min=0)
    
class posFloatPropDefault1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0)
    
class posFloatPropSoftMax2(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default = 1.0, min = 0, soft_max=2.0)
    
class posFloatPropSoftMax1(bpy.types.PropertyGroup):
    taperFactor: bpy.props.FloatProperty(name = "Taper factor", default=1, min=0, soft_max=1.0)
    
class posFloatPropSoftMax1taperFactor(bpy.types.PropertyGroup):
    taperFactor: bpy.props.FloatProperty(name = "Taper factor", default=1, min=0, soft_max=1.0)

class posFloatPropSoftMax1Default0(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0, min=0, soft_max=1.0)

class floatProp01(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue01", default=0, min=0, max=1)
    
class floatProp01default0p5(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue01", default=0.5, min=0, max=1)
    
class floatListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "floatListProperty", type=floatProp)
    
class floatListProp01(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "floatListProperty01", type=floatProp01)
        
class boolProp(bpy.types.PropertyGroup):
    value: bpy.props.BoolProperty(name = "boolValue", default=False)
    
class showSplitLevelsProp(bpy.types.PropertyGroup):
    show_split_levels: bpy.props.BoolProperty(
        name="Show Split Levels",
        description="Show/hide split levels",
        default=True
    )

class splitHeightFloatListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "splitHeightFloatListProperty", type=floatProp01)
    show_split_levels: bpy.props.BoolProperty(
        name="Show Split Levels",
        description="Show/hide split levels",
        default=True
    )
    
class parentClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "parentClusterBoolListProperty", type=boolProp)
    show_cluster: bpy.props.BoolProperty(
        name="Show Cluster",
        description="Show/hide parent clusters",
        default=True
    )
    
class leafParentClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "leafParentClusterBoolListProperty", type=boolProp)
    show_leaf_cluster: bpy.props.BoolProperty(
        name="Show Leaf Cluster",
        description="Show/hide leaf parent clusters",
        default=True
    )
    
class branchClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "branchClusterBoolListProperty", type=boolProp)
    show_branch_cluster: bpy.props.BoolProperty(
        name="Show Branch Cluster",
        description="Show/hide branch cluster",
        default=True
    )
    
class leafClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "leafClusterBoolListProperty", type=boolProp)
    show_leaf_cluster: bpy.props.BoolProperty(
        name="Show Leaf Cluster",
        description="Show/hide leaf clusters",
        default=True
    )

class treeShapeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "branchShape", 
        items = [
            ('CONICAL', "Conical", "A cone-shaped tree."),
            ('SPHERICAL', "Spherical", "A sphere-shaped tree."),
            ('HEMISPHERICAL', "Hemispherical", "A half-sphere shaped tree."),
            ('INVERSE_HEMISPHERICAL', "Inverse Hemispherical", "An upside-down half-sphere shaped tree."),
            ('CYLINDRICAL', "Cylindrical", "A cylinder-shaped tree."),
            ('TAPERED_CYLINDRICAL', "Tapered Cylindrical", "A cylinder that tapers towards the top."),
            ('FLAME', "Flame", "A flame-shaped tree."),
            ('INVERSE_CONICAL', "Inverse Conical", "An upside-down cone-shaped tree."),
            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
        ],
        default='CONICAL'        
    )
    
class treePresetEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "Preset",
        description="Select a preset.",
        items = [
            ('TREE1', "Tree1", "First tree"),
            ('TREE2', "Tree2", "Second tree"),
            ('MAPLE', "Maple tree", "Large maple tree"),
            ('SILVER_BIRCH', "Silver birch", "Silver birch tree")
        ],
        default='TREE1'
    )
  
class splitModeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "stemSplitMode",
        items=[
            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
            ('HORIZONTAL', "Horizontal", "Split horizontally")
        ],
        default='ROTATE_ANGLE',
    )
    
class angleModeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "branchAngleMode",
        items=[
            ('SYMMETRIC', "Symmetric", "symmetric branch angles"),
            ('WINDING', "Winding", "winding branch angles"),
            ('ADAPTIVE', "Adaptive winding", "adaptive winding branch angles")
        ],
        default='WINDING'
    )
    
class branchTypeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "branchType",
        items=[
            ('SINGLE', "Single", "single branch"),
            ('OPPOSITE', "Opposite", "opposite branches"),
            ('WHORLED', "Whorled", "whorled branches")
        ],
        default='SINGLE'
    )


class toggleBool(bpy.types.Operator):
    bl_idname = "scene.toggle_bool"
    bl_label = "Toggle Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.branchClusterSettingsList[self.list_index].parentClusterBoolList
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'}

class toggleLeafBool(bpy.types.Operator):
    bl_idname = "scene.toggle_leaf_bool"
    bl_label = "Toggle Leaf Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.leafClusterSettingsList[self.list_index].leafParentClusterBoolList.value
        #self.report({'INFO'}, f"boolList: {boolList}")
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'}

class leafAngleModeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "leafAngleMode",
        items=[
            ('ALTERNATING', "Alternating", "alternating leaf angles"),
            ('WINDING', "Winding", "winding leaf angles")
        ],
        default='WINDING'
    )
    
class leafTypeEnumProp(bpy.types.PropertyGroup):
    value: bpy.props.EnumProperty(
        name = "leafType",
        items=[
            ('SINGLE', "Single", "single leaf"),
            ('OPPOSITE', "Opposite", "opposite leaves"),
            ('WHORLED', "Whorled", "whorled leaves")
        ],
        default='SINGLE'
    )

class toggleUseTaperCurveOperator(bpy.types.Operator):
    bl_idname = "scene.toggle_use_taper_curve"
    bl_label = "Use Taper Curve"
    bl_description = "resets taper curve"
    
    idx: bpy.props.IntProperty()
    
    def execute(self, context):
        settings = context.scene.branchClusterSettingsList[self.idx]
        wasEnabled = settings.useTaperCurve
        settings.useTaperCurve = not wasEnabled
        
        bpy.ops.scene.reset_branch_cluster_curve(idx = self.idx)
            
        return {'FINISHED'}
    

class treeSettings(bpy.types.PropertyGroup):
    treePreset: bpy.props.PointerProperty(type = treePresetEnumProp)
    folder_path: bpy.props.StringProperty(name = "Folder", subtype='DIR_PATH', default="")
    file_name: bpy.props.StringProperty(name = "File Name", default="")
    treeHeight: bpy.props.FloatProperty(name = "Tree height", default = 10, min = 0, soft_max = 50, unit = 'LENGTH')
    treeGrowDir: bpy.props.FloatVectorProperty(name = "Tree Grow Direction", description = "Direction the tree grows in.", default = (0.0, 0.0, 1.0), subtype = 'XYZ')
    taper: bpy.props.FloatProperty(name = "taper", default = 0.1, min = 0, soft_max = 0.5)
    branchTipRadius: bpy.props.FloatProperty(name = "branch tip radius", default = 0, min = 0, soft_max = 0.1, unit = 'LENGTH')
    ringSpacing: bpy.props.FloatProperty(name = "Ring Spacing", default = 0.1, min = 0.001, unit = 'LENGTH')
    stemRingResolution: bpy.props.IntProperty(name = "Stem Ring Resolution", default = 16, min = 3)
    resampleDistance: bpy.props.FloatProperty(name = "Resample Distance", default = 10.0, min = 0.0, unit = 'LENGTH')
    noiseAmplitudeHorizontal: bpy.props.FloatProperty(name = "Noise Amplitude Horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVertical: bpy.props.FloatProperty(name = "Noise Amplitude Vertical", default = 0.0, min = 0.0)
    noiseAmplitudeGradient: bpy.props.FloatProperty(name = "Noise Amplitude Gradient", default = 0.1, min = 0.0)
    noiseAmplitudeExponent: bpy.props.FloatProperty(name = "Noise Amplitude Exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise Scale", default = 1.0, min = 0.0, unit = 'LENGTH')
    seed: bpy.props.IntProperty(name = "Seed", description = "Noise generator seed")
    curvatureStart: bpy.props.FloatProperty(name = "Curvature Start", description = "Curvature at start of branches", default = 0.0)
    curvatureEnd: bpy.props.FloatProperty(name = "Curvature End", description = "Curvature at end of branches", default = 0.0)
    maxCurveSteps: bpy.props.IntProperty(name = "Max Curve Steps", description = "max curve steps", default = 10, min = 0)
    nrSplits: bpy.props.IntProperty(name = "Number of Splits", default = 0, min = 0)
    variance: bpy.props.FloatProperty(name = "Variance", default = 0.0, min = 0.0, max = 1.0)
    stemSplitRotateAngle: bpy.props.FloatProperty(name = "Stem Split Rotate Angle", default = 0.0, min = 0.0, max = 360.0, unit = 'ROTATION')
    curvOffsetStrength: bpy.props.FloatProperty(name = "Curvature Offset Strength", default = 0.0, min = 0.0)
    showStemSplitHeights: bpy.props.BoolProperty(name = "Show/hide stem split heights", default = True)
    stemSplitHeightInLevelList: bpy.props.CollectionProperty(type=floatProp01)
    stemSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0)
    splitHeightVariation: bpy.props.FloatProperty(name = "Split Height Variation", default = 0.0, min = 0.0)
    splitLengthVariation: bpy.props.FloatProperty(name = "Split Length Variation", default = 0.0, min = 0.0)
    stemSplitAngle: bpy.props.FloatProperty(name = "Stem Split Angle", default = 0.0, min = 0.0, max = 360.0, unit = 'ROTATION')
    stemSplitPointAngle: bpy.props.FloatProperty(name = "Stem Split Point Angle", default = 0.0, min = 0.0, max = 360.0, unit = 'ROTATION')
    stemSplitMode: bpy.props.EnumProperty(
        name = "stemSplitMode",
        items=[
            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
            ('HORIZONTAL', "Horizontal", "Split horizontally")
        ],
        default='ROTATE_ANGLE',
    )
    branchClusters: bpy.props.IntProperty(default = 0, min = 0)
    leafClusters: bpy.props.IntProperty(default = 0, min = 0)
    leavesDensityListIndex: bpy.props.IntProperty(default = 0, min = 0)
    
    branchSplitHeightInLevelListList: bpy.props.CollectionProperty(type=floatListProp01)
    branchSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_0: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_0: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_1: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_1: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_2: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_2: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_3: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_3: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_4: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_4: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_5: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_5: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_6: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_6: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_7: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_7: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_8: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_8: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_9: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_9: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_10: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_10: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_11: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_11: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_12: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_12: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_13: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_13: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_14: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_14: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_15: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_15: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_16: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_16: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_17: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_17: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_18: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_18: bpy.props.IntProperty(default = 0)
    branchSplitHeightInLevelList_19: bpy.props.CollectionProperty(type=floatProp01default0p5)
    branchSplitHeightInLevelListIndex_19: bpy.props.IntProperty(default = 0)
    

class branchClusterSettings(bpy.types.PropertyGroup):
    parentClusterBoolList: bpy.props.PointerProperty(type=parentClusterBoolListProp)
    branchClusterBoolList: bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    show_branch_cluster: bpy.props.BoolProperty(default = True)
    nrBranches: bpy.props.IntProperty(name = "Number of branches", default = 3, min = 0)
    nrBranchesIndex: bpy.props.IntProperty(name = "nrBranchesListIndex", default=0)
    treeShape: bpy.props.PointerProperty(type = treeShapeEnumProp)
    branchShape: bpy.props.PointerProperty(type = treeShapeEnumProp)
    branchType: bpy.props.PointerProperty(type = branchTypeEnumProp)
    branchWhorlCountStart: bpy.props.IntProperty(name = "Whorl count start", default = 3, min = 1)
    branchWhorlCountEnd: bpy.props.IntProperty(name = "Whorl count end", default = 3, min = 1)
    relBranchLength: bpy.props.FloatProperty(name = "Relative branch length", default = 1.0, min = 0.0, max = 1.0)
    relBranchLengthVariation: bpy.props.FloatProperty(name = "Relative branch length variation", default = 0.0, min = 0.0, soft_max = 1.0)
    
    #branch_taper_curve: bpy.props.PointerProperty(type=bpy.types.CurveMapping)
    useTaperCurve: bpy.props.BoolProperty(name = "Use taper curve", default = False)
    ringResolution: bpy.props.IntProperty(name = "Ring resolution", default = 6, min = 3)
    branchesStartHeightGlobal: bpy.props.FloatProperty(name = "Branches start height global", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightGlobal: bpy.props.FloatProperty(name = "Branches end height global", default = 1.0, min = 0.0, max = 1.0)
    branchesStartHeightCluster: bpy.props.FloatProperty(name = "Branches start height cluster", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightCluster: bpy.props.FloatProperty(name = "Branches end height cluster", default = 1.0, min = 0.0, max = 1.0)
    branchesStartPointVariation: bpy.props.FloatProperty(name = "Branches start point variation", default = 0.0, min = 0.0, soft_max = 1.0)
    
    shownoiseSettingsPanel: bpy.props.BoolProperty(name = "Show/hide noise settings", default=True)
        
    noiseAmplitudeHorizontalBranch: bpy.props.FloatProperty(name = "Noise amplitude horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVerticalBranch: bpy.props.FloatProperty(name = "Noise amplitude vertical", default = 0.0, min = 0.0)
    noiseAmplitudeBranchGradient: bpy.props.FloatProperty(name = "Noise amplitude gradient", default = 0.0, min = 0.0)
    noiseAmplitudeBranchExponent: bpy.props.FloatProperty(name = "Noise amplitude exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise scale", default = 1.0, min = 0.0, unit='LENGTH')
        
    showangleSettingsPanel: bpy.props.BoolProperty(name = "Show/hide angle settings", default=True)
    
    verticalAngleCrownStart: bpy.props.FloatProperty(name = "Vertical angle crown start", default = math.pi / 4.0, unit = 'ROTATION')
    verticalAngleCrownEnd: bpy.props.FloatProperty(name = "Vertical angle crown end", default = math.pi / 4.0, unit = 'ROTATION')
    verticalAngleBranchStart: bpy.props.FloatProperty(name = "Vertical angle branch start", unit = 'ROTATION')
    verticalAngleBranchEnd: bpy.props.FloatProperty(name = "Vertical angle branch end", unit = 'ROTATION')
    branchAngleMode: bpy.props.PointerProperty(type = angleModeEnumProp)
    useFibonacciAngles: bpy.props.BoolProperty(name = "Use Fibonacci angles")
    fibonacciNr: bpy.props.PointerProperty(type = fibonacciProps)
    rotateAngleRange: bpy.props.FloatProperty(name = "Rotate angle range", unit = 'ROTATION')
    rotateAngleOffset: bpy.props.FloatProperty(name = "Rotate angle offset", unit = 'ROTATION')
    
    rotateAngleCrownStart: bpy.props.FloatProperty(name = "Rotate angle crown start", unit = 'ROTATION')
    rotateAngleCrownEnd: bpy.props.FloatProperty(name = "Rotate angle crown end", unit = 'ROTATION')
    rotateAngleBranchStart: bpy.props.FloatProperty(name = "Rotate angle branch start", unit = 'ROTATION')
    rotateAngleBranchEnd: bpy.props.FloatProperty(name = "Rotate angle branch end", unit = 'ROTATION')
    rotateAngleRangeFactor: bpy.props.FloatProperty(name = "Rotate angle range factor", default = 1.0, min = 0.0, soft_max = 2.0)
    
    reducedCurveStepCutoff: bpy.props.FloatProperty(name = "Reduced curve step cutoff", min = 0.0, soft_max = 1.0)
    reducedCurveStepFactor: bpy.props.FloatProperty(name = "Reduced curve step factor", min = 0.0, max = 1.0)
    branchGlobalCurvatureStart: bpy.props.FloatProperty(name = "Branch global curvature start", unit = 'ROTATION')
    branchGlobalCurvatureEnd: bpy.props.FloatProperty(name = "Branch global curvature end", unit = 'ROTATION')
    branchCurvatureStart: bpy.props.FloatProperty(name = "Branch curvature start", unit = 'ROTATION')
    branchCurvatureEnd: bpy.props.FloatProperty(name = "Branch curvature end", unit = 'ROTATION')
    branchCurvatureOffsetStrength: bpy.props.FloatProperty(name = "Branch curvature offset", min = 0.0, unit = 'LENGTH')
            
    showsplitSettingsPanel: bpy.props.BoolProperty(name = "Show/hide split settings", default=True)
    
    nrSplitsPerBranch: bpy.props.FloatProperty(name = "Nr splits per branch", default = 0.0, min = 0.0)
    branchSplitMode: bpy.props.PointerProperty(type=splitModeEnumProp)
    branchSplitRotateAngle: bpy.props.FloatProperty(name = "Branch split rotate angle", unit = 'ROTATION')
    branchSplitAxisVariation: bpy.props.FloatProperty(name = "Branch split axis variation", min = 0.0)
    
    branchSplitAngle: bpy.props.FloatProperty(name = "Branch split angle", min = 0.0, unit = 'ROTATION')
    branchSplitPointAngle: bpy.props.FloatProperty(name = "Branch split point angle", min = 0.0, unit = 'ROTATION')
    
    splitsPerBranchVariation: bpy.props.FloatProperty(name = "Splits per branch variation", min = 0.0, max = 1.0)
    branchVariance: bpy.props.FloatProperty(name = "Branch varianace", default = 0.0, min = 0.0, max = 1.0)
    outwardAttraction: bpy.props.FloatProperty(name = "Outward attraction", default = 0.0, min = 0.0, soft_max = 1.0)
    branchSplitHeightVariation: bpy.props.FloatProperty(name = "Branch split height variation", default = 0.0, min = 0.0, max = 1.0)
    branchSplitLengthVariation: bpy.props.FloatProperty(name = "Branch split length variation", default = 0.0, min = 0.0, max = 1.0)
        
    showBranchSplitHeights: bpy.props.BoolProperty(name = "Show/hide split heights", default=True)
    branchSplitHeightInLevelList: bpy.props.PointerProperty(type=floatListProp01)
    branchSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0)
    maxSplitHeightUsed: bpy.props.IntProperty(default = 0)
    
    
class leafClusterSettings(bpy.types.PropertyGroup):
    leafParentClusterBoolList: bpy.props.PointerProperty(type=leafParentClusterBoolListProp)
    showleafSettingsPanel: bpy.props.BoolProperty(name = "Show/hide leaf settings", default = True)
    leavesDensity: bpy.props.FloatProperty(name = "Leaves density", default = 0.0, min = 0.0)
    leafSize: bpy.props.FloatProperty(name = "Leaf size", default = 0.1, min = 0.0, unit = 'LENGTH')
    leafAspectRatio: bpy.props.FloatProperty(name = "Leaf aspect ratio", default = 1.0, min = 0.0, soft_max = 2.0)
    leafAngleMode: bpy.props.PointerProperty(type = leafAngleModeEnumProp)
    leafType: bpy.props.PointerProperty(type = leafTypeEnumProp)
    leafWhorlCount: bpy.props.IntProperty(name = "Whorl count", default = 3, min = 3)
    leafStartHeightGlobal: bpy.props.FloatProperty(name = "Leaf start height global", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightGlobal: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafStartHeightCluster: bpy.props.FloatProperty(name = "Leaf start height cluster", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightCluster: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafVerticalAngleBranchStart: bpy.props.FloatProperty(name = "Leaf vertical angle branch start", unit = 'ROTATION')
    leafVerticalAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf vertical angle branch end", unit = 'ROTATION')
    leafRotateAngleBranchStart: bpy.props.FloatProperty(name = "Leaf rotate angle branch start", unit = 'ROTATION')
    leafRotateAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf rotate angle branch end", unit = 'ROTATION')
    leafTiltAngleBranchStart: bpy.props.FloatProperty(name = "Leaf tilt angle branch start", unit = 'ROTATION')
    leafTiltAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf tilt angle branch end", unit = 'ROTATION')
    
    
class UL_stemSplitLevelList(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_0(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_1(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_2(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_3(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_4(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        
class UL_branchSplitLevelListLevel_5(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_6(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_7(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_8(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_9(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_10(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_11(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_12(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_13(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_14(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_15(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_16(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_17(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_18(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)

class UL_branchSplitLevelListLevel_19(bpy.types.UIList): #template for UIList
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
        

class treeGenPanel(bpy.types.Panel):
    bl_label = "Tree Generator"
    bl_idname = "PT_TreeGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        
        row.label(text=f"test: {test_instance.x}")
        
        layout.prop(context.scene.treeSettings, "folder_path")
        
        layout.prop(context.scene.treeSettings, "file_name")  # String input for file name
        
        #layout.operator("export.save_properties_file", text="Save Properties")
        #layout.operator("export.load_properties_file", text="Load Properties")
        
        row = layout.row()
        row.label(text="Preset: ")
        row.prop(context.scene.treeSettings.treePreset, "value", text="")
        row = layout.row()
        row.operator("export.load_preset", text="Load Preset")
        
        #row = layout.row()
        #row.label(icon = 'COLORSET_12_VEC')
        #row.operator("object.generate_tree", text="Generate Tree")
    
class treeSettingsPanel(bpy.types.Panel):
    bl_label = "Tree Settings"
    bl_idname = "PT_treeSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text="Select Bark Material:")
        row.prop_search(context.scene, "bark_material", bpy.data, "materials", text="")
        
        row = layout.row()
        row.label(text="Select Leaf Material:")
        row.prop_search(context.scene, "leaf_material", bpy.data, "materials", text="")
 
        row = layout.row()
        layout.prop(context.scene.treeSettings, "treeHeight")  
        row = layout.row()
        layout.prop(context.scene.treeSettings, "treeGrowDir")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "taper")
        row = layout.row()
        layout.template_curve_mapping(myCurveData('Stem'), "mapping")
        layout.operator("scene.init_button", text="Reset")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "branchTipRadius")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "ringSpacing")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemRingResolution")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "resampleDistance")

class noiseSettingsPanel(bpy.types.Panel):
    bl_label = "Noise Settings"
    bl_idname = "PT_noiseSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "noiseAmplitudeVertical")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "noiseAmplitudeHorizontal")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "noiseAmplitudeGradient")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "noiseAmplitudeExponent")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "noiseScale")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "seed")
        
class angleSettingsPanel(bpy.types.Panel):
    bl_label = "Angle Settings"
    bl_idname = "PT_angleSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "curvatureStart")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "curvatureEnd")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "maxCurveSteps")
        
class addStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_stem_split_level"
    bl_label = "Add split level"
    
    def execute(self, context):
        context.scene.treeSettings.showStemSplitHeights = True
        newSplitHeight = context.scene.treeSettings.stemSplitHeightInLevelList.add()
        newSplitHeight.value = 0.5
        context.scene.treeSettings.stemSplitHeightInLevelListIndex = len(context.scene.treeSettings.stemSplitHeightInLevelList) - 1
        return {'FINISHED'}
      
class removeStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_stem_split_level"
    bl_label = "Remove split level"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.treeSettings.showStemSplitHeights = True
        if len(context.scene.treeSettings.stemSplitHeightInLevelList) > 0:
            context.scene.treeSettings.stemSplitHeightInLevelList.remove(len(context.scene.treeSettings.stemSplitHeightInLevelList) - 1)
        return {'FINISHED'}

class addBranchSplitLevel(bpy.types.Operator):
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
    
class removeBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_branch_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        context.scene.branchClusterSettingsList[self.level].showBranchSplitHeights = True
        if self.level == 0:
            if len(context.scene.treeSettings.treeSettings.branchSplitHeightInLevelList_0) > 0:
                context.scene.treeSettings.treeSettings.branchSplitHeightInLevelList_0.remove(len(context.scene.treeSettings.treeSettings.branchSplitHeightInLevelList_0) - 1)
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

class splitSettingsPanel(bpy.types.Panel):
    bl_label = "Split Settings"
    bl_idname = "PT_splitSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "nrSplits")
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "variance", slider=True)
        
        row = layout.row()
        split = row.split(factor=0.5)
        split.label(text="Stem split mode")
        split.prop(context.scene.treeSettings, "stemSplitMode", text="")
        mode = scene.treeSettings.stemSplitMode
        if mode == "ROTATE_ANGLE":
            row = layout.row()
            layout.prop(context.scene.treeSettings, "stemSplitRotateAngle")
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "curvOffsetStrength")
        
        box = layout.box()
        row = box.row()
        
        row.prop(context.scene.treeSettings, "showStemSplitHeights", icon="TRIA_DOWN" if context.scene.treeSettings.showStemSplitHeights else "TRIA_RIGHT", emboss=False, text="")
        
        row.operator("scene.add_stem_split_level", text="Add split level")
        row.operator("scene.remove_stem_split_level", text="Remove").index = scene.treeSettings.stemSplitHeightInLevelListIndex
        if context.scene.treeSettings.showStemSplitHeights == True:
            row = layout.row()
            row.template_list("UL_stemSplitLevelList", "", scene.treeSettings, "stemSplitHeightInLevelList", scene.treeSettings, "stemSplitHeightInLevelListIndex")
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "splitHeightVariation")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "splitLengthVariation")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemSplitAngle")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemSplitPointAngle")
        row = layout.row()
        
def draw_parent_cluster_bools(layout, scene, cluster_index):
    boolListItem = scene.branchClusterSettingsList[cluster_index].parentClusterBoolList.value
    
    boolCount = 0
    for j, boolItem in enumerate(boolListItem):
        split = layout.split(factor=0.6)
        if boolCount == 0:
            split.label(text=f"Stem")
            boolCount += 1
        else:
            split.label(text=f"Branch cluster {boolCount - 1}")
            boolCount += 1
            
        rightColumn = split.column(align=True)
        row = rightColumn.row(align=True)
        row.alignment = 'CENTER'
        
        op = row.operator("scene.toggle_bool", text="", depress=boolItem.value)
        op.list_index = cluster_index
        op.bool_index = j

def draw_leaf_cluster_bools(layout, scene, cluster_index, leafParentClusterBool):
    boolListItem = scene.leafClusterSettingsList[cluster_index].leafParentClusterBoolList.value
    
    row = layout.row()
    row.prop(leafParentClusterBool, "show_leaf_cluster", icon="TRIA_DOWN" if leafParentClusterBool.show_leaf_cluster else "TRIA_RIGHT", emboss=False, text="Parent clusters", toggle=True)
    
    if scene.leafClusterSettingsList[cluster_index].leafParentClusterBoolList.show_leaf_cluster == True:
        row = layout.row()
        row.label(text=f"TEST cluster index {cluster_index}")
        for j, boolItem in enumerate(boolListItem):
            split = layout.split(factor=0.6)
            if j == 0:
                split.label(text=f"Stem")
            else:
                split.label(text=f"Branch cluster {j - 1}")
            rightColumn = split.column(align=True)
            row = rightColumn.row(align=True)
            row.alignment = 'CENTER'
            
            op = row.operator("scene.toggle_leaf_bool", text="", depress=boolItem.value)
            op.list_index = cluster_index
            op.bool_index = j

class toggleBool(bpy.types.Operator):
    bl_idname = "scene.toggle_bool"
    bl_label = "Toggle Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.branchClusterSettingsList[self.list_index].parentClusterBoolList.value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'}
        
class branchSettingsPanel(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_branchSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row(align = True)
        row.operator("scene.add_list_item", text="Add")
        row.operator("scene.remove_list_item", text="Remove")
                
        row = layout.row()
        for i, settings in enumerate(scene.branchClusterSettingsList):
            if i < len(scene.branchClusterSettingsList):
                box = layout.box()
                box.prop(scene.branchClusterSettingsList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
                
                if scene.branchClusterSettingsList[i].show_branch_cluster:
                    box1 = box.box()
                    row = box1.row()
                    
                    row.prop(scene.branchClusterSettingsList[i].parentClusterBoolList, "show_cluster", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].parentClusterBoolList.show_cluster else "TRIA_RIGHT", emboss=False, text=f"Parent clusters", toggle=True)
                    
                    if scene.branchClusterSettingsList[i].parentClusterBoolList.show_cluster:
                        draw_parent_cluster_bools(box1, scene, i)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Number of branches")
                    split.prop(scene.branchClusterSettingsList[i], "nrBranches", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Tree shape")
                    split.prop(scene.branchClusterSettingsList[i].treeShape, "value", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branch shape")
                    split.prop(scene.branchClusterSettingsList[i].branchShape, "value", text="")
                    
                    box2 = box.box()
                    split = box2.split(factor=0.6)
                    split.label(text="Branch type")
                    split.prop(scene.branchClusterSettingsList[i].branchType, "value", text="")
                    
                    if scene.branchClusterSettingsList[i].branchType.value == 'WHORLED':
                        split = box2.split(factor=0.6)
                        split.label(text="Branch whorl count start")
                        split.prop(scene.branchClusterSettingsList[i], "branchWhorlCountStart", text="")
                        
                        split = box2.split(factor=0.6)
                        split.label(text="Branch whorl count end")
                        split.prop(scene.branchClusterSettingsList[i], "branchWhorlCountEnd", text="")
                                        
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLength", text="", slider=True)
                                        
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length variation")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLengthVariation", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Taper factor")
                    if i < len(scene.taperFactorList):
                        split.prop(scene.taperFactorList[i], "taperFactor", text="", slider=True)
                    
                    
                    
                    
                    split = box.split(factor=0.6)
                    split.label(text="Ring resolution")
                    split.prop(scene.branchClusterSettingsList[i], "ringResolution", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches start height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightGlobal", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches end height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightGlobal", text="", slider=True)
                    
                    if i > 0: # hide for first branch cluster since it can only have the stem as parent
                        split = box.split(factor=0.6)
                        split.label(text="Branches start height cluster")
                        split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightCluster", text="", slider=True)
                        
                        split = box.split(factor=0.6)
                        split.label(text="Branches end height cluster")
                        split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightCluster", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches start point variation")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartPointVariation", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.prop(scene.branchClusterSettingsList[i], "shownoiseSettingsPanel", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].shownoiseSettingsPanel else "TRIA_RIGHT", emboss=False, text="Noise settings", toggle=True)
                if scene.branchClusterSettingsList[i].shownoiseSettingsPanel:
                    box1 = box.box()
                    split = box1.split(factor=0.6)
                    split.label(text="Noise Amplitude Horizontal")
                    split.prop(scene.branchClusterSettingsList[i], "noiseAmplitudeHorizontalBranch", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Noise Amplitude Vertical")
                    split.prop(scene.branchClusterSettingsList[i], "noiseAmplitudeVerticalBranch", text="")
                                        
                    split = box1.split(factor=0.6)
                    split.label(text="Noise Amplitude Gradient")
                    split.prop(scene.branchClusterSettingsList[i], "noiseAmplitudeBranchGradient", text="")
                                        
                    split = box1.split(factor=0.6)
                    split.label(text="Noise Amplitude Exponent")
                    split.prop(scene.branchClusterSettingsList[i], "noiseAmplitudeBranchExponent", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Noise Scale")
                    split.prop(scene.branchClusterSettingsList[i], "noiseScale", text="")
                
                split = box.split(factor=0.6)
                split.prop(scene.branchClusterSettingsList[i], "showangleSettingsPanel", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showangleSettingsPanel else "TRIA_RIGHT", emboss=False, text="Angle settings", toggle=True)
                if scene.branchClusterSettingsList[i].showangleSettingsPanel:
                    box1 = box.box()
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle crown start")
                    split.prop(scene.branchClusterSettingsList[i], "verticalAngleCrownStart", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle crown end")
                    split.prop(scene.branchClusterSettingsList[i], "verticalAngleCrownEnd", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle branch start")
                    split.prop(scene.branchClusterSettingsList[i], "verticalAngleBranchStart", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle branch end")
                    split.prop(scene.branchClusterSettingsList[i], "verticalAngleBranchEnd", text="")
                    
                    box2 = box1.box()
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch angle mode")
                    split.prop(scene.branchClusterSettingsList[i].branchAngleMode, "value", text="")
                    
                    if scene.branchClusterSettingsList[i].branchAngleMode.value == 'WINDING':
                        split = box2.split(factor=0.6)
                        split.label(text="Use Fibonacci angles")
                        split.prop(scene.branchClusterSettingsList[i], "useFibonacciAngles", text="")
                        if scene.branchClusterSettingsList[i].useFibonacciAngles == True:
                            split = box2.split(factor=0.6)
                            split.label(text="Fibonacci number")
                            split.prop(scene.branchClusterSettingsList[i].fibonacciNr, "fibonacci_nr", text="")
                            
                            split1 = box2.split(factor=0.6)
                            split1.label(text="Angle:")
                            split1.label(text=f"{scene.branchClusterSettingsList[i].fibonacciNr.fibonacci_angle * 180.0 / math.pi:.2f}°")
                            
                    if scene.branchClusterSettingsList[i].branchAngleMode.value != 'ADAPTIVE' and (scene.branchClusterSettingsList[i].useFibonacciAngles == False or scene.branchClusterSettingsList[i].branchAngleMode.value == 'SYMMETRIC'):
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle range")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleRange", text="")
                        
                    if scene.branchClusterSettingsList[i].useFibonacciAngles == False and scene.branchClusterSettingsList[i].branchAngleMode.value == 'WINDING':
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle offset")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleOffset", text="")
                        
                    if scene.branchClusterSettingsList[i].useFibonacciAngles == False or scene.branchClusterSettingsList[i].branchAngleMode.value == 'SYMMETRIC':
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle crown start")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleCrownStart", text="")
                        
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle crown end")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleCrownEnd", text="")
                        
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle branch start")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleBranchStart", text="")
                        
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle branch end")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleBranchEnd", text="")
                    
                    if scene.branchClusterSettingsList[i].branchAngleMode.value == 'ADAPTIVE':
                        split = box2.split(factor=0.6)
                        split.label(text="Rotate angle range factor")
                        split.prop(scene.branchClusterSettingsList[i], "rotateAngleRangeFactor", text="", slider=True)
                    
                    box3 = box1.box()
                                        
                    split = box3.split(factor=0.6)
                    split.label(text="Reduced curve step cutoff")
                    split.prop(scene.branchClusterSettingsList[i], "reducedCurveStepCutoff", text="")
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Reduced curve step factor")
                    split.prop(scene.branchClusterSettingsList[i], "reducedCurveStepFactor", text="", slider=True)
                    
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Branch global curvature start")
                    split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureStart", text="")
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Branch global curvature end")
                    split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureEnd", text="")
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Branch curvature start")
                    split.prop(scene.branchClusterSettingsList[i], "branchCurvatureStart", text="")
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Branch curvature end")
                    split.prop(scene.branchClusterSettingsList[i], "branchCurvatureEnd", text="")
                    
                    split = box3.split(factor=0.6)
                    split.label(text="Branch curvature offset")
                    split.prop(scene.branchClusterSettingsList[i], "branchCurvatureOffsetStrength", text="")
                    
                split = box.split(factor=0.6)
                split.prop(scene.branchClusterSettingsList[i], "showsplitSettingsPanel", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showsplitSettingsPanel else "TRIA_RIGHT", emboss=False, text="Split settings", toggle=True)
                
                if scene.branchClusterSettingsList[i].showsplitSettingsPanel:
                    box2 = box.box()
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Nr splits per branch")
                    split.prop(scene.branchClusterSettingsList[i], "nrSplitsPerBranch", text="")
                    
                    box3 = box2.box()
                    split = box3.split(factor=0.6)
                    split.label(text="Branch split mode")
                    split.prop(scene.branchClusterSettingsList[i].branchSplitMode, "value", text="")
                    mode = scene.branchClusterSettingsList[i].branchSplitMode.value
                    if mode == "ROTATE_ANGLE":
                        split = box3.split(factor=0.6)
                        split.label(text="Branch split rotate angle")
                        split.prop(scene.branchClusterSettingsList[i], "branchSplitRotateAngle", text="")
                            
                    if mode == "HORIZONTAL":
                        split = box3.split(factor=0.6)
                        split.label(text="Branch split axis variation")
                        split.prop(scene.branchClusterSettingsList[i], "branchSplitAxisVariation", text="")
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split angle")
                    split.prop(scene.branchClusterSettingsList[i], "branchSplitAngle", text="")
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split point angle")
                    split.prop(scene.branchClusterSettingsList[i], "branchSplitPointAngle", text="")
                        
                    split = box2.split(factor=0.6)
                    split.label(text="Splits per branch variation")
                    split.prop(scene.branchClusterSettingsList[i], "splitsPerBranchVariation", text="")
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch variance")
                    split.prop(scene.branchClusterSettingsList[i], "branchVariance", text="", slider=True)
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Outward attraction")
                    split.prop(scene.branchClusterSettingsList[i], "outwardAttraction", text="", slider=True)
                
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split height variation")
                    split.prop(scene.branchClusterSettingsList[i], "branchSplitHeightVariation", text="", slider=True)
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split length variation")
                    split.prop(scene.branchClusterSettingsList[i], "branchSplitLengthVariation", text="", slider=True)
                    
                    row = box2.row()
                    
                    row.prop(scene.branchClusterSettingsList[i], "showBranchSplitHeights", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showBranchSplitHeights else "TRIA_RIGHT", text="", toggle=True)
            
                    row.operator("scene.add_branch_split_level", text="Add split level").level = i
                    row.operator("scene.remove_branch_split_level", text="Remove").level = i
                    
                    if context.scene.branchClusterSettingsList[i].showBranchSplitHeights == True:
                        row = box2.row()
                        if i == 0:
                            row.template_list("UL_branchSplitLevelListLevel_0", "", scene.treeSettings, "branchSplitHeightInLevelList_0", scene.treeSettings, "branchSplitHeightInLevelListIndex_0")
                        if i == 1:
                            row.template_list("UL_branchSplitLevelListLevel_1", "", scene.treeSettings, "branchSplitHeightInLevelList_1", scene.treeSettings, "branchSplitHeightInLevelListIndex_1")
                        if i == 2:
                            row.template_list("UL_branchSplitLevelListLevel_2", "", scene.treeSettings, "branchSplitHeightInLevelList_2", scene.treeSettings, "branchSplitHeightInLevelListIndex_2")
                        if i == 3:
                            row.template_list("UL_branchSplitLevelListLevel_3", "", scene.treeSettings, "branchSplitHeightInLevelList_3", scene.treeSettings, "branchSplitHeightInLevelListIndex_3")
                        if i == 4:
                            row.template_list("UL_branchSplitLevelListLevel_4", "", scene.treeSettings, "branchSplitHeightInLevelList_4", scene.treeSettings, "branchSplitHeightInLevelListIndex_4")
                        if i == 5:
                            row.template_list("UL_branchSplitLevelListLevel_5", "", scene.treeSettings, "branchSplitHeightInLevelList_5", scene.treeSettings, "branchSplitHeightInLevelListIndex_5")
                        if i == 6:
                            row.template_list("UL_branchSplitLevelListLevel_6", "", scene.treeSettings, "branchSplitHeightInLevelList_6", scene.treeSettings, "branchSplitHeightInLevelListIndex_6")
                        if i == 7:
                            row.template_list("UL_branchSplitLevelListLevel_7", "", scene.treeSettings, "branchSplitHeightInLevelList_7", scene.treeSettings, "branchSplitHeightInLevelListIndex_7")
                        if i == 8:
                            row.template_list("UL_branchSplitLevelListLevel_8", "", scene.treeSettings, "branchSplitHeightInLevelList_8", scene.treeSettings, "branchSplitHeightInLevelListIndex_8")
                        if i == 9:
                            row.template_list("UL_branchSplitLevelListLevel_9", "", scene.treeSettings, "branchSplitHeightInLevelList_9", scene.treeSettings, "branchSplitHeightInLevelListIndex_9")
                        if i == 10:
                            row.template_list("UL_branchSplitLevelListLevel_10", "", scene.treeSettings, "branchSplitHeightInLevelList_10", scene.treeSettings, "branchSplitHeightInLevelListIndex_10")
                        if i == 11:
                            row.template_list("UL_branchSplitLevelListLevel_11", "", scene.treeSettings, "branchSplitHeightInLevelList_11", scene.treeSettings, "branchSplitHeightInLevelListIndex_11")
                        if i == 12:
                            row.template_list("UL_branchSplitLevelListLevel_12", "", scene.treeSettings, "branchSplitHeightInLevelList_12", scene.treeSettings, "branchSplitHeightInLevelListIndex_12")
                        if i == 13:
                            row.template_list("UL_branchSplitLevelListLevel_13", "", scene.treeSettings, "branchSplitHeightInLevelList_13", scene.treeSettings, "branchSplitHeightInLevelListIndex_13")
                        if i == 14:
                            row.template_list("UL_branchSplitLevelListLevel_14", "", scene.treeSettings, "branchSplitHeightInLevelList_14", scene.treeSettings, "branchSplitHeightInLevelListIndex_14")
                        if i == 15:
                            row.template_list("UL_branchSplitLevelListLevel_15", "", scene.treeSettings, "branchSplitHeightInLevelList_15", scene.treeSettings, "branchSplitHeightInLevelListIndex_15")
                        if i == 16:
                            row.template_list("UL_branchSplitLevelListLevel_16", "", scene.treeSettings, "branchSplitHeightInLevelList_16", scene.treeSettings, "branchSplitHeightInLevelListIndex_16")
                        if i == 17:
                            row.template_list("UL_branchSplitLevelListLevel_17", "", scene.treeSettings, "branchSplitHeightInLevelList_17", scene.treeSettings, "branchSplitHeightInLevelListIndex_17")
                        if i == 18:
                            row.template_list("UL_branchSplitLevelListLevel_18", "", scene.treeSettings, "branchSplitHeightInLevelList_18", scene.treeSettings, "branchSplitHeightInLevelListIndex_18")
                        if i == 19:
                            row.template_list("UL_branchSplitLevelListLevel_19", "", scene.treeSettings, "branchSplitHeightInLevelList_19", scene.treeSettings, "branchSplitHeightInLevelListIndex_19")
                        if i > 19:
                            j = 0
                            splitLevelList = scene.treeSettings.branchSplitHeightInLevelListList[i - 6].value
                            for splitLevel in splitLevelList:
                                box2.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
                                j += 1

class addItem(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        
        # TEST
        TESTstartNodeInfo = module.startNodeInfo(None, 0, 0.0, 0.8, 0.0, 0.5)
        self.report({'INFO'}, f"TESTstartNodeInfo: {TESTstartNodeInfo.endTval}")
        
        
        
        #taperCurveName = f"branchCluster{context.scene.branchClusters}TaperMapping"
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        #TESTcurveElement = nodeGroups.nodes[taper_node_mapping[taperCurveName]].mapping.curves[3]
        
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        #curveElement = nodeGroups.nodes[taper_node_mapping['branchCluster0TaperMapping']].mapping.curves[3] 
        
        
        
        context.scene.treeSettings.branchClusters += 1
        branchSettingsPanel = context.scene.branchClusterSettingsList.add()
        
        for b in range(0, context.scene.treeSettings.branchClusters):
            context.scene.branchClusterSettingsList[context.scene.treeSettings.branchClusters - 1].parentClusterBoolList.value.add()
        context.scene.branchClusterSettingsList[context.scene.treeSettings.branchClusters - 1].parentClusterBoolList.value[0].value = True
        
        #branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
        
        #while context.scene.branchClusters - 20 < len(context.scene.branchSplitHeightInLevelListList) and len(context.scene.branchSplitHeightInLevelListList) > 0:
        #    context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
        
        #while context.scene.branchClusters - 20 > len(context.scene.branchSplitHeightInLevelListList):
        #    context.scene.branchSplitHeightInLevelListList.add()
        
        taperFactorItem = context.scene.taperFactorList.add()
        taperFactorItem.taperFactor = 1.0
        
        for leafSettings in context.scene.leafClusterSettingsList:
            leafSettings.leafParentClusterBoolList.value.add()
        
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        if len(context.scene.branchClusterSettingsList) > 0:
            context.scene.treeSettings.branchClusters -= 1
            context.scene.branchClusterSettingsList.remove(len(context.scene.branchClusterSettingsList) - 1)
            
        #if len(context.scene.parentClusterBoolListList) > 0:
        #    listToClear = context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value
        #    lenToClear = len(listToClear)
        #    for i in range(0, lenToClear):
        #        context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value.remove(len(context.scene.parentClusterBoolListList[i].value) - 1)
        #    context.scene.parentClusterBoolListList.remove(len(context.scene.parentClusterBoolListList) - 1)
            
        #if len(context.scene.branchSplitHeightInLevelListList) > 0 and context.scene.branchClusters > 5:
        #    context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
            
        if len(context.scene.taperFactorList) > 0:
            context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
          
        for leafSettings in context.scene.leafClusterSettingsList:
            if len(leafSettings.leafParentClusterBoolList.value) > 1:
                leafSettings.leafParentClusterBoolList.remove(len(leafSettings.leafParentClusterBoolList.value) - 1)
                
                allFalse = True
                for b in leafSettings.leafParentClusterBoolList:
                    if b.value == True:
                        allFalse = False
                if allFalse == True:
                    leafSettings.leafParentClusterBoolList[0].value = True
            
        return {'FINISHED'}

class addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.treeSettings.leafClusters += 1
        newLeafSettings = context.scene.leafClusterSettingsList.add()
        
        
        leafParentClusterBoolList = newLeafSettings.leafParentClusterBoolList
        stemBool = leafParentClusterBoolList.value.add()
        stemBool = True
                
        #for b in range(0, len(context.scene.branchClusterSettingsList)):
        #    context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value.add()
        #
        #leafParentClusterBoolListList.value[0].value = True
        return {'FINISHED'}
        
class removeLeafItem(bpy.types.Operator):
    bl_idname = "scene.remove_leaf_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        if context.scene.treeSettings.leafClusters > 0:
            context.scene.treeSettings.leafClusters -= 1
        if len(context.scene.leafClusterSettingsList) > 0:
            context.scene.leafClusterSettingsList.remove(len(context.scene.leafClusterSettingsList) - 1)
           
        return {'FINISHED'}
    
class leafSettingsPanel(bpy.types.Panel):
    bl_label = "Leaf Settings"
    bl_idname = "PT_leafSettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row(align = True)
        row.operator("scene.add_leaf_item", text="Add")
        row.operator("scene.remove_leaf_item", text="Remove").index = context.scene.treeSettings.leavesDensityListIndex
        row = layout.row()
        
        for i, leaves in enumerate(scene.leafClusterSettingsList):
            box = layout.box()
            
            if leaves.showleafSettingsPanel:
                split = box.split(factor=0.6)
                split.label(text="Leaf density")
                split.prop(scene.leafClusterSettingsList[i], "leavesDensity", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf size")
                split.prop(scene.leafClusterSettingsList[i], "leafSize", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf aspect ratio")
                split.prop(scene.leafClusterSettingsList[i], "leafAspectRatio", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf start height global")
                split.prop(scene.leafClusterSettingsList[i], "leafStartHeightGlobal", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf end height global")
                split.prop(scene.leafClusterSettingsList[i], "leafEndHeightGlobal", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf start height cluster")
                split.prop(scene.leafClusterSettingsList[i], "leafStartHeightCluster", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf end height cluster")
                split.prop(scene.leafClusterSettingsList[i], "leafEndHeightCluster", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf type")
                split.prop(scene.leafClusterSettingsList[i].leafType, "value", text="")
                
                if scene.leafClusterSettingsList[i].leafType.value == "WHORLED":
                    box1 = box.box()
                    split = box1.split(factor=0.6)
                    split.label(text="Leaf whorl count")
                    split.prop(scene.leafClusterSettingsList[i], "leafWhorlCount", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf angle mode")
                split.prop(scene.leafClusterSettingsList[i].leafAngleMode, "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Vertical angle branch start")
                split.prop(scene.leafClusterSettingsList[i], "leafVerticalAngleBranchStart", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Vertical angle branch end")
                split.prop(scene.leafClusterSettingsList[i], "leafVerticalAngleBranchEnd", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Rotate angle branch start")
                split.prop(scene.leafClusterSettingsList[i], "leafRotateAngleBranchStart", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Rotate angle branch end")
                split.prop(scene.leafClusterSettingsList[i], "leafRotateAngleBranchEnd", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Tilt angle branch start")
                split.prop(scene.leafClusterSettingsList[i], "leafTiltAngleBranchStart", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Tilt angle branch end")
                split.prop(scene.leafClusterSettingsList[i], "leafTiltAngleBranchEnd", text="")
                
                box1 = box.box()
                draw_leaf_cluster_bools(box1, scene, i, scene.leafClusterSettingsList[i].leafParentClusterBoolList)


def register():
    #save and load
    # bpy.utils.register_class(importProperties) # TODO
    # bpy.utils.register_class(exportProperties) # TODO
    # bpy.utils.register_class(loadPreset) # TODO
    
    #data types
    bpy.utils.register_class(treePresetEnumProp)
    
    bpy.utils.register_class(treeShapeEnumProp)
    bpy.utils.register_class(splitModeEnumProp)
    bpy.utils.register_class(angleModeEnumProp)
    bpy.utils.register_class(branchTypeEnumProp)
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(intPropL)
    bpy.utils.register_class(posIntProp3)
    bpy.utils.register_class(fibonacciProps)
    bpy.utils.register_class(floatProp)
    bpy.utils.register_class(posFloatProp)
    bpy.utils.register_class(posFloatPropDefault1)
    bpy.utils.register_class(floatProp01)
    bpy.utils.register_class(floatProp01default0p5)
    bpy.utils.register_class(posFloatPropSoftMax1)
    bpy.utils.register_class(posFloatPropSoftMax1Default0)
    bpy.utils.register_class(posFloatPropSoftMax2)
    bpy.utils.register_class(floatListProp)
    bpy.utils.register_class(floatListProp01)
    bpy.utils.register_class(boolProp)
    bpy.utils.register_class(parentClusterBoolListProp)
    bpy.utils.register_class(branchClusterBoolListProp)
    bpy.utils.register_class(leafParentClusterBoolListProp)
    bpy.utils.register_class(leafAngleModeEnumProp)
    bpy.utils.register_class(leafTypeEnumProp)
    
    bpy.utils.register_class(treeSettings)
    bpy.utils.register_class(branchClusterSettings)
    bpy.utils.register_class(leafClusterSettings)
    
    #operators
    bpy.utils.register_class(addItem) # TODO
    bpy.utils.register_class(removeItem) # TODO
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(toggleLeafBool)
    bpy.utils.register_class(addStemSplitLevel) # TODO
    bpy.utils.register_class(removeStemSplitLevel) # TODO
    bpy.utils.register_class(addBranchSplitLevel) # TODO
    bpy.utils.register_class(removeBranchSplitLevel) # TODO
    # bpy.utils.register_class(generateTree) # TODO
    bpy.utils.register_class(addLeafItem) # TODO
    bpy.utils.register_class(removeLeafItem) # TODO
    bpy.utils.register_class(toggleUseTaperCurveOperator)
    bpy.utils.register_class(initButton)
    
    #panels
    bpy.utils.register_class(treeGenPanel) # TODO
    bpy.utils.register_class(treeSettingsPanel) # TODO
    bpy.utils.register_class(noiseSettingsPanel) # TODO
    bpy.utils.register_class(angleSettingsPanel) # TODO
    bpy.utils.register_class(splitSettingsPanel) # TODO
    bpy.utils.register_class(leafSettingsPanel) # TODO
    
    bpy.utils.register_class(branchSettingsPanel) # TODO
    
    
    #UILists
    bpy.utils.register_class(UL_stemSplitLevelList)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_5)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_6)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_7)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_8)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_9)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_10)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_11)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_12)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_13)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_14)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_15)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_16)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_17)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_18)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_19)
    
    # Properties
    bpy.types.Scene.treeSettings = bpy.props.PointerProperty(type=treeSettings)
    bpy.types.Scene.bark_material = bpy.props.PointerProperty(type=bpy.types.Material)
    bpy.types.Scene.leaf_material = bpy.props.PointerProperty(type=bpy.types.Material)
    
    # taperFactorList has to be its own property, because it needs to be passed to generateVerticesAndTriangles(), otherwise all branch cluster properties would have to be passed as a parameter. 
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    
    # Collections
    bpy.types.Scene.branchClusterSettingsList = bpy.props.CollectionProperty(type=branchClusterSettings)
    bpy.types.Scene.leafClusterSettingsList = bpy.props.CollectionProperty(type=leafClusterSettings)
    
def unregister():
    #save and load
    bpy.utils.unregister_class(importProperties)
    bpy.utils.unregister_class(exportProperties)
    bpy.utils.unregister_class(loadPreset)
        
    #data types
    bpy.utils.unregister_class(treeShapeEnumProp)
    bpy.utils.unregister_class(treePresetEnumProp)
    bpy.utils.unregister_class(splitModeEnumProp)
    bpy.utils.unregister_class(angleModeEnumProp)
    bpy.utils.unregister_class(branchTypeEnumProp)
    bpy.utils.unregister_class(intProp)
    bpy.utils.unregister_class(intPropL)
    bpy.utils.unregister_class(posIntProp3)
    bpy.utils.unregister_class(fibonacciProps)
    bpy.utils.unregister_class(floatProp)
    bpy.utils.unregister_class(posFloatProp)
    bpy.utils.unregister_class(posFloatPropDefault1)
    bpy.utils.unregister_class(floatProp01)
    bpy.utils.unregister_class(floatProp01default0p5)
    bpy.utils.unregister_class(posFloatPropSoftMax1)
    bpy.utils.unregister_class(posFloatPropSoftMax1Default0)
    bpy.utils.unregister_class(posFloatPropSoftMax2)
    bpy.utils.unregister_class(floatListProp)
    bpy.utils.unregister_class(floatListProp01)
    bpy.utils.unregister_class(boolProp)
    bpy.utils.unregister_class(parentClusterBoolListProp)
    bpy.utils.unregister_class(branchClusterBoolListProp)
    bpy.utils.unregister_class(leafParentClusterBoolListProp)
    bpy.utils.unregister_class(leafAngleModeEnumProp)
    bpy.utils.unregister_class(leafTypeEnumProp)
    
    bpy.utils.unregister_class(treeSettings)
    bpy.utils.unregister_class(branchClusterSettings)
    bpy.utils.unregister_class(leafClusterSettings)
    
    #operators
    bpy.utils.unregister_class(addItem)
    bpy.utils.unregister_class(removeItem)
    bpy.utils.unregister_class(toggleBool)
    bpy.utils.unregister_class(toggleLeafBool)
    bpy.utils.unregister_class(addStemSplitLevel)
    bpy.utils.unregister_class(removeStemSplitLevel)
    bpy.utils.unregister_class(addBranchSplitLevel)
    bpy.utils.unregister_class(removeBranchSplitLevel)
    bpy.utils.unregister_class(generateTree)
    bpy.utils.unregister_class(resetCurvesButton)
    bpy.utils.unregister_class(resetCurvesClusterButton)
    bpy.utils.unregister_class(addLeafItem)
    bpy.utils.unregister_class(removeLeafItem)
    
    #bpy.utils.unregister_class(evaluateButton)
    bpy.utils.unregister_class(updateButton)
    bpy.utils.unregister_class(AddBranchClusterButton)
    #bpy.utils.unregister_class(BranchClusterEvaluateButton)
    bpy.utils.unregister_class(BranchClusterResetButton)
    bpy.utils.unregister_class(initButton)
    bpy.utils.unregister_class(toggleUseTaperCurveOperator)
    
    
    #panels
    bpy.utils.unregister_class(treeGenPanel)
    bpy.utils.unregister_class(treeSettingsPanel)
    bpy.utils.unregister_class(noiseSettingsPanel)
    bpy.utils.unregister_class(angleSettingsPanel)
    bpy.utils.unregister_class(splitSettingsPanel)
    bpy.utils.unregister_class(leafSettingsPanel)
    
    bpy.utils.unregister_class(branchSettingsPanel)
    bpy.utils.unregister_class(bendBranchesPanel)
    
    #UILists
    bpy.utils.unregister_class(UL_stemSplitLevelList)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_0)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_1)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_2)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_3)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_4)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_5)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_6)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_7)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_8)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_9)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_10)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_11)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_12)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_13)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_14)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_15)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_16)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_17)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_18)
    bpy.utils.unregister_class(UL_branchSplitLevelListLevel_19)
    
    # properties
    del bpy.types.Scene.treeSettings
    del bpy.types.Scene.bark_material
    del bpy.types.Scene.leaf_material
    
    del bpy.types.Scene.taperFactorList
    
    # Collections
    del bpy.types.Scene.branchClusterSettingsList
    del bpy.types.Scene.leafClusterSettingsList
    
    
if __name__ == "__main__":
    register()