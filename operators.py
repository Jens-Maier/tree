import bpy.types

class generateTree(bpy.types.Operator):
    bl_label = "generateTree"
    bl_idname = "object.generate_tree"
    
    def execute(self, context):
        #delete all existing empties
        if context.active_object is not None and context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY':
                    obj.select_set(True)
            bpy.ops.object.delete()
        self.report({'INFO'}, "deleted all empties")
            
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
                maxSplitHeightUsed = splitRecursive(nodes[0], 
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
            
            nodes[0].resampleSpline(nodes[0], self, context.scene.treeSettings.resampleDistance)
            
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
                addBranches(
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
            
            bpy.context.view_layer.objects.active = bpy.data.objects["tree"]
            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class packUVs(bpy.types.Operator):
    bl_label = "packUVs"
    bl_idname = "object.pack_uvs"
    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=False, correct_aspect=True, use_subsurf_data=False, margin=0.1, no_flip=False, iterations=5, use_weights=True, weight_group="uv_importance", weight_factor=1)
    
        bpy.ops.uv.pack_islands(shape_method='CONVEX', scale=True, rotate=True, rotate_method='AXIS_ALIGNED', margin_method='FRACTION', margin=context.scene.treeSettings.uvMargin, pin=False, merge_overlap=False, udim_source='CLOSEST_UDIM')
    
        bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}
    

class BranchClusterResetButton(bpy.types.Operator):
    bl_idname = "scene.reset_branch_cluster_curve"
    bl_label = "Reset Branch Cluster"
    
    idx: bpy.props.IntProperty()
    
    def execute(self, context):
        curve_name = ensure_branch_curve_node(self.idx)
        self.report({'INFO'}, f"curve_name: {curve_name}")
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveNodeMapping = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping
        curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        
        self.report({'INFO'}, f"in reset: length: {len(curveElement.points)}")
        
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                
        curveNodeMapping.update()
        
        return {'FINISHED'}

class BranchClusterEvaluateButton(bpy.types.Operator):
    bl_idname = "scene.evaluate_branch_cluster"
    bl_label = "Evaluate Branch Cluster"
    
    idx: bpy.props.IntProperty()
    x: bpy.props.FloatProperty()
    
    def lerp(self, a, b, t):
        return (a + (b - 1) * t)
    
    def f0(self, t):
        return (2.0 - t) * (2.0 - t) * (1.0 - t) / 2.0
    def f1(self, t):
        return (2.0 - t) * (2.0 - t) * t + (t - 1.0) * (3.0 - t) * (2.0 - t) / 2.0
    def f2(self, t):
        return (2.0 - t) * (t - 1.0) * t / 2.0 + (3.0 - t) * (t - 1.0) * (t - 1.0)
    def f3(self, t):
        return (t - 1.0) * (t - 1.0) * (t - 2.0) / 2.0
    
    def sampleSpline(self, p0, p1, p2, p3, t):
        return self.f0(t + 1.0) * p0 + self.f1(t + 1.0) * p1 + self.f2(t + 1.0) * p2 + self.f3(t + 1.0) * p3
    
    def f0b(self, t):
        return (-0.5*t*t*t + t*t - 0.5*t)
    def f1b(self, t):
        return (1.5*t*t*t - 2.5*t*t + 1.0)
    def f2b(self, t):
        return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
    def f3b(self, t):
        return (0.5*t*t*t - 0.5*t*t)
    
    def sampleSplineB(self, p0, p1, p2, p3, t):
        return self.f0b(t) * p0 + self.f1b(t) * p1 + self.f2b(t) * p2 + self.f3b(t) * p3

    def execute(self, context):
        curve_name = ensure_branch_curve_node(self.idx)
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        y = 0.0
        nrSamplePoints = 20
        self.report({'INFO'}, f"length: {len(curveElement.points)}")
        for i in range(0, nrSamplePoints):  
            self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                
                #first segment
                if n == 0:
                    if curveElement.points[1].handle_type == "VECTOR":
                        #linear
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                    else:
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                #n = 0, n -> 2 * slope
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                            else: # only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                        else:
                            #n = 0, reflected == 1 * slope
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
                            # [0] -> reflected
                            if len(curveElement.points) > 2:
                                # cubic
                                p3 = curveElement.points[2].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p3 = p2 + (p2 - p1)
                    
                #last segment
                if n == len(curveElement.points) - 2:
                    if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                        #n = last, linear
                        p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                    
                    else:
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO" or curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO_CLAMPED":
                            p0 = curveElement.points[len(curveElement.points) - 3].location
                            #n = last, n -> 2 * slope
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))  
                            else:
                                p3 = p2 + (p2 - p1)
                                #n = last, p3: mirror
                        else:
                            #n = last, slope
                            if len(curveElement.points) > 2:
                                # cubic
                                p0 = curveElement.points[0].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p0 = p1 - (p2 - p1)
                    
                #middle segments
                if n > 0 and n < len(curveElement.points) - 2:
                    if curveElement.points[n].handle_type == "AUTO" or curveElement.points[n].handle_type == "AUTO_CLAMPED":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            #n = middle, n + 1 -> reflected
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #n = middle, (cubic (clamped)) -> spline!
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                                    
                    if curveElement.points[n].handle_type == "VECTOR":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            #linear
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            #n = middle, n -> reflected
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                
                if p1.x <= x and (p2.x > x or p2.x == 1.0):
                    
                    tx = (x - p1.x) / (p2.x - p1.x)
                    
                    px = self.sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
                    py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                            
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, x)
                            
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p0.x, 0.0, p0.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p1.x, 0.0, p1.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p2.x, 0.0, p2.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p3.x, 0.0, p3.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    
                    bpy.ops.object.empty_add(type='SPHERE', location= (x,0.0,py))
                
                    bpy.context.active_object.empty_display_size = 0.01
        return {'FINISHED'}

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
    
    
class evaluateButton(bpy.types.Operator):
    bl_idname="scene.evaluate_button"
    bl_label="evaluate"
    
    x: bpy.props.FloatProperty()
    
    def lerp(self, a, b, t):
        return (a + (b - 1) * t)
    
    def f0(self, t):
        return (2.0 - t) * (2.0 - t) * (1.0 - t) / 2.0
    def f1(self, t):
        return (2.0 - t) * (2.0 - t) * t + (t - 1.0) * (3.0 - t) * (2.0 - t) / 2.0
    def f2(self, t):
        return (2.0 - t) * (t - 1.0) * t / 2.0 + (3.0 - t) * (t - 1.0) * (t - 1.0)
    def f3(self, t):
        return (t - 1.0) * (t - 1.0) * (t - 2.0) / 2.0
    
    def sampleSpline(self, p0, p1, p2, p3, t):
        return self.f0(t + 1.0) * p0 + self.f1(t + 1.0) * p1 + self.f2(t + 1.0) * p2 + self.f3(t + 1.0) * p3
    
    def f0b(self, t):
        return (-0.5*t*t*t + t*t - 0.5*t)
    def f1b(self, t):
        return (1.5*t*t*t - 2.5*t*t + 1.0)
    def f2b(self, t):
        return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
    def f3b(self, t):
        return (0.5*t*t*t - 0.5*t*t)
    
    
    
    def sampleSplineB(self, p0, p1, p2, p3, t):
        return self.f0b(t) * p0 + self.f1b(t) * p1 + self.f2b(t) * p2 + self.f3b(t) * p3
        
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] 
        y = 0.0
        nrSamplePoints = 20
        self.report({'INFO'}, f"length: {len(curveElement.points)}")
        
        for i in range(0, nrSamplePoints):  
            self.report({'INFO'}, f"begin of sample point {i}")
            x = i / nrSamplePoints
            
            for n in range(0, len(curveElement.points) - 1):
                px = curveElement.points[n].location.x
                py = curveElement.points[n].location.y
                self.report({'INFO'}, f"begin of loop: n = {n}")
                
                #first segment
                if n == 0:
                    if curveElement.points[1].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = 0, linear") 
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                        self.report({'INFO'}, f"n = 0, linear: p0: {p0}, p1: {p1}, p2: {p2}, p3: {p3}")
                    else:
                        
                        p1 = curveElement.points[0].location
                        p2 = curveElement.points[1].location
                        if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                            if len(curveElement.points) > 2:
                                slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                                self.report({'INFO'}, f"n = 0, n -> 2 * slope2: {slope2}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p1: {p1}, p2: {p2}")
                                p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                            else: #only 2 points -> linear
                                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                                self.report({'INFO'}, f"in n = 0: only 2 points -> linear, p0.x: {p0.x}, p0.y: {p0.y}")
                                                            
                            if len(curveElement.points) > 2:                            
                                p3 = curveElement.points[2].location
                            else: # linear when only 2 points
                                p3 = p2 + (p2 - p1)
                                p0 = p1 - (p2 - p1)
                                
                                self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                                self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                            self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                        else:
                            self.report({'INFO'}, "n = 0, reflected == 1 * slope")
                            slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                            self.report({'INFO'}, f"n = 0, n -> 2 * slope1: {slope1}")
                            p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
                            # [0] -> reflected
                            if len(curveElement.points) > 2:
                                # cubic
                                p3 = curveElement.points[2].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # linear
                                p3 = p2 + (p2 - p1)
            
                #last segment
                if n == len(curveElement.points) - 2:
                    if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                        self.report({'INFO'}, "n = last, linear")
                        p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                    else:
                        p1 = curveElement.points[len(curveElement.points) - 2].location
                        p2 = curveElement.points[len(curveElement.points) - 1].location
                        p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                        if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO" or curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO_CLAMPED":
                            p0 = curveElement.points[len(curveElement.points) - 3].location
                            self.report({'INFO'}, "n = last, n -> 2 * slope")
                            slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                            if len(curveElement.points) > 2:
                                p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))
                            else:
                                p3 = p2 + (p2 - p1)
                        else:
                            self.report({'INFO'}, "n = last, slope")
                            if len(curveElement.points) > 2:
                                # cubic
                                p0 = curveElement.points[0].location
                            else:
                                # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                                # liear
                                p0 = p1 - (p2 - p1)
            
                #middle segments
                if n > 0 and n < len(curveElement.points) - 2:
                    if curveElement.points[n].handle_type == "AUTO" or curveElement.points[n].handle_type == "AUTO_CLAMPED":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            self.report({'INFO'}, "n = middle, n + 1 -> reflected")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            self.report({'INFO'}, "n = middle, (cubic (clamped)) -> spline!")
                            p0 = curveElement.points[n - 1].location
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
                            
                    if curveElement.points[n].handle_type == "VECTOR":
                        if curveElement.points[n + 1].handle_type == "VECTOR":
                            self.report({'INFO'}, "linear")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                        else:
                            self.report({'INFO'}, "n = middle, n -> reflected")
                            p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                            p1 = curveElement.points[n].location
                            p2 = curveElement.points[n + 1].location
                            p3 = curveElement.points[n + 2].location
            
                if p1.x <= x and p2.x >= x:
                    self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, x: {x}")
                    
                    
                    
                
                    #  x: [0..1]
                    # tx: [p1.x...p2.x]
                    #tx = p1.x + x * (p2.x - p1.x)
                    
                    tx = (x - p1.x) / (p2.x - p1.x)  #AI
                    
                    self.report({'INFO'}, f"tx: {tx}")
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    px = self.sampleSplineB(p0.x, p1.x, p2.x, p3.x, tx) # tx (not x) (AI)
                    py = self.sampleSplineB(p0.y, p1.y, p2.y, p3.y, tx)
                    
                    #py = self.sampleSpline(p0.y, p1.y, p2.y, p3.y, x)
                    
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p0.x, 0.0, p0.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p1.x, 0.0, p1.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p2.x, 0.0, p2.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(p3.x, 0.0, p3.y))
                    bpy.context.active_object.empty_display_size = 0.03
                    
                    bpy.ops.object.empty_add(type='SPHERE', location= (x,0.0,py))
                
                    bpy.context.active_object.empty_display_size = 0.01
        return {'FINISHED'} 

class addItem(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        
        #taperCurveName = f"branchCluster{context.scene.branchClusters}TaperMapping"
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        #TESTcurveElement = nodeGroups.nodes[taper_node_mapping[taperCurveName]].mapping.curves[3]
        
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        #curveElement = nodeGroups.nodes[taper_node_mapping['branchCluster0TaperMapping']].mapping.curves[3] 
        
        
        
        context.scene.treeSettings.branchClusters += 1
        branchSettings = context.scene.branchClusterSettingsList.add()
        
        bpy.ops.scene.reset_branch_cluster_curve(idx = context.scene.treeSettings.branchClusters - 1)
        
        parentClusterBoolListList = context.scene.treeSettings.parentClusterBoolListList.add()
        for b in range(0, context.scene.treeSettings.branchClusters):
            parentClusterBoolListList.value.add()
        parentClusterBoolListList.value[0].value = True
        
        branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
        
        while context.scene.treeSettings.branchClusters - 20 < len(context.scene.branchSplitHeightInLevelListList) and len(context.scene.branchSplitHeightInLevelListList) > 0:
            context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
        
        while context.scene.treeSettings.branchClusters - 20 > len(context.scene.branchSplitHeightInLevelListList):
            context.scene.branchSplitHeightInLevelListList.add()
        
        taperFactorItem = context.scene.taperFactorList.add()
        taperFactorItem.taperFactor = 1.0
        
        for leafParentClusterList in context.scene.treeSettings.leafParentClusterBoolListList:
            leafParentClusterList.value.add()
        
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        if len(context.scene.branchClusterSettingsList) > 0:
            context.scene.treeSettings.branchClusters -= 1
            context.scene.branchClusterSettingsList.remove(len(context.scene.branchClusterSettingsList) - 1)
        
        #TEMP
        #context.scene.treeSettings.branchClusters = 0
        #while len(context.scene.treeSettings.parentClusterBoolListList) > 0:
        #    self.report({'INFO'}, "removing item")
        #    listItem = context.scene.treeSettings.parentClusterBoolListList[0].value
        #    while len(listItem) > 0:
        #        listItem.remove(len(listItem) - 1)
        #        self.report({'INFO'}, "removing list item")
        #    context.scene.treeSettings.parentClusterBoolListList.remove(len(context.scene.treeSettings.parentClusterBoolListList) - 1)
        
        if len(context.scene.treeSettings.parentClusterBoolListList) > 0:
            listToClear = context.scene.treeSettings.parentClusterBoolListList[len(context.scene.treeSettings.parentClusterBoolListList) - 1].value
            lenToClear = len(listToClear)
            
            for i in range(0, lenToClear):
                listToClear.remove(len(listToClear) - 1)
                
            context.scene.treeSettings.parentClusterBoolListList.remove(len(context.scene.treeSettings.parentClusterBoolListList) - 1)
            
        if len(context.scene.branchSplitHeightInLevelListList) > 0 and context.scene.treeSettings.branchClusters > 5:
            context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
            
        if len(context.scene.taperFactorList) > 0:
            context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
          
        for leafParentClusterList in context.scene.treeSettings.leafParentClusterBoolListList:
            if len(leafParentClusterList.value) > 1:
                leafParentClusterList.value.remove(len(leafParentClusterList.value) - 1)
                
                allFalse = True
                for b in leafParentClusterList.value:
                    if b.value == True:
                        allFalse = False
                if allFalse == True:
                    leafParentClusterList.value[0].value = True
            
        return {'FINISHED'}
    
class addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.treeSettings.leafClusters += 1
        context.scene.leafClusterSettingsList.add()
        
        leafParentClusterBoolListList = context.scene.treeSettings.leafParentClusterBoolListList.add()
        stemBool = context.scene.treeSettings.leafParentClusterBoolListList[len(context.scene.treeSettings.leafParentClusterBoolListList) - 1].value.add()
        stemBool = True
                
        for b in range(0, len(context.scene.branchClusterSettingsList)):
            context.scene.treeSettings.leafParentClusterBoolListList[len(context.scene.treeSettings.leafParentClusterBoolListList) - 1].value.add()
        
        leafParentClusterBoolListList.value[0].value = True
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
        if len(context.scene.treeSettings.leafParentClusterBoolListList) > 0:
            context.scene.treeSettings.leafParentClusterBoolListList.remove(len(context.scene.treeSettings.leafParentClusterBoolListList) - 1)
       
        return {'FINISHED'}

    
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
            if len(context.scene.treeSettings.branchSplitHeightInLevelList_0) > 0:
                context.scene.treeSettings.branchSplitHeightInLevelList_0.remove(len(context.scene.treeSettings.branchSplitHeightInLevelList_0) - 1)
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
    
class exportProperties(bpy.types.Operator):
    bl_idname = "export.save_properties_file"
    bl_label = "Save Properties"
    
    def execute(self, context):
        props = context.scene  
        
        filename = props.file_name + ".json"  # Automatically append .json  
        
        filepath = os.path.join(props.folder_path, filename)
         
        save_properties(filepath, self)
        self.report({'INFO'}, f'Saved properties to {filepath}')
        return {'FINISHED'}
    
class importProperties(bpy.types.Operator):
    bl_idname = "export.load_properties_file"
    bl_label = "Load Properties"
    
    def execute(self, context):
        props = context.scene  
        filename = props.file_name + ".json"  # Automatically append .json  
        
        filepath = os.path.join(props.folder_path, filename)
        
        load_properties(filepath, context)
        
        return {'FINISHED'}
    
class loadPreset(bpy.types.Operator):
    bl_idname = "export.load_preset"
    bl_label = "Load Preset"
    
    def execute(self, context):
        props = context.scene
        
        load_preset(props.treePreset.value, context, self)
        return {'FINISHED'}
    
