bl_info = {
    "name" : "treeGen3",
    "author" : "Jens", 
    "version" : (0,1),
    "blender" : (4,3,1),
    "description" : "Tree generator",
    "location" : "View3d > Sidebar",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",
}

import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import json

def update_fibonacci_numbers(self):
    fn0 = 1.0
    fn1 = 1.0
    self.rotate_angle_range = 360.0
    if self.fibonacci_nr > 2:
        for n in range(2, self.fibonacci_nr + 1):
            temp = fn0 + fn1
            fn0 = fn1
            fn1 = temp
    self.fibonacci_angle = 360.0 * (1.0 - fn0 / fn1)
    
    
class fibonacciProps(bpy.types.PropertyGroup):
    fibonacci_nr: bpy.props.IntProperty(name = "fibonacciNr", default=3, min=3, 
        update = lambda self, context:update_fibonacci_numbers(self))
        
    fibonacci_angle: bpy.props.FloatProperty(name="", default=0.0, options={'HIDDEN'})
    
    use_fibonacci: bpy.props.BoolProperty(name = "useFibonacci", default=False,
        update = lambda self, context:update_fibonacci_numbers(self)) ##########  -> both in one propertyGroup!
        
    #rotate_angle_range: bpy.props.FloatProperty(name="", default=0.0, min=0.0)
    #rotate_angle_offset: bpy.props.FloatProperty(name="", default=0.0)
        

    
    # fn0 = 1.0
    # fn1 = 1.0
    # if scene.fibonacciNrList[i].value > 2:
    #     for n in range(2, scene.fibonacciNrList[i].value + 1):
    #         temp = fn0 + fn1
    #         fn0 = fn1
    #         fn1 = temp
    # scene.rotateAngleCrownStartList[i].value = 360.0 * (1.0 - fn0 / fn1) #TODO 

class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=10) # reuse for all ints (?)
    
class intPropL(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=200)

class posIntProp3(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "posIntProp3", default=3, min=3, soft_max=12)

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0) # reuse for all floats (?)
    
class posFloatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0, min=0)
    
class posFloatPropDefault1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0)
    
class posFloatPropSoftMax2(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default = 1.0, min = 0, soft_max=2.0)
    
class posFloatPropSoftMax1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0, soft_max=1.0)

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
            ('CYLINDRICAL', "Cylindrical", "A cylinder-shaped tree."),
            ('TAPERED_CYLINDRICAL', "Tapered Cylindrical", "A cylinder that tapers towards the top."),
            ('FLAME', "Flame", "A flame-shaped tree."),
            ('INVERSE_CONICAL', "Inverse Conical", "An upside-down cone-shaped tree."),
            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
        ],
        default='CONICAL'        
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
            ('WINDING', "Winding", "winding branch angles")
        ],
        default='WINDING'
    )
    
class toggleBool(bpy.types.Operator):
    bl_idname = "scene.toggle_bool"
    bl_label = "Toggle Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.parentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

class toggleLeafBool(bpy.types.Operator):
    bl_idname = "scene.toggle_leaf_bool"
    bl_label = "Toggle Leaf Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.leafParentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

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


class branchClusterSettings(bpy.types.PropertyGroup):
    branchClusterBoolList: bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    nrBranches: bpy.props.IntProperty(name = "Number of branches", default = 0, min = 0)
    nrBranchesIndex: bpy.props.IntProperty(name = "nrBranchesListIndex", default=0)
    branchShape: bpy.props.PointerProperty(type = treeShapeEnumProp)
    relBranchLength: bpy.props.FloatProperty(name = "Relative branch length", default = 1.0, min = 0.0, max = 1.0)
    relBranchLengthVariation: bpy.props.FloatProperty(name = "Relative branch length variation", default = 0.0, min = 0.0, soft_max = 1.0)
    taperFactor: bpy.props.FloatProperty(name = "Taper factor", default = 1.0, min = 0.0, soft_max = 1.0)
    ringResolution: bpy.props.IntProperty(name = "Ring resolution", default = 6, min = 3)
    branchesStartHeightGlobal: bpy.props.FloatProperty(name = "Branches start height global", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightGlobal: bpy.props.FloatProperty(name = "Branches end height global", default = 1.0, min = 0.0, max = 1.0)
    branchesStartHeightCluster: bpy.props.FloatProperty(name = "Branches start height cluster", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightCluster: bpy.props.FloatProperty(name = "Branches end height cluster", default = 1.0, min = 0.0, max = 1.0)
    
    #bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    
    showNoiseSettings: bpy.props.BoolProperty(name = "Show/hide noise settings", default=True)
        
    noiseAmplitudeHorizontalBranch: bpy.props.FloatProperty(name = "Noise amplitude horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVerticalBranch: bpy.props.FloatProperty(name = "Noise amplitude vertical", default = 0.0, min = 0.0)
    noiseAmplitudeBranchGradient: bpy.props.FloatProperty(name = "Noise amplitude gradient", default = 0.0, min = 0.0)
    noiseAmplitudeBranchExponent: bpy.props.FloatProperty(name = "Noise amplitude exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise scale", default = 1.0, min = 0.0)
        
    showAngleSettings: bpy.props.BoolProperty(name = "Show/hide angle settings", default=True)
    
    verticalAngleCrownStart: bpy.props.FloatProperty(name = "Vertical angle crown start")
    verticalAngleCrownEnd: bpy.props.FloatProperty(name = "Vertical angle crown end")
    verticalAngleBranchStart: bpy.props.FloatProperty(name = "Vertical angle branch start")
    verticalAngleBranchEnd: bpy.props.FloatProperty(name = "Vertical angle branch end")
    branchAngleMode: bpy.props.PointerProperty(type = angleModeEnumProp)
    useFibonacciAngles: bpy.props.BoolProperty(name = "Use Fibonacci angles")
    fibonacciNr: bpy.props.PointerProperty(type = fibonacciProps)
    rotateAngleRange: bpy.props.FloatProperty(name = "Rotate angle range") # -> no longer in fibonacciProps!
    rotateAngleOffset: bpy.props.FloatProperty(name = "Rotate angle offset") # -> no longer in fibonacciProps!
    
    rotateAngleCrownStart: bpy.props.FloatProperty(name = "Rotate angle crown start")
    rotateAngleCrownEnd: bpy.props.FloatProperty(name = "Rotate angle crown end")
    rotateAngleBranchStart: bpy.props.FloatProperty(name = "Rotate angle branch start")
    rotateAngleBranchEnd: bpy.props.FloatProperty(name = "Rotate angle branch end")
    
    hangingBranches: bpy.props.BoolProperty(name = "Hanging branches")
    branchGlobalCurvatureStart: bpy.props.FloatProperty(name = "Branch global curvature start")
    branchGlobalCurvatureEnd: bpy.props.FloatProperty(name = "Branch global curvature end")
    branchCurvatureStart: bpy.props.FloatProperty(name = "Branch curvature start")
    branchCurvatureEnd: bpy.props.FloatProperty(name = "Branch curvature end")
    branchCurvatureOffsetStrength: bpy.props.FloatProperty(name = "Branch curvature offset", min = 0.0)
            
    showSplitSettings: bpy.props.BoolProperty(name = "Show/hide split settings", default=True)
    
    nrSplitsPerBranch: bpy.props.FloatProperty(name = "Nr splits per branch", default = 0.0, min = 0.0)
    branchSplitMode: bpy.props.PointerProperty(type=splitModeEnumProp)
    branchSplitRotateAngle: bpy.props.FloatProperty(name = "Branch split rotate angle")
    branchSplitAxisVariation: bpy.props.FloatProperty(name = "Branch split axis variation", min = 0.0)
    
    branchSplitAngle: bpy.props.FloatProperty(name = "Branch split angle", min = 0.0)
    branchSplitPointAngle: bpy.props.FloatProperty(name = "Branch split point angle", min = 0.0)
    
    splitsPerBranchVariation: bpy.props.FloatProperty(name = "Splits per branch variation", min = 0.0, max = 1.0)
    branchVariance: bpy.props.FloatProperty(name = "Branch varianace", default = 0.0, min = 0.0, max = 1.0)
    branchSplitHeightVariation: bpy.props.FloatProperty(name = "Branch split height variation", default = 0.0, min = 0.0, max = 1.0)
    branchSplitLengthVariation: bpy.props.FloatProperty(name = "Branch split length variation", default = 0.0, min = 0.0, max = 1.0)
        
    showBranchSplitHeights: bpy.props.BoolProperty(name = "Show/hide split heights", default=True)
    branchSplitHeightInLevelListList: bpy.props.PointerProperty(type=floatListProp01)
    branchSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0)
    
class leafClusterSettings(bpy.types.PropertyGroup):
    showLeafSettings: bpy.props.BoolProperty(name = "Show/hide leaf settings", default = True)
    leavesDensity: bpy.props.FloatProperty(name = "Leaves density", default = 0.0, min = 0.0)
    leafSize: bpy.props.FloatProperty(name = "Leaf size", default = 0.1, min = 0.0)
    leafAspectRatio: bpy.props.FloatProperty(name = "Leaf aspect ratio", default = 1.0, min = 0.0, soft_max = 2.0)
    leafAngleMode: bpy.props.PointerProperty(type = leafAngleModeEnumProp)
    leafType: bpy.props.PointerProperty(type = leafTypeEnumProp)
    leafStartHeightGlobal: bpy.props.FloatProperty(name = "Leaf start height global", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightGlobal: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafStartHeightCluster: bpy.props.FloatProperty(name = "Leaf start height cluster", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightCluster: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafVerticalAngleBranchStart: bpy.props.FloatProperty(name = "Leaf vertical angle branch start")
    leafVerticalAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf vertical angle branch end")
    leafRotateAngleBranchStart: bpy.props.FloatProperty(name = "Leaf rotate angle branch start")
    leafRotateAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf rotate angle branch end")
    leafTiltAngleBranchStart: bpy.props.FloatProperty(name = "Leaf tilt angle branch start")
    leafTiltAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf tilt angle branch end")
    
    
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
        
        
class treeGenPanel(bpy.types.Panel):
    bl_label = "Tree Generator"
    bl_idname = "PT_TreeGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        layout.prop(context.scene, "file_name")  # String input for file name
        
        layout.operator("export.save_properties_file", text="Save Properties")
        layout.operator("export.load_properties_file", text="Load Properties")
        
        row = layout.row()
        row.label(icon = 'COLORSET_12_VEC')
        
        row.operator("object.generate_tree", text="Generate Tree")
        
        #if context.scene.my_tool.is_running:
        #    layout.label(text="Task in progress...")
        #    layout.prop(scene.my_tool, "progress", text="Progress")
        #else:
        #    layout.label(text="Task Complete!")
            
class treeSettings(bpy.types.Panel):
    bl_label = "Tree Settings"
    bl_idname = "PT_TreeSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text="Select Brak Material:")
        row.prop_search(context.scene, "bark_material", bpy.data, "materials", text="")
        
        row = layout.row()
        row.label(text="Select Leaf Material:")
        row.prop_search(context.scene, "leaf_material", bpy.data, "materials", text="")
        
        row = layout.row()
        layout.prop(context.scene, "treeHeight")
        row = layout.row()
        layout.prop(context.scene, "treeGrowDir")
        row = layout.row()
        layout.prop(context.scene, "taper")
        row = layout.row()
        layout.operator("scene.reset_curves", text="Reset taper curve")
        row = layout.row()
        layout.template_curve_mapping(taperCurveData('taperMapping'), "mapping")
        row = layout.row()
        layout.prop(context.scene, "branchTipRadius")
        row = layout.row()
        layout.prop(context.scene, "ringSpacing")
        row = layout.row()
        layout.prop(context.scene, "stemRingResolution")
        row = layout.row()
        layout.prop(context.scene, "resampleDistance")
        
class noiseSettings(bpy.types.Panel):
    bl_label = "Noise Settings"
    bl_idname = "PT_NoiseSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeVertical")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeHorizontal")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeGradient")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeExponent")
        row = layout.row()
        layout.prop(context.scene, "noiseScale")
        row = layout.row()
        layout.prop(context.scene, "seed")
        
class angleSettings(bpy.types.Panel):
    bl_label = "Angle Settings"
    bl_idname = "PT_AngleSettings"
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
        layout.prop(context.scene, "curvatureStart")
        row = layout.row()
        layout.prop(context.scene, "curvatureEnd")
        row = layout.row()
        layout.prop(context.scene, "maxCurveSteps")
        
class addStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_stem_split_level"
    bl_label = "Add split level"
    
    def execute(self, context):
        context.scene.showStemSplitHeights = True
        newSplitHeight = context.scene.stemSplitHeightInLevelList.add()
        newSplitHeight.value = 0.5
        context.scene.stemSplitHeightInLevelListIndex = len(context.scene.stemSplitHeightInLevelList) - 1
        return {'FINISHED'}
      
class removeStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_stem_split_level"
    bl_label = "Remove split level"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.showStemSplitHeights = True
        if len(context.scene.stemSplitHeightInLevelList) > 0:
            context.scene.stemSplitHeightInLevelList.remove(len(context.scene.stemSplitHeightInLevelList) - 1)
        return {'FINISHED'}
    
class addBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_branch_split_level"
    bl_label = "Add split level"
    level: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.branchClusterSettingsList[self.level].showBranchSplitHeights = True
        
        newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value.add()
        newSplitHeight = 0.5
        if self.level == 0:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_0.add()
            newSplitHeight.value = 0.5
        if self.level == 1:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_1.add()
            newSplitHeight.value = 0.5
        if self.level == 2:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_2.add()
            newSplitHeight.value = 0.5
        if self.level == 3:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_3.add()
            newSplitHeight.value = 0.5
        if self.level == 4:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_4.add()
            newSplitHeight.value = 0.5
        if self.level == 5:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_5.add()
            newSplitHeight.value = 0.5
        
        
        if self.level > 5:
            newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value
            newSplitHeight = 0.5
            return {'FINISHED'}
        
        #context.scene.branchSplitHeightInLevelListIndex[len(context.scene.branchSplitHeightInLevelListIndex) - 1].value = 0
        return {'FINISHED'}
    
class removeBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_branch_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        context.scene.branchClusterSettingsList[self.level].showBranchSplitHeights = True
        if self.level == 0:
            if len(context.scene.branchSplitHeightInLevelList_0) > 0:
                context.scene.branchSplitHeightInLevelList_0.remove(context.scene.branchSplitHeightInLevelListIndex_0)
                #context.scene.branchSplitHeightInLevelListIndex_0 -= 1
        if self.level == 1:
            if len(context.scene.branchSplitHeightInLevelList_1) > 0:
                context.scene.branchSplitHeightInLevelList_1.remove(len(context.scene.branchSplitHeightInLevelList_1) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_1 -= 1
        if self.level == 2:
            if len(context.scene.branchSplitHeightInLevelList_2) > 0:
                context.scene.branchSplitHeightInLevelList_2.remove(len(context.scene.branchSplitHeightInLevelList_2) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_2 -= 1
        if self.level == 3:
            if len(context.scene.branchSplitHeightInLevelList_3) > 0:
                context.scene.branchSplitHeightInLevelList_3.remove(len(context.scene.branchSplitHeightInLevelList_3) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_3 -= 1
        if self.level == 4:
            if len(context.scene.branchSplitHeightInLevelList_4) > 0:
                context.scene.branchSplitHeightInLevelList_4.remove(len(context.scene.branchSplitHeightInLevelList_4) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_4 -= 1
        if self.level == 5:
            if len(context.scene.branchSplitHeightInLevelList_5) > 0:
                context.scene.branchSplitHeightInLevelList_5.remove(len(context.scene.branchSplitHeightInLevelList_4) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_5 -= 1
        if self.level > 5:
            context.scene.branchSplitHeightInLevelListList[self.level].value.remove(len(context.scene.branchSplitHeightInLevelListList[self.level].value) - 1)
            
               #context.scene.branchSplitModeList.remove(len(context.scene.branchSplitModeList) - 1)         
        #self.report({'INFO'}, f"remove split level")
        return {'FINISHED'}
        
class splitSettings(bpy.types.Panel):
    bl_label = "Split Settings"
    bl_idname = "PT_SplitSettings"
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
        layout.prop(context.scene, "nrSplits")
        
        row = layout.row()
        layout.prop(context.scene, "variance", slider=True)
        row = layout.row()
        #layout.prop(context.scene, "stemSplitMode")
        split = row.split(factor=0.5)
        split.label(text="Stem split mode")
        split.prop(context.scene, "stemSplitMode", text="")
        mode = scene.stemSplitMode
        if mode == "ROTATE_ANGLE":
            row = layout.row()
            layout.prop(context.scene, "stemSplitRotateAngle")
        row = layout.row()
        layout.prop(context.scene, "curvOffsetStrength")
        
        box = layout.box()
        row = box.row()
        
        #box.prop(scene.branchClusterBoolListList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterBoolListList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
            
        
        row.prop(context.scene, "showStemSplitHeights", icon="TRIA_DOWN" if context.scene.showStemSplitHeights else "TRIA_RIGHT", emboss=False, text="")
        
        row.operator("scene.add_stem_split_level", text="Add split level")
        row.operator("scene.remove_stem_split_level", text="Remove").index = scene.stemSplitHeightInLevelListIndex
        if context.scene.showStemSplitHeights == True:
            row = layout.row()
            row.template_list("UL_stemSplitLevelList", "", scene, "stemSplitHeightInLevelList", scene, "stemSplitHeightInLevelListIndex")
                        
        #j = 0
        #for splitLevel in context.scene.stemSplitHeightInLevelList:
        #    box.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
        #    j += 1
            
            
        #box.template_list("UI_UL_list", "stemSplitHeightInLevelList", context.scene, "stemSplitHeightInLevelList", context.scene.stemSplitHeightInLevelList,  0)
        #box.template_list("myList", "stemSplitHeightInLevelList", context.scene, "stemSplitHeightInLevelListIndex", active_propname, *, item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)
        #row = box.row()
        
        
        row = layout.row()
        layout.prop(context.scene, "splitHeightVariation")
        row = layout.row()
        layout.prop(context.scene, "splitLengthVariation")
        row = layout.row()
        layout.prop(context.scene, "stemSplitAngle")
        row = layout.row()
        layout.prop(context.scene, "stemSplitPointAngle")
        row = layout.row()
        
def taperNodeTree():
    if 'taperNodeGroup' not in bpy.data.node_groups:
        taperCurveNodeGroup = bpy.data.node_groups.new('taperNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['taperNodeGroup'].nodes

taper_node_mapping = {}

def taperCurveData(taperCurve):
    if taperCurve not in taper_node_mapping:
        TaperNodeTree = taperNodeTree().new('ShaderNodeRGBCurve')
        taper_node_mapping[taperCurve] = TaperNodeTree.name
        
        #resetTaperCurve()
        
    nodeTree = taperNodeTree()[taper_node_mapping[taperCurve]]
    
    
    return nodeTree

class resetCurvesButton(bpy.types.Operator):
    bl_idname = "scene.reset_curves"
    bl_label = "initialise"
    
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        nrCurves = len(nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves)
        #self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
        
        #initialise values
        resetTaperCurve()
        return {'FINISHED'}
    
def reset_taper_curve_deferred():
    bpy.ops.scene.reset_curves()
    return None

def resetTaperCurve():
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    if not nodeGroups:
        return
    curveNode = nodeGroups.nodes.get(taper_node_mapping.get('taperMapping'))
    if not curveNode:
        return
    curveElement = curveNode.mapping.curves[3]
    # Initialise values
    curveElement.points[0].location = (0.0, 1.0)
    curveElement.points[1].location = (1.0, 0.0)
    curveElement.points[0].handle_type = "VECTOR"
    curveElement.points[1].handle_type = "VECTOR"
    if len(curveElement.points) > 2:
        for i in range(2, len(curveElement.points)):
            curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
    curveNode.mapping.update()
    
class exportProperties(bpy.types.Operator):
    bl_idname = "export.save_properties_file"
    bl_label = "Save Properties"
    
    def execute(self, context):
        props = context.scene  
        filename = props.file_name + ".json"  # Automatically append .json  
        filepath = bpy.path.abspath(f"//{filename}")  # Save to the specified filename  
        save_properties(filepath, self)
        self.report({'INFO'}, f'Saved properties to {filepath}')
        return {'FINISHED'}

class importProperties(bpy.types.Operator):
    bl_idname = "export.load_properties_file"
    bl_label = "Load Properties"
    
    def execute(self, context):
        props = context.scene  
        filename = props.file_name + ".json"  # Automatically append .json  
        filepath = bpy.path.abspath(f"//{filename}")  # Load from the specified filename  
        load_properties(filepath, context)
        self.report({'INFO'}, f'Loaded properties from {filepath}')
        
        #bpy.ops.object.generate_tree()
        return {'FINISHED'}
    
def load_properties(filePath, context):
    with open(filePath, 'r') as f:
        data = json.load(f)
        props = context.scene
        
        props.treeHeight = data.get("treeHeight", props.treeHeight)
        treeGrowDir = data.get("treeGrowDir", props.treeGrowDir)
        if isinstance(treeGrowDir, list) and len(treeGrowDir) == 3:
            props.treeGrowDir = treeGrowDir
        props.taper = data.get("taper", props.taper)
        
        controlPts = []
        controlPts = data.get("taperCurvePoints", controlPts)
        handleTypes = []
        handleTypes = data.get("taperCurveHandleTypes", handleTypes)
        nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
        
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
        curveElement.points[0].location = controlPts[0]
        curveElement.points[0].handle_type = handleTypes[0]
        curveElement.points[1].location = controlPts[1]
        curveElement.points[1].handle_type = handleTypes[0]
        if len(controlPts) > 2:
            for i in range(2, len(controlPts)):
                curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                curveElement.points[len(curveElement.points) - 1].location.x = controlPts[i][0]
                curveElement.points[len(curveElement.points) - 1].location.y = controlPts[i][1]
                
                curveElement.points[len(curveElement.points) - 1].handle_type = handleTypes[i]
        nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.update()
        
        props.branchTipRadius = data.get("branchTipRadius", props.branchTipRadius)
        props.ringSpacing = data.get("ringSpacing", props.ringSpacing)
        props.stemRingResolution = data.get("stemRingResolution", props.stemRingResolution)
        props.resampleDistance = data.get("resampleDistance", props.resampleDistance)
        
        props.noiseAmplitudeVertical = data.get("noiseAmplitudeVertical", props.noiseAmplitudeVertical)
        props.noiseAmplitudeHorizontal = data.get("noiseAmplitudeHorizontal", props.noiseAmplitudeHorizontal)
        props.noiseAmplitudeGradient = data.get("noiseAmplitudeGradient", props.noiseAmplitudeGradient)
        props.noiseAmplitudeExponent = data.get("noiseAmplitudeExponent", props.noiseAmplitudeExponent)
        props.noiseScale = data.get("noiseScale", props.noiseScale)
        props.seed = data.get("seed", props.seed)
        
        props.curvatureStart = data.get("curvatureStart", props.curvatureStart)
        props.curvatureEnd = data.get("curvatureEnd", props.curvatureEnd)
        props.maxCurveSteps = data.get("maxCurveSteps", props.maxCurveSteps)
        
        props.nrSplits = data.get("nrSplits", props.nrSplits)
        props.variance = data.get("variance", props.variance)
        props.stemSplitMode = data.get("stemSplitMode", props.stemSplitMode)
        props.stemSplitRotateAngle = data.get("stemSplitRotateAngle", props.stemSplitRotateAngle)
        props.curvOffsetStrength = data.get("curvOffsetStrength", props.curvOffsetStrength)
        
        for value in data.get("stemSplitHeightInLevelList", []):
            item = props.stemSplitHeightInLevelList.add()
            item.value = value
        props.stemSplitHeightInLevelListIndex = data.get("stemSplitHeightInLevelListIndex", props.stemSplitHeightInLevelListIndex)
                
        props.splitHeightVariation = data.get("splitHeightVariation", props.splitHeightVariation)
        props.splitLengthVariation = data.get("splitLengthVariation", props.splitLengthVariation)
        props.stemSplitAngle = data.get("stemSplitAngle", props.stemSplitAngle)
        props.stemSplitPointAngle = data.get("stemSplitPointAngle", props.stemSplitPointAngle)
        
        
        for outerList in props.parentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.parentClusterBoolListList.clear()
        
        props.branchClusters = data.get("branchClusters", props.branchClusters)
        
        nestedList = []
        nestedList = data.get("parentClusterBoolListList", nestedList)
        for n in range(0, props.branchClusters):
            innerList = nestedList[n]
            item = props.parentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            for b in innerList:
                i = item.value.add()
                i.value = b
                
        for outerList in props.leafParentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.leafParentClusterBoolListList.clear()
        
        nestedLeafList = []
        nestedLeafList = data.get("leafParentClusterBoolListList", nestedLeafList)
        for n in range(0, len(nestedLeafList)):
            innerLeafList = nestedLeafList[n]
            item = props.leafParentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            for b in innerLeafList:
                i = item.value.add()
                i.value = b
        
        
        props.branchClusterSettingsList.clear()
        
        for i in range(0, props.branchClusters):
            props.branchClusterSettingsList.add()
        
        for i, value in enumerate(data.get("nrBranchesList", [])):
            props.branchClusterSettingsList[i].nrBranches = value
            
        for i, value in enumerate(data.get("branchShapeList", [])):
            props.branchClusterSettingsList[i].branchShape.value = value
            
        for i, value in enumerate(data.get("relBranchLengthList", [])):
            props.branchClusterSettingsList[i].relBranchLength = value
            
        for i, value in enumerate(data.get("relBranchLengthVariationList", [])):
            props.branchClusterSettingsList[i].relBranchLengthVariation = value
            
        for i, value in enumerate(data.get("taperFactorList", [])):
            props.branchClusterSettingsList[i].taperFactor = value
        
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
            
        # "useFibonacciAnglesList": [props.useFibonacciAnglesList[i].value for i in range(props.branchClusters)],
        # "fibonacciNr": [props.fibonacciNrList[i].fibonacci_nr for i in range(props.branchClusters)],
        # "rotateAngleRangeList": [props.fibonacciNrList[i].rotate_angle_range for i in range(props.branchClusters)],
        # "rotateAngleOffsetList": [props.fibonacciNrList[i].rotate_angle_offset for i in range(props.branchClusters)],
        
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
        
        for i, value in enumerate(data.get("branchSplitHeightVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitHeightVariation = value
        
        for i, value in enumerate(data.get("branchSplitLengthVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitLengthVariation = value
        
        #for i, value in enumerate(data.get("hangingBranchesList", [])):
        #    props.branchClusterSettingsList[i].hangingBranchesList.add()
        #    item.value = value
            
        props.branchSplitHeightInLevelListIndex = data.get("branchSplitHeightInLevelListIndex", props.branchSplitHeightInLevelListIndex)
            
        for value in data.get("branchSplitHeightInLevelList_0", []):
            item = props.branchSplitHeightInLevelList_0.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_0 = data.get("branchSplitHeightInLevelListIndex_0", props.branchSplitHeightInLevelListIndex_0)
        
        for value in data.get("branchSplitHeightInLevelList_1", []):
            item = props.branchSplitHeightInLevelList_1.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_1 = data.get("branchSplitHeightInLevelListIndex_1", props.branchSplitHeightInLevelListIndex_1)
        
        for value in data.get("branchSplitHeightInLevelList_2", []):
            item = props.branchSplitHeightInLevelList_2.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_2 = data.get("branchSplitHeightInLevelListIndex_2", props.branchSplitHeightInLevelListIndex_2)
        
        for value in data.get("branchSplitHeightInLevelList_3", []):
            item = props.branchSplitHeightInLevelList_3.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_3 = data.get("branchSplitHeightInLevelListIndex_3", props.branchSplitHeightInLevelListIndex_3)
        
        for value in data.get("branchSplitHeightInLevelList_4", []):
            item = props.branchSplitHeightInLevelList_4.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_4 = data.get("branchSplitHeightInLevelListIndex_4", props.branchSplitHeightInLevelListIndex_4)
        
        for value in data.get("branchSplitHeightInLevelList_5", []):
            item = props.branchSplitHeightInLevelList_5.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_5 = data.get("branchSplitHeightInLevelListIndex_5", props.branchSplitHeightInLevelListIndex_5)
        
        props.leafClusterSettingsList.clear()
        
        for value in data.get("leavesDensityList", []):
            item = props.leafClusterSettingsList.add()
            item.leavesDensity = value
        
        i = 0
        for value in data.get("leafSizeList", []):
            props.leafClusterSettingsList[i].leafSize = value
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
            
    
def save_properties(filePath, treeGen):
    props = bpy.context.scene
    
    controlPts = []
    handleTypes = []
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
    for n in range(0, len(curveElement.points)):
        controlPts.append(list(curveElement.points[n].location))
        handleTypes.append(curveElement.points[n].handle_type)
    
    nestedBranchList = []
    for cluster in props.parentClusterBoolListList:
        innerList = []
        for boolProp in cluster.value:
            innerList.append(boolProp.value)
        nestedBranchList.append(innerList)
        
    nestedLeafList = []
    for cluster in props.leafParentClusterBoolListList:
        innerLeafList = []
        for boolProp in cluster.value:
            innerLeafList.append(boolProp.value)
        nestedLeafList.append(innerLeafList)
    
    treeGen.report({'INFO'}, f"max split height used: {bpy.context.scene.maxSplitHeightUsed}")
    storeSplitHeights_0 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 0:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_0):
            storeSplitHeights_0 = [props.branchSplitHeightInLevelList_0[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 0:
                storeSplitHeights_0 = props.branchSplitHeightInLevelList_0
        
    storeSplitHeights_1 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 1:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_1):
            storeSplitHeights_1 = [props.branchSplitHeightInLevelList_1[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
            treeGen.report({'INFO'}, "store splitHeights_1 max")
        else:
            if len(props.branchClusterSettingsList) > 1:
                storeSplitHeights_1 = props.branchSplitHeightInLevelList_1
                treeGen.report({'INFO'}, "store splitHeights_1")
            
    storeSplitHeights_2 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 2:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_2):
            storeSplitHeights_2 = [props.branchSplitHeightInLevelList_2[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 2:
                storeSplitHeights_2 = props.branchSplitHeightInLevelList_2
        
    storeSplitHeights_3 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 3:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_3):
            storeSplitHeights_3 = [props.branchSplitHeightInLevelList_3[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 3:
                storeSplitHeights_3 = props.branchSplitHeightInLevelList_3
        
    storeSplitHeights_4 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 4:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_4):
            storeSplitHeights_4 = [props.branchSplitHeightInLevelList_4[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 4:
                storeSplitHeights_4 = props.branchSplitHeightInLevelList_4
        
    storeSplitHeights_5 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 5:
        if bpy.context.scene.maxSplitHeightUsed <= len(props.branchSplitHeightInLevelList_5):
            storeSplitHeights_5 = [props.branchSplitHeightInLevelList_5[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 5:
                storeSplitHeights_5 = props.branchSplitHeightInLevelList_5
    
    
    
    data = {
        "treeHeight": props.treeHeight,
        "treeGrowDir": list(props.treeGrowDir),
        "taper": props.taper,
        
        "taperCurvePoints": [list(pt.location) for pt in bpy.data.node_groups.get('taperNodeGroup').nodes[taper_node_mapping['taperMapping']].mapping.curves[3].points],
        "taperCurveHandleTypes": [pt.handle_type for pt in bpy.data.node_groups.get('taperNodeGroup').nodes[taper_node_mapping['taperMapping']].mapping.curves[3].points],
    
        "branchTipRadius": props.branchTipRadius,
        "ringSpacing": props.ringSpacing,
        "stemRingResolution": props.stemRingResolution,
        "resampleDistance": props.resampleDistance,
    
        "noiseAmplitudeVertical": props.noiseAmplitudeVertical,
        "noiseAmplitudeHorizontal": props.noiseAmplitudeHorizontal,
        "noiseAmplitudeGradient": props.noiseAmplitudeGradient,
        "noiseAmplitudeExponent": props.noiseAmplitudeExponent,
        "noiseScale": props.noiseScale,
        "seed": props.seed,
        
        "curvatureStart": props.curvatureStart,
        "curvatureEnd": props.curvatureEnd,
        "maxCurveSteps": props.maxCurveSteps,
        
        "nrSplits": props.nrSplits,
        "variance": props.variance,
        "stemSplitMode": props.stemSplitMode,
        "stemSplitRotateAngle": props.stemSplitRotateAngle,
        "curvOffsetStrength": props.curvOffsetStrength,
        
        "stemSplitHeightInLevelList": [item.value for item in props.stemSplitHeightInLevelList],
        "stemSplitHeightInLevelListIndex": props.stemSplitHeightInLevelListIndex,
            
        "splitHeightVariation": props.splitHeightVariation,
        "splitLengthVariation": props.splitLengthVariation,
        "stemSplitAngle": props.stemSplitAngle,
        "stemSplitPointAngle": props.stemSplitPointAngle,
    
        "branchClusters": props.branchClusters,
        "showBranchClusterList": [props.branchClusterBoolListList[i].show_branch_cluster for i in range(props.branchClusters)],
        "showParentClusterList": [props.parentClusterBoolListList[i].show_cluster for i in range(props.branchClusters)],
    
        "parentClusterBoolListList": nestedBranchList,
        
        "nrBranchesList": [props.branchClusterSettingsList[i].nrBranches for i in range(props.branchClusters)],
        "branchShapeList": [props.branchClusterSettingsList[i].branchShape.value for i in range(props.branchClusters)],
        "relBranchLengthList": [props.branchClusterSettingsList[i].relBranchLength for i in range(props.branchClusters)],
        "relBranchLengthVariationList": [props.branchClusterSettingsList[i].relBranchLengthVariation for i in range(props.branchClusters)],
        "taperFactorList": [props.branchClusterSettingsList[i].taperFactor for i in range(props.branchClusters)],
        "ringResolutionList": [props.branchClusterSettingsList[i].ringResolution for i in range(props.branchClusters)],
        "branchesStartHeightGlobalList": [props.branchClusterSettingsList[i].branchesStartHeightGlobal for i in range(props.branchClusters)],
        "branchesEndHeightGlobalList": [props.branchClusterSettingsList[i].branchesEndHeightGlobal for i in range(props.branchClusters)],
        "branchesStartHeightClusterList": [props.branchClusterSettingsList[i].branchesStartHeightCluster for i in range(props.branchClusters)],
        "branchesEndHeightClusterList": [props.branchClusterSettingsList[i].branchesEndHeightCluster for i in range(props.branchClusters)],
        
        "showNoiseSettingsList": [props.branchClusterSettingsList[i].showNoiseSettings for i in range(props.branchClusters)],
        
        "noiseAmplitudeHorizontalList": [props.branchClusterSettingsList[i].noiseAmplitudeHorizontalBranch for i in range(props.branchClusters)],
        "noiseAmplitudeVerticalList": [props.branchClusterSettingsList[i].noiseAmplitudeVerticalBranch for i in range(props.branchClusters)],
        "noiseAmplitudeGradientList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchGradient for i in range(props.branchClusters)],
        "noiseAmplitudeExponentList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchExponent for i in range(props.branchClusters)],
        "noiseScaleList": [props.branchClusterSettingsList[i].noiseScale for i in range(props.branchClusters)],
        
        "showAngleSettingsList": [props.branchClusterSettingsList[i].showAngleSettings for i in range(props.branchClusters)],
        
        "verticalAngleCrownStartList": [props.branchClusterSettingsList[i].verticalAngleCrownStart for i in range(props.branchClusters)],
        "verticalAngleCrownEndList": [props.branchClusterSettingsList[i].verticalAngleCrownEnd for i in range(props.branchClusters)],
        "verticalAngleBranchStartList": [props.branchClusterSettingsList[i].verticalAngleBranchStart for i in range(props.branchClusters)],
        "verticalAngleBranchEndList": [props.branchClusterSettingsList[i].verticalAngleBranchEnd for i in range(props.branchClusters)],
        "branchAngleModeList": [props.branchClusterSettingsList[i].branchAngleMode.value for i in range(props.branchClusters)],
        "useFibonacciAnglesList": [props.branchClusterSettingsList[i].useFibonacciAngles for i in range(props.branchClusters)],
        "fibonacciNr": [props.branchClusterSettingsList[i].fibonacciNr.fibonacci_nr for i in range(props.branchClusters)],
        "rotateAngleRangeList": [props.branchClusterSettingsList[i].rotateAngleRange for i in range(props.branchClusters)],
        "rotateAngleOffsetList": [props.branchClusterSettingsList[i].rotateAngleOffset for i in range(props.branchClusters)],
        
        "rotateAngleCrownStartList": [props.branchClusterSettingsList[i].rotateAngleCrownStart for i in range(props.branchClusters)],
        "rotateAngleCrownEndList": [props.branchClusterSettingsList[i].rotateAngleCrownEnd for i in range(props.branchClusters)],
        "rotateAngleBranchStartList": [props.branchClusterSettingsList[i].rotateAngleBranchStart for i in range(props.branchClusters)],
        "rotateAngleBranchEndList": [props.branchClusterSettingsList[i].rotateAngleBranchEnd for i in range(props.branchClusters)],
        
        "branchGlobalCurvatureStartList": [props.branchClusterSettingsList[i].branchGlobalCurvatureStart for i in range(props.branchClusters)],
        "branchGlobalCurvatureEndList": [props.branchClusterSettingsList[i].branchGlobalCurvatureEnd for i in range(props.branchClusters)],
        "branchCurvatureStartList": [props.branchClusterSettingsList[i].branchCurvatureStart for i in range(props.branchClusters)],
        "branchCurvatureEndList": [props.branchClusterSettingsList[i].branchCurvatureEnd for i in range(props.branchClusters)],
        "branchCurvatureOffsetStrengthList": [props.branchClusterSettingsList[i].branchCurvatureOffsetStrength for i in     range(props.branchClusters)],
        
        "showSplitSettingsList": [props.branchClusterSettingsList[i].showSplitSettings for i in range(props.branchClusters)],
        
        "nrSplitsPerBranchList": [props.branchClusterSettingsList[i].nrSplitsPerBranch for i in range(props.branchClusters)],
        "branchSplitModeList": [props.branchClusterSettingsList[i].branchSplitMode.value for i in range(props.branchClusters)],
        "branchSplitRotateAngleList": [props.branchClusterSettingsList[i].branchSplitRotateAngle for i in range(props.branchClusters)],
        "branchSplitAxisVariationList": [props.branchClusterSettingsList[i].branchSplitAxisVariation for i in range(props.branchClusters)],
        
        "branchSplitAngleList": [props.branchClusterSettingsList[i].branchSplitAngle for i in range(props.branchClusters)],
        "branchSplitPointAngleList": [props.branchClusterSettingsList[i].branchSplitPointAngle for i in range(props.branchClusters)],
        
        "splitsPerBranchVariationList": [props.branchClusterSettingsList[i].splitsPerBranchVariation for i in range(props.branchClusters)],
        "branchVarianceList": [props.branchClusterSettingsList[i].branchVariance for i in range(props.branchClusters)],
        "branchSplitHeightVariationList": [props.branchClusterSettingsList[i].branchSplitHeightVariation for i in range(props.branchClusters)],
        "branchSplitLengthVariationList": [props.branchClusterSettingsList[i].branchSplitLengthVariation for i in range(props.branchClusters)],
        #"hangingBranchesList": [props.hangingBranchesList[i].value for i in range(props.branchClusters)],
        
        "showBranchSplitHeights": [props.branchClusterSettingsList[i].showBranchSplitHeights for i in range(props.branchClusters)],
        
        "branchSplitHeightInLevelListIndex": props.branchSplitHeightInLevelListIndex,
        #------
        "branchSplitHeightInLevelList_0": storeSplitHeights_0,
        "branchSplitHeightInLevelListIndex_0": props.branchSplitHeightInLevelListIndex_0,
        
        "branchSplitHeightInLevelList_1": storeSplitHeights_1,
        "branchSplitHeightInLevelListIndex_1": props.branchSplitHeightInLevelListIndex_1,
        
        "branchSplitHeightInLevelList_2": storeSplitHeights_2,
        "branchSplitHeightInLevelListIndex_2": props.branchSplitHeightInLevelListIndex_2,
        
        "branchSplitHeightInLevelList_3": storeSplitHeights_3,
        "branchSplitHeightInLevelListIndex_3": props.branchSplitHeightInLevelListIndex_3,
        
        "branchSplitHeightInLevelList_4": storeSplitHeights_4,
        "branchSplitHeightInLevelListIndex_4": props.branchSplitHeightInLevelListIndex_4,
        
        "branchSplitHeightInLevelList_5": storeSplitHeights_5,
        "branchSplitHeightInLevelListIndex_5": props.branchSplitHeightInLevelListIndex_5,
        
        "showLeafSettings": [props.leafClusterSettingsList[i].showLeafSettings for i in range(props.leafClusters)],
        #------------
        "leavesDensityList": [props.leafClusterSettingsList[i].leavesDensity for i in range(props.leafClusters)],
        "leafSizeList": [props.leafClusterSettingsList[i].leafSize for i in range(props.leafClusters)],
        "leafAspectRatioList": [props.leafClusterSettingsList[i].leafAspectRatio for i in range(props.leafClusters)],
        "leafStartHeightGlobalList": [props.leafClusterSettingsList[i].leafStartHeightGlobal for i in range(props.leafClusters)],
        "leafEndHeightGlobalList": [props.leafClusterSettingsList[i].leafEndHeightGlobal for i in range(props.leafClusters)],
        "leafStartHeightClusterList": [props.leafClusterSettingsList[i].leafStartHeightCluster for i in range(props.leafClusters)],
        "leafEndHeightClusterList": [props.leafClusterSettingsList[i].leafEndHeightCluster for i in range(props.leafClusters)],
        "leafTypeList": [props.leafClusterSettingsList[i].leafType.value for i in range(props.leafClusters)],
        "leafAngleModeList": [props.leafClusterSettingsList[i].leafAngleMode.value for i in range(props.leafClusters)],
        
        "leafVerticalAngleBranchStartList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchStart for i in range(props.leafClusters)],
        "leafVerticalAngleBranchEndList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchEnd for i in range(props.leafClusters)],
        "leafRotateAngleBranchStartList": [props.leafClusterSettingsList[i].leafRotateAngleBranchStart for i in range(props.leafClusters)],
        "leafRotateAngleBranchEndList": [props.leafClusterSettingsList[i].leafRotateAngleBranchEnd for i in range(props.leafClusters)],
        "leafTiltAngleBranchStartList": [props.leafClusterSettingsList[i].leafTiltAngleBranchStart for i in range(props.leafClusters)],
        "leafTiltAngleBranchEndList": [props.leafClusterSettingsList[i].leafTiltAngleBranchEnd for i in range(props.leafClusters)],
        
        "showLeafClusterList": [props.leafParentClusterBoolListList[i].show_leaf_cluster for  i in range(len(props.leafParentClusterBoolListList))],
        "leafParentClusterBoolListList": nestedLeafList
    }

    with open(filePath, 'w') as f:
        json.dump(data, f)
    
def draw_leaf_cluster_bools(layout, scene, cluster_index, leafParentClusterBool):
    boolListItem = scene.leafParentClusterBoolListList[cluster_index].value
    
    row = layout.row()
    row.prop(leafParentClusterBool, "show_leaf_cluster", icon="TRIA_DOWN" if leafParentClusterBool.show_leaf_cluster else "TRIA_RIGHT", emboss=False, text="Parent clusters", toggle=True)
    
    if leafParentClusterBool.show_leaf_cluster == True:
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
            
            
def draw_parent_cluster_bools(layout, scene, cluster_index):
    boolListItem = scene.parentClusterBoolListList[cluster_index].value
    
    boolCount = 0
    for j, boolItem in enumerate(boolListItem):
        split = layout.split(factor=0.6)
        #row = box.row()
        if boolCount == 0:
            split.label(text=f"Stem")
            boolCount += 1
        else:
            split.label(text=f"Branch cluster {boolCount - 1}")
            boolCount += 1
            
        rightColumn = split.column(align=True)
        row = rightColumn.row(align=True)
        row.alignment = 'CENTER'              # align to center
        
        op = row.operator("scene.toggle_bool", text="", depress=boolItem.value)
        op.list_index = cluster_index
        op.bool_index = j
        
class toggleBool(bpy.types.Operator):
    bl_idname = "scene.toggle_bool"
    bl_label = "Toggle Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.parentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)
    
class toggleLeafBool(bpy.types.Operator):
    bl_idname = "scene.toggle_leaf_bool"
    bl_label = "Toggle Leaf Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.leafParentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

class addItem(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.branchClusters += 1
        branchSettings = context.scene.branchClusterSettingsList.add()
        
        parentClusterBoolListList = context.scene.parentClusterBoolListList.add()
        for b in range(0, context.scene.branchClusters):
            parentClusterBoolListList.value.add()
        parentClusterBoolListList.value[0].value = True
        
        branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
        
        context.scene.branchSplitHeightInLevelListList.add()
        context.scene.showBranchSplitHeights.add()
        
        for leafParentClusterList in context.scene.leafParentClusterBoolListList:
            leafParentClusterList.value.add()
        
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        if len(context.scene.branchClusterSettingsList) > 0:
            context.scene.branchClusters -= 1
            context.scene.branchClusterSettingsList.remove(len(context.scene.branchClusterSettingsList) - 1)
            
        if len(context.scene.parentClusterBoolListList) > 0:
            listToClear = context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value
            lenToClear = len(listToClear)
            for i in range(0, lenToClear):
                context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value.remove(len(context.scene.parentClusterBoolListList[i].value) - 1)
            context.scene.parentClusterBoolListList.remove(len(context.scene.parentClusterBoolListList) - 1)
            
        if len(context.scene.branchSplitHeightInLevelListList) > 0:
            context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
            
        if len(context.scene.showBranchSplitHeights) > 0:
            context.scene.showBranchSplitHeights.remove(len(context.scene.showBranchSplitHeights) - 1)
            
        for leafParentClusterList in context.scene.leafParentClusterBoolListList:
            if len(leafParentClusterList.value) > 1:
                leafParentClusterList.value.remove(len(leafParentClusterList.value) - 1)
                
                allFalse = True
                for b in leafParentClusterList.value:
                    if b.value == True:
                        allFalse = False
                if allFalse == True:
                    leafParentClusterList.value[0].value = True
            
        return {'FINISHED'}
        
class branchSettings(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_BranchSettings"
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
        row.operator("scene.add_list_item", text="Add")
        row.operator("scene.remove_list_item", text="Remove")#.index = context.scene.nrBranchesListIndex
        #row = layout.row()
        #row.label(text = f"branchClusters: {scene.branchClusters}")
        #row = layout.row()
        #row.label(text = f"len(parentClusterBoolListList): {len(scene.parentClusterBoolListList)}")
        
        row = layout.row()
        for i, outer in enumerate(scene.parentClusterBoolListList):
            if i < len(scene.branchClusterBoolListList):
                box = layout.box()
                box.prop(scene.branchClusterBoolListList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterBoolListList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
                if scene.branchClusterBoolListList[i].show_branch_cluster:
                    box1 = box.box()
                    row = box1.row()
                    
                    row.prop(outer, "show_cluster", icon="TRIA_DOWN" if outer.show_cluster else "TRIA_RIGHT", emboss=False, text=f"Parent clusters", toggle=True)
                    
                    if outer.show_cluster:
                        if i < len(scene.branchClusterSettingsList):
                            draw_parent_cluster_bools(box1, scene, i)
                            
                    split = box.split(factor=0.6)
                    split.label(text="Number of branches")
                    split.prop(scene.branchClusterSettingsList[i], "nrBranches", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branch shape")
                    split.prop(scene.branchClusterSettingsList[i].branchShape, "value", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLength", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length variation")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLengthVariation", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Taper factor")
                    split.prop(scene.branchClusterSettingsList[i], "taperFactor", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Ring resolution")
                    split.prop(scene.branchClusterSettingsList[i], "ringResolution", text="")
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches start height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightGlobal", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches end height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightGlobal", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches start height cluster")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightCluster", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branches end height cluster")
                    split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightCluster", text="", slider=True)
                
                
                split = box.split(factor=0.6)
                split.prop(scene.branchClusterSettingsList[i], "showNoiseSettings", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showNoiseSettings else "TRIA_RIGHT", emboss=False, text="Noise settings", toggle=True)
                if scene.branchClusterSettingsList[i].showNoiseSettings:
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
                split.prop(scene.branchClusterSettingsList[i], "showAngleSettings", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showAngleSettings else "TRIA_RIGHT", emboss=False, text="Angle settings", toggle=True)
                if scene.branchClusterSettingsList[i].showAngleSettings:
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
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Branch angle mode")
                    split.prop(scene.branchClusterSettingsList[i].branchAngleMode, "value", text="")
                    
                    box2 = box1.box()
                    split = box2.split(factor=0.6)
                    
                    if scene.branchClusterSettingsList[i].branchAngleMode.value == 'WINDING':
                        split.label(text="Use Fibonacci angles")
                        split.prop(scene.branchClusterSettingsList[i], "useFibonacciAngles", text="")
                        if scene.branchClusterSettingsList[i].useFibonacciAngles == True:
                            split = box2.split(factor=0.6)
                            split.label(text="Fibonacci number")
                            split.prop(scene.branchClusterSettingsList[i].fibonacciNr, "fibonacci_nr", text="")
                            
                            split1 = box2.split(factor=0.6)
                            split1.label(text="Angle:")
                            split1.label(text=f"{scene.branchClusterSettingsList[i].fibonacciNr.fibonacci_angle:.2f}°")
                    
                    if scene.branchClusterSettingsList[i].useFibonacciAngles == False or scene.branchClusterSettingsList[i].branchAngleMode.value == 'SYMMETRIC':
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
        
                    box3 = box1.box()
                    #if scene.hangingBranchesList[i].value == True:
                    #    split = box3.split(factor=0.6)
                    #    split.label(text="Branch global curvature start")
                    #    split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureStart", text="")
                    #    
                    #    split = box3.split(factor=0.6)
                    #    split.label(text="Branch global curvature end")
                    #    split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureEnd", text="")
                    #else:
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
                split.prop(scene.branchClusterSettingsList[i], "showSplitSettings", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showSplitSettings else "TRIA_RIGHT", emboss=False, text="Split settings", toggle=True)
                
                if scene.branchClusterSettingsList[i].showSplitSettings:
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
                            row.template_list("UL_branchSplitLevelListLevel_0", "", scene, "branchSplitHeightInLevelList_0", scene, "branchSplitHeightInLevelListIndex_0")
                        if i == 1:
                            row.template_list("UL_branchSplitLevelListLevel_1", "", scene, "branchSplitHeightInLevelList_1", scene, "branchSplitHeightInLevelListIndex_1")
                        if i == 2:
                            row.template_list("UL_branchSplitLevelListLevel_2", "", scene, "branchSplitHeightInLevelList_2", scene, "branchSplitHeightInLevelListIndex_2")
                        if i == 3:
                            row.template_list("UL_branchSplitLevelListLevel_3", "", scene, "branchSplitHeightInLevelList_3", scene, "branchSplitHeightInLevelListIndex_3")
                        if i == 4:
                            row.template_list("UL_branchSplitLevelListLevel_4", "", scene, "branchSplitHeightInLevelList_4", scene, "branchSplitHeightInLevelListIndex_4")
                        if i == 5:
                            row.template_list("UL_branchSplitLevelListLevel_5", "", scene, "branchSplitHeightInLevelList_5", scene, "branchSplitHeightInLevelListIndex_5")
                        if i > 5:
                            j = 0
                            for splitLevel in context.scene.branchClusterSettingsList[i].branchSplitHeightInLevelList:
                                box2.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
                                j += 1


class addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.leafClusters += 1
        context.scene.leafClusterSettingsList.add()
        
        leafParentClusterBoolListList = context.scene.leafParentClusterBoolListList.add()
        stemBool = context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value.add()
        stemBool = True
                
        for b in range(0, len(context.scene.branchClusterSettingsList)):
            self.report({'INFO'}, f"adding leaf cluster")
            context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value.add()
            self.report({'INFO'}, f"len(leafParentClusterBoolListList): {len(context.scene.leafParentClusterBoolListList)}")
        
        leafParentClusterBoolListList.value[0].value = True
        return {'FINISHED'}
        
class removeLeafItem(bpy.types.Operator):
    bl_idname = "scene.remove_leaf_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        if context.scene.leafClusters > 0:
            context.scene.leafClusters -= 1
        if len(context.scene.leafClusterSettingsList) > 0:
            context.scene.leafClusterSettingsList.remove(len(context.scene.leafClusterSettingsList) - 1)
        if len(context.scene.leafParentClusterBoolListList) > 0:
            context.scene.leafParentClusterBoolListList.remove(len(context.scene.leafParentClusterBoolListList) - 1)
       
        return {'FINISHED'}

class leafSettings(bpy.types.Panel):
    bl_label = "Leaf Settings"
    bl_idname = "PT_LeafSettings"
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
        row.operator("scene.remove_leaf_item", text="Remove").index = context.scene.leavesDensityListIndex
        row = layout.row()
        
        for i, leaves in enumerate(scene.leafClusterSettingsList):
            box = layout.box()
            box.prop(leaves, "showLeafSettings", icon="TRIA_DOWN" if leaves.showLeafSettings else "TRIA_RIGHT", emboss=False, text=f"Leaf cluster {i}", toggle=True)
            
            if leaves.showLeafSettings:
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
                draw_leaf_cluster_bools(box1, scene, i, scene.leafParentClusterBoolListList[i])
        
def register():
    #save and load
    bpy.utils.register_class(importProperties)
    bpy.utils.register_class(exportProperties)
    
    
    
    #bpy.utils.register_class(MyToolProperties)
    #bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyToolProperties)

    
    #data types
    bpy.utils.register_class(treeShapeEnumProp)
    bpy.utils.register_class(splitModeEnumProp)
    bpy.utils.register_class(angleModeEnumProp)
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
    
    bpy.utils.register_class(branchClusterSettings)
    bpy.utils.register_class(leafClusterSettings)
    
    #operators
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(toggleLeafBool)
    bpy.utils.register_class(addStemSplitLevel)
    bpy.utils.register_class(removeStemSplitLevel)
    bpy.utils.register_class(addBranchSplitLevel)
    bpy.utils.register_class(removeBranchSplitLevel)
    #bpy.utils.register_class(generateTree)
    bpy.utils.register_class(resetCurvesButton)
    #bpy.utils.register_class(sampleCruvesButton)
    bpy.utils.register_class(addLeafItem)
    bpy.utils.register_class(removeLeafItem)
    
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(treeSettings)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(angleSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(branchSettings)
    bpy.utils.register_class(leafSettings)
    
    #bpy.utils.register_class(parentClusterPanel)
    
    #UILists
    bpy.utils.register_class(UL_stemSplitLevelList)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_5)
          
    #collections
    
    bpy.types.Scene.branchClusterSettingsList = bpy.props.CollectionProperty(type=branchClusterSettings)
    
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.showStemSplitHeights = bpy.props.BoolProperty(
        name = "Show/hide stem split heights",
        default = True
    )
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.file_name = bpy.props.StringProperty(name="File Name", default="my_tree_properties")
    
    #bpy.types.Scene.showLeafSettings = bpy.props.CollectionProperty(type=boolProp) -> move to leafSettings...
    
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.parentClusterBoolListList = bpy.props.CollectionProperty(type=parentClusterBoolListProp)
    bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    #bpy.types.Scene.nrBranchesList = bpy.props.CollectionProperty(type=intProp)
    bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    #bpy.types.Scene.branchSplitModeList = bpy.props.CollectionProperty(type=splitModeEnumProp)
    #bpy.types.Scene.branchVarianceList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitRotateAngleList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchSplitAxisVariationList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.rotateAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchSplitAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.branchSplitPointAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.branchShapeList = bpy.props.CollectionProperty(type=treeShapeEnumProp)
    #bpy.types.Scene.relBranchLengthList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    #bpy.types.Scene.relBranchLengthVariationList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1Default0)
    #bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    #bpy.types.Scene.ringResolutionList = bpy.props.CollectionProperty(type=posIntProp3)
    #bpy.types.Scene.noiseAmplitudeBranchGradientList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.noiseAmplitudeVerticalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.noiseAmplitudeHorizontalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.noiseAmplitudeBranchExponentList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    #bpy.types.Scene.noiseScaleList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    #bpy.types.Scene.verticalAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchAngleModeList = bpy.props.CollectionProperty(type=angleModeEnumProp)
    #bpy.types.Scene.useFibonacciAnglesList = bpy.props.CollectionProperty(type=boolProp)
    #bpy.types.Scene.fibonacciNrList = bpy.props.CollectionProperty(type=fibonacciProps)
    #bpy.types.Scene.rotateAngleRangeList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchesStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.hangingBranchesList = bpy.props.CollectionProperty(type=boolProp)
    #bpy.types.Scene.branchGlobalCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchGlobalCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureOffsetStrengthList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.nrSplitsPerBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitLengthVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_0 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_0 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_1 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_1 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_2 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_2 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_3 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_3 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_4 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_4 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_5 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_5 = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.leafClusterSettingsList = bpy.props.CollectionProperty(type=leafClusterSettings)
    
    #bpy.types.Scene.leavesDensityList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.leavesDensityListIndex = bpy.props.IntProperty(default=0)
    #bpy.types.Scene.leafSizeList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    #bpy.types.Scene.leafAspectRatioList = bpy.props.CollectionProperty(type=posFloatPropSoftMax2)
    #bpy.types.Scene.leafAngleModeList = bpy.props.CollectionProperty(type=leafAngleModeEnumProp)
    #bpy.types.Scene.leafTypeList = bpy.props.CollectionProperty(type=leafTypeEnumProp)
    #bpy.types.Scene.leafStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.leafEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.leafStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.leafEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.leafVerticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.leafVerticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.leafRotateAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.leafRotateAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.leafTiltAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.leafTiltAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    
    bpy.types.Scene.bark_material = bpy.props.PointerProperty(type=bpy.types.Material)
    bpy.types.Scene.leaf_material = bpy.props.PointerProperty(type=bpy.types.Material)
    
    bpy.types.Scene.maxSplitHeightUsed = bpy.props.IntProperty(default = 0)
    
    #leafParentClusterBoolListProp
    bpy.types.Scene.leafParentClusterBoolListList = bpy.props.CollectionProperty(type=leafParentClusterBoolListProp)
    
    # bpy.props.CollectionProperty(type=intProp)
        
    bpy.types.Scene.treeHeight = bpy.props.FloatProperty(
        name = "tree height",
        description = "the heihgt of the tree",
        default = 10,
        min = 0,
        soft_max = 50
    )
    
    bpy.types.Scene.taper = bpy.props.FloatProperty(
        name = "taper",
        description = "taper of the stem",
        default = 0.1,
        min = 0,
        soft_max = 0.5
    )
    
    bpy.types.Scene.branchTipRadius = bpy.props.FloatProperty(
        name = "branch tip radius",
        description = "branch radius at the tip",
        default = 0, 
        min = 0,
        soft_max = 0.1
    )
    
    bpy.types.Scene.ringSpacing = bpy.props.FloatProperty(
        name = "Ring Spacing",
        description = "Spacing between rings",
        default = 0.1,
        min = 0.001
    )
    bpy.types.Scene.noiseAmplitudeHorizontal = bpy.props.FloatProperty(
        name = "Noise Amplitude Horizontal",
        description = "Noise amplitude horizontal",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeVertical = bpy.props.FloatProperty(
        name = "Noise Amplitude Vertical",
        description = "Noise amplitude vertical",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeGradient = bpy.props.FloatProperty(
        name = "Noise Amplitude Gradient",
        description = "Gradient of noise Amplitude at the base of the tree",
        default = 0.1,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeExponent = bpy.props.FloatProperty(
        name = "Noise Amplitude Exponent",
        description = "Exponent for noise amplitude",
        default = 1.0,
        min = 0.0
    )
    bpy.types.Scene.noiseScale = bpy.props.FloatProperty(
        name = "Noise Scale",
        description = "Scale of the noise",
        default = 1.0,
        min = 0.0
    )
    bpy.types.Scene.seed = bpy.props.IntProperty(
        name = "Seed",
        description = "Noise generator seed"
    )
    bpy.types.Scene.curvatureStart = bpy.props.FloatProperty(
        name = "Curvature Start",
        description = "Curvature at start of branches",
        default = 0.0
    )
    bpy.types.Scene.curvatureEnd = bpy.props.FloatProperty(
        name = "Curvature End",
        description = "Curvature at end of branches",
        default = 0.0
    )
    bpy.types.Scene.maxCurveSteps = bpy.props.IntProperty(
        name = "Max Curve Steps",
        description = "debug max curve steps",
        default = 10,
        min = 0
    )
    #bpy.types.Scene.shyBranchesMaxDistance = bpy.props.FloatProperty(
    #    name = "Shy Branches Max Distance",
    #    description = "Maximum distance for shy branches",
    #    default = 0.1,
    #    min = 0.0
    #)
    bpy.types.Scene.stemSplitRotateAngle = bpy.props.FloatProperty(
        name = "Stem Split Rotate Angle",
        description = "Rotation angle for stem splits",
        default = 0.0,
        min = 0.0,
        max = 360.0
    )
    bpy.types.Scene.variance = bpy.props.FloatProperty(
        name = "Variance",
        description = "Variance",
        default = 0.0,
        min = 0.0,
        max = 1.0
    )
    bpy.types.Scene.curvOffsetStrength = bpy.props.FloatProperty(
        name = "Curvature Offset Strength",
        description = "Strength of the curvature offset",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.stemSplitAngle = bpy.props.FloatProperty(
        name = "Stem Split Angle",
        description = "Angle of stem splits",
        default = 0.0,
        min = 0.0,
        max = 360.0
    )
    
    
    bpy.types.Scene.stemSplitPointAngle = bpy.props.FloatProperty(
        name = "Stem Split Point Angle",
        description = "Point angle of stem splits",
        default = 0.0,
        min = 0.0,
        max = 360.0
    )
    bpy.types.Scene.splitHeightVariation = bpy.props.FloatProperty(
        name = "Split Height Variation",
        description = "Variation in split height",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.splitLengthVariation = bpy.props.FloatProperty(
        name = "Split Length Variation",
        description = "Variation in split length",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.treeShape = bpy.props.EnumProperty(
        name="Shape",
        description="The shape of the tree.",
        items=[
            ('CONICAL', "Conical", "A cone-shaped tree."),
            ('SPHERICAL', "Spherical", "A sphere-shaped tree."),
            ('HEMISPHERICAL', "Hemispherical", "A half-sphere shaped tree."),
            ('CYLINDRICAL', "Cylindrical", "A cylinder-shaped tree."),
            ('TAPERED_CYLINDRICAL', "Tapered Cylindrical", "A cylinder that tapers towards the top."),
            ('FLAME', "Flame", "A flame-shaped tree."),
            ('INVERSE_CONICAL', "Inverse Conical", "An upside-down cone-shaped tree."),
            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
        ],
        default='CONICAL'
    )
    
    # Integer Properties
    bpy.types.Scene.stemRingResolution = bpy.props.IntProperty(
        name = "Stem Ring Resolution",
        description = "Resolution of the stem rings",
        default = 16,
        min = 3
    )
    bpy.types.Scene.resampleDistance = bpy.props.FloatProperty(
        name = "Resample Distance", 
        description = "Distance between nodes",
        default = 10.0,
        min = 0.0
    )
    bpy.types.Scene.shyBranchesIterations = bpy.props.IntProperty(
        name = "Shy Branches Iterations",
        description = "Iterations for shy branches",
        default = 0,
        min = 0
    )
    bpy.types.Scene.nrSplits = bpy.props.IntProperty(
        name = "Number of Splits",
        description = "Number of splits",
        default = 0,
        min = 0
    )
    bpy.types.Scene.stemSplitMode = bpy.props.EnumProperty(
        name = "Stem Split Mode",
        description = "Mode for stem splits",
        items=[
            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
            ('HORIZONTAL', "Horizontal", "Split horizontally"),
        ],
        default='ROTATE_ANGLE',
    )
    bpy.types.Scene.branchClusters = bpy.props.IntProperty(
        name = "Branch Clusters",
        description = "Number of branch clusters",
        default = 0,
        min = 0
    )

    # Vector3 Property
    bpy.types.Scene.treeGrowDir = bpy.props.FloatVectorProperty(
        name = "Tree Grow Direction",
        description = "Direction the tree grows in",
        default = (0.0, 1.0, 0.0),
        subtype = 'XYZ'  # Important for direction vectors
    )

    # *** List Properties - More Complex ***
    # These need more handling.  You can't just directly add them like the floats.
    # You'll likely want to use a custom UI for editing these.  Here's the basic idea:

    # ringResolution
    bpy.types.Scene.ringResolution = bpy.props.IntVectorProperty(
        name="Ring Resolution",
        description="Resolution per ring",
        size = 1, # Start with a single element
        default = [16],
        min = 3
    )

    ## nrBranches
    #bpy.types.Scene.nrBranches = bpy.props.IntVectorProperty(
    #    name="Number of Branches",
    #    description="Number of branches per level",
    #    size = 1, # Start with a single element
    #    default = [3],
    #    min = 0
    #)
#
    ## branchShape
    #bpy.types.Scene.branchShape = bpy.props.IntVectorProperty(
    #    name="Branch Shape",
    #    description="Shape of the branches",
    #    size = 1, # Start with a single element
    #    default = [0],
    #    min = 0
    #)
    
    ## branchSplitAngle
    #bpy.types.Scene.branchSplitAngle = bpy.props.FloatVectorProperty(
    #    name="Branch Split Angle",
    #    description="Angle for branch splits",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    ##    max = 360.0
    #)
    # branchSplitPointAngle
    #bpy.types.Scene.branchSplitPointAngle = bpy.props.FloatVectorProperty(
    #    name="Branch Split Point Angle",
    #    description="Point angle for branch splits",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## branchSplitRotateAngle
    #bpy.types.Scene.branchSplitRotateAngle = bpy.props.FloatVectorProperty(
    #    name="Branch Split Rotate Angle",
    #    description="Rotation angle for branch splits",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## relBranchLength
    #bpy.types.Scene.relBranchLength = bpy.props.FloatVectorProperty(
    #    name="Relative Branch Length",
    #    description="Relative length of branches",
    #    size = 1, # Start with a single element
    #    default = [1.0],
    #    min = 0.0
    #)
    ## taperFactor
    #bpy.types.Scene.taperFactor = bpy.props.FloatVectorProperty(
    #    name="Taper Factor",
    #    description="Taper factor",
    #    size = 1, # Start with a single element
    #    default = [0.1],
    #    min = 0.0
    #)
    ## verticalRange # not used (for now)
    #bpy.types.Scene.verticalRange = bpy.props.FloatVectorProperty(
    #    name="Vertical Range",
    #    description="Vertical range",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0
    #)
    # verticalAngleCrownStart
    #bpy.types.Scene.verticalAngleCrownStart = bpy.props.FloatVectorProperty(
    #    name="Vertical Angle Crown Start",
    #    description="Crown start angle",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## verticalAngleCrownEnd
    #bpy.types.Scene.verticalAngleCrownEnd = bpy.props.FloatVectorProperty(
    #    name="Vertical Angle Crown End",
    #    description="Crown end angle",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## verticalAngleBranchStart
    #bpy.types.Scene.verticalAngleBranchStart = bpy.props.FloatVectorProperty(
    #    name="Vertical Angle Branch Start",
    #    description="Branch start angle",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## verticalAngleBranchEnd
    #bpy.types.Scene.verticalAngleBranchEnd = bpy.props.FloatVectorProperty(
    #    name="Vertical Angle Branch End",
    #    description="Branch end angle",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## branchAngleMode
    #bpy.types.Scene.branchAngleMode = bpy.props.IntVectorProperty(
    #    name="Branch Angle Mode",
    #    description="Branch angle mode",
    #    size = 1, # Start with a single element
    #    default = [0],
    #    min = 0
    #)
    ## rotateAngle
    #bpy.types.Scene.rotateAngle = bpy.props.FloatVectorProperty(
    #    name="Rotate Angle",
    #    description="Rotation angle",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## rotateAngleRange
    #bpy.types.Scene.rotateAngleRange = bpy.props.FloatVectorProperty(
    #    name="Rotate Angle Range",
    #    description="Rotation angle range",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0,
    #    max = 360.0
    #)
    ## branchesStartHeightGlobal
    ##bpy.types.Scene.branchesStartHeightGlobal = bpy.props.FloatVectorProperty(
    #    name="Branches Start Height Global",
    #    description="Global start height",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0
##    )
    # branchesStartHeightCluster
    #bpy.types.Scene.branchesStartHeightCluster = bpy.props.FloatVectorProperty(
    #    name="Branches Start Height Cluster",
    #    description="Cluster start height",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0
    #)
    ### branchesEndHeightGlobal
    #b#py.types.Scene.branchesEndHeightGlobal = bpy.props.FloatVectorProperty(
     #   name="Branches End Height Global",
     #   description="Global end height",
    #    size = 1, # Start with a single element
    #    default = [1.0],
    #    min = 0.0
    #)
    ## branchesEndHeightCluster
    #bpy.types.Scene.branchesEndHeightCluster = bpy.props.FloatVectorProperty(
    #    name="Branches End Height Cluster",
    #    description="Cluster end height",
    #    size = 1, # Start with a single element
    #    default = [1.0],
    #    min = 0.0
    #)
    ## branchCurvature
 #   bpy.types.Scene.branchCurvature = bpy.props.FloatVectorProperty(
#        name="Branch Curvature",
#        description="Branch curvature",
 #       size = 1, # Start with a single element
 #       default = [0.0],
 #       min = 0.0
 #   )
 #   # branchCurvatureOffsetStrength
 #   bpy.types.Scene.branchCurvatureOffsetStrength = bpy.props.FloatVectorProperty(
 #       name="Branch Curvature Offset",
 #       description="Branch curvature offset strength",
 #       size = 1,
 #       default = [0.0],
 #       min = 0.0
 #   )
 #   # nrSplitsPerBranch
 #   bpy.types.Scene.nrSplitsPerBranch = bpy.props.FloatVectorProperty(
 #       name="Splits Per Branch",
 #       description="Splits per branch",
 #       size = 1, # Start with a single element
 #       default = [1.0],
 #       min = 0.0
 #   )
 #   # splitsPerBranchVariation
 ##   bpy.types.Scene.splitsPerBranchVariation = bpy.props.FloatVectorProperty(
  #      name="Splits Per Branch Variation",
  #      description="Variation in splits per branch",
  #      size = 1, # Start with a single element
  #      default = [0.0],
  #      min = 0.0
  #  )
    
    bpy.types.Scene.leafClusters = bpy.props.IntProperty(
        name = "Leaf Clusters",
        description = "Number of leaf clusters",
        default = 0,
        min = 0
    )
    
    bpy.app.timers.register(reset_taper_curve_deferred, first_interval=0.1)
    
if __name__ == "__main__":
    register();
