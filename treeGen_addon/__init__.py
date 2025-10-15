import importlib
import bpy
import sys
import os
import random



# Dynamically add current folder to sys.path

# for testing.......................................................................................................
#import importlib
#addon_dir = "/home/j/Downloads/treeGen_v5_minimal_addon"
#if addon_dir not in sys.path:
#    sys.path.append(addon_dir)
#if 'my_property' in sys.modules:  # For reliable reload during development
#    del sys.modules['my_property']
#if 'start_node_info' in sys.modules:
#    del sys.modules['start_node_info']
#if 'node_info' in sys.modules:
#    del sys.modules['node_info']
#if 'start_point_data' in sys.modules:
#    del sys.modules['start_point_data']
#if 'rotation_step' in sys.modules:
#    del sys.modules['rotation_step']
#if 'node_' in sys.modules:
#    del sys.modules['node_']
#if 'segment_' in sys.modules:
#    del sys.modules['segment_']
#if 'property_groups' in sys.modules:
#    del sys.modules['property_groups']
#if 'operators' in sys.modules:
#    del sys.modules['operators']
#if 'panels' in sys.modules:
#    del sys.modules['panels']
#if 'tree_generator' in sys.modules:
#    del sys.modules['tree_generator']
#if 'treegen_utils_' in sys.modules:
#    del sys.modules['treegen_utils_']
#
#
#
## Import property class from another file
#
#import my_property
#from my_property import MyProperties
#importlib.reload(my_property)
#
#import start_node_info
#from start_node_info import startNodeInfo
#importlib.reload(start_node_info)
#
#import node_info
#from node_info import nodeInfo
#importlib.reload(node_info)
#
#import start_point_data
#from start_point_data import StartPointData
#from start_point_data import DummyStartPointData
#importlib.reload(start_point_data)
#
#import rotation_step
#from rotation_step import rotationStep
#importlib.reload(rotation_step)
#
#import node_
#from node_ import node
#importlib.reload(node_)
#
#import segment_
#from segment_ import segment
#importlib.reload(segment_)
#
#import property_groups
#from property_groups import floatProp, fibonacciProps, intProp, intPropL, posIntProp3, floatProp, posFloatProp, posFloatPropDefault1, posFloatPropSoftMax2, posFloatPropSoftMax1, posFloatPropSoftMax1taperFactor, posFloatPropSoftMax1Default0, floatProp01, floatProp01default0p5,  floatListProp, floatListProp01, boolProp, showSplitLevelsProp, splitHeightFloatListProp, parentClusterBoolListProp, leafParentClusterBoolListProp, branchClusterBoolListProp, leafClusterBoolListProp, treeShapeEnumProp, treePresetEnumProp, splitModeEnumProp, angleModeEnumProp,  branchTypeEnumProp, toggleBool, toggleLeafBool, leafAngleModeEnumProp, leafTypeEnumProp, toggleUseTaperCurveOperator, treeSettings, branchClusterSettings, leafClusterSettings, TREEGEN_UL_stemSplitLevelList, TREEGEN_UL_branchSplitLevelListLevel_0, TREEGEN_UL_branchSplitLevelListLevel_1, TREEGEN_UL_branchSplitLevelListLevel_2, TREEGEN_UL_branchSplitLevelListLevel_3, TREEGEN_UL_branchSplitLevelListLevel_4, TREEGEN_UL_branchSplitLevelListLevel_5, TREEGEN_UL_branchSplitLevelListLevel_6, TREEGEN_UL_branchSplitLevelListLevel_7, TREEGEN_UL_branchSplitLevelListLevel_8, TREEGEN_UL_branchSplitLevelListLevel_9, TREEGEN_UL_branchSplitLevelListLevel_10, TREEGEN_UL_branchSplitLevelListLevel_11, TREEGEN_UL_branchSplitLevelListLevel_12, TREEGEN_UL_branchSplitLevelListLevel_13, TREEGEN_UL_branchSplitLevelListLevel_14, TREEGEN_UL_branchSplitLevelListLevel_15, TREEGEN_UL_branchSplitLevelListLevel_16, TREEGEN_UL_branchSplitLevelListLevel_17, TREEGEN_UL_branchSplitLevelListLevel_18, TREEGEN_UL_branchSplitLevelListLevel_19
#importlib.reload(property_groups)
#
#import operators
#from operators import generateTree, packUVs, BranchClusterResetButton, BranchClusterEvaluateButton, initButton, evaluateButton, addBranchCluster, removeBranchCluster, addLeafItem, removeLeafItem, toggleBool, toggleLeafBool, toggleUseTaperCurveOperator, addStemSplitLevel, removeStemSplitLevel, addBranchSplitLevel, removeBranchSplitLevel, exportProperties, importProperties, loadPreset
#importlib.reload(operators)
#
#import panels
#from panels import treeGenPanel, treeSettingsPanel, noiseSettings, angleSettings, splitSettings, branchSettings, leafSettings
#importlib.reload(panels)
#
#import noise_generator
#from noise_generator import SimplexNoiseGenerator
#importlib.reload(noise_generator)
#
#import tree_generator
#from tree_generator import treeGenerator
#importlib.reload(tree_generator)
#
#import treegen_utils_
#from treegen_utils_ import treegen_utils

# for addon.......................................................................................................

#from . import start_node_info
#from . import node_info
#from . import start_point_data
#from . import rotation_step
#from . import node_
#from . import segment_
#from . import property_groups
#from . import operators
#from . import panels
#from . import noise_generator
#from . import tree_generator
#from . import treegen_utils_

import_modules = [
'property_groups', # import first!
'noise_generator', # import first!

'start_node_info',
'node_info',
'start_point_data',
'rotation_step',
'node_',
'segment_',
'operators',
'panels',
'tree_generator',
'treegen_utils_']

names = [__name__ + '.' + name for name in import_modules]

for name in names:
    try:
        importlib.import_module(name)
        print(f"{name} imported successfully")
    except ImportError as e:
        print(f"Error importing {name}: {e}")
              

# TODO: reload logic...


def register():
    #save and load
    bpy.utils.register_class(operators.EXPORT_OT_importProperties)
    bpy.utils.register_class(operators.EXPORT_OT_exportProperties)
    bpy.utils.register_class(operators.EXPORT_OT_loadPreset)
    
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
    bpy.utils.register_class(property_groups.TREEGEN_UL_stemSplitLevelList)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_5)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_6)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_7)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_8)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_9)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_10)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_11)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_12)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_13)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_14)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_15)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_16)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_17)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_18)
    bpy.utils.register_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_19)
    
    bpy.utils.register_class(property_groups.treeSettings) # -> in property_groups.py
    bpy.utils.register_class(property_groups.branchClusterSettings) # -> in property_groups.py
    bpy.utils.register_class(property_groups.leafClusterSettings) # -> in property_groups.py
    
    #operators
    bpy.utils.register_class(operators.SCENE_OT_addBranchCluster)
    bpy.utils.register_class(operators.SCENE_OT_removeBranchCluster)
    bpy.utils.register_class(operators.SCENE_OT_toggleBool)
    bpy.utils.register_class(operators.SCENE_OT_toggleLeafBool)
    bpy.utils.register_class(operators.SCENE_OT_addStemSplitLevel)
    bpy.utils.register_class(operators.SCENE_OT_removeStemSplitLevel)
    bpy.utils.register_class(operators.SCENE_OT_addBranchSplitLevel)
    bpy.utils.register_class(operators.SCENE_OT_removeBranchSplitLevel)
    bpy.utils.register_class(operators.OBJECT_OT_generateTree)
    bpy.utils.register_class(operators.OBJECT_OT_packUVs)
    bpy.utils.register_class(operators.SCENE_OT_addLeafItem)
    bpy.utils.register_class(operators.SCENE_OT_removeLeafItem)
    bpy.utils.register_class(operators.SCENE_OT_toggleUseTaperCurveOperator)
    bpy.utils.register_class(operators.SCENE_OT_evaluateButton)
    bpy.utils.register_class(operators.SCENE_OT_initButton)
    bpy.utils.register_class(operators.SCENE_OT_BranchClusterEvaluateButton)
    bpy.utils.register_class(operators.SCENE_OT_BranchClusterResetButton)

    #panels
    bpy.utils.register_class(panels.treeGenPanel)
    bpy.utils.register_class(panels.treeSettingsPanel)
    bpy.utils.register_class(panels.noiseSettings)
    bpy.utils.register_class(panels.angleSettings)
    bpy.utils.register_class(panels.splitSettings)
    
    bpy.utils.register_class(panels.branchSettings)
    bpy.utils.register_class(panels.leafSettings) # TODO
    
    
    
    
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
    panels.ensure_stem_curve_node(None)
    bpy.ops.scene.init_button()


def unregister():
    #save and load
    bpy.utils.unregister_class(operators.EXPORT_OT_importProperties)
    bpy.utils.unregister_class(operators.EXPORT_OT_exportProperties)
    bpy.utils.unregister_class(operators.EXPORT_OT_loadPreset)
        
    #data types
    bpy.utils.unregister_class(property_groups.treeShapeEnumProp)
    bpy.utils.unregister_class(property_groups.treePresetEnumProp)
    bpy.utils.unregister_class(property_groups.splitModeEnumProp)
    bpy.utils.unregister_class(property_groups.angleModeEnumProp)
    bpy.utils.unregister_class(property_groups.branchTypeEnumProp)
    bpy.utils.unregister_class(property_groups.intProp)
    bpy.utils.unregister_class(property_groups.intPropL)
    bpy.utils.unregister_class(property_groups.posIntProp3)
    bpy.utils.unregister_class(property_groups.fibonacciProps)
    bpy.utils.unregister_class(property_groups.floatProp)
    bpy.utils.unregister_class(property_groups.posFloatProp)
    bpy.utils.unregister_class(property_groups.posFloatPropDefault1)
    bpy.utils.unregister_class(property_groups.floatProp01)
    bpy.utils.unregister_class(property_groups.floatProp01default0p5)
    bpy.utils.unregister_class(property_groups.posFloatPropSoftMax1)
    bpy.utils.unregister_class(property_groups.posFloatPropSoftMax1Default0)
    bpy.utils.unregister_class(property_groups.posFloatPropSoftMax2)
    bpy.utils.unregister_class(property_groups.floatListProp)
    bpy.utils.unregister_class(property_groups.floatListProp01)
    bpy.utils.unregister_class(property_groups.boolProp)
    bpy.utils.unregister_class(property_groups.parentClusterBoolListProp)
    bpy.utils.unregister_class(property_groups.branchClusterBoolListProp)
    bpy.utils.unregister_class(property_groups.leafParentClusterBoolListProp)
    bpy.utils.unregister_class(property_groups.leafAngleModeEnumProp)
    bpy.utils.unregister_class(property_groups.leafTypeEnumProp)
    
    bpy.utils.unregister_class(property_groups.treeSettings)
    bpy.utils.unregister_class(property_groups.branchClusterSettings)
    bpy.utils.unregister_class(property_groups.leafClusterSettings)
    
    #operators
    bpy.utils.unregister_class(operators.SCENE_OT_addBranchCluster)
    bpy.utils.unregister_class(operators.SCENE_OT_removeBranchCluster)
    bpy.utils.unregister_class(operators.SCENE_OT_toggleBool)
    bpy.utils.unregister_class(operators.SCENE_OT_toggleLeafBool)
    bpy.utils.unregister_class(operators.SCENE_OT_addStemSplitLevel)
    bpy.utils.unregister_class(operators.SCENE_OT_removeStemSplitLevel)
    bpy.utils.unregister_class(operators.SCENE_OT_addBranchSplitLevel)
    bpy.utils.unregister_class(operators.SCENE_OT_removeBranchSplitLevel)
    bpy.utils.unregister_class(operators.OBJECT_OT_generateTree)
    bpy.utils.unregister_class(operators.OBJECT_OT_packUVs)
    bpy.utils.unregister_class(operators.SCENE_OT_addLeafItem)
    bpy.utils.unregister_class(operators.SCENE_OT_removeLeafItem)
    bpy.utils.unregister_class(operators.SCENE_OT_evaluateButton)
    bpy.utils.unregister_class(operators.SCENE_OT_BranchClusterEvaluateButton)
    bpy.utils.unregister_class(operators.SCENE_OT_BranchClusterResetButton)
    bpy.utils.unregister_class(operators.SCENE_OT_initButton)
    bpy.utils.unregister_class(operators.SCENE_OT_toggleUseTaperCurveOperator)
    
    
    #panels
    bpy.utils.unregister_class(panels.treeGenPanel)
    bpy.utils.unregister_class(panels.treeSettingsPanel)
    bpy.utils.unregister_class(panels.noiseSettings)
    bpy.utils.unregister_class(panels.angleSettings)
    bpy.utils.unregister_class(panels.splitSettings)
    
    bpy.utils.unregister_class(panels.branchSettings)
    bpy.utils.unregister_class(panels.leafSettings)
    
    #UILists
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_stemSplitLevelList)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_0)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_1)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_2)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_3)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_4)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_5)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_6)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_7)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_8)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_9)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_10)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_11)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_12)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_13)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_14)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_15)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_16)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_17)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_18)
    bpy.utils.unregister_class(property_groups.TREEGEN_UL_branchSplitLevelListLevel_19)
    
    
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

#if __name__ == "__main__":
#    register()
