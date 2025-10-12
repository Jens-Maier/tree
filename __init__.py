import bpy
import sys
import os




# Dynamically add current folder to sys.path

# for testing...
import importlib
addon_dir = "/home/j/Downloads/treeGen_v5_minimal_addon"
if addon_dir not in sys.path:
    sys.path.append(addon_dir)
if 'my_property' in sys.modules:  # For reliable reload during development
    del sys.modules['my_property']
if 'start_node_info' in sys.modules:
    del sys.modules['start_node_info']
#...


import my_property
# Import property class from another file
from my_property import MyProperties


from start_node_info import startNodeInfo


importlib.reload(my_property)
importlib.reload(start_node_info)


#from node_info import nodeInfo
#importlib.reload(node_info)
#from start_point_data import startPointData
#importlib.reload(start_point_data)
#from dummy_start_point_data import dummyStartPointData
#importlib.reload(dummy_start_point_data)
#from rotation_step import rotationStep
#importlib.reload(rotation_step)
#from node import node
#importlib.reload(node)
#from segment import segment
#importlib.reload(segment)
#from split_mode import splitMode
#importlib.reload(split_mode)
#from property_groups import floatProp, fibonacciProps, intProp, intPropL, posIntProp3, floatProp, posFloatProp, posFloatPropDefault1, posFloatPropSoftMax2, posFloatPropSoftMax1, posFloatPropSoftMax1taperFactor, posFloatPropSoftMax1Default0, floatProp01, floatProp01default0p5,  floatListProp, floatListProp01, boolProp, show_split_levels, splitHeightFloatListProp, parentClusterBoolListProp, leafParentClusterBoolListProp, branchClusterBoolListProp, leafClusterBoolListProp, treeShapeEnumProp, treePresetEnumProp, splitModeEnumProp, angleModeEnumProp,  branchTypeEnumProp, toggleBool, toggleLeafBool, leafAngleModeEnumProp, leafTypeEnumProp, toggleUseTaperCurveOperator, treeSettings, branchClusterSettings, leafClusterSettings, UL_stemSplitLevelList, UL_branchSplitLevelListLevel_0, UL_branchSplitLevelListLevel_1, UL_branchSplitLevelListLevel_2, UL_branchSplitLevelListLevel_3, UL_branchSplitLevelListLevel_4, UL_branchSplitLevelListLevel_5, UL_branchSplitLevelListLevel_6, UL_branchSplitLevelListLevel_7, UL_branchSplitLevelListLevel_8, UL_branchSplitLevelListLevel_9, UL_branchSplitLevelListLevel_10, UL_branchSplitLevelListLevel_11, UL_branchSplitLevelListLevel_12, UL_branchSplitLevelListLevel_13, UL_branchSplitLevelListLevel_14, UL_branchSplitLevelListLevel_15, UL_branchSplitLevelListLevel_16, UL_branchSplitLevelListLevel_17, UL_branchSplitLevelListLevel_18, UL_branchSplitLevelListLevel_19

# for addon
#from .my_property import MyProperties
#from .start_node_info import startNodeInfo
#from .node_info import nodeInfo
#from .start_point_data import startPointData
#from .dummy_start_point_data import dummyStartPointData
#from .rotation_step import rotationStep
#from .node import node
#from .segment import segment
#from .split_mode import splitMode





# Create a Blender PropertyGroup using the imported class value
class MinimalProps(bpy.types.PropertyGroup):
    my_int: bpy.props.IntProperty(
        name="My Int",
        default=MyProperties().default_value
    )

class MinimalPanel(bpy.types.Panel):
    bl_label = "Minimal Panel"
    bl_idname = "PT_MinimalPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Minimal'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.minimal_props, "my_int")
        layout.operator("object.my_operator", text="my Operator")
        
class MinimalOperator(bpy.types.Operator):
    bl_idname = "object.my_operator"
    bl_label = "My Operator"
    
    def execute(self, context):
        self.report({'INFO'}, "setting value in imported class to 4: ")
        MyProperties().default_value = 4
        self.report({'INFO'}, f"imported from MyProperties(): MyProperties().default_value: {MyProperties().default_value}")
        # only updated after reopening .blend file
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MinimalProps)
    bpy.types.Scene.minimal_props = bpy.props.PointerProperty(type=MinimalProps)
    bpy.utils.register_class(MinimalPanel)
    
    bpy.utils.register_class(MinimalOperator)

def unregister():
    bpy.utils.unregister_class(MinimalPanel)
    del bpy.types.Scene.minimal_props
    bpy.utils.unregister_class(MinimalProps)
    
    bpy.utils.unregister_class(MinimalOperator)

if __name__ == "__main__":
    register()