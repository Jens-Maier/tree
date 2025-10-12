import bpy.props
import math

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0)
    
class fibonacciProps(bpy.types.PropertyGroup):
    fibonacci_nr: bpy.props.IntProperty(name = "fibonacciNr", default=3, min=3, 
        update = lambda self, context:update_fibonacci_numbers(self))
        
    fibonacci_angle: bpy.props.FloatProperty(name="", default=2.0 * math.pi / 3.0, options={'HIDDEN'})
    
    use_fibonacci: bpy.props.BoolProperty(name = "useFibonacci", default=False,
        update = lambda self, context:update_fibonacci_numbers(self))


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
        boolList = context.scene.treeSettings.parentClusterBoolListList[self.list_index].value
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
        boolList = context.scene.treeSettings.leafParentClusterBoolListList[self.list_index].value
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
        if wasEnabled:
            bpy.ops.scene.reset_branch_cluster_curve(idx = self.idx)
            
        return {'FINISHED'}
 

class treeSettings(bpy.types.PropertyGroup):
    uvMargin: bpy.props.FloatProperty(name = "UV margin", default = 0.1, min = 0, precision = 3)
    treeHeight: bpy.props.FloatProperty(name = "Tree height", default = 10.0, min = 0, unit = 'LENGTH')
    taper: bpy.props.FloatProperty(name = "taper", default = 0.1, min = 0, soft_max = 0.5)
    branchTipRadius:bpy.props.FloatProperty(name = "branch tip radius", default = 0, min = 0, soft_max = 0.1, unit = 'LENGTH')
    ringSpacing: bpy.props.FloatProperty(name = "Ring Spacing", default = 0.1, min = 0.001, unit = 'LENGTH')
    noiseAmplitudeHorizontal: bpy.props.FloatProperty(name = "Noise Amplitude Horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVertical: bpy.props.FloatProperty(name = "Noise Amplitude Vertical", default = 0.0, min = 0.0)
    noiseAmplitudeGradient: bpy.props.FloatProperty(name = "Noise Amplitude Gradient", default = 0.1, min = 0.0)
    noiseAmplitudeExponent: bpy.props.FloatProperty(name = "Noise Amplitude Exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise Scale", default = 1.0, min = 0.0)
    seed: bpy.props.IntProperty(name = "Seed")
    curvatureStart: bpy.props.FloatProperty(name = "Curvature Start", default = 0.0, unit = 'ROTATION')
    curvatureEnd: bpy.props.FloatProperty(name = "Curvature End", default = 0.0, unit = 'ROTATION')
    stemSplitRotateAngle: bpy.props.FloatProperty(name = "Stem Split Rotate Angle", default = 0.0, min = 0.0, max = 2.0 * math.pi, unit = 'ROTATION')
    variance: bpy.props.FloatProperty(name = "Variance", default = 0.0, min = 0.0, max = 1.0)
    curvOffsetStrength: bpy.props.FloatProperty(name = "Curvature Offset Strength", default = 0.0, min = 0.0)
    stemSplitAngle: bpy.props.FloatProperty(name = "Stem Split Angle", default = 0.0, min = 0.0, max = 2.0 * math.pi, unit = 'ROTATION')
    stemSplitHeightInLevelList: bpy.props.CollectionProperty(type=floatProp01)
    stemSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0, min = 0)
    
    stemSplitPointAngle: bpy.props.FloatProperty(name = "Stem Split Point Angle", default = 0.0, min = 0.0, max = 2.0 * math.pi, unit = 'ROTATION')
    splitHeightVariation: bpy.props.FloatProperty(name = "Split Height Variation", default = 0.0, min = 0.0)
    splitLengthVariation: bpy.props.FloatProperty(name = "Split Length Variation", default = 0.0, min = 0.0)
    treeShape: bpy.props.EnumProperty(
        name="Shape",
        description="The shape of the tree.",
        items=[
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
    
    stemRingResolution: bpy.props.IntProperty(name = "Stem Ring Resolution", default = 16, min = 3)
    resampleDistance: bpy.props.FloatProperty( name = "Resample Distance", default = 10.0, min = 0.0, unit = 'LENGTH')
    nrSplits: bpy.props.IntProperty(name = "Number of Splits", default = 0, min = 0)
    showStemSplitHeights: bpy.props.BoolProperty(name = "Show/hide stem split heights", default = True)
    stemSplitMode: bpy.props.EnumProperty(
        name = "Stem Split Mode",
        description = "Mode for stem splits",
        items=[
            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
            ('HORIZONTAL', "Horizontal", "Split horizontally"),
        ],
        default='ROTATE_ANGLE',
    )
    maxSplitHeightUsed: bpy.props.IntProperty(default = 0)
    
    parentClusterBoolListList: bpy.props.CollectionProperty(type=parentClusterBoolListProp)
    leafParentClusterBoolListList: bpy.props.CollectionProperty(type=leafParentClusterBoolListProp)
    
    branchClusters: bpy.props.IntProperty(name = "Branch Clusters", default = 0, min = 0)

    treeGrowDir: bpy.props.FloatVectorProperty(
        name = "Tree Grow Direction",
        description = "Direction the tree grows in",
        default = (0.0, 0.0, 1.0),
        subtype = 'XYZ'  # Important for direction vectors
    )
    ringResolution: bpy.props.IntProperty(name="Ring Resolution", default = 16, min = 3)
    leafClusters: bpy.props.IntProperty(name = "Leaf Clusters", default = 0, min = 0)
    
    branchSplitHeightInLevelListList: bpy.props.CollectionProperty(type = floatListProp01)
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
    
    leavesDensityListIndex: bpy.props.IntProperty(default = 0)

class branchClusterSettings(bpy.types.PropertyGroup):
    branchClusterBoolList: bpy.props.CollectionProperty(type=branchClusterBoolListProp)
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
    
    showNoiseSettings: bpy.props.BoolProperty(name = "Show/hide noise settings", default=True)
        
    noiseAmplitudeHorizontalBranch: bpy.props.FloatProperty(name = "Noise amplitude horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVerticalBranch: bpy.props.FloatProperty(name = "Noise amplitude vertical", default = 0.0, min = 0.0)
    noiseAmplitudeBranchGradient: bpy.props.FloatProperty(name = "Noise amplitude gradient", default = 0.0, min = 0.0)
    noiseAmplitudeBranchExponent: bpy.props.FloatProperty(name = "Noise amplitude exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise scale", default = 1.0, min = 0.0)
        
    showAngleSettings: bpy.props.BoolProperty(name = "Show/hide angle settings", default=True)
    
    verticalAngleCrownStart: bpy.props.FloatProperty(name = "Vertical angle crown start", default = math.pi / 4.0, unit = 'ROTATION')
    verticalAngleCrownEnd: bpy.props.FloatProperty(name = "Vertical angle crown end", default = math.pi / 4.0, unit = 'ROTATION')
    verticalAngleBranchStart: bpy.props.FloatProperty(name = "Vertical angle branch start", default = 0.0, unit = 'ROTATION')
    verticalAngleBranchEnd: bpy.props.FloatProperty(name = "Vertical angle branch end", default = 0.0, unit = 'ROTATION')
    branchAngleMode: bpy.props.PointerProperty(type = angleModeEnumProp)
    useFibonacciAngles: bpy.props.BoolProperty(name = "Use Fibonacci angles")
    fibonacciNr: bpy.props.PointerProperty(type = fibonacciProps)
    rotateAngleRange: bpy.props.FloatProperty(name = "Rotate angle range", default = math.pi, unit = 'ROTATION')
    rotateAngleOffset: bpy.props.FloatProperty(name = "Rotate angle offset", default = 0.0, unit = 'ROTATION')
    
    rotateAngleCrownStart: bpy.props.FloatProperty(name = "Rotate angle crown start", default = 0.0, unit = 'ROTATION')
    rotateAngleCrownEnd: bpy.props.FloatProperty(name = "Rotate angle crown end", default = 0.0, unit = 'ROTATION')
    rotateAngleBranchStart: bpy.props.FloatProperty(name = "Rotate angle branch start", default = 0.0, unit = 'ROTATION')
    rotateAngleBranchEnd: bpy.props.FloatProperty(name = "Rotate angle branch end", default = 0.0, unit = 'ROTATION')
    rotateAngleRangeFactor: bpy.props.FloatProperty(name = "Rotate angle range factor", default = 1.0, min = 0.0, soft_max = 2.0)
    
    reducedCurveStepCutoff: bpy.props.FloatProperty(name = "Reduced curve step cutoff", min = 0.0, soft_max = 1.0)
    reducedCurveStepFactor: bpy.props.FloatProperty(name = "Reduced curve step factor", min = 0.0, max = 1.0)
    branchGlobalCurvatureStart: bpy.props.FloatProperty(name = "Branch global curvature start", default = 0.0, unit = 'ROTATION')
    branchGlobalCurvatureEnd: bpy.props.FloatProperty(name = "Branch global curvature end", default = 0.0, unit = 'ROTATION')
    branchCurvatureStart: bpy.props.FloatProperty(name = "Branch curvature start", default = 0.0, unit = 'ROTATION')
    branchCurvatureEnd: bpy.props.FloatProperty(name = "Branch curvature end", default = 0.0, unit = 'ROTATION')
    branchCurvatureOffsetStrength: bpy.props.FloatProperty(name = "Branch curvature offset", min = 0.0)
            
    showSplitSettings: bpy.props.BoolProperty(name = "Show/hide split settings", default=True)
    
    nrSplitsPerBranch: bpy.props.FloatProperty(name = "Nr splits per branch", default = 0.0, min = 0.0)
    branchSplitMode: bpy.props.PointerProperty(type=splitModeEnumProp)
    branchSplitRotateAngle: bpy.props.FloatProperty(name = "Branch split rotate angle", default = 0.0, unit = 'ROTATION')
    branchSplitAxisVariation: bpy.props.FloatProperty(name = "Branch split axis variation", min = 0.0)
    
    branchSplitAngle: bpy.props.FloatProperty(name = "Branch split angle", min = 0.0, default = 0.0, unit = 'ROTATION')
    branchSplitPointAngle: bpy.props.FloatProperty(name = "Branch split point angle", min = 0.0, default = 0.0, unit = 'ROTATION')
    
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
    showLeafSettings: bpy.props.BoolProperty(name = "Show/hide leaf settings", default = True)
    leavesDensity: bpy.props.FloatProperty(name = "Leaves density", default = 0.0, min = 0.0)
    leafSize: bpy.props.FloatProperty(name = "Leaf size", default = 0.1, min = 0.0)
    leafAspectRatio: bpy.props.FloatProperty(name = "Leaf aspect ratio", default = 1.0, min = 0.0, soft_max = 2.0)
    leafAngleMode: bpy.props.PointerProperty(type = leafAngleModeEnumProp)
    leafType: bpy.props.PointerProperty(type = leafTypeEnumProp)
    leafWhorlCount: bpy.props.IntProperty(name = "Whorl count", default = 3, min = 3)
    leafStartHeightGlobal: bpy.props.FloatProperty(name = "Leaf start height global", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightGlobal: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafStartHeightCluster: bpy.props.FloatProperty(name = "Leaf start height cluster", default = 0.0, min = 0.0, max = 1.0)
    leafEndHeightCluster: bpy.props.FloatProperty(name = "Leaf end height global", default = 1.0, min = 0.0, max = 1.0)
    leafVerticalAngleBranchStart: bpy.props.FloatProperty(name = "Leaf vertical angle branch start", default = 0.0, unit = 'ROTATION')
    leafVerticalAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf vertical angle branch end", default = 0.0, unit = 'ROTATION')
    leafRotateAngleBranchStart: bpy.props.FloatProperty(name = "Leaf rotate angle branch start", default = 0.0, unit = 'ROTATION')
    leafRotateAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf rotate angle branch end", default = 0.0, unit = 'ROTATION')
    leafTiltAngleBranchStart: bpy.props.FloatProperty(name = "Leaf tilt angle branch start", default = 0.0, unit = 'ROTATION')
    leafTiltAngleBranchEnd: bpy.props.FloatProperty(name = "Leaf tilt angle branch end", default = 0.0, unit = 'ROTATION')

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