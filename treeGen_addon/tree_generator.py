import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import bmesh

from .noise_generator import SimplexNoiseGenerator

from .node_ import node
from .segment_ import segment
from .treegen_utils_ import treegen_utils
from .start_point_data import StartPointData
from .start_point_data import DummyStartPointData


class treeGenerator:
    def __init__():
        pass
    
    def generate_tree(self, context):
        dir = context.scene.treeSettings.treeGrowDir
        height = context.scene.treeSettings.treeHeight
        taper = context.scene.treeSettings.taper
        radius = context.scene.treeSettings.branchTipRadius
        stemRingRes = context.scene.treeSettings.stemRingResolution
        
        context.scene.treeSettings.maxSplitHeightUsed = 0
        
        context.scene.treeSettings.seed += 1
        noise_generator = SimplexNoiseGenerator(self, context.scene.treeSettings.seed)
        
        if context.active_object is None:
            treeMesh = bpy.data.meshes.new("treeMesh")
            treeObject = bpy.data.objects.new("tree", treeMesh)
            context.collection.objects.link(treeObject)
            bpy.context.view_layer.objects.active = bpy.data.objects["tree"]
        
        if context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            
            nodes = []
            nodeTangents = []
            nodeTangents.append(Vector((0.0,0.0,1.0)))
            nodes.append(node(Vector((0.0,0.0,0.0)), 0.1, Vector((1.0,0.0,0.0)), -1, context.scene.treeSettings.stemRingResolution, context.scene.treeSettings.taper, 0.0, 0.0, height))
            nodes[0].tangent.append(Vector((0.0,0.0,1.0)))
            nodes[0].cotangent = Vector((1.0,0.0,0.0))
            nodes.append(node(dir * height, 0.1, Vector((1.0,0.0,0.0)), -1, context.scene.treeSettings.stemRingResolution, context.scene.treeSettings.taper, 1.0, 0.0, height))
            nodes[1].tangent.append(Vector((0.0,0.0,1.0)))
            nodes[1].cotangent = Vector((1.0,0.0,0.0))
            nodes[0].next.append(nodes[1])
            nodes[0].outwardDir.append(nodes[0].cotangent)
            nodes[0].rotateAngleRange.append(math.pi)
            nodes[1].outwardDir.append(nodes[0].cotangent)
            nodes[1].rotateAngleRange.append(math.pi)
            
            if context.scene.treeSettings.nrSplits > 0:
                maxSplitHeightUsed = treeGenerator.splitRecursive(nodes[0], 
                                                    context.scene.treeSettings.nrSplits, 
                                                    context.scene.treeSettings.stemSplitAngle, 
                                                    context.scene.treeSettings.stemSplitPointAngle, 
                                                    context.scene.treeSettings.variance, 
                                                    context.scene.treeSettings.stemSplitHeightInLevelList, 
                                                    context.scene.treeSettings.splitHeightVariation, 
                                                    context.scene.treeSettings.splitLengthVariation, 
                                                    context.scene.treeSettings.stemSplitMode, 
                                                    context.scene.treeSettings.stemSplitRotateAngle, 
                                                    nodes[0], 
                                                    context.scene.treeSettings.stemRingResolution, 
                                                    context.scene.treeSettings.curvOffsetStrength, self, nodes[0])
                self.report({'INFO'}, f"maxSplitHeightUsed: {maxSplitHeightUsed}")
                context.scene.treeSettings.maxSplitHeightUsed = max(context.scene.treeSettings.maxSplitHeightUsed, maxSplitHeightUsed)
            
            nodes[0].resampleSpline(nodes[0], context.scene.treeSettings.resampleDistance)
            
            nodes[0].applyCurvature(self,
                                    nodes[0], 
                                    context.scene.treeSettings.treeGrowDir, 
                                    context.scene.treeSettings.treeHeight, 
                                    context.scene.treeSettings.curvatureStart / context.scene.treeSettings.resampleDistance, 
                                    0.0, 
                                    context.scene.treeSettings.curvatureEnd / context.scene.treeSettings.resampleDistance, 
                                    0.0, 
                                    -1, 
                                    Vector((0.0,0.0,0.0)),
                                    0.0,
                                    0.0)
                                    
            if context.scene.treeSettings.noiseAmplitudeHorizontal > 0.0 or context.scene.treeSettings.noiseAmplitudeVertical > 0.0:
                nodes[0].applyNoise(self, 
                                    noise_generator, 
                                    context.scene.treeSettings.noiseAmplitudeHorizontal,
                                    context.scene.treeSettings.noiseAmplitudeVertical, 
                                    context.scene.treeSettings.noiseAmplitudeGradient, 
                                    context.scene.treeSettings.noiseAmplitudeExponent, 
                                    context.scene.treeSettings.noiseScale, 
                                    nodes[0].point - (nodes[0].next[0].point - nodes[0].point), 
                                    context.scene.treeSettings.treeHeight)
            
            #nodes[0].drawTangentArrows(self)
                        
            if context.scene.treeSettings.branchClusters > 0:
                treeGenerator.addBranches(
                self, 
                self, 
                context.scene.treeSettings.resampleDistance,
                
                context,
                nodes[0], 
                context.scene.treeSettings.branchClusters,
                
                context.scene.branchClusterSettingsList,
                
                context.scene.treeSettings.parentClusterBoolListList, 
                
                context.scene.treeSettings.treeGrowDir, 
                context.scene.treeSettings.treeHeight,
                
                context.scene.treeSettings.taper, 
                context.scene.taperFactorList, 
                
                context.scene.treeSettings.branchSplitHeightInLevelList_0, 
                context.scene.treeSettings.branchSplitHeightInLevelList_1, 
                context.scene.treeSettings.branchSplitHeightInLevelList_2, 
                context.scene.treeSettings.branchSplitHeightInLevelList_3, 
                context.scene.treeSettings.branchSplitHeightInLevelList_4, 
                context.scene.treeSettings.branchSplitHeightInLevelList_5, 
                context.scene.treeSettings.branchSplitHeightInLevelList_6, 
                context.scene.treeSettings.branchSplitHeightInLevelList_7, 
                context.scene.treeSettings.branchSplitHeightInLevelList_8, 
                context.scene.treeSettings.branchSplitHeightInLevelList_9, 
                context.scene.treeSettings.branchSplitHeightInLevelList_10, 
                context.scene.treeSettings.branchSplitHeightInLevelList_11, 
                context.scene.treeSettings.branchSplitHeightInLevelList_12, 
                context.scene.treeSettings.branchSplitHeightInLevelList_13, 
                context.scene.treeSettings.branchSplitHeightInLevelList_14, 
                context.scene.treeSettings.branchSplitHeightInLevelList_15, 
                context.scene.treeSettings.branchSplitHeightInLevelList_16, 
                context.scene.treeSettings.branchSplitHeightInLevelList_17, 
                context.scene.treeSettings.branchSplitHeightInLevelList_18, 
                context.scene.treeSettings.branchSplitHeightInLevelList_19, 
                
                context.scene.branchSplitHeightInLevelListList,
                
                noise_generator)
              
            calculateRadius(self, nodes[0], 100.0, context.scene.treeSettings.branchTipRadius)
            segments = []
            nodes[0].getAllSegments(self, nodes[0], segments, False)
            
            addLeaves(self, self, nodes[0], 
                context.scene.treeSettings.treeGrowDir, 
                context.scene.treeSettings.treeHeight, 
                context.scene.leafClusterSettingsList,
                context.scene.treeSettings.leafParentClusterBoolListList, 
                context.scene.leaf_material)
            
            generateVerticesAndTriangles(self, self, context, 
                segments, 
                dir, 
                context.scene.treeSettings.taper, 
                radius, 
                context.scene.treeSettings.ringSpacing, 
                context.scene.treeSettings.stemRingResolution, 
                context.scene.taperFactorList, 
                context.scene.treeSettings.branchTipRadius, 
                context.scene.bark_material)
            
            if len(context.scene.treeSettings.stemSplitHeightInLevelList) > context.scene.treeSettings.maxSplitHeightUsed + 1:
                for i in range(context.scene.treeSettings.maxSplitHeightUsed + 1, len(context.scene.treeSettings.stemSplitHeightInLevelList)):
                    context.scene.treeSettings.stemSplitHeightInLevelList.remove(len(context.scene.treeSettings.stemSplitHeightInLevelList) - 1)
                    
            if len(context.scene.treeSettings.stemSplitHeightInLevelList) < context.scene.treeSettings.maxSplitHeightUsed + 1:
                for i in range(context.scene.treeSettings.maxSplitHeightUsed + 1, len(context.scene.treeSettings.stemSplitHeightInLevelList)):
                    h = context.scene.treeSettings.stemSplitHeightInLevelList.add()
                    
            
            if len(context.scene.branchClusterSettingsList) > 0:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_0) > context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_0)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_0.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_0) - 1)
                    
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_0) < context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_0)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_0.add()
                  
                  
            if len(context.scene.branchClusterSettingsList) > 1:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_1) > context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_1)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_1.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_1) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_1) < context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_1)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_1.add()
              
            
            if len(context.scene.branchClusterSettingsList) > 2:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_2) > context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_2)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_2.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_2) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_2) < context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_2)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_2.add()
            
            if len(context.scene.branchClusterSettingsList) > 3:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_3) > context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_3)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_3.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_3) - 1)
                
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_3) < context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_3)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_3.add()
              
            if len(context.scene.branchClusterSettingsList) > 4:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_4) > context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_4)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_4.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_4) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_4) < context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_4)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_4.add()
              
            if len(context.scene.branchClusterSettingsList) > 5:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_5) > context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_5)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_5.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_5) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_5) < context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_5)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_5.add()
            
            if len(context.scene.branchClusterSettingsList) > 6:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_6) > context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_6)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_6.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_6) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_6) < context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_6)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_6.add()
            
            if len(context.scene.branchClusterSettingsList) > 7:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_7) > context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_7)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_7.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_7) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_7) < context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_7)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_7.add()
            
            if len(context.scene.branchClusterSettingsList) > 8:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_8) > context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_8)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_8.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_8) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_8) < context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_8)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_8.add()
            
            if len(context.scene.branchClusterSettingsList) > 9:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_9) > context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_9)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_9.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_9) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_9) < context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_9)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_9.add()
            
            if len(context.scene.branchClusterSettingsList) > 10:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_10) > context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_10)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_10.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_10) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_10) < context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_10)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_10.add()
            
            if len(context.scene.branchClusterSettingsList) > 11:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_11) > context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_11)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_11.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_11) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_11) < context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_11)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_11.add()
            
            if len(context.scene.branchClusterSettingsList) > 12:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_12) > context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_12)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_12.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_12) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_12) < context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_12)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_12.add()
            
            if len(context.scene.branchClusterSettingsList) > 13:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_13) > context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_13)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_13.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_13) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_13) < context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_13)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_13.add()
            
            if len(context.scene.branchClusterSettingsList) > 14:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_14) > context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_14)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_14.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_14) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_14) < context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_14)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_14.add()
            
            if len(context.scene.branchClusterSettingsList) > 15:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_15) > context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_15)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_15.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_15) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_15) < context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_15)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_15.add()
            
            if len(context.scene.branchClusterSettingsList) > 16:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_16) > context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_16)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_16.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_16) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_16) < context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_16)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_16.add()
            
            if len(context.scene.branchClusterSettingsList) > 17:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_17) > context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_17)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_17.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_17) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_17) < context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_17)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_17.add()
            
            if len(context.scene.branchClusterSettingsList) > 18:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_18) > context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_18)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_18.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_18) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_18) < context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_18)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_18.add()
            
            if len(context.scene.branchClusterSettingsList) > 19:
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_19) > context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_19)):
                        context.scene.treeSettings.branchSplitHeightInLevelList_19.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_19) - 1)
            
                if len(context.scene.treeSettings.branchSplitHeightInLevelList_19) < context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1:
                    for i in range(context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1, len(context.scene.treeSettings.branchSplitHeightInLevelList_19)):
                        h = context.scene.treeSettings.branchSplitHeightInLevelList_19.add()
            
    
    def splitRecursive(startNode, 
                       nrSplits, 
                       splitAngle, 
                       splitPointAngle, 
                       variance, 
                       splitHeightInLevel, 
                       splitHeightVariation, 
                       splitLengthVariation, 
                       stemSplitMode, 
                       stemSplitRotateAngle, 
                       root_node, 
                       stemRingResolution, 
                       curvOffsetStrength, 
                       self, 
                       rootNode):
        self.report({'INFO'}, f"nrSplits: {nrSplits}")
        while len(splitHeightInLevel) < nrSplits:
            newHeight = splitHeightInLevel.add()
            newHeight.value = 0.5
        
        minSegments = math.ceil(math.log(nrSplits + 1, 2))
    
        splitProbabilityInLevel = [0.0] * nrSplits
        expectedSplitsInLevel = [0] * nrSplits
        
        meanLevel = int(math.log(nrSplits, 2))
        if meanLevel == 0:
            meanLevel = 1
        if nrSplits > 0:
            splitProbabilityInLevel[0] = 1.0
            expectedSplitsInLevel[0] = 1
        else:
            splitProbabilityInLevel[0] = 0.0
            expectedSplitsInLevel[0] = 0
    
        for i in range(1, int(round(meanLevel - variance * meanLevel))):
            splitProbabilityInLevel[i] = 1.0
            expectedSplitsInLevel[i] = int(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
    
        if int(round(meanLevel - variance * meanLevel)) > 0:
            for i in range(int(round(meanLevel - variance * meanLevel)), int(round(meanLevel + variance * meanLevel))):
                splitProbabilityInLevel[i] = 1.0 - (7.0 / 8.0) * (i - int(round(meanLevel - variance * meanLevel))) / (
                    round(meanLevel + variance * meanLevel) - round(meanLevel - variance * meanLevel))
                expectedSplitsInLevel[i] = int(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
            for i in range(int(round(meanLevel + variance * meanLevel)), nrSplits):
                splitProbabilityInLevel[i] = 1.0 / 8.0
                expectedSplitsInLevel[i] = int(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
    
        if nrSplits == 2:
            expectedSplitsInLevel[0] = 1
            expectedSplitsInLevel[1] = 1
    
        addToLevel = 0
        maxPossibleSplits = 1
        totalExpectedSplits = 0
        for i in range(nrSplits):
            totalExpectedSplits += expectedSplitsInLevel[i]
            if expectedSplitsInLevel[i] < maxPossibleSplits:
                addToLevel = i
                break
            maxPossibleSplits *= 2
        addAmount = nrSplits - totalExpectedSplits
        
        if addAmount > 0: 
            expectedSplitsInLevel[addToLevel] += min(addAmount, maxPossibleSplits - expectedSplitsInLevel[addToLevel])
    
        splitProbabilityInLevel[addToLevel] = float(expectedSplitsInLevel[addToLevel]) / float(maxPossibleSplits)
    
        nodesInLevelNextIndex = [[] for _ in range(nrSplits + 1)]
        for n in range(len(startNode.next)):
            nodesInLevelNextIndex[0].append((startNode, n))
            
        maxSplitHeightUsed = 0
    
        totalSplitCounter = 0
        for level in range(nrSplits):
            splitsInLevel = 0
            safetyCounter = 0
    
            nodeIndices = list(range(len(nodesInLevelNextIndex[level])))
    
            while splitsInLevel < expectedSplitsInLevel[level]:
                if not nodeIndices:
                    break
                if totalSplitCounter == nrSplits:
                    break
                r = random.random()
                h = random.random() - 0.5
                if r <= splitProbabilityInLevel[level]:
                    indexToSplit = random.randint(0, len(nodeIndices) - 1)
                    if len(nodeIndices) > indexToSplit:
                        splitHeight = splitHeightInLevel[level].value
                        if h * splitHeight < 0:
                            splitHeight = max(splitHeight + h * splitHeightVariation, 0.05)
                        else:
                            splitHeight = min(splitHeight + h * splitHeightVariation, 0.95)
                        
                        maxSplitHeightUsed = max(maxSplitHeightUsed, level)
                        splitNode = split(
                            nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0],
                            nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][1],
                            splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, stemSplitMode, stemSplitRotateAngle, 0.0, stemRingResolution, curvOffsetStrength, self, rootNode)
                        
                        nodeIndices.pop(indexToSplit)
                        nodesInLevelNextIndex[level + 1].append((splitNode, 0))
                        nodesInLevelNextIndex[level + 1].append((splitNode, 1))
                        splitsInLevel += 1
                        totalSplitCounter += 1
                safetyCounter += 1
                if safetyCounter > 100:
                    self.report({'INFO'}, f"iteration 100 reached -> break!")
                    break
        return maxSplitHeightUsed

    
    
    def addBranches(
        self, 
        treeGen, 
        resampleDistance,
        
        context,
        rootNode, 
        branchClusters,
        
        branchClusterSettingsList,
        
        parentClusterBoolListList, 
        
        treeGrowDir, 
        treeHeight, 
        taper, 
        taperFactorList, 
        
        branchSplitHeightInLevel, #==branchSplitHeightInLevelList_0
        branchSplitHeightInLevelList_1,
        branchSplitHeightInLevelList_2,
        branchSplitHeightInLevelList_3,
        branchSplitHeightInLevelList_4,
        branchSplitHeightInLevelList_5, 
        branchSplitHeightInLevelList_6, 
        branchSplitHeightInLevelList_7, 
        branchSplitHeightInLevelList_8, 
        branchSplitHeightInLevelList_9, 
        branchSplitHeightInLevelList_10, 
        branchSplitHeightInLevelList_11, 
        branchSplitHeightInLevelList_12, 
        branchSplitHeightInLevelList_13, 
        branchSplitHeightInLevelList_14, 
        branchSplitHeightInLevelList_15, 
        branchSplitHeightInLevelList_16, 
        branchSplitHeightInLevelList_17, 
        branchSplitHeightInLevelList_18, 
        branchSplitHeightInLevelList_19, 
        
        branchSplitHeightInLevelListList,
        noiseGenerator):
    
            treeGen.report({'INFO'}, f"in addBranches(): branchClusters: {branchClusters}")
            
            for clusterIndex in range(0, branchClusters):
                nrBranches = branchClusterSettingsList[clusterIndex].nrBranches      
                branchesStartHeightGlobal = branchClusterSettingsList[clusterIndex].branchesStartHeightGlobal
                branchesEndHeightGlobal = branchClusterSettingsList[clusterIndex].branchesEndHeightGlobal
                branchesStartHeightCluster = branchClusterSettingsList[clusterIndex].branchesStartHeightCluster
                branchesEndHeightCluster = branchClusterSettingsList[clusterIndex].branchesEndHeightCluster
                branchesStartPointVariation = branchClusterSettingsList[clusterIndex].branchesStartPointVariation
                
                startNodesNextIndexStartTvalEndTval = []
                branchNodesNextIndexStartTvalEndTval = []
                branchNodes = []
                centerDirs = []
                c = 0
                if clusterIndex - 1 >= 0:
                    c = clusterIndex - 1
                else:
                    c = clusterIndex
                    
                for i in range(0, branchClusterSettingsList[clusterIndex].nrBranches):
                    branchNodesNextIndexStartTvalEndTval.append([])
                
                if len(parentClusterBoolListList) > 0:
                    rootNode.getAllStartNodes(
                        self, 
                        startNodesNextIndexStartTvalEndTval, 
                        branchNodesNextIndexStartTvalEndTval,
                        -1, 
                        branchesStartHeightGlobal, 
                        branchesEndHeightGlobal, 
                        branchesStartHeightCluster, 
                        branchesEndHeightCluster, 
                        parentClusterBoolListList, 
                        clusterIndex)
                
                treeGen.report({'INFO'}, f"in addBranches(): len(startNodes): {len(startNodesNextIndexStartTvalEndTval)}")   
                if len(startNodesNextIndexStartTvalEndTval) > 0:
                    segmentLengths = []
                    
                    totalLength = calculateSegmentLengthsAndTotalLength(self, treeGen, startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal, branchesEndHeightGlobal, branchesStartHeightCluster, branchesEndHeightCluster)
                    
                    treeGen.report({'INFO'}, f"in addBranches(): totalLength: {totalLength}")
            
                    startPointData = []
                    branchPositions = []
                    
                    for branchIndex in range(0, nrBranches):
                        branchPos = branchIndex * totalLength / nrBranches + random.uniform(-branchesStartPointVariation, branchesStartPointVariation)
                        if branchPos < 0.0:
                            branchPos = 0.0
                        if branchPos > totalLength:
                            branchPos = totalLength
                        branchPositions.append(branchPos)
                        startPointData.append(StartPointData.generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False))
                    
                    treeGen.report({'INFO'}, "before sorting:")
                    for data in startPointData:
                        treeGen.report({'INFO'}, f"outwardDir: {data.outwardDir}")
                        
                    startPointData.sort(key=lambda x: x.startPointTvalGlobal)
            
                    treeGen.report({'INFO'}, "after sorting:")
                    for n, data in enumerate(startPointData):
                        treeGen.report({'INFO'}, f"startPointData[{n}].outwardDir: {data.outwardDir}")
                    
                    dummyStartPointData = []
                    centerPoints = []
                    rightRotationRange = []
                    leftRotationRange = []
                    for data in startPointData:
                        (dummyData, centerPoint) = DummyStartPointData.generateDummyStartPointData(treeGen, rootNode, data)
                        dummyStartPointData.append(dummyData)
                        centerPoints.append(centerPoint)
                        # generates all parallel start points for one startPoint
                    
                    # -> calculate outwardDir per startPoint startPointData.outwardDir
                    
                    # calculate right and left dummy neighbor
                    for n, data in enumerate(dummyStartPointData): # n == branchIndex
                        # -> calculate rotate angle range per startPoint
                        startPointAngle = math.atan2(startPointData[n].outwardDir[0], startPointData[n].outwardDir[1])
                        rightNeighborAngle = (startPointAngle + math.pi) % (2.0 * math.pi)
                        leftNeighborAngle = (startPointAngle + math.pi) % (2.0 * math.pi)
                        rightDir = Vector((0.0,0.0,0.0))
                        leftDir = Vector((0.0,0.0,0.0))
                        
                        directions = []
                        for spData in data:
                            directions.append(Vector(((spData.startPoint - centerPoints[n]).x, (spData.startPoint - centerPoints[n]).y, 0.0)))
                        
                        (cwVector, acwVector, halfCwVector, halfAcwVector, halfAngleCW, halfAngleACW) = StartPointData.findClosestVectors(treeGen, directions, startPointData[n].outwardDir) # -> adaptive rotate angle range !!!
                        
                        rightRotationRange.append(halfAngleCW)
                        leftRotationRange.append(halfAngleACW)
                        
                    for n, data in enumerate(startPointData):
                        treeGen.report({'INFO'}, f"data.startPoint: {data.startPoint}")
                        treeGen.report({'INFO'}, f"centerPoints[{n}]: {centerPoints[n]}")
                        if (data.startPoint - centerPoints[n]).length > 0.0001:
                            data.outwardDir = data.startPoint - centerPoints[n]
                            treeGen.report({'INFO'}, f"re-asigning data.outwardDir: {data.outwardDir}")
                        else:
                            treeGen.report({'INFO'}, f"setting data.outwardDir = data.startNode.cotangent")
                            data.outwardDir = data.startNode.cotangent
                        
                        
                        
                        
                    maxAngle = 0.0
                    minAngle = 0.0
                    windingAngle = 0.0
                    for branchIndex in range(0, nrBranches):
                        branchPos = branchPositions[branchIndex]
                        
                        data = StartPointData.generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False)
                        
                        startPoint = data.startPoint
                        startNodeNextIndex = data.startNodeNextIndex
                        startPointTangent = treegen_utils.sampleSplineTangentT(data.startNode.point, 
                                                                data.startNode.next[startNodeNextIndex].point, 
                                                                data.tangent, 
                                                                data.startNode.next[startNodeNextIndex].tangent[0], 
                                                                data.t)
                                                                
                        branchStartTvalGlobal = treegen_utils.lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                        
                        globalVerticalAngle = treegen_utils.lerp(branchClusterSettingsList[clusterIndex].verticalAngleCrownStart, branchClusterSettingsList[clusterIndex].verticalAngleCrownEnd, data.startNode.tValGlobal)
                        
                        branchVerticalAngle = treegen_utils.lerp(branchClusterSettingsList[clusterIndex].verticalAngleBranchStart, branchClusterSettingsList[clusterIndex].verticalAngleBranchEnd, treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                        
                        verticalAngle = globalVerticalAngle + branchVerticalAngle
                        
                        globalRotateAngle = treegen_utils.lerp(branchClusterSettingsList[clusterIndex].rotateAngleCrownStart, branchClusterSettingsList[clusterIndex].rotateAngleCrownEnd, branchStartTvalGlobal)
                        
                        branchRotateAngle = treegen_utils.lerp(branchClusterSettingsList[clusterIndex].rotateAngleBranchStart, branchClusterSettingsList[clusterIndex].rotateAngleBranchEnd, treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t)) # tValBranch == 0 !!!
                        
                        if branchClusterSettingsList[clusterIndex].rotateAngleRange == 0.0:
                            branchClusterSettingsList[clusterIndex].rotateAngleRange = math.pi
                            
                        if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "ADAPTIVE":
                            centerDir = data.outwardDir
                            centerDirs.append(centerDir)
                            
                            if rightRotationRange[branchIndex] + leftRotationRange[branchIndex] < 2.0 * math.pi:
                                angle = windingAngle % ((rightRotationRange[branchIndex] + leftRotationRange[branchIndex]) * branchClusterSettingsList[clusterIndex].rotateAngleRangeFactor)  - leftRotationRange[branchIndex] * branchClusterSettingsList[clusterIndex].rotateAngleRangeFactor 
                            else:
                                angle = windingAngle % (rightRotationRange[branchIndex] + leftRotationRange[branchIndex])  - leftRotationRange[branchIndex]
                            
                            if angle > maxAngle:
                                maxAngle = angle
                            if angle < minAngle:
                                minAngle = angle
                            
                            right = startPointData[branchIndex].outwardDir.cross(startPointTangent)
                            axis = -centerDir.cross(startPointTangent)
                            
                            branchDir = Quaternion(axis, verticalAngle) @ startPointTangent
                            branchDir = Quaternion(startPointTangent, angle) @ branchDir
                            
                            
                        if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "WINDING":
                            centerDir = data.outwardDir
                            centerDirs.append(centerDir)            
                            if branchClusterSettingsList[clusterIndex].useFibonacciAngles == True:
                                angle = (windingAngle + 2.0 * math.pi) % (2.0 * math.pi)
                                right = startPointTangent.cross(Vector((1.0,0.0,0.0))).normalized() # -> most likely vertical
                            else:
                                if branchClusterSettingsList[clusterIndex].rotateAngleRange <= 0.0:
                                    branchClusterSettingsList[clusterIndex].rotateAngleRange = math.pi
                                angle = windingAngle % branchClusterSettingsList[clusterIndex].rotateAngleRange + branchClusterSettingsList[clusterIndex].rotateAngleOffset - branchClusterSettingsList[clusterIndex].rotateAngleRange / 2.0
                                right = data.outwardDir.cross(startPointTangent)
                                
                                if right.length <= 0.001:
                                    d = data.startNode.next[data.startNodeNextIndex].point - data.startNode.point
                                    h = Vector((d.x, d.y, 0.0))
                                    if h.length > 0:
                                        right = h.cross(data.startNode.tangent[0])
                                    else:
                                        right = Vector((1.0,0.0,0.0))
                                else:
                                    right = right.normalized()
                        
                            axis = right.cross(startPointTangent).normalized()
                            branchDir = Quaternion(axis, -verticalAngle) @ startPointTangent
                            branchDir = Quaternion(startPointTangent, angle) @ branchDir
                            
                        if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "SYMMETRIC":
                            centerDir = Quaternion(startPointTangent.cross(data.outwardDir), -verticalAngle) @ data.outwardDir
                            centerDirs.append(centerDir)
                            axis = startPointTangent.cross(centerDir).normalized()
                            
                            rotateAngle = (globalRotateAngle + branchRotateAngle)
                            
                            if branchIndex % 2 == 0:
                                right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                                axis = right.cross(startPointTangent).normalized()
                                branchDir = Quaternion(axis, -verticalAngle) @ startPointTangent
                                branchDir = Quaternion(startPointTangent, -rotateAngle) @ branchDir
                            else:
                                right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                                axis = right.cross(startPointTangent).normalized()
                                branchDir = Quaternion(axis, verticalAngle) @ startPointTangent
                                branchDir = Quaternion(startPointTangent, rotateAngle) @ branchDir
                        
                        branchCotangent = Vector((0.0, 0.0, 0.0))            
                        #There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem
                        
                        if branchDir.x != 0.0:
                            branchCotangent = Vector((-branchDir.y, branchDir.x, 0.0))
                        else:
                            if branchDir.y != 0.0:
                                branchCotangent = Vector((0.0, -branchDir.z, branchDir.y))
                            else:
                                branchCotangent = Vector((branchDir.z, 0.0, -branchDir.y))
                        
                        startTvalGlobal = treegen_utils.lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                        startTvalBranch = treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[startNodeNextIndex].tValBranch, data.t)
                        treeShapeRatioValue = treeGenerator.shapeRatio(startTvalGlobal, branchClusterSettingsList[clusterIndex].treeShape.value)
                        
                        branchShapeRatioValue = treeGenerator.shapeRatio(startTvalBranch, branchClusterSettingsList[clusterIndex].branchShape.value)
                        
                        branchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * random.uniform(-1.0, 1.0)) * treeShapeRatioValue * branchShapeRatioValue
                        
                        branch = node(data.startPoint, 
                              1.0, 
                              branchCotangent, 
                              clusterIndex, 
                              branchClusterSettingsList[clusterIndex].ringResolution,
                              taper * taperFactorList[clusterIndex].taperFactor, 
                              startTvalGlobal,
                              0.0, 
                              branchLength)
                        
                        branch.tangent.append(branchDir)
                        branch.tValBranch = 0.0
                        
                        nextIndex = startNodesNextIndexStartTvalEndTval[data.startNodeIndex].nextIndex
                        
                        branchNext = node(data.startPoint + branchDir * branchLength, 
                                  1.0, 
                                  branchCotangent, 
                                  clusterIndex, 
                                  branchClusterSettingsList[clusterIndex].ringResolution, 
                                  taper * taperFactorList[clusterIndex].taperFactor, 
                                  data.startNode.tValGlobal, 
                                  0.0, 
                                  branchLength)
                        branchNext.tangent.append(branchDir)
                        branchNext.tValBranch = 1.0
                        branch.next.append(branchNext)
                        
                        if len(data.startNode.branches) < startNodeNextIndex + 1:
                            for m in range(len(data.startNode.next)):
                                data.startNode.branches.append([])
                        
                        data.startNode.branches[startNodeNextIndex].append(branch)
                        branchNodes.append(branch)
                        
                        if branchClusterSettingsList[clusterIndex].useFibonacciAngles == True:
                            windingAngle += branchClusterSettingsList[clusterIndex].fibonacciNr.fibonacci_angle
                        else:
                            if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "WINDING":
                                rotateAngle = (globalRotateAngle + branchRotateAngle) % branchClusterSettingsList[clusterIndex].rotateAngleRange
                                windingAngle += rotateAngle
                            
                            if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "ADAPTIVE":
                                rotateAngle = globalRotateAngle + branchRotateAngle
                                windingAngle += rotateAngle                    
                        
                        if branchClusterSettingsList[clusterIndex].branchType.value == "OPPOSITE":
                            centerDirs.append(centerDirs[len(centerDirs) - 1])
                            oppositeBranchDir = Quaternion(startPointTangent, math.radians(180.0)) @ branchDir
                            oppositeBranchCotangent = Quaternion(branchCotangent, math.radians(180.0)) @ branchCotangent
                            
                            if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "SYMMETRIC":
                                if branchIndex % 2 == 0:
                                    oppositeBranchDir = Quaternion(startPointTangent, 2.0 * rotateAngle) @ oppositeBranchDir
                                else:
                                    oppositeBranchDir = Quaternion(startPointTangent, -2.0 * rotateAngle) @ oppositeBranchDir
                            
                            oppositeBranchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * random.uniform(-1.0, 1.0)) * treeShapeRatioValue * branchShapeRatioValue
                            
                            oppositeBranch = node(data.startPoint, 
                                          1.0, 
                                          oppositeBranchCotangent, 
                                          clusterIndex, 
                                          branchClusterSettingsList[clusterIndex].ringResolution,
                                          taper * taperFactorList[clusterIndex].taperFactor, 
                                          startTvalGlobal,
                                          0.0, 
                                          oppositeBranchLength)
                                          
                            oppositeBranch.tangent.append(oppositeBranchDir)
                            oppositeBranch.tValBranch = 0.0
                            
                            oppositeBranchNext = node(data.startPoint + oppositeBranchDir * oppositeBranchLength, 
                                              1.0,
                                              oppositeBranchCotangent,
                                              clusterIndex,
                                              branchClusterSettingsList[clusterIndex].ringResolution,
                                              taper * taperFactorList[clusterIndex].taperFactor,
                                              data.startNode.tValGlobal,
                                              0.0,
                                              oppositeBranchLength)
                            oppositeBranchNext.tangent.append(oppositeBranchDir)
                            oppositeBranchNext.tValBranch = 1.0
                            oppositeBranch.next.append(oppositeBranchNext)
                            
                            if len(data.startNode.branches) < startNodeNextIndex + 1:
                                for m in range(len(data.startNode.next)):
                                    data.startNode.branches.append([])
                            
                            data.startNode.branches[startNodeNextIndex].append(oppositeBranch)
                            branchNodes.append(oppositeBranch)
                            
                        if branchClusterSettingsList[clusterIndex].branchType.value == "WHORLED":
                            whorlCount = int(round(treegen_utils.lerp(branchClusterSettingsList[clusterIndex].branchWhorlCountStart, branchClusterSettingsList[clusterIndex].branchWhorlCountEnd, startTvalGlobal)))
                            
                            for n in range(1, whorlCount):
                                centerDirs.append(centerDirs[len(centerDirs) - 1])
                                whorlDir = Quaternion(startPointTangent, math.radians(n * 360.0 / whorlCount)) @ branchDir
                                whorlCotangent = Quaternion(branchCotangent, math.radians(n * 360.0 / whorlCount)) @ branchCotangent
                                
                                whorlBranchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * random.uniform(-1.0, 1.0)) * treeShapeRatioValue * branchShapeRatioValue
                                
                                whorlBranch = node(data.startPoint, 
                                           1.0, 
                                           whorlCotangent, 
                                           clusterIndex, 
                                           branchClusterSettingsList[clusterIndex].ringResolution, 
                                           taper * taperFactorList[clusterIndex].taperFactor, 
                                           startTvalGlobal, 
                                           0.0, 
                                           whorlBranchLength)
                                           
                                whorlBranch.tangent.append(whorlDir)
                                whorlBranch.tValBranch = 0.0
                                
                                whorlBranchNext = node(data.startPoint + whorlDir * whorlBranchLength, 
                                               1.0,
                                               whorlCotangent,
                                               clusterIndex,
                                               branchClusterSettingsList[clusterIndex].ringResolution,
                                               taper * taperFactorList[clusterIndex].taperFactor,
                                               data.startNode.tValGlobal,
                                               0.0,
                                               branchLength)
                                whorlBranchNext.tangent.append(whorlDir)
                                whorlBranchNext.tValBranch = 1.0
                                whorlBranch.next.append(whorlBranchNext)
                                
                                if len(data.startNode.branches) < startNodeNextIndex + 1:
                                    for m in range(len(data.startNode.next)):
                                        data.startNode.branches.append([])
                                
                                data.startNode.branches[startNodeNextIndex].append(whorlBranch)
                                branchNodes.append(whorlBranch)
        
                #-----------------------------------------------------------------
                # for each branch cluster:        
                maxSplitHeightUsed = 0
                if branchClusterSettingsList[clusterIndex].nrSplitsPerBranch > 0.0: # [clusterIndex]
                    
                    splitHeightInLevelList = branchSplitHeightInLevel  # == branchSplitHeightInLevelList_0
                    if clusterIndex == 1:
                        splitHeightInLevelList = branchSplitHeightInLevelList_1
                    if clusterIndex == 2:
                        splitHeightInLevelList = branchSplitHeightInLevelList_2
                    if clusterIndex == 3:
                        splitHeightInLevelList = branchSplitHeightInLevelList_3
                    if clusterIndex == 4:
                        splitHeightInLevelList = branchSplitHeightInLevelList_4
                    if clusterIndex == 5:
                        splitHeightInLevelList = branchSplitHeightInLevelList_5
                    if clusterIndex == 6:
                        splitHeightInLevelList = branchSplitHeightInLevelList_6
                    if clusterIndex == 7:
                        splitHeightInLevelList = branchSplitHeightInLevelList_7
                    if clusterIndex == 8:
                        splitHeightInLevelList = branchSplitHeightInLevelList_8
                    if clusterIndex == 9:
                        splitHeightInLevelList = branchSplitHeightInLevelList_9
                    if clusterIndex == 10:
                        splitHeightInLevelList = branchSplitHeightInLevelList_10
                    if clusterIndex == 11:
                        splitHeightInLevelList = branchSplitHeightInLevelList_11
                    if clusterIndex == 12:
                        splitHeightInLevelList = branchSplitHeightInLevelList_12
                    if clusterIndex == 13:
                        splitHeightInLevelList = branchSplitHeightInLevelList_13
                    if clusterIndex == 14:
                        splitHeightInLevelList = branchSplitHeightInLevelList_14
                    if clusterIndex == 15:
                        splitHeightInLevelList = branchSplitHeightInLevelList_15
                    if clusterIndex == 16:
                        splitHeightInLevelList = branchSplitHeightInLevelList_16
                    if clusterIndex == 17:
                        splitHeightInLevelList = branchSplitHeightInLevelList_17
                    if clusterIndex == 18:
                        splitHeightInLevelList = branchSplitHeightInLevelList_18
                    if clusterIndex == 19:
                        splitHeightInLevelList = branchSplitHeightInLevelList_19
                    if clusterIndex > 19:
                        splitHeightInLevelList = branchSplitHeightInLevelListList[clusterIndex - 20].value
                    
                    nrSplits = int(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches)
                    
                    length = len(splitHeightInLevelList)
                    if length < int(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches):
                        for i in range(length, nrSplits):
                            newHeight = splitHeightInLevelList.add()
                            newHeight = 0.5
                            
                    branchClusterSettingsList[clusterIndex].maxSplitHeightUsed = splitBranches(treeGen,
                        rootNode, 
                        clusterIndex, 
                        nrSplits, 
                        
                        branchClusterSettingsList[clusterIndex].branchSplitAngle, 
                        branchClusterSettingsList[clusterIndex].branchSplitPointAngle, 
                        branchClusterSettingsList[clusterIndex].nrSplitsPerBranch, 
                        
                        branchClusterSettingsList[clusterIndex].splitsPerBranchVariation, 
                        splitHeightInLevelList,
                        branchClusterSettingsList[clusterIndex].branchSplitHeightVariation, 
                        branchClusterSettingsList[clusterIndex].branchSplitLengthVariation,
                        
                        branchClusterSettingsList[clusterIndex].branchSplitMode.value, 
                        branchClusterSettingsList[clusterIndex].branchSplitRotateAngle,
                        
                        branchClusterSettingsList[clusterIndex].ringResolution, 
                        branchClusterSettingsList[clusterIndex].branchCurvatureOffsetStrength,
                        branchClusterSettingsList[clusterIndex].branchVariance, 
                        
                        branchClusterSettingsList[clusterIndex].branchSplitAxisVariation, 
                        
                        branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                        branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd)
                
                for i, branchNode in enumerate(branchNodes):
                    
                    treeGen.report({'INFO'}, f"branchCurvatueEnd: {branchClusterSettingsList[clusterIndex].branchCurvatureEnd}")
                    branchNode.resampleSpline(rootNode, resampleDistance)
                    branchNode.applyCurvature(treeGen, 
                                      rootNode, 
                                      treeGrowDir, 
                                      treeHeight, 
                                      branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                                      branchClusterSettingsList[clusterIndex].branchCurvatureStart, 
                                      branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd, 
                                      branchClusterSettingsList[clusterIndex].branchCurvatureEnd, 
                                      clusterIndex, 
                                      branchNode.point, 
                                      branchClusterSettingsList[clusterIndex].reducedCurveStepCutoff, 
                                      branchClusterSettingsList[clusterIndex].reducedCurveStepFactor)
                    
                    if clusterIndex == 0:
                        branchNode.attractOutward(treeGen, branchClusterSettingsList[clusterIndex].outwardAttraction, branchNode.tangent[0])
                    else:
                        branchNode.attractOutward(treeGen, branchClusterSettingsList[clusterIndex].outwardAttraction, centerDirs[i])
                                               
                    if branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch > 0.0 or branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch > 0.0:
                        branchNode.applyNoise(treeGen, 
                                      noiseGenerator,
                                      branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch, 
                                      branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch, 
                                      branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchGradient, 
                                      branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchExponent, 
                                      branchClusterSettingsList[clusterIndex].noiseScale, 
                                      branchNode.point - (branchNode.next[0].point - branchNode.point), 
                                      branchLength)
    
    
    def shapeRatio(tValGlobal, treeShape):
        if treeShape == "CONICAL":
            return 0.2 + 0.8 * tValGlobal
        if treeShape == "SPHERICAL":
            return 0.2 + 0.8 * math.sin(math.pi * tValGlobal)
        if treeShape == "HEMISPHERICAL":
            return 0.2 + 0.8 * math.sin(0.5 * math.pi * tValGlobal)
        if treeShape == "INVERSE_HEMISPHERICAL":
            return 0.2 + 0.8 * math.sin(0.5 * math.pi * (1.0 - tValGlobal))
        if treeShape == "CYLINDRICAL":
            return 1.0;
        if treeShape == "TAPERED_CYLINDRICAL":
            return 0.5 + 0.5 * tValGlobal
        if treeShape == "FLAME":
            if tValGlobal <= 0.7:
                return tValGlobal / 0.7
            else:
                return (1 - tValGlobal) / 0.3
        if treeShape == "INVERSE_CONICAL":
            return 1.0 - 0.8 * tValGlobal
        if treeShape == "TEND_FLAME":
            if tValGlobal <= 0.7:
                return 0.5 + 0.5 * tValGlobal / 0.7
            else:
                return 0.5 + 0.5 * (1.0 - tValGlobal) / 0.3
    
def splitBranches(treeGen, 
                      rootNode, 
                      branchCluster, 
                      nrBranchSplits, # = int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value)
                                      # used because branchSplitHeightInLevel needs max possible nrBranchSplits!
                      
                      splitAngle, 
                      splitPointAngle, 
                      nrSplitsPerBranch, 
                      
                      splitsPerBranchVariation, 
                      branchSplitHeightInLevel, # == branchSplitHeightInLevelList_0
                      branchSplitHeightVariation, 
                      branchSplitLengthVariation, 
                      
                      branchSplitMode, 
                      branchSplitRotateAngle, 
                      
                      stemRingResolution, 
                      curvOffsetStrength, 
                      variance, 
                      
                      branchSplitAxisVariation, 
                      
                      curvatureStartGlobal, 
                      curvatureEndGlobal):
                          
        allBranchNodes = []
        
        maxSplitHeightInLevelUsed = 0
        
        rootNode.getAllBranchStartNodes(treeGen, allBranchNodes, branchCluster)
        
        splitsForBranch = [0 for i in range(len(allBranchNodes))]
            
        branchLengths = []
        branchWeights = []
        totalLength = 0.0
        totalWeight = 0.0
        for i in range(len(allBranchNodes)):
            length = allBranchNodes[i].lengthToTip(treeGen)
            branchLengths.append(length)
            totalLength += length
            
            treeGen.report({'INFO'}, f"adding length: {length}")
            weight = pow(length, 2.0)
            branchWeights.append(weight)
            totalWeight += weight
            treeGen.report({'INFO'}, f"adding {weight} to totalWeight: {totalWeight}")
        for i in range(len(allBranchNodes)):
            treeGen.report({'INFO'}, f"len(allBranchNodes): {len(allBranchNodes)}")
            treeGen.report({'INFO'}, f"nrBranchSplits: {nrBranchSplits}")
            treeGen.report({'INFO'}, f"branchWeights[{i}]: {branchWeights[i]}")
            treeGen.report({'INFO'}, f"totalWeight: {totalWeight}")
            treeGen.report({'INFO'}, f"splitsPerBranchVariation: {splitsPerBranchVariation}")
            treeGen.report({'INFO'}, f"nrSplitsPerBranch: {nrSplitsPerBranch}")
            
            
            splitsForBranch[i] = int(round(nrBranchSplits * branchWeights[i] / totalWeight + random.uniform(-splitsPerBranchVariation * nrSplitsPerBranch, splitsPerBranchVariation * nrSplitsPerBranch)))
            
            if splitsForBranch[i] < 1:
                splitsForBranch[i] = 1
            
            splitProbabilityInLevel = [0.0 for j in range(splitsForBranch[i])]
            expectedSplitsInLevel = [0 for j in range(splitsForBranch[i])]
            
            if splitsForBranch[i] > 0:
                meanLevel = int(math.log(splitsForBranch[i], 2))
            else:
                meanLevel = 0
                
            if meanLevel < 0:
                meanLevel = 0
            
            if splitsForBranch[i] > 0:
                splitProbabilityInLevel[0] = 1.0
                expectedSplitsInLevel[0] = 1
            else:
                splitProbabilityInLevel[0] = 0.0
                expectedSplitsInLevel[0] = 0
            
            for j in range(1, int(round(meanLevel - variance * meanLevel))):
                splitProbabilityInLevel[j] = 1.0
                expectedSplitsInLevel[j] = int(splitProbabilityInLevel[j] * 2.0 * expectedSplitsInLevel[j - 1])
                
            if int(round(meanLevel - variance * meanLevel)) > 0:
                for k in range(int(round(meanLevel - variance * meanLevel)), int(round(meanLevel + variance * meanLevel))):
                    splitProbabilityInLevel[k] = 1.0 - (7.0 / 8.0) * (k - int(round(meanLevel - variance * meanLevel))) / (
                        round(meanLevel + variance * meanLevel) - round(meanLevel - variance * meanLevel))
                    expectedSplitsInLevel[k] = int(splitProbabilityInLevel[k] * 2.0 * expectedSplitsInLevel[k - 1])
                for m in range(int(round(meanLevel + variance * meanLevel)), int(round(splitsForBranch[i]))):
                    splitProbabilityInLevel[m] = 1.0 / 8.0
                    expectedSplitsInLevel[m] = int(splitProbabilityInLevel[m] * 2.0 * expectedSplitsInLevel[m - 1])
            if splitsForBranch[i] == 2:
                expectedSplitsInLevel[0] = 1
                expectedSplitsInLevel[1] = 1
    
            addToLevel = 0
            maxPossibleSplits = 1
            totalExpectedSplits = 0
            for j in range(splitsForBranch[i]):
                totalExpectedSplits += expectedSplitsInLevel[j]
                if expectedSplitsInLevel[j] < maxPossibleSplits:
                    addToLevel = j
                    break
                maxPossibleSplits *= 2
            addAmount = splitsForBranch[i] - totalExpectedSplits
            if addAmount > 0:
                expectedSplitsInLevel[addToLevel] += min(addAmount, maxPossibleSplits - expectedSplitsInLevel[addToLevel])
    
            splitProbabilityInLevel[addToLevel] = float(expectedSplitsInLevel[addToLevel]) / float(maxPossibleSplits)
            
            nodesInLevelNextIndex = [[] for _ in range(splitsForBranch[i] + 1)]
            
            for n in range(len(allBranchNodes[i].next)):
                nodesInLevelNextIndex[0].append((allBranchNodes[i], n))
                
            splitCounter = 0
            for level in range(splitsForBranch[i]):
                splitsInLevel = 0
                safetyCounter = 0
                
                nodeIndices = list(range(len(nodesInLevelNextIndex[level])))
                
                while splitsInLevel < expectedSplitsInLevel[level]:
                    if not nodeIndices:
                        break
                    if splitCounter == splitsForBranch[i]:
                        break
                    r = random.random()
                    h = random.random() - 0.5
                    if r <= splitProbabilityInLevel[level]:
                        indexToSplit = random.randint(0, len(nodeIndices) - 1)
                        if len(nodeIndices) > indexToSplit:
                            splitHeight = branchSplitHeightInLevel[level].value
                            treeGen.report({'INFO'}, f"branch splitHeight before: {splitHeight}")
                            treeGen.report({'INFO'}, f"branchSplitHeightVariation: {branchSplitHeightVariation}")
                            treeGen.report({'INFO'}, f"h: {h}")
                            if h * splitHeight < 0:
                                splitHeight = max(splitHeight + h * branchSplitHeightVariation, 0.05)
                            else:
                                splitHeight = min(splitHeight + h * branchSplitHeightVariation, 0.95)
                            treeGen.report({'INFO'}, f"branch splitHeight: {splitHeight}")
                            splitNode = split(
                                nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0],
                                nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][1], 
                                splitHeight, 
                                branchSplitLengthVariation,
                                splitAngle,
                                splitPointAngle, 
                                level, 
                                branchSplitMode, 
                                branchSplitRotateAngle, 
                                branchSplitAxisVariation, 
                                stemRingResolution,
                                curvOffsetStrength,
                                treeGen, 
                                rootNode
                                )
                            
                            if splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0]:
                                #did not split
                                totalWeight -= branchWeights[indexToSplit]
                                del branchWeights[indexToSplit]
                                del nodeIndices[indexToSplit]
                            else:
                                if maxSplitHeightInLevelUsed < level:
                                    maxSplitHeightInLevelUsed = level
                                
                                nodesInLevelNextIndex[level + 1].append((splitNode, 0))
                                nodesInLevelNextIndex[level + 1].append((splitNode, 1))
                                
                                del nodeIndices[indexToSplit]
                                
                                splitsInLevel += 1
                                
        return maxSplitHeightInLevelUsed

def split(startNode, 
          nextIndex, 
          splitHeight, 
          splitLengthVariation,
          splitAngle, 
          splitPointAngle, 
          level, 
          mode, 
          rotationAngle, 
          branchSplitAxisVariation, 
          stemRingResolution, 
          curvOffsetStrength, 
          self, 
          rootNode):
    if len(startNode.next) > 0 and nextIndex < len(startNode.next):
        nrNodesToTip = nodesToTip(startNode.next[nextIndex], 0)
        splitHeight = min(splitHeight, 0.999)
        splitAfterNodeNr = int(nrNodesToTip * splitHeight)

        if nrNodesToTip > 0:
            # Split at existing node if close enough
            if nrNodesToTip * splitHeight - splitAfterNodeNr < 0.1:
                splitNode = startNode
                for i in range(splitAfterNodeNr):
                    if i == 0:
                        splitNode = splitNode.next[nextIndex]
                        nextIndex = 0
                    else:
                        splitNode = splitNode.next[0]
                        
                if splitNode != startNode:
                    calculateSplitData(splitNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, splitNode.outwardDir)
                else:
                    # -> split at new node!!!
                    return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength, self, rootNode)
                    
            else:
                return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength, self, rootNode) # clusterIndex???
    
    return startNode


def splitAtNewNode(nrNodesToTip, 
                   splitAfterNodeNr, 
                   startNode, 
                   nextIndex, 
                   splitHeight, 
                   splitLengthVariation, 
                   splitAngle, 
                   splitPointAngle, 
                   level, 
                   mode, 
                   rotationAngle, 
                   branchSplitAxisVariation, 
                   stemRingResolution, 
                   curvOffsetStrength, 
                   self, 
                   rootNode):
    # Split at new node between two nodes
    
    splitAfterNode = startNode
    splitAtStartNode = True
    for i in range(splitAfterNodeNr):
        if i == 0:
            splitAfterNode = splitAfterNode.next[nextIndex]
            splitAtStartNode = False
            nextIndex = 0
        else:
            splitAfterNode = splitAfterNode.next[0]
            splitAtStartNode = False
                        
    tangentIndex = 0
    if splitAtStartNode == True and len(startNode.next) > 1:
        tangentIndex = nextIndex + 1
    else:
        tangentIndex = nextIndex

    # Interpolate position and attributes for the new node
    t = nrNodesToTip * splitHeight - splitAfterNodeNr
    p0 = splitAfterNode.point
    p1 = splitAfterNode.next[nextIndex].point
    t0 = splitAfterNode.tangent[tangentIndex]
    t1 = splitAfterNode.next[nextIndex].tangent[0]
    c0 = splitAfterNode.cotangent
    c1 = splitAfterNode.next[nextIndex].cotangent
    r0 = splitAfterNode.radius
    r1 = splitAfterNode.next[nextIndex].radius
    ring_res = splitAfterNode.ringResolution
    taper = splitAfterNode.taper
    
    newPoint = treegen_utils.sampleSplineT(p0, p1, t0, t1, t)
    newTangent = treegen_utils.sampleSplineTangentT(p0, p1, t0, t1, t)
    newCotangent = treegen_utils.lerp(c0, c1, t)
    newRadius = treegen_utils.lerp(r0, r1, t)
    newTvalGlobal = treegen_utils.lerp(splitAfterNode.tValGlobal, splitAfterNode.next[nextIndex].tValGlobal, nrNodesToTip * splitHeight - splitAfterNodeNr)
    
    newTvalBranch = treegen_utils.lerp(splitAfterNode.tValBranch, splitAfterNode.next[nextIndex].tValBranch, splitHeight);
        
    newNode = node(newPoint, newRadius, newCotangent, splitAfterNode.clusterIndex, ring_res, taper, newTvalGlobal, newTvalBranch, splitAfterNode.branchLength)
    newNode.tangent.append(newTangent)
    
    # Insert new node in the chain
    newNode.next.append(splitAfterNode.next[nextIndex])
    splitAfterNode.next[nextIndex] = newNode
    
    newNode.outwardDir = splitAfterNode.outwardDir
    
    calculateSplitData(newNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, newNode.outwardDir)
    return newNode


def calculateSplitData(splitNode, 
                       splitAngle, 
                       splitPointAngle, 
                       splitLengthVariation, 
                       branchSplitAxisVariation, 
                       level, 
                       sMode, 
                       rotationAngle, 
                       stemRingResolution, 
                       curvOffsetStrength, 
                       self, 
                       outwardDir):
    
    n = splitNode
    nodesAfterSplitNode = 0
    
    while n.next:
        nodesAfterSplitNode += 1
        n = n.next[0]

    # Initialize splitAxis
    splitAxis = Vector((0, 0, 0))

    if sMode == "HORIZONTAL":
        right = splitNode.tangent[0].cross(Vector((0.0, 0.0, 1.0)))
        splitAxis = right.cross(splitNode.tangent[0]).normalized()
        splitAxis = Quaternion(splitNode.tangent[0], random.uniform(-branchSplitAxisVariation, branchSplitAxisVariation)) @ splitAxis

    elif sMode == "ROTATE_ANGLE":
        splitAxis = splitNode.cotangent.normalized()
        splitAxis = (Quaternion(splitNode.tangent[0], rotationAngle * level) @ splitAxis).normalized()
    else:
        self.report({'INFO'}, f"ERROR: invalid splitMode: {sMode}")
        splitAxis = splitNode.cotangent.normalized()
        if level % 2 == 1:
            splitAxis = (Quaternion(splitNode.tangent[0], math.radians(90)) @ splitAxis).normalized()

    splitDirA = (Quaternion(splitAxis, splitPointAngle) @ splitNode.tangent[0]).normalized()
    splitDirB = (Quaternion(splitAxis, -splitPointAngle) @ splitNode.tangent[0]).normalized()

    splitNode.tangent.append(splitDirA)
    splitNode.tangent.append(splitDirB)

    s = splitNode
    previousNodeA = splitNode
    previousNodeB = splitNode
    curv_offset = splitNode.tangent[0].normalized() * (s.next[0].point - s.point).length * (splitAngle / 360.0) * curvOffsetStrength
    s.outwardDir = outwardDir

    for i in range(nodesAfterSplitNode):
        s = s.next[0]
        rel_pos = s.point - splitNode.point
        s.outwardDir = outwardDir

        tangent_a = (Quaternion(splitAxis, splitAngle) @ s.tangent[0]).normalized()
        tangent_b = (Quaternion(splitAxis, -splitAngle) @ s.tangent[0]).normalized()
        cotangent_a = (Quaternion(splitAxis, splitAngle) @ s.cotangent).normalized()
        cotangent_b = (Quaternion(splitAxis, -splitAngle) @ s.cotangent).normalized()

        offset_a = (Quaternion(splitAxis, splitAngle) @ rel_pos)
        offset_a = offset_a * (1.0 + random.uniform(-1.0, 1.0) * splitLengthVariation)
        offset_b = (Quaternion(splitAxis, -splitAngle) @ rel_pos)
        offset_b = offset_b * (1.0 + random.uniform(-1.0, 1.0) * splitLengthVariation)
        
        ring_resolution = stemRingResolution

        nodeA = node(splitNode.point + offset_a + curv_offset, 1.0, cotangent_a, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength)
        nodeA.tangent.append(tangent_a)
        nodeB = node(splitNode.point + offset_b + curv_offset, 1.0, cotangent_b, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength)
        nodeB.tangent.append(tangent_b)

        if i == 0:
            splitNode.next[0] = nodeA
            splitNode.next.append(nodeB)
            previousNodeA = nodeA
            previousNodeB = nodeB
        else:
            previousNodeA.next.append(nodeA)
            previousNodeB.next.append(nodeB)
            previousNodeA = nodeA
            previousNodeB = nodeB


def nodesToTip(n, i):
    if len(n.next) > 0:
        if i > 500:
            self.report({'INFO'}, f"ERROR: in nodesToTip(): max iteration reached!")
            return i
        return 1 + nodesToTip(n.next[0], i + 1)
    else:
        return 1


def shapeRatio(self, context, tValGlobal, treeShape):
    if treeShape == "CONICAL":
        return 0.2 + 0.8 * tValGlobal
    if treeShape == "SPHERICAL":
        return 0.2 + 0.8 * math.sin(math.pi * tValGlobal)
    if treeShape == "HEMISPHERICAL":
        return 0.2 + 0.8 * math.sin(0.5 * math.pi * tValGlobal)
    if treeShape == "INVERSE_HEMISPHERICAL":
        return 0.2 + 0.8 * math.sin(0.5 * math.pi * (1.0 - tValGlobal))
    if treeShape == "CYLINDRICAL":
        return 1.0;
    if treeShape == "TAPERED_CYLINDRICAL":
        return 0.5 + 0.5 * tValGlobal
    if treeShape == "FLAME":
        if tValGlobal <= 0.7:
            return tValGlobal / 0.7
        else:
            return (1 - tValGlobal) / 0.3
    if treeShape == "INVERSE_CONICAL":
        return 1.0 - 0.8 * tValGlobal
    if treeShape == "TEND_FLAME":
        if tValGlobal <= 0.7:
            return 0.5 + 0.5 * tValGlobal / 0.7
        else:
            return 0.5 + 0.5 * (1.0 - tValGlobal) / 0.3
    
    
def calculateSegmentLengthsAndTotalLength(self, 
                                          treeGen, 
                                          startNodesNextIndexStartTvalEndTval, 
                                          segmentLengths, 
                                          branchesStartHeightGlobal, 
                                          branchesEndHeightGlobal, 
                                          branchesStartHeightCluster, 
                                          branchesEndHeightCluster):
        totalLength = 0.0
        for i in range(0, len(startNodesNextIndexStartTvalEndTval)):
            
            segmentLength = 0.0
            if startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex] != None:
                
                segmentLength = (startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex].point - startNodesNextIndexStartTvalEndTval[i].startNode.point).length
            
            tA_global = startNodesNextIndexStartTvalEndTval[i].startNode.tValGlobal
            tB_global = startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex].tValGlobal
            
            tA_branch = startNodesNextIndexStartTvalEndTval[i].startNode.tValBranch
            tB_branch = startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex].tValBranch
            
            if tA_global > tB_global:
                temp = tA_global
                tA_global = tB_global
                tB_global = temp
            
            segmentLengthAbove = 0.0
            
            if startNodesNextIndexStartTvalEndTval[i].startNode.clusterIndex == -1:
                # use t-global
                tStart = max(tA_global, branchesStartHeightGlobal)
                tEnd = min(tB_global, branchesEndHeightGlobal)
                
                frac = 0.0
                if tB_global - tA_global != 0.0:
                    frac = (tEnd - tStart) / (tB_global - tA_global)
                segmentLengthAbove = segmentLength * frac
            else:
                # use t-branch
                if tB_global <= branchesStartHeightGlobal:
                    continue
                if tA_global > branchesEndHeightGlobal:
                    continue
            
                if tA_branch > tB_branch:
                    temp = tA_branch
                    tA_branch = tB_branch
                    tB_branch = temp
                
                tStart = max(tA_branch, branchesStartHeightCluster)
                tEnd = min(tB_branch, branchesEndHeightCluster)
                
                frac = 0.0
                if tA_branch - tB_branch != 0.0:
                    frac = (tEnd - tStart) / (tB_branch - tA_branch)
                segmentLengthAbove = segmentLength * frac
            segmentLengths.append(segmentLengthAbove)
            totalLength += segmentLengthAbove
            
            # t-global only influences segmentLengths if segment is in stem! -> else only use t-branch !!!
        return totalLength



def calculateRadius(self, activeNode, maxRadius, branchTipRadius):
    if len(activeNode.next) > 0 or len(activeNode.branches) > 0:
        
        sum = 0.0
        if len(activeNode.next) > 0:
            max = 0.0
            for n in activeNode.next:
                s = calculateRadius(self, n, maxRadius, branchTipRadius)
                s += (n.point - activeNode.point).length * activeNode.taper * activeNode.taper
                if s > max:
                    max = s
            sum = max
        
        if len(activeNode.branches) > 0:
            for c in activeNode.branches:
                for n in c:
                    calculateRadius(self, n, sum, branchTipRadius)
                    
        if sum < maxRadius:
            activeNode.radius = sum
        else:
            activeNode.radius = maxRadius
        return sum
    else:
        activeNode.radius = branchTipRadius
        return branchTipRadius
        
def generateVerticesAndTriangles(self, 
                                 treeGen, 
                                 context, 
                                 segments, 
                                 dir, 
                                 taper, 
                                 radius, 
                                 ringSpacing, 
                                 stemRingRes, 
                                 taperFactor, 
                                 branchTipRadius, 
                                 barkMaterial):
        vertices = []
        normals = []
        vertexTvalGlobal = []
        ringAngle = []
        faces = []
        #faceUVs = []
        
        offset = 0
        counter = 0
        
        startSection = 0
        
        uvStartOffset = 0.0
        
        for s in range(0, len(segments)):
            segmentLength = (segments[s].end - segments[s].start).length
            if segmentLength > 0:
                sections = round(segmentLength / ringSpacing)
                if sections <= 0:
                    sections = 1
                branchRingSpacing = segmentLength / sections
                
                if s > 0:
                    if segments[s].connectedToPrevious == True and segments[s - 1].connectedToPrevious == False: # only on first segment 
                        #-> later connected segments: dont subtract stemRingRes again!
                        startSection = 1
                        offset -= segments[s].ringResolution + 1
                        
                    if segments[s].connectedToPrevious == False:
                        startSection = 0
                        offset = len(vertices)
                        
                controlPt1 = segments[s].start + segments[s].startTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
                controlPt2 = segments[s].end - segments[s].endTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
            
                for section in range(startSection, sections + 1):
                    pos = treegen_utils.sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections)
                    tangent = treegen_utils.sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections).normalized()
                    
                    if section == 0:
                        tangent = segments[s].firstTangent
                    
                    dirA = treegen_utils.lerp(segments[s].startCotangent, segments[s].endCotangent, section / sections)
                    dirB = (tangent.cross(dirA)).normalized()
                    dirA = (dirB.cross(tangent)).normalized()
                    
                    tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / sections)
                    
                    tValBranch = segments[s].startTvalBranch + (segments[s].endTvalBranch - segments[s].startTvalBranch) * (section / sections)
                    tValGlobal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].endTvalGlobal) * (section / sections)
                    if segments[s].clusterIndex == -1:
                        taper = treegen_utils.lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                        startRadius = segments[s].startRadius
                        endRadius = segments[s].endRadius
                        linearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                        normalizedCurve = (1.0 - branchTipRadius) * tVal + treegen_utils.sampleCurveStem(treeGen, tVal)
                        
                        radius = linearRadius * normalizedCurve
                    else:
                        taper = treegen_utils.lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                        startRadius = segments[s].startRadius
                        endRadius = segments[s].endRadius
                        linearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                        normalizedCurve = (1.0 - branchTipRadius) * tValBranch + treegen_utils.sampleCurveBranch(treeGen, tValBranch, segments[s].clusterIndex) * context.scene.taperFactorList[segments[s].clusterIndex].taperFactor 
                        radius = linearRadius * normalizedCurve
                    
                    for i in range(0, segments[s].ringResolution + 1):
                        angle = (2 * math.pi * i) / segments[s].ringResolution
                        x = math.cos(angle)
                        y = math.sin(angle)
                        normalVector = dirA * radius * math.cos(angle) + dirB * radius * math.sin(angle) 
                        v = pos + normalVector
                        
                        vertices.append(v)
                        normals.append(normalVector)
                        vertexTvalGlobal.append(tVal)
                        ringAngle.append(angle)
                        
                        counter += 1
                
                startRadius = 0.0
                for c in range(0, sections): 
                    tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / sections)
                    nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / sections)
                    
                    pos = treegen_utils.sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / sections)
                    nextPos = treegen_utils.sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, (c + 1) / sections)
                    
                    linearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing))
                    normalizedCurve = (1.0 - branchTipRadius) * tVal + treegen_utils.sampleCurveStem(treeGen, tVal)
                    
                    radius = linearRadius * normalizedCurve
                    
                    if c == 0:
                        startRadius = radius
                    
                    nextLinearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, (c + 1) / (segmentLength / branchRingSpacing))
                    nextNormalizedCurve = (1.0 - branchTipRadius) * nextTval + treegen_utils.sampleCurveStem(treeGen, nextTval)
                    nextRadius = nextLinearRadius * nextNormalizedCurve
                    
                    for j in range(0, segments[s].ringResolution):
                        faces.append((offset + c * (segments[s].ringResolution + 1) + j,
                                      offset + c * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1), 
                                      offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + (j + 1) % (segments[s].ringResolution + 1), 
                                      offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + j))
                        
                        #faceUVdata = []
                        #faceUVdata.append((uvStartOffset + ( j      * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength , (0 + c) / sections)) # 0
                        
                        #faceUVdata.append((uvStartOffset + ((j + 1) * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength, (0 + c) / sections)) # 1
                        
                        #faceUVdata.append((uvStartOffset + ((j + 1) * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 7
                        
                        #faceUVdata.append((uvStartOffset + ( j      * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 6
                        
                        #faceUVs.append(faceUVdata)
                
                #uvStartOffset += segments[s].startRadius * segments[s].ringResolution / segmentLength
                offset += counter
                counter = 0
            
        meshData = bpy.data.meshes.new("treeMesh")
        meshData.from_pydata(vertices, [], faces)
        
        ############################################################    
        custom_normals = [None] * len(meshData.loops)
        
        for poly in meshData.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = meshData.loops[loop_index].vertex_index
                custom_normals[loop_index] = normals[vertex_index]  # Your custom normal !!!!!!!!!!
    
        meshData['use_auto_smooth'] = True
        meshData.normals_split_custom_set(custom_normals)
        
        bmesh_obj = bmesh.new()
        bmesh_obj.from_mesh(meshData)
        
        for i, vertex in enumerate(bmesh_obj.verts):
            vertex.normal = normals[i]
        #############################################################
        # Update the mesh with the new normals
        bmesh_obj.to_mesh(meshData)
        bmesh_obj.free()
        meshData.update()
        
        
        #if len(meshData.uv_layers) == 0:
        #    meshData.uv_layers.new()
        
        uvLayer = meshData.uv_layers.active
        
        #for i, face in enumerate(faces):
        #    uvLayer.data[meshData.polygons[i].loop_indices[0]].uv = (faceUVs[i][0][0], faceUVs[i][0][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[1]].uv = (faceUVs[i][1][0], faceUVs[i][1][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[2]].uv = (faceUVs[i][2][0], faceUVs[i][2][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[3]].uv = (faceUVs[i][3][0], faceUVs[i][3][1])
        
        
        
        meshData.update()
        
        
        for polygon in meshData.polygons:
            polygon.use_smooth = True
        
        name = "tree"
        if name in bpy.data.objects:
            bpy.data.objects[name].data = meshData
            treeObject = bpy.data.objects[name]
            treeObject.select_set(True)
            self.report({'INFO'}, "Found object 'tree'!")
        else:
            treeObject = bpy.data.objects.new("tree", meshData)
            bpy.context.collection.objects.link(treeObject)
            treeObject.select_set(True)
            self.report({'INFO'}, "Created new object!")
        
        bpy.context.view_layer.objects.active = treeObject
        
        bpy.ops.object.shade_auto_smooth(angle=0.01)
        
        mesh = treeObject.data
        
        if "tVal" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="tVal", domain='POINT', data_type='FLOAT')
        
        if "ringAngle" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="ringAngle", domain='POINT', data_type='FLOAT')
        
        tValAttribute = mesh.attributes["tVal"]
        ringAngleAttribute = mesh.attributes["ringAngle"]
        
        for i, vertex in enumerate(mesh.vertices):
            tValAttribute.data[i].value = vertexTvalGlobal[i]
            ringAngleAttribute.data[i].value = ringAngle[i] / (2.0 * math.pi)
        
        treeObject.data.materials.clear()
        treeObject.data.materials.append(barkMaterial)
    
    
    
def addLeaves(self, treeGen, rootNode,
        treeGrowDir, 
        treeHeight, 
        leafClusterSettingsList, 
        leafParentClusterBoolListList, 
        leafMaterial):
            
        for leafClusterIndex in range(0, len(leafClusterSettingsList)):
            
            startNodesNextIndexStartTvalEndTval = []
            branchNodesNextIndexStartTvalEndTval = []
            
            if len(leafParentClusterBoolListList) > 0:
                rootNode.getAllStartNodes(
                    self, 
                    startNodesNextIndexStartTvalEndTval, 
                    branchNodesNextIndexStartTvalEndTval,
                    -1, 
                    leafClusterSettingsList[leafClusterIndex].leafStartHeightGlobal,
                    leafClusterSettingsList[leafClusterIndex].leafEndHeightGlobal,
                    leafClusterSettingsList[leafClusterIndex].leafStartHeightCluster,
                    leafClusterSettingsList[leafClusterIndex].leafEndHeightCluster,
                    leafParentClusterBoolListList, 
                    leafClusterIndex)
                            
            if len(startNodesNextIndexStartTvalEndTval) > 0:
                segmentLengths = []
                totalLength = calculateSegmentLengthsAndTotalLength(self, treeGen, 
                                                                    startNodesNextIndexStartTvalEndTval, 
                                                                    segmentLengths, 
                                                                    leafClusterSettingsList[leafClusterIndex].leafStartHeightGlobal, 
                                                                    leafClusterSettingsList[leafClusterIndex].leafEndHeightGlobal, 
                                                                    leafClusterSettingsList[leafClusterIndex].leafStartHeightCluster, 
                                                                    leafClusterSettingsList[leafClusterIndex].leafEndHeightCluster) 
                
                nrLeaves = totalLength * leafClusterSettingsList[leafClusterIndex].leavesDensity
                
                leafFaces = []
                leafVertices = []
                leafUVs = []
                windingAngle = 0.0
                
                for leafIndex in range(0, int(nrLeaves)):
                    leafPos = leafIndex * totalLength / nrLeaves
                    
                    data = StartPointData.generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, leafPos, treeGrowDir, rootNode, treeHeight,    False)
                    
                    startPoint = data.startPoint
                    
                    startNodeNextIndex = data.startNodeNextIndex
                    startPointTangent = treegen_utils.sampleSplineTangentT(data.startNode.point, 
                                                             data.startNode.next[startNodeNextIndex].point, 
                                                             data.tangent, 
                                                             data.startNode.next[startNodeNextIndex].tangent[0], 
                                                             data.t)
                                                             
                    startPointRadius = treegen_utils.lerp(data.startNode.radius, data.startNode.next[startNodeNextIndex].radius, data.t)
                    
                    verticalAngle = treegen_utils.lerp(leafClusterSettingsList[leafClusterIndex].leafVerticalAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafVerticalAngleBranchEnd, treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                 
                    rotateAngle = treegen_utils.lerp(leafClusterSettingsList[leafClusterIndex].leafRotateAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafRotateAngleBranchEnd, treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                    
                    tiltAngle = treegen_utils.lerp(leafClusterSettingsList[leafClusterIndex].leafTiltAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafTiltAngleBranchEnd, treegen_utils.lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                    
                    offset = 0.0
                    factor = math.cos(verticalAngle)
                    offset = startPointRadius
                                    
                    right = startPointTangent.cross(Vector((0.0,0.0,1.0)))
                    if right.length > 0.001:
                        right = right.normalized()
                    else:
                        #vertical
                        right = data.outwardDir
                        
                    leafTangent = Quaternion(right, verticalAngle) @ startPointTangent
                    leafCotangent = right
                    
                    if leafClusterSettingsList[leafClusterIndex].leafType.value == "SINGLE":
                        if leafClusterSettingsList[leafClusterIndex].leafAngleMode.value == "ALTERNATING":
                            axis = right.cross(startPointTangent)
                            if leafIndex % 2 == 0:
                                leafTangent = Quaternion(axis, rotateAngle) @ leafTangent
                                leafCotangent = Quaternion(axis, rotateAngle) @ leafCotangent
                                leafCotangent = Quaternion(leafTangent, tiltAngle) @ leafCotangent
                            else:
                                leafTangent = Quaternion(axis, -rotateAngle) @ leafTangent
                                leafCotangent = Quaternion(axis, -rotateAngle) @ leafCotangent
                                leafCotangent = Quaternion(leafTangent, -tiltAngle) @ leafCotangent
                        
                        if leafClusterSettingsList[leafClusterIndex].leafAngleMode.value == "WINDING":
                            axis = startPointTangent
                            leafTangent = Quaternion(axis, windingAngle) @ leafTangent
                            leafCotangent = Quaternion(axis, windingAngle) @ leafCotangent
                            leafCotangent = Quaternion(leafTangent, -tiltAngle * math.sin(windingAngle)) @ leafCotangent
                        
                        leafVertices.append(startPoint - leafCotangent *  leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangent * offset)
                        leafVertices.append(startPoint - leafCotangent *  leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangent   * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint + leafCotangent *  leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangent   * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint + leafCotangent *  leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangent * offset)
                        leafFaces.append((4 * leafIndex, 4 * leafIndex + 1, 4 * leafIndex + 2, 4 * leafIndex + 3))
                        
                        leafUVs.append((0.0,0.0))
                        leafUVs.append((0.0,1.0))
                        leafUVs.append((1.0,1.0))
                        leafUVs.append((1.0,0.0))
                        
                    if leafClusterSettingsList[leafClusterIndex].leafType.value == "OPPOSITE":
                        if leafClusterSettingsList[leafClusterIndex].leafAngleMode.value == "ALTERNATING":
                            axis = right.cross(startPointTangent)
                            
                            leafTangentA = Quaternion(axis, rotateAngle) @ leafTangent
                            leafCotangentA = Quaternion(axis, rotateAngle) @ leafCotangent
                            leafCotangentA = Quaternion(leafTangent, tiltAngle) @ leafCotangentA
                            
                            leafTangentB = Quaternion(axis, -rotateAngle) @ leafTangent
                            leafCotangentB = Quaternion(axis, -rotateAngle) @ leafCotangent
                            leafCotangentB = Quaternion(leafTangent, -tiltAngle) @ leafCotangentB
                        
                        if leafClusterSettingsList[leafClusterIndex].leafAngleMode.value == "WINDING":
                            axis = startPointTangent
                            
                            leafTangentA = Quaternion(axis, windingAngle) @ leafTangent
                            leafCotangentA = Quaternion(axis, windingAngle) @ leafCotangent
                            leafCotangentA = Quaternion(leafTangentA, tiltAngle * math.sin(windingAngle)) @ leafCotangentA
                            
                            leafTangentB = Quaternion(axis, math.radians(180)) @ leafTangentA
                            leafCotangentB = Quaternion(axis, math.radians(180)) @ leafCotangentA
                            leafCotangentB = Quaternion(leafTangentB, tiltAngle * math.sin(windingAngle + math.radians(180))) @ leafCotangentB
                            
                        leafVertices.append(startPoint - leafCotangentA * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentA * offset)
                        leafVertices.append(startPoint - leafCotangentA * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentA * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint + leafCotangentA * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentA * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint + leafCotangentA * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentA * offset)
                        leafFaces.append((8 * leafIndex, 8 * leafIndex + 1, 8 * leafIndex + 2, 8 * leafIndex + 3))
                        
                        leafVertices.append(startPoint + leafCotangentB * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentB * offset)
                        leafVertices.append(startPoint + leafCotangentB * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentB * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint - leafCotangentB * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentB * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                        leafVertices.append(startPoint - leafCotangentB * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + leafTangentB * offset)
                        
                        leafFaces.append((8 * leafIndex + 4, 8 * leafIndex + 5, 8 * leafIndex + 6, 8 * leafIndex + 7))
                        
                        leafUVs.append((0.0,0.0))
                        leafUVs.append((0.0,1.0))
                        leafUVs.append((1.0,1.0))
                        leafUVs.append((1.0,0.0))
                         
                        leafUVs.append((0.0,0.0))
                        leafUVs.append((0.0,1.0))
                        leafUVs.append((1.0,1.0))
                        leafUVs.append((1.0,0.0))
                        
                    if leafClusterSettingsList[leafClusterIndex].leafType.value == "WHORLED":
                        axis = startPointTangent
                        whorlAngle = 2.0 * math.pi / leafClusterSettingsList[leafClusterIndex].leafWhorlCount
                        
                        for i in range(0, leafClusterSettingsList[leafClusterIndex].leafWhorlCount):
                            whorledLeafTangent = Quaternion(axis, windingAngle + i * whorlAngle) @ leafTangent
                            whorledLeafCotangent = Quaternion(axis, windingAngle + i * whorlAngle) @ leafCotangent
                            whorledLeafCotangent = Quaternion(whorledLeafTangent, tiltAngle * math.sin(windingAngle + i * whorlAngle)) @    whorledLeafCotangent
                            
                            leafVertices.append(startPoint - whorledLeafCotangent *  leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + whorledLeafTangent * offset)
                            leafVertices.append(startPoint - whorledLeafCotangent * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + whorledLeafTangent * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                            leafVertices.append(startPoint + whorledLeafCotangent * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + whorledLeafTangent * (leafClusterSettingsList[leafClusterIndex].leafSize + offset))
                            leafVertices.append(startPoint + whorledLeafCotangent * leafClusterSettingsList[leafClusterIndex].leafSize * leafClusterSettingsList[leafClusterIndex].leafAspectRatio / 2.0 + whorledLeafTangent * offset)
                            
                            leafFaces.append((4 * (leafIndex * leafClusterSettingsList[leafClusterIndex].leafWhorlCount + i), 
                                              4 * (leafIndex * leafClusterSettingsList[leafClusterIndex].leafWhorlCount + i) + 1, 
                                              4 * (leafIndex * leafClusterSettingsList[leafClusterIndex].leafWhorlCount + i) + 2, 
                                              4 * (leafIndex * leafClusterSettingsList[leafClusterIndex].leafWhorlCount + i) + 3))
                            
                            leafUVs.append((0.0,0.0))
                            leafUVs.append((0.0,1.0))
                            leafUVs.append((1.0,1.0))
                            leafUVs.append((1.0,0.0))
                    
                    windingAngle += rotateAngle
                    
                leafMeshData = bpy.data.meshes.new("leafMesh")
                leafMeshData.from_pydata(leafVertices, [], leafFaces)
                if len(leafMeshData.uv_layers) == 0:
                    leafMeshData.uv_layers.new()
                
                uvLayer = leafMeshData.uv_layers.active
                
                for i, face in enumerate(leafFaces):
                    uvLayer.data[leafMeshData.polygons[i].loop_indices[0]].uv = leafUVs[face[0]]
                    uvLayer.data[leafMeshData.polygons[i].loop_indices[1]].uv = leafUVs[face[1]]
                    uvLayer.data[leafMeshData.polygons[i].loop_indices[2]].uv = leafUVs[face[2]]
                    uvLayer.data[leafMeshData.polygons[i].loop_indices[3]].uv = leafUVs[face[3]]
                    
                leafMeshData.update()
                leafMeshData.flip_normals()
                
                for polygon in leafMeshData.polygons:
                    polygon.use_smooth = True
        
                name = "leaves_" + str(leafClusterIndex)
                if name in bpy.data.objects:
                    bpy.data.objects[name].data = leafMeshData
                    leafObject = bpy.data.objects[name]
                    leafObject.select_set(True)
                else:
                    leafObject = bpy.data.objects.new("leaves_" + str(leafClusterIndex), leafMeshData)
                    bpy.context.collection.objects.link(leafObject)
                    leafObject.select_set(True)
                
                leafObject.data.materials.clear()
                leafObject.data.materials.append(leafMaterial)
