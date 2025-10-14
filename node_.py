import utils_
import rotation_step
import start_node_info
import segment_
import noise_generator
from segment_ import segment

from mathutils import Vector, Quaternion

class node():
    def __init__(self, Point, Radius, Cotangent, ClusterIndex, RingResolution, Taper, TvalGlobal, TvalBranch, BranchLength):
        self.point = Point
        self.radius = Radius
        self.tangent = []
        self.cotangent = Cotangent
        self.clusterIndex = ClusterIndex
        self.ringResolution = RingResolution
        self.taper = Taper
        self.tValGlobal = TvalGlobal
        self.tValBranch = TvalBranch
        self.next = []
        self.branches = []
        self.branchLength = BranchLength
        self.isLastRotated = False
        self.outwardDir = []
        self.rotateAngleRange = []
        
    def drawDebugPoint(pos, size, name="debugPoint"):
        bpy.ops.object.empty_add(type='SPHERE', location=pos)
        bpy.context.active_object.empty_display_size = size
        bpy.context.active_object.name=name
        
    def drawTangentArrows(self, treeGen):
        #treeGen.report({'INFO'}, "in drawTangentArrows")
        #drawArrow(self.point, self.point + self.tangent[0].normalized())
        # Step 1: Create the empty at the position of point A with type 'SINGLE_ARROW'
        bpy.ops.object.empty_add(type='SINGLE_ARROW', location=self.point)
        empty = bpy.context.object  # Get the newly created empty
        
        # Step 2: Calculate the direction vector from A to B
        direction = self.tangent[0].normalized()
        
        # Step 3: Calculate the rotation to point from A to B
        # Create a rotation matrix that makes the Z-axis of the empty point towards point B
        rotation = direction.to_track_quat('Z', 'Y')  # 'Z' axis points towards B, 'Y' is up
        
        # Apply the rotation to the empty
        empty.rotation_euler = rotation.to_euler()
    
        # Step 4: Scale the empty based on the distance from A to B
        distance = direction.length
        empty.scale = (distance, distance, distance)  # Scale uniformly along all axes
    
        
    def getAllSegments(self, treeGen, rootNode, segments, connectedToPrev):
        #for t in self.tangent:
            #drawArrow(self.point, self.point + t / 2.0)
        #if self.clusterIndex == -1: 
        #drawDebugPoint(self.point, 0.005)
        
        for n, nextNode in enumerate(self.next):
            longestBranchLengthInCluster = 1.0
            
            if len(self.next) > 1:
                segments.append(segment(self.clusterIndex, 
                                        self.point, 
                                        nextNode.point, 
                                        self.tangent[0], # -> firstTangent = self.tangent[0] 
                                        self.tangent[n + 1], 
                                        nextNode.tangent[0], 
                                        self.cotangent, 
                                        nextNode.cotangent, 
                                        self.radius, 
                                        nextNode.radius, 
                                        self.tValGlobal, 
                                        nextNode.tValGlobal, 
                                        self.tValBranch, 
                                        nextNode.tValBranch, 
                                        self.ringResolution, 
                                        False, self.branchLength, 
                                        longestBranchLengthInCluster, 
                                        self.taper, 
                                        nextNode.taper))
            else:
                segments.append(segment(self.clusterIndex, 
                                        self.point, 
                                        nextNode.point, 
                                        self.tangent[0], # -> firstTangent = self.tangent[0] 
                                        self.tangent[0], 
                                        nextNode.tangent[0], 
                                        self.cotangent, 
                                        nextNode.cotangent, 
                                        self.radius, 
                                        nextNode.radius, 
                                        self.tValGlobal, 
                                        nextNode.tValGlobal, 
                                        self.tValBranch, 
                                        nextNode.tValBranch, 
                                        self.ringResolution, 
                                        connectedToPrev, 
                                        self.branchLength, 
                                        longestBranchLengthInCluster, 
                                        self.taper, 
                                        nextNode.taper))
        
            nextNode.getAllSegments(treeGen, rootNode, segments, True)
        
        for branchList in self.branches:
            for b in branchList:
                b.getAllSegments(treeGen, rootNode, segments, False)
            
    
    def getAllBranchStartNodes(self, treeGen, allBranchNodes, branchCluster):
        for c in self.branches:
            for n in c:
                if n.clusterIndex == branchCluster:
                    allBranchNodes.append(n)
                n.getAllBranchStartNodes(treeGen, allBranchNodes, branchCluster)
        
        for n in self.next:
            n.getAllBranchStartNodes(treeGen, allBranchNodes, branchCluster)
    
    
    
    def getAllStartNodes(
        self, 
        treeGen, 
        startNodesNextIndexStartTvalEndTval, 
        branchNodesNextIndexStartTvalEndTval, 
        activeBranchIndex, 
        startHeightGlobal, 
        endHeightGlobal, 
        startHeightCluster, 
        endHeightCluster, 
        parentClusterBoolListList, 
        newClusterIndex):
        
        if self.clusterIndex == -1:
            #stem
            if parentClusterBoolListList[newClusterIndex].value[0].value == True:
                for n in range(len(self.next)):
                    # test if overlap    |----*--v--*----*---v--*
                    if self.next[n].tValGlobal > startHeightGlobal and self.tValGlobal < endHeightGlobal:
                        segmentStartGlobal = max(self.tValGlobal, startHeightGlobal)
                        segmentEndGlobal = min(self.next[n].tValGlobal, endHeightGlobal)
                        
                        startTvalSegment = (segmentStartGlobal - self.tValGlobal) / (self.next[n].tValGlobal - self.tValGlobal)
                        endTvalSegment = (segmentEndGlobal - self.tValGlobal) / (self.next[n].tValGlobal - self.tValGlobal)
                     
                        startNodesNextIndexStartTvalEndTval.append(start_node_info.startNodeInfo(self, n, startTvalSegment, endTvalSegment, segmentStartGlobal, segmentEndGlobal))
        
        else: # not in stem         
            if len(parentClusterBoolListList[newClusterIndex].value) > self.clusterIndex + 1:
                if parentClusterBoolListList[newClusterIndex].value[self.clusterIndex + 1].value == True:
                    for n in range(len(self.next)):
                        
                        if self.tValGlobal >= startHeightGlobal and self.tValGlobal < endHeightGlobal:
                            tA = self.tValBranch
                            tB = self.next[n].tValBranch
                            if tA > tB:
                                tmp = tA
                                tA = tB
                                tB = tmp
                                
                            #only process if ther is overlap
                            if tB > startHeightCluster and tA < endHeightCluster:
                                segStart = max(tA, startHeightCluster)
                                segEnd = min(tB, endHeightCluster)
                                
                                startTval = (segStart - tA) / (tB - tA)
                                endTval = (segEnd - tA) / (tB - tA)
                                startNodesNextIndexStartTvalEndTval.append(start_node_info.startNodeInfo(self, n, startTval, endTval, segStart, segEnd))
                                
                                if activeBranchIndex != -1:
                                    branchNodesNextIndexStartTvalEndTval[activeBranchIndex].append(start_node_info.startNodeInfo(self, n, startTval, endTval))
        for n in self.next:
            n.getAllStartNodes(treeGen, 
                               startNodesNextIndexStartTvalEndTval, 
                               branchNodesNextIndexStartTvalEndTval, 
                               activeBranchIndex, 
                               startHeightGlobal, 
                               endHeightGlobal, 
                               startHeightCluster, 
                               endHeightCluster, 
                               parentClusterBoolListList, 
                               newClusterIndex)
                               
                
        for b in self.branches:
            branchNodesNextIndexStartTvalEndTval.append([])
            for n in b:
                for i in range(0, len(n.next)):
                    branchNodesNextIndexStartTvalEndTval[len(branchNodesNextIndexStartTvalEndTval) - 1].append(start_node_info.startNodeInfo(n, i, 0.0, 1.0, 0.0, 1.0))
                n.getAllStartNodes(
                    treeGen,
                    startNodesNextIndexStartTvalEndTval, 
                    branchNodesNextIndexStartTvalEndTval, 
                    activeBranchIndex, 
                    startHeightGlobal, 
                    endHeightGlobal,
                    startHeightCluster, 
                    endHeightCluster, 
                    parentClusterBoolListList, 
                    newClusterIndex)
                    
                  
    def getAllParallelStartPoints(self, treeGen, startPointTvalGlobal, startNode, parallelPoints):
        
        #treeGen.report({'INFO'}, "in getAllParallelStartPoints() startNode.point: {startNode.point}") #OK
        #treeGen.report({'INFO'}, "in getAllParallelStartPoints() startPointTvalGlobal: {startPointTvalGlobal}")
        #treeGen.report({'INFO'}, "in getAllParallelStartPoints() self.tValGlobal: {self.tValGlobal}") 
        
        
        if self != startNode:
            if self.tValGlobal < startPointTvalGlobal:
                for i, n in enumerate(self.next):
                    if n.tValGlobal > startPointTvalGlobal:
                        tVal = (startPointTvalGlobal - self.tValGlobal) / (n.tValGlobal - self.tValGlobal)
                        if len(self.next) == 2:
                            #treeGen.report({'INFO'}, "in getAllParallelStartPoints() appinding point 2")
                            parallelPoints.append(utils_.utils.sampleSplineT(self.point, n.point, self.tangent[i + 1], n.tangent[0], tVal))
                        if len(self.next) == 1:
                            #treeGen.report({'INFO'}, "in getAllParallelStartPoints() appinding point 1")
                            parallelPoints.append(utils_.utils.sampleSplineT(self.point, n.point, self.tangent[0], n.tangent[0], tVal))
                    else:
                        n.getAllParallelStartPoints(treeGen, startPointTvalGlobal, startNode, parallelPoints)
        else:
            for n in self.next:
                if n.tValGlobal < startPointTvalGlobal:
                    n.getAllParallelStartPoints(treeGen, startPointTvalGlobal, startNode, parallelPoints)        
        return parallelPoints
    
         
    def lengthToTip(self, treeGen):        
        if len(self.next) > 0:
            length_added = (self.next[0].point - self.point).length
            treeGen.report({'INFO'}, f"self.point: {self.point}")
            treeGen.report({'INFO'}, f"next.point: {self.next[0].point}")
            treeGen.report({'INFO'}, f"length added: {length_added}")
            return self.next[0].lengthToTip(treeGen) + (self.next[0].point - self.point).length
        else:
            return 0.0
    
    
    def applyNoise(
        self, 
        treeGen, 
        noise_generator, 
        noiseAmplitudeHorizontal,
        noiseAmplitudeVertical, 
        noiseAmplitudeGradient, 
        noiseAmplitudeExponent,
        noiseScale, 
        prevPoint, 
        treeHeight):
        
        def computeAmplitude(position, amplitude, gradient, exponent):
            """Helper to compute noise amplitude based on tVal and treeHeight."""
            # For stem nodes, position = absolute height; 
            # for branch nodes, position = normalized branch position
            if position < gradient and gradient > 0:
                return pow(utils_.utils.lerp(0.0, amplitude, position / gradient), exponent)
            else:
                if gradient > 0:
                    return pow(amplitude, exponent)
                else:
                    return 0.0
                
        if self.clusterIndex == -1:
            noiseAmplitudeH = computeAmplitude(self.tValGlobal * treeHeight, noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
            noiseAmplitudeV = computeAmplitude(self.tValGlobal * treeHeight, noiseAmplitudeVertical, noiseAmplitudeGradient, noiseAmplitudeExponent)
            right = self.cotangent
        else:
            noiseAmplitudeH = computeAmplitude(self.tValBranch * treeHeight, noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
            noiseAmplitudeV = computeAmplitude(self.tValBranch * treeHeight, noiseAmplitudeVertical, noiseAmplitudeGradient, noiseAmplitudeExponent)
            right = self.tangent[0].cross(Vector((0.0,0.0,1.0)))
        
        if right.length <= 0.001:
            right = Vector((1.0,0.0,0.0))
        else:
            right = right.normalized()
        
        noiseX = noise_generator.coherent_noise(x=self.point.x / noiseScale, y=self.point.y / noiseScale, z=self.point.z / noiseScale)
        noiseY = noise_generator.coherent_noise(x=self.point.x / noiseScale + 1000.0, y=self.point.y / noiseScale + 1000.0, z=self.point.z / noiseScale + 1000.0)
        self.point += noiseX * noiseAmplitudeH * right + noiseY * noiseAmplitudeV * right.cross(self.tangent[0].normalized())
        
        if len(self.next) > 0:
            
            def nextAmplitude(node, amplitude, gradient, exponent):
                if self.clusterIndex == -1:
                    # For stem nodes, position = absolute height; for branch nodes, position = normalized branch position
                    position = node.tValGlobal * treeHeight
                else:
                    position = node.tValBranch
                return computeAmplitude(position, amplitude, gradient, exponent)
    
            nextNoiseX = noise_generator.coherent_noise(x=self.next[0].point.x / noiseScale, y=self.next[0].point.y / noiseScale, z=self.next[0].point.z / noiseScale)
            nextNoiseY = noise_generator.coherent_noise(x=self.next[0].point.x / noiseScale + 1000.0, y=self.next[0].point.y / noiseScale + 1000.0, z=self.next[0].point.z / noiseScale + 1000.0)
        
            nextNoiseAmplitudeH = nextAmplitude(self.next[0], noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
            nextNoiseAmplitudeV = nextAmplitude(self.next[0], noiseAmplitudeVertical, noiseAmplitudeGradient, noiseAmplitudeExponent)
        
            nextRight = self.next[0].cotangent if self.clusterIndex == -1 else self.next[0].tangent[0].cross(Vector((0.0,0.0,1.0)))
            if nextRight.length <= 0.001:
                nextRight = Vector((1.0,0.0,0.0))
            else:
                nextRight = nextRight.normalized()
            
            nextPoint = self.next[0].point + nextNoiseX * nextNoiseAmplitudeH * nextRight + nextNoiseY * nextNoiseAmplitudeV * nextRight.cross(self.next[0].tangent[0].normalized())

            if len(self.next) > 1:
                nextNoiseAmplitudeHb = nextAmplitude(self.next[1], noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
                nextNoiseAmplitudeVb = nextAmplitude(self.next[1], noiseAmplitudeVertical, noiseAmplitudeGradient,  noiseAmplitudeExponent)
                nextNoiseYb = noise_generator.coherent_noise(x=self.next[1].point.x / noiseScale + 1000.0, y=self.next[1].point.y / noiseScale + 1000.0, z=self.next[1].point.z / noiseScale + 1000.0)
                nextRightB = self.next[1].cotangent if self.clusterIndex == -1 else self.next[1].tangent[0].cross(Vector((0.0,0.0,1.0)))
                if nextRightB.length <= 0.001:
                    nextRightB = Vector((1.0,0.0,0.0))
                else:
                    nextRightB = nextRightB.normalized()
                nextPointB = self.next[1].point + nextNoiseX * nextNoiseAmplitudeHb * nextRightB + nextNoiseYb * nextNoiseAmplitudeVb * nextRightB.cross(self.next[1].tangent[0].normalized())
                self.tangent[0] = (nextPoint + nextPointB) / 2.0 - self.point
                self.tangent[1] = nextPoint - self.point
                self.tangent[2] = nextPointB - self.point
            else:
                self.tangent[0] = (nextPoint - prevPoint) / 2.0

        for n in self.next:
            n.applyNoise(
                treeGen, 
                noise_generator, 
                noiseAmplitudeHorizontal,
                noiseAmplitudeVertical,  
                noiseAmplitudeGradient, 
                noiseAmplitudeExponent, 
                noiseScale, 
                self.point, 
                treeHeight
            )
    
    
    def attractOutward(self,
                       treeGen, 
                       outwardAttraction, 
                       outwardDir,
                       rotationSteps = None, 
                       prevPoint = None,
                       prevNode = None
    ):
        if rotationSteps is None:
            rotationSteps = []
        
        right = self.tangent[0].cross(Vector((0.0,0.0,1.0)))
        axis = right.cross(self.tangent[0]).normalized()
        
        if (self.tangent[0].cross(outwardDir)).dot(axis) > 0.0:
            # right side
            angle = self.tangent[0].angle(outwardDir) * outwardAttraction
        else:
            # left side
            angle = -self.tangent[0].angle(outwardDir) * outwardAttraction
            
        if len(self.tangent) == 3:
            if (self.tangent[1].cross(outwardDir)).dot(axis) > 0.0:
                # right side
                angleA = self.tangent[1].angle(outwardDir) * outwardAttraction
            else:
                #left side
                angleA = -self.tangent[1].angle(outwardDir) * outwardAttraction
            
            if (self.tangent[2].cross(outwardDir)).dot(axis) > 0.0:
                #right side
                angleB = self.tangent[2].angle(outwardDir) * outwardAttraction
            else:
                #left side
                angleB = self.tangent[2].angle(outwardDir) * outwardAttraction
                
            angleA = angleA * (1.0 - self.tValBranch)
            angleB = angleB * (1.0 - self.tValBranch)
        
        angle = angle * (1.0 - self.tValBranch)
        
        for step in rotationSteps:
            self.point = step.rotationPoint + Quaternion(step.curveAxis, step.curvature) @ (self.point - step.rotationPoint)
            if step.isLast == False:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature) @ self.tangent[tangentIndex]
                self.cotangent = Quaternion(step.curveAxis, step.curvature) @ self.cotangent
            else:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature / 2.0) @ self.tangent[tangentIndex]
                self.cotangent = Quaternion(step.curveAxis, step.curvature / 2.0) @ self.cotangent
        
        for n in self.next:
            
            nextRotationSteps = rotationSteps.copy()
            
            if len(rotationSteps) > 0:
                nextRotationSteps[len(rotationSteps) - 1].isLast = False
            
            if len(self.next) == 1:
                nextRotationSteps.append(rotation_step.rotationStep(self.point, angle, axis, True))
            if len(self.next) == 2 and n == 0:
                nextRotationSteps.append(rotation_step.rotationStep(self.point, angleA, axis, True))
            if len(self.next) == 2 and n == 1:
                nextRotationSteps.append(rotation_step.rotationStep(self.point, angleB, axis, True))
            
            n.attractOutward(treeGen, 
                             outwardAttraction, 
                             outwardDir, 
                             nextRotationSteps, 
                             self.point,
                             self)
                             
        tanCount = len(self.tangent)
        if prevPoint != None:
            if tanCount == 1 and len(self.next) == 1:
                self.tangent[0] = (self.next[0].point - prevPoint).normalized()
            if tanCount == 3 and len(self.next) == 2:
                self.tangent[0] = ((self.next[0].point + self.next[1].point) / 2.0 - prevPoint).normalized()
                self.tangent[1] = (self.next[0].point - self.point).normalized()
                self.tangent[2] = (self.next[1].point - self.point).normalized()
    
            
    
    def applyCurvature(
        self,
        treeGen,
        rootNode,
        treeGrowDir,
        treeHeight,
        curvatureStartGlobal,
        curvatureStartBranch,
        curvatureEndGlobal,
        curvatureEndBranch,
        clusterIndex,
        branchStartPoint,
        reducedCurveStepCutoff, 
        reducedCurveStepFactor, 
        
        rotationSteps=None, 
        prevPoint = None,
        prevNode = None, 
        firstVertical = True
    ):
        #treeGen.report({'INFO'}, f"in applyCurvature: clusterIndex: {self.clusterIndex}, curvatureStartBranch: {curvatureStartBranch}")
        #treeGen.report({'INFO'}, f"in applyCurvature: clusterIndex: {self.clusterIndex}, curvatureEndBranch: {curvatureEndBranch}")
        if rotationSteps is None:
            rotationSteps = []
                
        if clusterIndex == -1:
            nextTangent = (treeGrowDir.normalized() * treeHeight - (rootNode.point + rootNode.tangent[0] * (treeGrowDir.normalized() * treeHeight - rootNode.point).length * (1.5 / 3.0))).normalized()
            
            centerPoint = utils_.utils.sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0,0.0,1.0)), nextTangent, self.tValGlobal)
        else:
            centerPoint = branchStartPoint
        
        outwardDir = self.point - centerPoint
            
        right = self.tangent[0].cross(Vector((0.0,0.0,1.0))) 
        if right.length < 0.01:
            #near vertical branch
            if outwardDir.length < 0.001:
                curveAxis = self.cotangent
            else:
                curveAxis = outwardDir.cross(self.tangent[0]).normalized()
        else:
            curveAxis = right.normalized()
            
        globalCurvature = utils_.utils.lerp(curvatureStartGlobal, curvatureEndGlobal, self.tValGlobal)
        branchCurvature = utils_.utils.lerp(curvatureStartBranch, curvatureEndBranch, self.tValBranch)
        
        curvature = globalCurvature + branchCurvature
        #treeGen.report({'INFO'}, f"self.tValBranch: {self.tValBranch}, interpolated curvature: {curvature}")
                
        for step in rotationSteps:
            self.point = step.rotationPoint + Quaternion(step.curveAxis, step.curvature) @ (self.point - step.rotationPoint)
            if step.isLast == False:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature) @ self.tangent[tangentIndex]
                self.cotangent = Quaternion(step.curveAxis, step.curvature) @ self.cotangent
            else:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature / 1.0) @ self.tangent[tangentIndex]
                    self.cotangent = Quaternion(step.curveAxis, step.curvature / 1.0) @ self.cotangent
            
        if len(rotationSteps) > 0:
            rotationSteps[len(rotationSteps) - 1].isLast = False
        
        if len(self.next) > 0:
            isLast = False
            if len(self.next[0].next) == 0:
                isLast = True
                
            sectionLength = (self.next[0].point - self.point).length
            
            if Vector((self.tangent[0].x, self.tangent[0].y, 0.0)).dot(Vector((self.next[0].tangent[0].x, self.next[0].tangent[0].y, 0.0))) < reducedCurveStepCutoff:
                rotationSteps.append(rotation_step.rotationStep(self.point, curvature * sectionLength * reducedCurveStepFactor, curveAxis, isLast))
            else:
                rotationSteps.append(rotation_step.rotationStep(self.point, curvature * sectionLength, curveAxis, isLast))
            # utils_.utils.sampleSplineT(
        
        for n in self.next:
                n.applyCurvature(
                treeGen,
                rootNode,
                treeGrowDir,
                treeHeight,
                curvatureStartGlobal,
                curvatureStartBranch,
                curvatureEndGlobal,
                curvatureEndBranch,
                clusterIndex,
                branchStartPoint,
                reducedCurveStepCutoff,
                reducedCurveStepFactor,
                rotationSteps.copy(), 
                self.point, 
                self, 
                firstVertical)
        
        tanCount = len(self.tangent)
        if prevPoint != None:
            if tanCount == 1 and len(self.next) == 1:
                self.tangent[0] = (self.next[0].point - prevPoint).normalized()
            if tanCount == 3 and len(self.next) == 2:
                self.tangent[0] = ((self.next[0].point + self.next[1].point) / 2.0 - prevPoint).normalized()
                self.tangent[1] = (self.next[0].point - self.point).normalized()
                self.tangent[2] = (self.next[1].point - self.point).normalized()
    
    
    
    def resampleSpline(self, rootNode, resampleDistance):
        #treeGen.report({'INFO'}, f"in resampleSpline: point: {self.point}")
        #treeGen.report({'INFO'}, f"in resampleSpline: next[0].point: {self.next[0].point}")
        #treeGen.report({'INFO'}, f"in resampleSpline: resampleDistance: {resampleDistance}")
        #treeGen.report({'INFO'}, f"in resampleSpline: len(self.next): {len(self.next)}")
        for i in range(0, len(self.next)):
            activeNode = self
            startNode = self
            nextNode = self.next[i]
            
            resampleNr = round((nextNode.point - startNode.point).length / resampleDistance)
            #treeGen.report({'INFO'}, f"resampleNr: {resampleNr}, startNode.ringResolution: {startNode.ringResolution}")
            if resampleNr > 1:
                for n in range(1, resampleNr):
                    if len(self.next) > 1:
                        samplePoint = utils_.utils.sampleSplineT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], n / resampleNr)
                        sampleTangent = utils_.utils.sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], n / resampleNr)
                    else:
                        samplePoint = utils_.utils.sampleSplineT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], n / resampleNr)
                        sampleTangent = utils_.utils.sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], n / resampleNr)
                        
                    sampleCotangent = utils_.utils.lerp(startNode.cotangent, nextNode.cotangent, n / resampleNr)
                    sampleRadius = utils_.utils.lerp(startNode.radius, nextNode.radius, n / resampleNr)
                    sampleTvalGlobal = utils_.utils.lerp(startNode.tValGlobal, nextNode.tValGlobal, n / resampleNr)
                    sampleTvalBranch = utils_.utils.lerp(startNode.tValBranch, nextNode.tValBranch, n / resampleNr)
                    #drawDebugPoint(samplePoint, 0.4)
                    
                    newNode = node(samplePoint, sampleRadius, sampleCotangent, startNode.clusterIndex, startNode.ringResolution, self.taper, sampleTvalGlobal, sampleTvalBranch, startNode.branchLength)
                    newNode.tangent.append(sampleTangent)
                    newNode.connectedToPrevious = True
                    if n == 1:
                        activeNode.next[i] = newNode
                    else:
                        activeNode.next.append(newNode)
                    activeNode = newNode
                    
                activeNode.next.append(nextNode)
                #drawDebugPoint(nextNode.point, 0.1) #OK
                #treeGen.report({'INFO'}, f"in resampleSpline: len(Next.next): {len(Next.next)}")
                
            if len(nextNode.next) > 0:
                nextNode.resampleSpline(rootNode, resampleDistance)
 
def drawDebugPoint(pos, size, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = size
    bpy.context.active_object.name=name
    
def drawArrow(a, b):
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=a)
    empty = bpy.context.object
    
    direction = b - a
    rotation = direction.to_track_quat('Z', 'Y')  # 'Z' axis points towards B, 'Y' is up
    empty.rotation_euler = rotation.to_euler()
    distance = direction.length
    empty.scale = (distance, distance, distance)  # Scale uniformly along all axes
    
    return empty