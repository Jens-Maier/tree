bl_info = {
    "name" : "treeGen3",
    "author" : "Jens", 
    "version" : (0,1),
    "blender" : (4,3,1),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",
}

import bpy
import math
import mathutils


class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default = 0)
    
class addItem(bpy.types.Operator):
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        item = context.scene.myList.add()
        item.value = 1
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        mylist = context.scene.myList
        if len(mylist) > self.index:
            mylist.remove(self.index)
        return {'FINISHED'}
    
class myList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "value", text=f"Item {index}")


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
        
        row.template_list("UL_MyList", "", context.scene, "myList", context.scene, "myListIndex")
        
        row = layout.row(align = True)
        row.operator("scene.add_list_item", text="Add")
        row.operator("scene.remove_list_item", text="Remove").index = context.scene.myListIndex
    
    
        row = layout.row()
        row.label(text = "Tree Generator", icon = 'COLORSET_12_VEC')
        row = layout.row()
        layout.prop(context.scene, "treeHeight")
        row = layout.row()
        layout.prop(context.scene, "treeGrowDir")
        row = layout.row()
        layout.prop(context.scene, "treeShape")
        row = layout.row()
        layout.prop(context.scene, "taper")
        row = layout.row()
        layout.prop(context.scene, "branchTipRadius")
        row = layout.row()
        layout.prop(context.scene, "ringSpacing")
        row = layout.row()
        layout.prop(context.scene, "stemRingResolution")
        row = layout.row()
        layout.prop(context.scene, "resampleNr")
        row = layout.row()
        
        
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
        layout.prop(context.scene, "noiseAmplitudeLower")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeUpper")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeLowerUpperExponent")
        row = layout.row()
        layout.prop(context.scene, "noiseScale")
        
        
class splitSettings(bpy.types.Panel):
    bl_label = "Split Settings"
    bl_idname = "PT_SplitSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        row = layout.row()
        layout.prop(context.scene, "nrSplits")
        row = layout.row()
        layout.prop(context.scene, "splitCurvature")
        row = layout.row()
        layout.prop(context.scene, "testRecursionStop")
        row = layout.row()
        layout.prop(context.scene, "variance")
        row = layout.row()
        layout.prop(context.scene, "stemSplitMode")
        row = layout.row()
        layout.prop(context.scene, "stemSplitRotateAngle")
        row = layout.row()
        layout.prop(context.scene, "curvOffsetStrength")
        row = layout.row()
        layout.prop(context.scene, "splitHeightVariation") 
        row = layout.row()
        layout.prop(context.scene, "stemSplitAngle")
        row = layout.row()
        layout.prop(context.scene, "stemSplitPointAngle")
        row = layout.row()
        
    
        
        
class branchSettings(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_BranchSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        layout.prop(context.scene, "branchClusters")
        
        
            
def register():
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(myList)
    bpy.types.Scene.myList = bpy.props.CollectionProperty(type=intProp)
    bpy.types.Scene.myListIndex = bpy.props.IntProperty(default=0)
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(branchSettings)
    
   
    
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
        min = 0
    )
    bpy.types.Scene.noiseAmplitudeLower = bpy.props.FloatProperty(
        name = "Noise Amplitude Lower",
        description = "Lower bound of noise amplitude",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeUpper = bpy.props.FloatProperty(
        name = "Noise Amplitude Upper",
        description = "Upper bound of noise amplitude",
        default = 0.1,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeLowerUpperExponent = bpy.props.FloatProperty(
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
    bpy.types.Scene.splitCurvature = bpy.props.FloatProperty(
        name = "Split Curvature",
        description = "Curvature of splits",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.shyBranchesMaxDistance = bpy.props.FloatProperty(
        name = "Shy Branches Max Distance",
        description = "Maximum distance for shy branches",
        default = 0.1,
        min = 0.0
    )
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
        min = 0.0
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
            ('TEND_FLAME', "TendFlame", "A more slender flame-shaped tree.")
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
    bpy.types.Scene.resampleNr = bpy.props.IntProperty(
        name = "Resample Nr",
        description = "Number of resamples",
        default = 1,
        min = 1
    )
    bpy.types.Scene.testRecursionStop = bpy.props.IntProperty(
        name = "Test Recursion Stop",
        description = "Recursion stop condition",
        default = 0,
        min = 0
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
            ('rotateAngle', "Rotate Angle", "Split by rotating the angle"),
            ('horizontal', "Horizontal", "Split horizontally"),
        ],
        default='rotateAngle',
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

    # nrBranches
    bpy.types.Scene.nrBranches = bpy.props.IntVectorProperty(
        name="Number of Branches",
        description="Number of branches per level",
        size = 1, # Start with a single element
        default = [3],
        min = 0
    )

    # branchShape
    bpy.types.Scene.branchShape = bpy.props.IntVectorProperty(
        name="Branch Shape",
        description="Shape of the branches",
        size = 1, # Start with a single element
        default = [0],
        min = 0
    )
    # branchSplitMode
    bpy.types.Scene.branchSplitMode = bpy.props.IntVectorProperty(
        name="Branch Split Mode",
        description="Mode for branch splits",
        size = 1, # Start with a single element
        default = [0],
        min = 0
    )
    # branchSplitAngle
    bpy.types.Scene.branchSplitAngle = bpy.props.FloatVectorProperty(
        name="Branch Split Angle",
        description="Angle for branch splits",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # branchSplitPointAngle
    bpy.types.Scene.branchSplitPointAngle = bpy.props.FloatVectorProperty(
        name="Branch Split Point Angle",
        description="Point angle for branch splits",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # branchSplitRotateAngle
    bpy.types.Scene.branchSplitRotateAngle = bpy.props.FloatVectorProperty(
        name="Branch Split Rotate Angle",
        description="Rotation angle for branch splits",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # relBranchLength
    bpy.types.Scene.relBranchLength = bpy.props.FloatVectorProperty(
        name="Relative Branch Length",
        description="Relative length of branches",
        size = 1, # Start with a single element
        default = [1.0],
        min = 0.0
    )
    # taperFactor
    bpy.types.Scene.taperFactor = bpy.props.FloatVectorProperty(
        name="Taper Factor",
        description="Taper factor",
        size = 1, # Start with a single element
        default = [0.1],
        min = 0.0
    )
    # verticalRange
    bpy.types.Scene.verticalRange = bpy.props.FloatVectorProperty(
        name="Vertical Range",
        description="Vertical range",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0
    )
    # verticalAngleCrownStart
    bpy.types.Scene.verticalAngleCrownStart = bpy.props.FloatVectorProperty(
        name="Vertical Angle Crown Start",
        description="Crown start angle",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # verticalAngleCrownEnd
    bpy.types.Scene.verticalAngleCrownEnd = bpy.props.FloatVectorProperty(
        name="Vertical Angle Crown End",
        description="Crown end angle",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # verticalAngleBranchStart
    bpy.types.Scene.verticalAngleBranchStart = bpy.props.FloatVectorProperty(
        name="Vertical Angle Branch Start",
        description="Branch start angle",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # verticalAngleBranchEnd
    bpy.types.Scene.verticalAngleBranchEnd = bpy.props.FloatVectorProperty(
        name="Vertical Angle Branch End",
        description="Branch end angle",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # branchAngleMode
    bpy.types.Scene.branchAngleMode = bpy.props.IntVectorProperty(
        name="Branch Angle Mode",
        description="Branch angle mode",
        size = 1, # Start with a single element
        default = [0],
        min = 0
    )
    # rotateAngle
    bpy.types.Scene.rotateAngle = bpy.props.FloatVectorProperty(
        name="Rotate Angle",
        description="Rotation angle",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # rotateAngleRange
    bpy.types.Scene.rotateAngleRange = bpy.props.FloatVectorProperty(
        name="Rotate Angle Range",
        description="Rotation angle range",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0,
        max = 360.0
    )
    # branchesStartHeightGlobal
    bpy.types.Scene.branchesStartHeightGlobal = bpy.props.FloatVectorProperty(
        name="Branches Start Height Global",
        description="Global start height",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0
    )
    # branchesStartHeightCluster
    bpy.types.Scene.branchesStartHeightCluster = bpy.props.FloatVectorProperty(
        name="Branches Start Height Cluster",
        description="Cluster start height",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0
    )
    # branchesEndHeightGlobal
    bpy.types.Scene.branchesEndHeightGlobal = bpy.props.FloatVectorProperty(
        name="Branches End Height Global",
        description="Global end height",
        size = 1, # Start with a single element
        default = [1.0],
        min = 0.0
    )
    # branchesEndHeightCluster
    bpy.types.Scene.branchesEndHeightCluster = bpy.props.FloatVectorProperty(
        name="Branches End Height Cluster",
        description="Cluster end height",
        size = 1, # Start with a single element
        default = [1.0],
        min = 0.0
    )
    # branchCurvature
    bpy.types.Scene.branchCurvature = bpy.props.FloatVectorProperty(
        name="Branch Curvature",
        description="Branch curvature",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0
    )
    # nrSplitsPerBranch
    bpy.types.Scene.nrSplitsPerBranch = bpy.props.FloatVectorProperty(
        name="Splits Per Branch",
        description="Splits per branch",
        size = 1, # Start with a single element
        default = [1.0],
        min = 0.0
    )
    # splitsPerBranchVariation
    bpy.types.Scene.splitsPerBranchVariation = bpy.props.FloatVectorProperty(
        name="Splits Per Branch Variation",
        description="Variation in splits per branch",
        size = 1, # Start with a single element
        default = [0.0],
        min = 0.0
    )

    #  The List<List<float>> properties (branchSplitHeightInLevel, splitHeightInLevel) are even more complex.

    #  The BoolLstWrapper is not directly translatable.  You'll need to determine what it's doing and
    #  implement a suitable Blender equivalent (likely a list of booleans or something more elaborate
    #  depending on its function).  For now, I'm skipping it, and you'll need to figure out the best
    #  way to represent this data in Blender.

    
    
    
    
def unregister():
    bpy.utils.unregister_class(intProp)
    bpy.utils.unregister_class(addItem)
    bpy.utils.unregister_class(removeItem)
    bpy.utils.unregister_class(myList)
    bpy.utils.unregister_class(addItem)
    bpy.utils.unregister_class(treeGenPanel)
    bpy.utils.unregister_class(noiseSettings)
    bpy.utils.unregister_class(splitSettings)
    
    
    
    
    del bpy.types.Scene.myList
    del bpy.types.Scene.myListIndex
    
    # Unregister the properties.  Important!
    del bpy.types.Scene.treeHeight
    del bpy.types.Scene.treeGrowDir
    del bpy.types.Scene.treeShape
    del bpy.types.Scene.taper
    del bpy.types.Scene.branchTipRadius
    del bpy.types.Scene.ringSpacing
    del bpy.types.Scene.stemRingResolution
    del bpy.types.Scene.resampleNr
    del bpy.types.Scene.noiseAmplitudeLower
    del bpy.types.Scene.noiseAmplitudeUpper
    del bpy.types.Scene.noiseAmplitudeLowerUpperExponent
    del bpy.types.Scene.noiseScale
    del bpy.types.Scene.splitCurvature
    del bpy.types.Scene.testRecursionStop
    del bpy.types.Scene.shyBranchesIterations
    del bpy.types.Scene.shyBranchesMaxDistance
    del bpy.types.Scene.nrSplits
    del bpy.types.Scene.stemSplitMode
    del bpy.types.Scene.stemSplitRotateAngle
    del bpy.types.Scene.variance
    del bpy.types.Scene.curvOffsetStrength
    del bpy.types.Scene.splitHeightVariation
    del bpy.types.Scene.stemSplitAngle
    del bpy.types.Scene.stemSplitPointAngle
    del bpy.types.Scene.branchClusters

    # List properties - Unregister these too.
    del bpy.types.Scene.ringResolution
    del bpy.types.Scene.nrBranches
    del bpy.types.Scene.branchShape
    del bpy.types.Scene.branchSplitMode
    del bpy.types.Scene.branchSplitAngle
    del bpy.types.Scene.branchSplitPointAngle
    del bpy.types.Scene.branchSplitRotateAngle
    del bpy.types.Scene.relBranchLength
    del bpy.types.Scene.taperFactor
    del bpy.types.Scene.verticalRange
    del bpy.types.Scene.verticalAngleCrownStart
    del bpy.types.Scene.verticalAngleCrownEnd
    del bpy.types.Scene.verticalAngleBranchStart
    del bpy.types.Scene.verticalAngleBranchEnd
    del bpy.types.Scene.branchAngleMode
    del bpy.types.Scene.rotateAngle
    del bpy.types.Scene.rotateAngleRange
    del bpy.types.Scene.branchesStartHeightGlobal
    del bpy.types.Scene.branchesStartHeightCluster
    del bpy.types.Scene.branchesEndHeightGlobal
    del bpy.types.Scene.branchesEndHeightCluster
    del bpy.types.Scene.branchCurvature
    del bpy.types.Scene.nrSplitsPerBranch
    del bpy.types.Scene.splitsPerBranchVariation
    
    
if __name__ == "__main__":
    register();