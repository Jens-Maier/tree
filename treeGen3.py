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
from mathutils import Vector

class node():
    def __init__(self, Point, Radius, Tangent, Cotangent, RingResolution):
        self.point = Point
        self.radius = Radius
        self.tangent = Tangent
        self.cotangent = Cotangent
        self.ringResolution = RingResolution
        self.next = None
        
class segment():
    def __init__(self, Start, End, StartTangent, EndTangent, StartCotangent, EndCotangent, StartRadius, EndRadius, RingResolution):
        self.start = Start
        self.end = End
        self.startTangent = StartTangent
        self.endTangent = EndTangent
        self.startCotangent = StartCotangent
        self.endCotangent = EndCotangent
        self.startRadius = StartRadius
        self.endRadius = EndRadius
        self.ringResolution = RingResolution

        
class generateTree(bpy.types.Operator):
    bl_label = "generateTree"
    bl_idname = "object.generate_tree"
    
    def execute(self, context):
        dir = context.scene.treeGrowDir
        height = context.scene.treeHeight
        taper = context.scene.taper
        radius = context.scene.branchTipRadius
        n = context.scene.stemRingResolution
        
        #normals: mesh overlays (only in edit mode) -> Normals
        
        #delete all existing empties
        if context.active_object is not None and context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY':
                    obj.select_set(True)
            bpy.ops.object.delete()
            
            nodes = []
            nodes.append(node(Vector((0.0, 0.0, 0.0)), 0.3, Vector((0.0, 0.0, 1.0)), Vector((1.0, 0.0, 0.0)),   6 ))
            nodes.append(node(dir * height, 0.1, Vector((0.0, 0.0, 1.0)), Vector((1.0, 0.0, 0.0)), 6 ))
            nodes[0].next = nodes[1]
        
            #drawDebugPoint(nodes[0].point)
            #drawDebugPoint(nodes[1].point)
            
            segments = []
            segments = getAllSegments(segments, nodes[0])
            
            generateVerticesAndTriangles(segments, dir, taper, radius, n)
            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
    
def drawDebugPoint(pos, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = 0.1
    bpy.context.active_object.name=name
    
def getAllSegments(segments, activeNode):
    if (activeNode.next != None):
        segments.append(segment(activeNode.point, activeNode.next.point, activeNode.tangent, activeNode.next.tangent, activeNode.cotangent, activeNode.next.cotangent, activeNode.radius, activeNode.next.radius, activeNode.ringResolution))
    
    
    return segments

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
    return (-3.0 * (1.0 - t)**2.0 * controlPt0 + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * controlPt3).normalized()

def lerp(a, b, t):
    return a + (b - a) * t
    
def generateVerticesAndTriangles(segments, dir, taper, radius, n):
    vertices = []
    faces = []
    
    sections = 6 # TEMP !! TODO
    branchRingSpacing = 0.1 # TEMP !! TODO
    
    for segment in segments:
        controlPt1 = segment.start + segment.startTangent.normalized() * (segment.end - segment.start).length / 3.0
        controlPt2 = segment.end - segment.endTangent.normalized() * (segment.end - segment.start).length / 3.0
        length = (segment.end - segment.start).length
            
        for section in range(0, sections): #TODO: sampleSpline...
            pos = sampleSplineC(segment.start, controlPt1, controlPt2, segment.end, section / sections)
            tangent = sampleSplineTangentC(segment.start, controlPt1, controlPt2, segment.end, section / sections).normalized()
            dirA = lerp(segment.startCotangent, segment.endCotangent, section / sections)
            dirB = (tangent.cross(dirA)).normalized()
            dirA = (dirB.cross(tangent)).normalized()
            
            for i in range(n):
                angle = (2 * math.pi * i) / n
                x = math.cos(angle)
                y = math.sin(angle)
                v = pos + dirA * lerp(segment.startRadius, segment.endRadius, section / (length / branchRingSpacing)) * math.cos(angle) + dirB * lerp(segment.startRadius, segment.endRadius, section / (length / branchRingSpacing)) * math.sin(angle)
                vertices.append(v)
                drawDebugPoint(v)
                
            #for i in range(n):
            #    angle = (2 * math.pi * i) / n
            #    x = math.cos(angle)
            #    y = math.sin(angle)
            #    v = segment.end + segment.endCotangent * math.cos(angle) + segment.endTangent.cross(segment.endCotangent) * math.sin(angle)
            #    vertices.append(v)
            #    drawDebugPoint(v)
    
    #TODO...sections!
    for i in range(0, len(segments)):
        for j in range(n):
            faces.append((j, (j + 1) % n, n + (j + 1) % n , n + (j ) % n))
    
    
    #for i in range(1, n):
    #    j = i + 1 if i < n else 1
    #    faces.append((i, i + 1, i + n - 1, i + n))
    
    #vertices.append((0.0,0.0,0.0))
    #for i in range(n):
    #    angle = (2 * math.pi * i) / n
    #    x = math.cos(angle)
    #    y = math.sin(angle)
    #    v = mathutils.Vector((x, y, 0.0))
    #    vertices.append(v)
    #
    #faces = []
    #for i in range(1, n + 1):
    #    j = i + 1 if i < n else 1
    #    faces.append((0, i, j))
        
    meshData = bpy.data.meshes.new("treeMesh")
    meshData.from_pydata(vertices, [], faces)
    meshData.update()
    
    name = "tree"
    if name in bpy.data.objects:
        bpy.data.objects[name].data = meshData
        treeObject = bpy.data.objects[name]
        treeObject.select_set(True)
    else:
        treeObject = bpy.data.objects.new("tree", meshData)
        bpy.context.collection.objects.link(treeObject)
        treeObject.select_set(True)
        

        



class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=10) # reuse for all ints (?)
    
class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0) # reuse for all floats (?)
    
class posFloatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0, min=0)

class floatProp01(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue01", default=0, min=0, max=1)
    
class floatListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "floatListProperty", type=floatProp)
        
class boolProp(bpy.types.PropertyGroup):
    value: bpy.props.BoolProperty(name = "boolValue", default=False)
    
class boolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "boolListProperty", type=boolProp)
    show_cluster: bpy.props.BoolProperty(
        name="Show Cluster",
        description="Show/hide branch cluster",
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
            ('TEND_FLAME', "TendFlame", "A more slender flame-shaped tree.")
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
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.parentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)
    
    
class addSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_split_level"
    bl_label = "Add split level"
    level: bpy.props.IntProperty()
    
    def execute(self, context):
        newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value.add()
        newSplitHeight = 0.5
        return {'FINISHED'}

class removeSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        branchSplitHeightInLevelList = context.scene.branchSplitHeightInLevelListList
        if self.level < len(branchSplitHeightInLevelList):
            branchSplitHeightInLevelList[self.level].value.remove(len(branchSplitHeightInLevelList[self.level].value) - 1)
                        
        print("remove split level")
        return {'FINISHED'}
    
class addItem(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.branchClusters += 1
        
        nrBranches = context.scene.nrBranchesList.add()
        nrBranches.value = 2       # default for nrBranches!
        
        parentClusterBoolListList = context.scene.parentClusterBoolListList.add()
        for b in range(0, context.scene.branchClusters):
            parentClusterBoolListList.value.add()
        parentClusterBoolListList.value[0].value = True
                
        branchSplitMode = context.scene.branchSplitModeList.add()  # TODO (???)
        branchSplitRotateAngle = context.scene.branchSplitRotateAngleList.add()
        branchSplitRotateAngle.value = 0.0
        branchSplitAngle = context.scene.branchSplitAngleList.add()
        branchSplitAngle.value = 0.0
        branchSplitPointAngle = context.scene.branchSplitPointAngleList.add()
        branchSplitPointAngle.value = 0.0
        branchShape = context.scene.branchShapeList.add()
        relBranchLength = context.scene.relBranchLengthList.add()
        relBranchLength.value = 1.0
        taperFactor = context.scene.taperFactorList.add()
        taperFactor.value = 1.0
        #verticalRange = context.scene.verticalRangeList.add()
        #verticalRange.value = 0.0
        verticalAngleCrownStart = context.scene.verticalAngleCrownStartList.add()
        verticalAngleCrownStart.value = 0.0
        verticalAngleCrownEnd = context.scene.verticalAngleCrownEndList.add()
        verticalAngleCrownEnd.value = 0.0
        verticalAngleBranchStart = context.scene.verticalAngleBranchStartList.add()
        verticalAngleBranchStart.value = 0.0
        verticalAngleBranchEnd = context.scene.verticalAngleBranchEndList.add()
        verticalAngleBranchEnd.value = 0.0
        branchAngleMode = context.scene.branchAngleModeList.add()
        rotateAngle = context.scene.rotateAngleList.add()
        rotateAngle.value = 0.0
        rotateAngleRange = context.scene.rotateAngleRangeList.add()
        rotateAngleRange.value = 0.0
        branchesStartHeightGlobal = context.scene.branchesStartHeightGlobalList.add()
        branchesStartHeightGlobal.value = 0.0
        branchesEndHeightGlobal = context.scene.branchesEndHeightGlobalList.add()
        branchesEndHeightGlobal.value = 1.0
        branchesStartHeightCluster = context.scene.branchesStartHeightClusterList.add()
        branchesStartHeightCluster.value = 0.0
        branchesEndHeightCluster = context.scene.branchesEndHeightClusterList.add()
        branchesEndHeightCluster.value = 1.0
        branchCurvature = context.scene.branchCurvatureList.add()
        branchCurvature.value = 0.0
        nrSplitsPerBranch = context.scene.nrSplitsPerBranchList.add()
        nrSplitsPerBranch.value = 0.0
        splitsPerBranchVariation = context.scene.splitsPerBranchVariationList.add()
        splitsPerBranchVariation.value = 0.0
        branchSplitHeightVariation = context.scene.branchSplitHeightVariationList.add()
        branchSplitHeightVariation.value = 0.0
        branchSplitHeightInLevelListListItem = context.scene.branchSplitHeightInLevelListList.add()
        
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        context.scene.branchClusters -= 1
        
        if len(context.scene.parentClusterBoolListList) > 0:
            listToClear = context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value
            lenToClear = len(listToClear)
            for i in range(0, lenToClear):
                context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value.remove(len(context.scene.parentClusterBoolListList[i].value) - 1)
            context.scene.parentClusterBoolListList.remove(len(context.scene.parentClusterBoolListList) - 1)
        
        
        context.scene.branchSplitModeList.remove(len(context.scene.branchSplitModeList) - 1)
        context.scene.branchSplitRotateAngleList.remove(len(context.scene.branchSplitRotateAngleList) - 1)
        context.scene.branchSplitAngleList.remove(len(context.scene.branchSplitAngleList) - 1)
        context.scene.branchSplitPointAngleList.remove(len(context.scene.branchSplitPointAngleList) - 1)
        context.scene.branchShapeList.remove(len(context.scene.branchShapeList) - 1)
        context.scene.relBranchLengthList.remove(len(context.scene.relBranchLengthList) - 1)
        context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
        #context.scene.verticalRangeList.remove(len(context.scene.verticalRangeList) - 1)
        context.scene.verticalAngleCrownStartList.remove(len(context.scene.verticalAngleCrownStartList) - 1)
        context.scene.verticalAngleCrownEndList.remove(len(context.scene.verticalAngleCrownEndList) - 1)
        context.scene.verticalAngleBranchStartList.remove(len(context.scene.verticalAngleBranchStartList) - 1)
        context.scene.verticalAngleBranchEndList.remove(len(context.scene.verticalAngleBranchEndList) - 1)
        context.scene.branchAngleModeList.remove(len(context.scene.branchAngleModeList) - 1)
        context.scene.rotateAngleList.remove(len(context.scene.rotateAngleList) - 1)
        context.scene.branchesStartHeightGlobalList.remove(len(context.scene.branchesStartHeightGlobalList) - 1)
        context.scene.branchesEndHeightGlobalList.remove(len(context.scene.branchesEndHeightGlobalList) - 1)
        context.scene.branchesStartHeightClusterList.remove(len(context.scene.branchesStartHeightClusterList) - 1)
        context.scene.branchesEndHeightClusterList.remove(len(context.scene.branchesEndHeightClusterList) - 1)
        context.scene.branchCurvatureList.remove(len(context.scene.branchCurvatureList) - 1)
        context.scene.nrSplitsPerBranchList.remove(len(context.scene.nrSplitsPerBranchList) - 1)
        context.scene.splitsPerBranchVariationList.remove(len(context.scene.splitsPerBranchVariationList) - 1)
        context.scene.branchSplitHeightVariationList.remove(len(context.scene.branchSplitHeightVariationList) - 1)
        context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
            
        if len(context.scene.nrBranchesList) > 0:
            context.scene.nrBranchesList.remove(len(context.scene.nrBranchesList) - 1)
        
        return {'FINISHED'}
    
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
            
        row = layout.row()
        row.label(text = "Tree Generator", icon = 'COLORSET_12_VEC')
        row = layout.row()
        layout.operator("object.generate_tree", text="Generate Tree")
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
        layout.prop(context.scene, "treeShapeEnumProp")
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
        #layout.prop(context.scene, "stemSplitMode")
        split = row.split(factor=0.5)
        split.label(text="Stem split mode")
        split.prop(context.scene, "stemSplitMode", text="")
        
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
            
        op = split.operator("scene.toggle_bool", text="", depress=boolItem.value) # github copilot...
        op.list_index = cluster_index
        op.bool_index = j
        

        
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
        row.operator("scene.remove_list_item", text="Remove").index = context.scene.nrBranchesListIndex
    
        for i, outer in enumerate(scene.parentClusterBoolListList):
            box = layout.box()
            box.label(text=f"Branch cluster {i}")
            
            row = box.row()
            
            row.prop(outer, "show_cluster", icon="TRIA_DOWN" if outer.show_cluster else "TRIA_RIGHT",
                emboss=False, text=f"Parent clusters", toggle=True)
            
            if outer.show_cluster:
                if i < len(context.scene.nrBranchesList):
                    
                    box1 = box.box()
                    draw_parent_cluster_bools(box1, scene, i) #FUNKT!
                    
                    parentClusterBoolListList = context.scene.parentClusterBoolListList
                    
            
            ##########################################################################################
            
            if i < len(scene.nrBranchesList):
                split = box.split(factor=0.6)
                split.label(text="Number of branches")
                split.prop(scene.nrBranchesList[i], "value", text="")#, slider=True)
                
            #row = layout.row()
            #split = row.split(factor=0.6)
            split = box.split(factor=0.6)
            split.label(text="Branch split mode")
            if i < len(scene.branchSplitModeList):
                split.prop(scene.branchSplitModeList[i], "value", text="")
            
                if scene.branchSplitModeList[i].value == 'ROTATE_ANGLE':
                    split = box.split(factor=0.6)
                    split.label(text="Branch split rotate angle")
                    if i < len(scene.branchSplitRotateAngleList):
                        split.prop(scene.branchSplitRotateAngleList[i], "value", text="")
            
            if i < len(scene.branchSplitAngleList):
                split = box.split(factor=0.6)
                split.label(text="Branch split angle")
                split.prop(scene.branchSplitAngleList[i], "value", text="")
            
            if i < len(scene.branchSplitPointAngleList):
                split = box.split(factor=0.6)
                split.label(text="Branch split point angle")
                split.prop(scene.branchSplitPointAngleList[i], "value", text="")
            
            if i < len(scene.branchShapeList):
                split = box.split(factor=0.6)
                split.label(text="Branch shape")
                split.prop(scene.branchShapeList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Relative branch length")
            if i < len(scene.relBranchLengthList):
                split.prop(scene.relBranchLengthList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Taper factor")
            if i < len(scene.taperFactorList):
                split.prop(scene.taperFactorList[i], "value", text="", slider=True)
                
            #split = box.split(factor=0.6)
            #split.label(text="Vertical range")
            #split.prop(scene.verticalRangeList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Vertical angle crown start")
            if i < len(scene.verticalAngleCrownStartList):
                split.prop(scene.verticalAngleCrownStartList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Vertical angle crown end")
            if i < len(scene.verticalAngleCrownEndList):
                split.prop(scene.verticalAngleCrownEndList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Vertical angle branch start")
            if i < len(scene.verticalAngleBranchStartList):
                split.prop(scene.verticalAngleBranchStartList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Vertical angle branch end")
            if i < len(scene.verticalAngleBranchEndList):
                split.prop(scene.verticalAngleBranchEndList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Branch angle mode")
            if i < len(scene.branchAngleModeList):
                split.prop(scene.branchAngleModeList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Rotate angle")
            if i < len(scene.rotateAngleList):
                split.prop(scene.rotateAngleList[i], "value", text="")
            
            if i < len(scene.branchAngleModeList):
                if scene.branchAngleModeList[i].value == 'WINDING':
                    split = box.split(factor=0.6)
                    split.label(text="Rotate angle range")
                    split.prop(scene.rotateAngleRangeList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Branches start height global")
            if i < len(scene.branchesStartHeightGlobalList):
                split.prop(scene.branchesStartHeightGlobalList[i], "value", text="")
        
            split = box.split(factor=0.6)
            split.label(text="Branches end height global")
            if i < len(scene.branchesEndHeightGlobalList):
                split.prop(scene.branchesEndHeightGlobalList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Branches start height cluster")
            if i < len(scene.branchesStartHeightClusterList):
                split.prop(scene.branchesStartHeightClusterList[i], "value", text="")
        
            split = box.split(factor=0.6)
            split.label(text="Branches end height cluster")
            if i < len(scene.branchesEndHeightClusterList):
                split.prop(scene.branchesEndHeightClusterList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Branch curvature")
            if i < len(scene.branchCurvatureList):
                split.prop(scene.branchCurvatureList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Nr splits per branch")
            if i < len(scene.nrSplitsPerBranchList):
                split.prop(scene.nrSplitsPerBranchList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Splits per branch variation")
            if i < len(scene.splitsPerBranchVariationList):
                split.prop(scene.splitsPerBranchVariationList[i], "value", text="")
            
            split = box.split(factor=0.6)
            split.label(text="Branch split height variation")
            if i < len(scene.branchSplitHeightVariationList):
                split.prop(scene.branchSplitHeightVariationList[i], "value", text="")
            
            box.operator("scene.add_split_level", text="Add split level").level = i
            box.operator("scene.remove_split_level", text="Remove split level").level = i
            if i < len(scene.branchSplitHeightInLevelListList):
                j = 0
                for splitLevel in scene.branchSplitHeightInLevelListList[i].value:
                    box.prop(splitLevel, "value", text=f"Split height level {j}")
                    j += 1
            
            
def register():
    #properties
    bpy.utils.register_class(treeShapeEnumProp)
    bpy.utils.register_class(splitModeEnumProp)
    bpy.utils.register_class(angleModeEnumProp)
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(floatProp)
    bpy.utils.register_class(posFloatProp)
    bpy.utils.register_class(floatProp01)
    bpy.utils.register_class(floatListProp)
    bpy.utils.register_class(boolProp)
    bpy.utils.register_class(boolListProp)
    
    #operators
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(addSplitLevel)
    bpy.utils.register_class(removeSplitLevel)
    bpy.utils.register_class(generateTree)
    
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(branchSettings)
    #bpy.utils.register_class(parentClusterPanel)
          
    #collections
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.parentClusterBoolListList = bpy.props.CollectionProperty(type=boolListProp)
    bpy.types.Scene.nrBranchesList = bpy.props.CollectionProperty(type=intProp)
    bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    bpy.types.Scene.branchSplitModeList = bpy.props.CollectionProperty(type=splitModeEnumProp)
    bpy.types.Scene.branchSplitRotateAngleList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitAngleList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitPointAngleList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchShapeList = bpy.props.CollectionProperty(type=treeShapeEnumProp)
    bpy.types.Scene.relBranchLengthList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.verticalRangeList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchAngleModeList = bpy.props.CollectionProperty(type=angleModeEnumProp)
    bpy.types.Scene.rotateAngleList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.rotateAngleRangeList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchesStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchesEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchesStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchesEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchCurvatureList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.nrSplitsPerBranchList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp)
        
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
    ## verticalRange # not used (for now)
    #bpy.types.Scene.verticalRange = bpy.props.FloatVectorProperty(
    #    name="Vertical Range",
    #    description="Vertical range",
    #    size = 1, # Start with a single element
    #    default = [0.0],
    #    min = 0.0
    #)
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

    
    
    
    
def unregister():
    
    #properties
    bpy.utils.unregister_class(treeShapeEnumProp)
    #bpy.utils.unregister_class(splitModeEnumProp)
    #bpy.utils.unregister_class(angleModeEnumProp)
    #bpy.utils.unregister_class(intProp)
    #bpy.utils.unregister_class(floatProp)
    #bpy.utils.unregister_class(posFloatProp)
    #bpy.utils.unregister_class(floatProp01)
    #bpy.utils.unregister_class(floatListProp)
    #bpy.utils.unregister_class(boolProp)
    #bpy.utils.unregister_class(boolListProp)
    
    
    #operators
    #bpy.utils.unregister_class(addItem)
    #bpy.utils.unregister_class(removeItem)
    #bpy.utils.unregister_class(addSplitLevel)
    #bpy.utils.unregister_class(removeSplitLevel)
    #bpy.utils.unregister_class(addParentCluster)
    #bpy.utils.unregister_class(removeParentCluster)
    
    #panels
    #bpy.utils.unregister_class(treeGenPanel)
    #bpy.utils.unregister_class(noiseSettings)
    #bpy.utils.unregister_class(splitSettings)
    #bpy.utils.unregister_class(branchSettings)
    
        
    #del bpy.types.Scene.nrBranchesList
    #del bpy.types.Scene.nrBranchesListIndex
    #del bpy.types.Scene.treeShape
    
    
    # Unregister the properties.  Important!
    #del bpy.types.Scene.treeHeight
    #del bpy.types.Scene.treeGrowDir
    #del bpy.types.Scene.treeShape
    #del bpy.types.Scene.taper
    #del bpy.types.Scene.branchTipRadius
    #del bpy.types.Scene.ringSpacing
    #del bpy.types.Scene.stemRingResolution
    #del bpy.types.Scene.resampleNr
    #del bpy.types.Scene.noiseAmplitudeLower
    #del bpy.types.Scene.noiseAmplitudeUpper
    #del bpy.types.Scene.noiseAmplitudeLowerUpperExponent
    #del bpy.types.Scene.noiseScale
    #del bpy.types.Scene.splitCurvature
    #del bpy.types.Scene.testRecursionStop
    #del bpy.types.Scene.shyBranchesIterations
    #del bpy.types.Scene.shyBranchesMaxDistance
    #del bpy.types.Scene.nrSplits
    #del bpy.types.Scene.stemSplitMode
    #del bpy.types.Scene.stemSplitRotateAngle
    #del bpy.types.Scene.variance
    #del bpy.types.Scene.curvOffsetStrength
    #del bpy.types.Scene.splitHeightVariation
    #del bpy.types.Scene.stemSplitAngle
    #del bpy.types.Scene.stemSplitPointAngle
    #del bpy.types.Scene.branchClusters

    # List properties - Unregister these too.
    #del bpy.types.Scene.nrBranchesList
    #del bpy.types.Scene.nrBranchesListIndex
    #
    #del bpy.types.Scene.ringResolution #todo
    #del bpy.types.Scene.branchShapeList
    #del bpy.types.Scene.branchSplitModeList
    #del bpy.types.Scene.branchSplitAngleList
    #del bpy.types.Scene.branchSplitPointAngleList
    #del bpy.types.Scene.branchSplitRotateAngle
    #del bpy.types.Scene.relBranchLengthList
    #del bpy.types.Scene.taperFactorList
    ##del bpy.types.Scene.verticalRangeList
    #del bpy.types.Scene.verticalAngleCrownStartList
    #del bpy.types.Scene.verticalAngleCrownEndList
    #del bpy.types.Scene.verticalAngleBranchStartList
    #del bpy.types.Scene.verticalAngleBranchEndList
    #del bpy.types.Scene.branchAngleModeList
    #del bpy.types.Scene.rotateAngleList
    #del bpy.types.Scene.rotateAngleRangeList
    #del bpy.types.Scene.branchesStartHeightGlobalList
    #del bpy.types.Scene.branchesStartHeightCluster
    #del bpy.types.Scene.branchesEndHeightGlobalList
    #del bpy.types.Scene.branchesEndHeightCluster
    #del bpy.types.Scene.branchCurvatureList
    #del bpy.types.Scene.nrSplitsPerBranchList
    #del bpy.types.Scene.splitsPerBranchVariationList
    #del bpy.types.Scene.branchSplitHeightVariationList
    #del bpy.types.Scene.branchSplitHeightInLevelListList
    
if __name__ == "__main__":
    register();