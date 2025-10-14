import bpy.types
import property_groups
import math

def myNodeTree():
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['CurveNodeGroup'].nodes



def myCurveData(curve_name):
    if curve_name not in property_groups.curve_node_mapping: # #in propertyGroups !!! (???)
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        property_groups.curve_node_mapping[curve_name] = cn.name
    nodeTree = myNodeTree()[property_groups.curve_node_mapping[curve_name]]
    return nodeTree

#        curve_node_mapping = {}
#        taper_node_mapping = {}

def ensure_stem_curve_node(treeGeneratorInstance): # called from operators
    curve_name = "Stem"
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    if curve_name not in property_groups.curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        property_groups.curve_node_mapping[curve_name] = cn.name
    return curve_name

def ensure_branch_curve_node(treeGeneratorInstance, idx):
    curve_name = f"BranchCluster_{idx}"
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    if curve_name not in property_groups.curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        #cn.label = curve_name
        property_groups.curve_node_mapping[curve_name] = cn.name
    return curve_name


def drawDebugPoint(pos, size, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = size
    bpy.context.active_object.name=name

class treeGenPanel(bpy.types.Panel):
    bl_label = "Tree Generator"
    bl_idname = "PT_TreeGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        layout.prop(context.scene, "folder_path")
        
        layout.prop(context.scene, "file_name")  # String input for file name
        
        layout.operator("export.save_properties_file", text="Save Properties")
        layout.operator("export.load_properties_file", text="Load Properties")
        
        row = layout.row()
        row.label(text="Preset: ")
        row.prop(context.scene.treeSettings.treePreset, "value", text="")
        row = layout.row()
        row.operator("export.load_preset", text="Load Preset")
        
        row = layout.row()
        row.label(icon = 'COLORSET_12_VEC')
        row.operator("object.generate_tree", text="Generate Tree")
        
        layout.prop(context.scene.treeSettings, "uvMargin")
        row = layout.row()
        row.operator("object.pack_uvs", text="Pack UVs")
        
class treeSettingsPanel(bpy.types.Panel):
    bl_label = "Tree Settings"
    bl_idname = "PT_TreeSettings"
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
        
        layout.template_curve_mapping(myCurveData('Stem'), "mapping") # TODO! TEMP OFF ...
        
        #layout.prop(context.scene, "evaluate", slider=True)
        #layout.operator("scene.evaluate_button", text="Evaluate").x = context.scene.evaluate
        layout.operator("scene.init_button", text="Reset")
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "branchTipRadius")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "ringSpacing")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemRingResolution")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "resampleDistance")
        
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
        layout.prop(context.scene.treeSettings, "curvatureStart")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "curvatureEnd")
        
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
        row.operator("scene.remove_stem_split_level", text="Remove").index = context.scene.treeSettings.stemSplitHeightInLevelListIndex
        if context.scene.treeSettings.showStemSplitHeights == True:
            row = layout.row()
            row.template_list("UL_stemSplitLevelList", "", context.scene.treeSettings, "stemSplitHeightInLevelList", context.scene.treeSettings, "stemSplitHeightInLevelListIndex")
        
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
    boolListItem = scene.treeSettings.parentClusterBoolListList[cluster_index].value
    
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

class branchSettings(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_branchSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    curve_node_mapping = {}
    taper_node_mapping = {}
    
    def draw(self, context):
        layout = self.layout
                
        #layout = self.layout
        #obj = context.object
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        
        row = layout.row(align = True)
        row.operator("scene.add_branch_cluster", text="Add")
        row.operator("scene.remove_branch_cluster", text="Remove")
        
        row = layout.row()
        for i, outer in enumerate(scene.treeSettings.parentClusterBoolListList):
            if i < len(scene.branchClusterBoolListList) and i < len(scene.branchClusterSettingsList):
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
                    
                    #split = box.split(factor=0.6)
                    #split.label(text="Use taper curve")
                    #split.prop(scene.branchClusterSettingsList[i], "useTaperCurve", text="")
                    #
                    #
                    #
                    #    taperCurveName = f"taperMappingBranchCluster{i}"
                    #    box.template_curve_mapping(taperCurveData(taperCurveName), "mapping")
                    box3 = box.box()
                    row = box3.row()
                    
                    #split.prop(scene.branchClusterSettingsList[i], "useTaperCurve", text="")
                    
                    row.operator("scene.toggle_use_taper_curve", text="Use taper curve", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].useTaperCurve else "TRIA_RIGHT").idx = i
                    
                    #box.prop(scene.branchClusterBoolListList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterBoolListList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
                    
                    if scene.branchClusterSettingsList[i].useTaperCurve == True:
                        #row = box3.row()
                        #op = row.operator("scene.evaluate_branch_cluster", text="Evaluate branch")
                        #op.idx = i
                        reset = row.operator("scene.reset_branch_cluster_curve", text="Reset")
                        reset.idx = i
                        curve_name = ensure_branch_curve_node(self, i)
                        curve_node = myCurveData(curve_name)
                        box3.template_curve_mapping(curve_node, "mapping")
                    
                    #row = box2.row()
                    
                    #row.prop(scene.branchClusterSettingsList[i], "showBranchSplitHeights", icon="TRIA_DOWN" if scene.branchClusterSettingsList[i].showBranchSplitHeights else "TRIA_RIGHT", text="", toggle=True)
                    #
                    #row.operator("scene.add_branch_split_level", text="Add split level").level = i
                    #row.operator("scene.remove_branch_split_level", text="Remove").level = i
                    #
            
                    
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
                            split1.label(text=f"{(180.0 / math.pi) * scene.branchClusterSettingsList[i].fibonacciNr.fibonacci_angle:.2f}°")
                    
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
                                
def draw_leaf_cluster_bools(layout, scene, cluster_index, leafParentClusterBool):
    boolListItem = scene.treeSettings.leafParentClusterBoolListList[cluster_index].value
    
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
        row.operator("scene.add_leaf_cluster", text="Add")
        row.operator("scene.remove_leaf_cluster", text="Remove").index = context.scene.treeSettings.leavesDensityListIndex
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
                draw_leaf_cluster_bools(box1, scene, i, scene.treeSettings.leafParentClusterBoolListList[i])
