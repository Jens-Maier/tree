import bpy
import sys
import os




# Dynamically add current folder to sys.path

# for testing.......................................................................................................
import importlib
addon_dir = "/home/j/Downloads/treeGen_v5_minimal_addon"
if addon_dir not in sys.path:
    sys.path.append(addon_dir)
if 'my_property' in sys.modules:  # For reliable reload during development
    del sys.modules['my_property']
if 'start_node_info' in sys.modules:
    del sys.modules['start_node_info']
if 'node_info' in sys.modules:
    del sys.modules['node_info']
if 'start_point_data' in sys.modules:
    del sys.modules['start_point_data']
if 'rotation_step' in sys.modules:
    del sys.modules['rotation_step']
if 'node_' in sys.modules:
    del sys.modules['node_']
if 'segment_' in sys.modules:
    del sys.modules['segment_']
if 'property_groups' in sys.modules:
    del sys.modules['property_groups']
if 'operators' in sys.modules:
    del sys.modules['operators']
if 'panels' in sys.modules:
    del sys.modules['panels']
if 'tree_generator' in sys.modules:
    del sys.modules['tree_generator']
if 'utils_' in sys.modules:
    del sys.modules['utils_']



# Import property class from another file

import my_property
from my_property import MyProperties
importlib.reload(my_property)

import start_node_info
from start_node_info import startNodeInfo
importlib.reload(start_node_info)

import node_info
from node_info import nodeInfo
importlib.reload(node_info)

import start_point_data
from start_point_data import StartPointData
from start_point_data import DummyStartPointData
importlib.reload(start_point_data)

import rotation_step
from rotation_step import rotationStep
importlib.reload(rotation_step)

import node_
from node_ import node
importlib.reload(node_)

import segment_
from segment_ import segment
importlib.reload(segment_)

import property_groups
from property_groups import floatProp, fibonacciProps, intProp, intPropL, posIntProp3, floatProp, posFloatProp, posFloatPropDefault1, posFloatPropSoftMax2, posFloatPropSoftMax1, posFloatPropSoftMax1taperFactor, posFloatPropSoftMax1Default0, floatProp01, floatProp01default0p5,  floatListProp, floatListProp01, boolProp, showSplitLevelsProp, splitHeightFloatListProp, parentClusterBoolListProp, leafParentClusterBoolListProp, branchClusterBoolListProp, leafClusterBoolListProp, treeShapeEnumProp, treePresetEnumProp, splitModeEnumProp, angleModeEnumProp,  branchTypeEnumProp, toggleBool, toggleLeafBool, leafAngleModeEnumProp, leafTypeEnumProp, toggleUseTaperCurveOperator, treeSettings, branchClusterSettings, leafClusterSettings, UL_stemSplitLevelList, UL_branchSplitLevelListLevel_0, UL_branchSplitLevelListLevel_1, UL_branchSplitLevelListLevel_2, UL_branchSplitLevelListLevel_3, UL_branchSplitLevelListLevel_4, UL_branchSplitLevelListLevel_5, UL_branchSplitLevelListLevel_6, UL_branchSplitLevelListLevel_7, UL_branchSplitLevelListLevel_8, UL_branchSplitLevelListLevel_9, UL_branchSplitLevelListLevel_10, UL_branchSplitLevelListLevel_11, UL_branchSplitLevelListLevel_12, UL_branchSplitLevelListLevel_13, UL_branchSplitLevelListLevel_14, UL_branchSplitLevelListLevel_15, UL_branchSplitLevelListLevel_16, UL_branchSplitLevelListLevel_17, UL_branchSplitLevelListLevel_18, UL_branchSplitLevelListLevel_19
importlib.reload(property_groups)

import operators
from operators import generateTree, packUVs, BranchClusterResetButton, BranchClusterEvaluateButton, initButton, evaluateButton, addBranchCluster, removeBranchCluster, addLeafItem, removeLeafItem, toggleBool, toggleLeafBool, toggleUseTaperCurveOperator, addStemSplitLevel, removeStemSplitLevel, addBranchSplitLevel, removeBranchSplitLevel, exportProperties, importProperties, loadPreset
importlib.reload(operators)

import panels
from panels import treeGenPanel, treeSettingsPanel, noiseSettings, angleSettings, splitSettings, branchSettings, leafSettings
importlib.reload(panels)

import noise_generator
from noise_generator import SimplexNoiseGenerator
importlib.reload(noise_generator)

import tree_generator
from tree_generator import treeGenerator
importlib.reload(tree_generator)

import utils_
from utils_ import utils

# for addon.......................................................................................................
#from .my_property import MyProperties
#from .start_node_info import startNodeInfo
#from .node_info import nodeInfo
#from .start_point_data import startPointData
#from .start_point_data import dummyStartPointData
#from .rotation_step import rotationStep
#from .node_ import node
#from .segment_ import segment
#from .property_groups import floatProp, fibonacciProps, intProp, intPropL, posIntProp3, floatProp, posFloatProp, posFloatPropDefault1, posFloatPropSoftMax2, posFloatPropSoftMax1, posFloatPropSoftMax1taperFactor, posFloatPropSoftMax1Default0, floatProp01, floatProp01default0p5,  floatListProp, floatListProp01, boolProp, showSplitLevelsProp, splitHeightFloatListProp, parentClusterBoolListProp, leafParentClusterBoolListProp, branchClusterBoolListProp, leafClusterBoolListProp, treeShapeEnumProp, treePresetEnumProp, splitModeEnumProp, angleModeEnumProp,  branchTypeEnumProp, toggleBool, toggleLeafBool, leafAngleModeEnumProp, leafTypeEnumProp, toggleUseTaperCurveOperator, treeSettings, branchClusterSettings, leafClusterSettings, UL_stemSplitLevelList, UL_branchSplitLevelListLevel_0, UL_branchSplitLevelListLevel_1, UL_branchSplitLevelListLevel_2, UL_branchSplitLevelListLevel_3, UL_branchSplitLevelListLevel_4, UL_branchSplitLevelListLevel_5, UL_branchSplitLevelListLevel_6, UL_branchSplitLevelListLevel_7, UL_branchSplitLevelListLevel_8, UL_branchSplitLevelListLevel_9, UL_branchSplitLevelListLevel_10, UL_branchSplitLevelListLevel_11, UL_branchSplitLevelListLevel_12, UL_branchSplitLevelListLevel_13, UL_branchSplitLevelListLevel_14, UL_branchSplitLevelListLevel_15, UL_branchSplitLevelListLevel_16, UL_branchSplitLevelListLevel_17, UL_branchSplitLevelListLevel_18, UL_branchSplitLevelListLevel_19
#from .operators import generateTree, packUVs, BranchClusterResetButton, BranchClusterEvaluateButton, initButton, evaluateButton, addBranchCluster, removeBranchCluster, addLeafItem, removeLeafItem, toggleBool, toggleLeafBool, toggleUseTaperCurveOperator, addStemSplitLevel, removeStemSplitLevel, addBranchSplitLevel, removeBranchSplitLevel, exportProperties, importProperties, loadPreset
#from .noise_generator import SimplexNoiseGenerator
#from .tree_generator import treeGenerator
#from .utils_ import utils

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
    
    #----------------------------------------
    
    #save and load #  TEST OFF
    bpy.utils.register_class(operators.importProperties)
    bpy.utils.register_class(operators.exportProperties)
#    bpy.utils.register_class(loadPreset)
    
#    #data types
    bpy.utils.register_class(property_groups.treePresetEnumProp)
    bpy.utils.register_class(property_groups.treeShapeEnumProp)
    bpy.utils.register_class(property_groups.splitModeEnumProp)
    bpy.utils.register_class(property_groups.angleModeEnumProp)
    bpy.utils.register_class(property_groups.branchTypeEnumProp)
    bpy.utils.register_class(property_groups.intProp)
    bpy.utils.register_class(property_groups.intPropL)
    bpy.utils.register_class(property_groups.posIntProp3)
    bpy.utils.register_class(property_groups.fibonacciProps)
    bpy.utils.register_class(property_groups.floatProp)
    bpy.utils.register_class(property_groups.posFloatProp)
    bpy.utils.register_class(property_groups.posFloatPropDefault1)
    bpy.utils.register_class(property_groups.floatProp01)
    bpy.utils.register_class(property_groups.floatProp01default0p5)
    bpy.utils.register_class(property_groups.posFloatPropSoftMax1)
    bpy.utils.register_class(property_groups.posFloatPropSoftMax1Default0)
    bpy.utils.register_class(property_groups.posFloatPropSoftMax2)
    bpy.utils.register_class(property_groups.floatListProp)
    bpy.utils.register_class(property_groups.floatListProp01)
    bpy.utils.register_class(property_groups.boolProp)
    bpy.utils.register_class(property_groups.parentClusterBoolListProp)
    bpy.utils.register_class(property_groups.branchClusterBoolListProp)
    bpy.utils.register_class(property_groups.leafParentClusterBoolListProp)
    bpy.utils.register_class(property_groups.leafAngleModeEnumProp)
    bpy.utils.register_class(property_groups.leafTypeEnumProp)
    
    #UILists
    bpy.utils.register_class(property_groups.UL_stemSplitLevelList)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_5)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_6)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_7)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_8)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_9)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_10)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_11)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_12)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_13)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_14)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_15)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_16)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_17)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_18)
    bpy.utils.register_class(property_groups.UL_branchSplitLevelListLevel_19)
    
    bpy.utils.register_class(property_groups.treeSettings) # -> in property_groups.py
    bpy.utils.register_class(property_groups.branchClusterSettings) # -> in property_groups.py
    bpy.utils.register_class(property_groups.leafClusterSettings) # -> in property_groups.py
    
    #operators
    bpy.utils.register_class(operators.addBranchCluster)
    bpy.utils.register_class(operators.removeBranchCluster)
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(toggleLeafBool)
    bpy.utils.register_class(addStemSplitLevel)
    bpy.utils.register_class(removeStemSplitLevel)
    bpy.utils.register_class(addBranchSplitLevel)
    bpy.utils.register_class(removeBranchSplitLevel)
    bpy.utils.register_class(generateTree)
    bpy.utils.register_class(packUVs)
    bpy.utils.register_class(addLeafItem)
    bpy.utils.register_class(removeLeafItem)
    bpy.utils.register_class(toggleUseTaperCurveOperator)
    
    #panels
    bpy.utils.register_class(panels.treeGenPanel)
    bpy.utils.register_class(panels.treeSettingsPanel)
    bpy.utils.register_class(panels.noiseSettings)
    bpy.utils.register_class(panels.angleSettings)
    bpy.utils.register_class(panels.splitSettings)
    
    
    bpy.utils.register_class(branchSettings) # TODO...
#    bpy.utils.register_class(leafSettings) # TODO
#    
#    
#    
    bpy.utils.register_class(evaluateButton)
    bpy.utils.register_class(initButton)
    bpy.utils.register_class(BranchClusterEvaluateButton)
    bpy.utils.register_class(BranchClusterResetButton)
    
    
    #collections    
    bpy.types.Scene.branchClusterSettingsList = bpy.props.CollectionProperty(type=property_groups.branchClusterSettings)
    
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=property_groups.floatProp01)
    bpy.types.Scene.showStemSplitHeights = bpy.props.BoolProperty(
        name = "Show/hide stem split heights",
        default = True
    )
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.treePreset = bpy.props.PointerProperty(type=property_groups.treePresetEnumProp)
    
    bpy.types.Scene.folder_path = bpy.props.StringProperty(name="Folder", subtype='DIR_PATH', default="")
    bpy.types.Scene.file_name = bpy.props.StringProperty(name="File Name", default="")
        
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=property_groups.boolProp)
    bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=property_groups.branchClusterBoolListProp)
    bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=property_groups.posFloatPropSoftMax1)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=property_groups.floatListProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)

    
    bpy.types.Scene.leafClusterSettingsList = bpy.props.CollectionProperty(type=property_groups.leafClusterSettings)
    
    
    bpy.types.Scene.bark_material = bpy.props.PointerProperty(type=bpy.types.Material)
    bpy.types.Scene.leaf_material = bpy.props.PointerProperty(type=bpy.types.Material)
                
    bpy.types.Scene.treeSettings = bpy.props.PointerProperty(type=property_groups.treeSettings)
    
    bpy.app.timers.register(delayed_init, first_interval=0.1) # TODO
    
def delayed_init():
    panels.ensure_stem_curve_node(curve_node_mapping = {}, taper_node_mapping = {})
    bpy.ops.scene.init_button()


def unregister():
    bpy.utils.unregister_class(MinimalPanel)
    del bpy.types.Scene.minimal_props
    bpy.utils.unregister_class(MinimalProps)
    
    bpy.utils.unregister_class(MinimalOperator)
    
    #------------------------------------------
    
    #save and load
    #bpy.utils.unregister_class(importProperties)
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
    bpy.utils.unregister_class(addBranchCluster)
    bpy.utils.unregister_class(removeBranchCluster)
    bpy.utils.unregister_class(toggleBool)
    bpy.utils.unregister_class(toggleLeafBool)
    bpy.utils.unregister_class(addStemSplitLevel)
    bpy.utils.unregister_class(removeStemSplitLevel)
    bpy.utils.unregister_class(addBranchSplitLevel)
    bpy.utils.unregister_class(removeBranchSplitLevel)
    bpy.utils.unregister_class(generateTree)
    bpy.utils.unregister_class(packUVs)
    bpy.utils.unregister_class(addLeafItem)
    bpy.utils.unregister_class(removeLeafItem)
    
    bpy.utils.unregister_class(evaluateButton)
    bpy.utils.unregister_class(BranchClusterEvaluateButton)
    bpy.utils.unregister_class(BranchClusterResetButton)
    bpy.utils.unregister_class(initButton)
    bpy.utils.unregister_class(toggleUseTaperCurveOperator)
    
    
    #panels
    bpy.utils.unregister_class(treeGenPanel)
    bpy.utils.unregister_class(treeSettingsPanel)
    bpy.utils.unregister_class(noiseSettings)
    bpy.utils.unregister_class(angleSettings)
    bpy.utils.unregister_class(splitSettings)
    bpy.utils.unregister_class(leafSettings)
    
    bpy.utils.unregister_class(BranchSettings)
    
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
    
    
    # Unregister collections
    del bpy.types.Scene.branchClusterSettingsList
    del bpy.types.Scene.stemSplitHeightInLevelList
    del bpy.types.Scene.showStemSplitHeights
    del bpy.types.Scene.stemSplitHeightInLevelListIndex
    del bpy.types.Scene.file_name
    del bpy.types.Scene.folder_path
    del bpy.types.Scene.treePreset
    del bpy.types.Scene.parentClusterBoolList
    del bpy.types.Scene.branchClusterBoolListList
    del bpy.types.Scene.nrBranchesListIndex
    del bpy.types.Scene.taperFactorList
    del bpy.types.Scene.branchSplitHeightInLevelListList
    del bpy.types.Scene.leafClusterSettingsList
    del bpy.types.Scene.bark_material
    del bpy.types.Scene.leaf_material

if __name__ == "__main__":
    register()