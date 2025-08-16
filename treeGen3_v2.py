bl_info = {
    "name" : "treeGen3",
    "author" : "Jens", 
    "version" : (0,1),
    "blender" : (4,3,1),
    "description" : "Tree generator",
    "location" : "View3d > Sidebar",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",
}

import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import json

class startNodeInfo():
    def __init__(self, StartNode, NextIndex, StartTval, EndTval):
        self.startNode = StartNode
        self.nextIndex = NextIndex
        self.startTval = StartTval
        self.endTval = EndTval
        
class nodeInfo():
    def __init__(self, NodeInLevel, NextIndex, SplitsPerBranch):
        self.nodeInLevel = NodeInLevel
        self.nextIndex = NextIndex
        self.splitsPerBranch = SplitsPerBranch
        
class startPointData():
    def __init__(self, StartPoint, StartPointTvalGlobal, OutwardDir, StartNode, StartNodeIndex, StartNodeNextIndex, T, Tangent, Cotangent):
        self.startPoint = StartPoint
        self.startPointTvalGlobal = StartPointTvalGlobal
        self.outwardDir = OutwardDir
        self.startNode = StartNode
        self.startNodeIndex = StartNodeIndex
        self.startNodeNextIndex = StartNodeNextIndex
        self.t = T
        self.tangent = Tangent
        self.cotangent = Cotangent
        

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
        #    drawArrow(self.point, self.point + t / 2.0)
        #if self.clusterIndex == -1: 
        drawDebugPoint(self.point, 0.1)
        
        for n, nextNode in enumerate(self.next):
            longestBranchLengthInCluster = 1.0
            
            treeGen.report({'INFO'}, f"in getAllSegments(): clusterIndex: {self.clusterIndex}, ringResolution: {self.ringResolution}")
            
            if len(self.next) > 1:
                segments.append(segment(self.clusterIndex, self.point, nextNode.point, self.tangent[n + 1], nextNode.tangent[0], self.cotangent, nextNode.cotangent, self.radius, nextNode.radius, self.tValGlobal, nextNode.tValGlobal, self.tValBranch, nextNode.tValBranch, self.ringResolution, False, self.branchLength, longestBranchLengthInCluster, self.taper, nextNode.taper))
            else:
                segments.append(segment(self.clusterIndex, self.point, nextNode.point, self.tangent[0], nextNode.tangent[0], self.cotangent, nextNode.cotangent, self.radius, nextNode.radius, self.tValGlobal, nextNode.tValGlobal, self.tValBranch, nextNode.tValBranch, self.ringResolution, connectedToPrev, self.branchLength, longestBranchLengthInCluster, self.taper, nextNode.taper))
        
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
            
        treeGen.report({'INFO'}, f"in getAllStartNodes() self.cluster: {self.clusterIndex}")
        #if self.clusterIndex == -1:
        #    drawDebugPoint(self.point, 0.8)
        #if self.clusterIndex == 0:
        #    drawDebugPoint(self.point, 0.3)
        #if self.clusterIndex == 1:
        #    drawDebugPoint(self.point, 0.1)
        
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
                     
                        startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, startTvalSegment, endTvalSegment))
                        #treeGen.report({'INFO'}, f"in getAllStartNodes(): stem: adding node: self.point: {self.point}, newClusterIndex: {newClusterIndex}")
        
        else: # not in stem    
            if self.clusterIndex == 0:
               treeGen.report({'INFO'}, f"self.clusterIndex == 0 len(self.next): {len(self.next)}")
                                        
            if len(parentClusterBoolListList[newClusterIndex].value) > self.clusterIndex + 1:
                if parentClusterBoolListList[newClusterIndex].value[self.clusterIndex + 1].value == True:
                    for n in range(len(self.next)):
                        treeGen.report({'INFO'}, f"self.tValGlobal: {self.tValGlobal}, startHeightGlobal: {startHeightGlobal}, endHeightGlobal: {endHeightGlobal}")
                        
                        if self.tValGlobal >= startHeightGlobal and self.tValGlobal < endHeightGlobal:
                            tA = self.tValBranch
                            tB = self.next[n].tValBranch
                            if tA > tB:
                                tmp = tA
                                tA = tB
                                tB = tmp
                            treeGen.report({'INFO'}, f"self.tValBranch: {self.tValBranch}, next.tValBranch: {self.next[n].tValBranch}")
                            # ERROR HERE !!!
                             
                             
                            treeGen.report({'INFO'}, f"startHeightCluster: {startHeightCluster}, endHeightCluster: {endHeightCluster}")
                            #only process if ther is overlap
                            if tB > startHeightCluster and tA < endHeightCluster:
                                treeGen.report({'INFO'}, "overlap!")
                                segStart = max(tA, startHeightCluster)
                                segEnd = min(tB, endHeightCluster)
                                
                                startTval = (segStart - tA) / (tB - tA)
                                endTval = (segEnd - tA) / (tB - tA)
                                startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, startTval, endTval))
                                if self.clusterIndex == 0:
                                    treeGen.report({'INFO'}, f"adding in self.clusterIndex == 0 len(self.next): {len(self.next)}")
                                    #drawDebugPoint(self.point, 0.5)
                                if activeBranchIndex != -1:
                                    branchNodesNextIndexStartTvalEndTval[activeBranchIndex].append(startNodeInfo(self, n, startTval, endTval))
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
                               
                               #def getAllStartNodes(
        #self, 
        #treeGen, 
        #startNodesNextIndexStartTvalEndTval, 
        #branchNodesNextIndexStartTvalEndTval, 
        #activeBranchIndex, 
        #startHeightGlobal, 
        #endHeightGlobal, 
        #startHeightCluster, 
        #endHeightCluster, 
        #parentClusterBoolListList, 
        #newClusterIndex):
                
        for b in self.branches:
            branchNodesNextIndexStartTvalEndTval.append([])
            for n in b:
                for i in range(0, len(n.next)):
                    branchNodesNextIndexStartTvalEndTval[len(branchNodesNextIndexStartTvalEndTval) - 1].append(startNodeInfo(n, i, 0.0, 1.0))
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
                    
                #def getAllStartNodes(
        #self, 
        #treeGen, 
        #startNodesNextIndexStartTvalEndTval, 
        #branchNodesNextIndexStartTvalEndTval, 
        #activeBranchIndex, 
        #startHeightGlobal, 
        #endHeightGlobal, 
        #startHeightCluster, 
        #endHeightCluster, 
        #parentClusterBoolListList, 
        #newClusterIndex):
                  
            
    def lengthToTip(self):
        if len(self.next) > 0:
            return self.next[0].lengthToTip() + (self.next[0].point - self.point).length
        else:
            return 0.0
    
    
    def curveBranches(self, treeGen, curvature, axis):
        #treeGen.report({'INFO'}, f"in curveBranches: curvature: {curvature}")
        self.curveStep(-curvature, axis.normalized(), self.point, true, 0, 100000000)
        for n in self.next:
            n.curveBranches(treeGen, curvature, axis)
            
    
    
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
                return pow(lerp(0.0, amplitude, position / gradient), exponent)
            else:
                return pow(amplitude, exponent)
                
        if self.clusterIndex == -1:
            noiseAmplitudeH = computeAmplitude(self.tValGlobal * treeHeight, noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
            noiseAmplitudeV = computeAmplitude(self.tValGlobal * treeHeight, noiseAmplitudeVertical, noiseAmplitudeGradient, noiseAmplitudeExponent)
            right = self.cotangent
        else:
            treeGen.report({'INFO'}, f"tValBranch: {self.tValBranch}, treeHeight: {treeHeight}, noiseAmplitudeGradient: {noiseAmplitudeGradient}")
            noiseAmplitudeH = computeAmplitude(self.tValBranch * treeHeight, noiseAmplitudeHorizontal, noiseAmplitudeGradient, noiseAmplitudeExponent)
            noiseAmplitudeV = computeAmplitude(self.tValBranch * treeHeight, noiseAmplitudeVertical, noiseAmplitudeGradient, noiseAmplitudeExponent)
            right = self.tangent[0].cross(Vector((0.0,0.0,1.0)))
        
        if right.length <= 0.001:
            right = Vector((1.0,0.0,0.0))
            treeGen.report({'INFO'}, f"right = (1,0,0), self.point: {self.point}, self.tangent[0]: {self.tangent[0]}")
        else:
            right = right.normalized()
        
        noiseX = noise_generator.coherent_noise(x=self.point.x / noiseScale, y=self.point.y / noiseScale, z=self.point.z / noiseScale)
        noiseY = noise_generator.coherent_noise(x=self.point.x / noiseScale + 1000.0, y=self.point.y / noiseScale + 1000.0, z=self.point.z / noiseScale + 1000.0)
        self.point += noiseX * noiseAmplitudeH * right + noiseY * noiseAmplitudeV * right.cross(self.tangent[0].normalized())
        treeGen.report({'INFO'}, f"self.point: {self.point}, self.cotangent: {self.cotangent}, noiseX: {noiseX}")
        
        # --- Next node noise logic remains the same, but also can be factored ---
        if len(self.next) > 0:
            
            def nextAmplitude(node, amplitude, gradient, exponent):
                if self.clusterIndex == -1:
                    # For stem nodes, position = absolute height; for branch nodes, position = normalized branch position
                    position = node.tValGlobal * treeHeight
                    # nextNoiseAmplitudeH = pow(lerp(0.0, noiseAmplitudeHorizontal, (self.next[0].tValGlobal * treeHeight) / noiseAmplitudeGradient), noiseAmplitudeExponent)
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
                treeGen.report({'INFO'}, f"nextRight = (1,0,0), self.next[0].point: {self.next[0].point}, self.next[0].tangent[0]: {self.next[0].tangent[0]}")
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
                    
        #def applyNoise(
        # self, 
        # treeGen, 
        # noise_generator, 
        # noiseAmplitudeHorizontal,
        # noiseAmplitudeVertical, 
        # noiseAmplitudeGradient, 
        # noiseAmplitudeExponent,
        # noiseScale, 
        # prevPoint, 
        # treeHeight):
        
    
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
        curveStep,
        maxCurveSteps):
        
        if clusterIndex == -1:
            nextTangent = (treeGrowDir.normalized() * treeHeight - (rootNode.point + rootNode.tangent[0] * (treeGrowDir.normalized() * treeHeight - rootNode.point).length * (1.5 / 3.0))).normalized()
        
            centerPoint = sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0,0.0,1.0)), nextTangent, self.tValGlobal)
            #drawDebugPoint(centerPoint, 0.1)
        else:
            # in branch cluster ... TODO
            centerPoint = branchStartPoint
        
        outwardDir = self.point - centerPoint
        #drawArrow(self.point, self.point + 3.0 * outwardDir.normalized())
        
        #curveAxis = outwardDir.cross(self.tangent[0]) #ERROR HERE...TODO
        
        right = self.tangent[0].cross(Vector((0.0,0.0,0.1)))
        if right.length < 0.01:
            #near vertical branch
            if outwardDir.length < 0.001:
                curveAxis = self.cotangent
            else:
                curveAxis = outwardDir.cross(self.tangent[0])
        else:
            curveAxis = right.normalized()
        
        #drawDebugPoint(self.point, 0.1)
        #drawDebugPoint(self.point + curveAxis.normalized() / 2.0, 0.1)
        #drawArrow(self.point, self.point + curveAxis.normalized())
        
        #treeGen.report({'INFO'}, f"in applyCurvature: self.tValGlobal: {self.tValGlobal}, curvatureStartGlobal: {curvatureStartGlobal}, curvatureEndGlobal: {curvatureEndGlobal}")
        globalCurvature = lerp(curvatureStartGlobal, curvatureEndGlobal, self.tValGlobal) # ERROR HERE---
        branchCurvature = lerp(curvatureStartBranch, curvatureEndBranch, self.tValBranch)
        
        curvature = globalCurvature + branchCurvature
        
        curveStepTangent = Quaternion(curveAxis, math.radians(curvature)) @ self.tangent[0]
        
        curveAxis = curveAxis.normalized()
        
        self.curveStep(treeGen, curvature, curveAxis, self.point, True)
        
        
        for n in self.next:
            if curveStep <= maxCurveSteps:
                n.applyCurvature(treeGen, 
                                 rootNode, 
                                 treeGrowDir, 
                                 treeHeight, 
                                 curvatureStartGlobal,
                                 curvatureStartBranch, #TODO: lerp between cutvature Start and curvature End
                                 curvatureEndGlobal,
                                 curvatureEndBranch,
                                 clusterIndex, 
                                 branchStartPoint, 
                                 curveStep + 1, 
                                 maxCurveSteps)
    
    def curveStep(self, treeGen, curvature, curveAxis, rotationPoint, firstNode):        
        if firstNode == True:
            for tangentIndex in range(0, len(self.tangent)):
                self.tangent[tangentIndex] = Quaternion(curveAxis, math.radians(curvature / 2.0)) @ self.tangent[tangentIndex] # TODO: tValBranch...
            self.cotangent = Quaternion(curveAxis, math.radians(curvature / 2.0)) @ self.cotangent
        else:
            self.point = rotationPoint + Quaternion(curveAxis, math.radians(curvature)) @ (self.point - rotationPoint)
            rotLength = (self.point - rotationPoint).length
            #treeGen.report({'INFO'}, f"in curveStep(): rotLength: {rotLength}")
            for tangentIndex in range(0, len(self.tangent)):
                self.tangent[tangentIndex] = Quaternion(curveAxis, math.radians(curvature)) @ self.tangent[tangentIndex]
            self.cotangent = Quaternion(curveAxis, math.radians(curvature)) @ self.cotangent
        
        for n in self.next:
            n.curveStep(treeGen, curvature, curveAxis, rotationPoint, False)
    
    #def alignVerticalStep(self, treeGen, angle, axis, rotationPoint, previousPoint, firstNode, previousCurvature, transitionVal, isSplit, splitVector):
    #    treeGen.report({'INFO'}, f"in alignVerticalStep, angle: {angle}, transitionVal: {transitionVal}")
    #    
    #    self.point = rotationPoint + Quaternion(axis, angle) @ (self.point - rotationPoint)
    #    
    #    if len(self.tangent) == 1:
    #        self.tangent[0] = Quaternion(axis, angle) @ self.tangent[0] #TODO.............. (is this the solution?!?!?)
    #    else:
    #        for t in self.tangent:
    #            t = Quaternion(axis, angle) @ t #TEST    
    #    
    #    
    #    treeGen.report({'INFO'}, f"transitionVal: {transitionVal}")
    #    
    #    rotatedPoint = Vector((0.0,0.0,0.0))
    #    
    #    self.cotangent = Quaternion(axis, angle) @ self.cotangent
    #    
    #    for n in self.next:
    #        if len(self.next) > 1:
    #            n.alignVerticalStep(treeGen, angle, axis, self.point, self.point, False, previousCurvature, transitionVal, True, Vector((0.0,0.0,0.0))) # at split: self.point becomes new rotation point
    #        else:
    #            if transitionVal > 0.9:
    #                n.alignVerticalStep(treeGen, angle, axis, rotationPoint, self.point, False, previousCurvature, transitionVal, False, Vector((0.0,0.0,0.0)))
    #            else:
    #                n.alignVerticalStep(treeGen, angle, axis, rotationPoint, self.point, False, previousCurvature, transitionVal, False, Vector((0.0,0.0,0.0)))
        
    
    
    
    
    
    # hanging branches independent of resample, only 3 nodes!, curveBranches -> directly with spline! curved section, vertical section!
    
    
    
    
    
    
    
    
    
    
    
    
    
    def resampleSpline(self, rootNode, treeGen, resampleDistance):
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
                        samplePoint = sampleSplineT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], n / resampleNr)
                        sampleTangent = sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], n / resampleNr)
                    else:
                        samplePoint = sampleSplineT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], n / resampleNr)
                        sampleTangent = sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], n / resampleNr)
                        
                    sampleCotangent = lerp(startNode.cotangent, nextNode.cotangent, n / resampleNr)
                    sampleRadius = lerp(startNode.radius, nextNode.radius, n / resampleNr)
                    sampleTvalGlobal = lerp(startNode.tValGlobal, nextNode.tValGlobal, n / resampleNr)
                    sampleTvalBranch = lerp(startNode.tValBranch, nextNode.tValBranch, n / resampleNr)
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
                nextNode.resampleSpline(rootNode, treeGen, resampleDistance)
                        
    def hangingBranches(self, treeGen, curvatureStartGlobal, curvatureEndGlobal): #TODO: correct tVal -> for branch radius!
        
        curvature  = lerp(curvatureStartGlobal, curvatureEndGlobal, self.tValGlobal)
        treeGen.report({'INFO'}, f"in hangingBranches(), curvature: {curvature}")
        
        if curvature != 0.0:
            
            radius = abs(1.0 / curvature)
            
            branchLength = (self.next[0].point - self.point).length
            branchDir = (self.next[0].point - self.point) / branchLength
            
            totalRotationAngle = math.acos(branchDir.dot(Vector((0.0,0.0,-1.0))))
            
            if branchLength <= radius * totalRotationAngle:
                centerDir = Quaternion(self.cotangent, math.radians(90)) @ self.tangent[0]
                centerPoint = self.point + centerDir * radius
                drawArrow(self.point, self.point + centerDir)
                #drawDebugPoint(centerPoint, 1.0)
                
                branchEndAngle = branchLength / radius
                newDir = Quaternion(self.cotangent, branchEndAngle) @ (self.tangent[0]).normalized()
                drawArrow(centerPoint, centerPoint + newDir)
                treeGen.report({'INFO'}, f"length: {(self.point - centerPoint).length}") #OK (5.376)
                treeGen.report({'INFO'}, f"self.point: {self.point}")
                treeGen.report({'INFO'}, f"centerPoint: {centerPoint}")
                treeGen.report({'INFO'}, f"newDir.length: {newDir.length}") # 1.0
                
                branchEndPoint = centerPoint + (self.point - centerPoint).length * (Quaternion(self.cotangent, -90.0) @ newDir) 
                #drawDebugPoint(branchEndPoint, 0.2)
                
                branchEndTangent = Quaternion(self.cotangent, branchEndAngle) @ self.next[0].tangent[0]
                self.next[0].point = branchEndPoint
                self.next[0].tangent[0] = branchEndTangent
            
            if branchLength > radius * totalRotationAngle:
                
                verticalRadiusFactor = 0.75
                
                outwardDir = Vector((self.tangent[0].x, self.tangent[0].y, 0.0)) 
                
                drawArrow(self.point, self.point + self.tangent[0])
                drawArrow(self.point, self.point + self.cotangent)
                self.cotangent = self.cotangent.normalized()
                
                centerDir = Quaternion(self.cotangent, math.radians(90)) @ self.tangent[0]
                drawArrow(self.point, self.point + centerDir)
                                
                centerPoint = self.point + centerDir * radius
               #drawDebugPoint(centerPoint, 1.0)
                
                verticalPoint = centerPoint + radius * Vector((outwardDir.x, outwardDir.y, 0.0)) / Vector((outwardDir.x, outwardDir.y, 0.0)).length
                
                verticalPointReducedRadius = centerPoint + radius * verticalRadiusFactor * Vector((outwardDir.x, outwardDir.y, 0.0)) / Vector((outwardDir.x, outwardDir.y, 0.0)).length #TEST: reduce radius!
                
                #drawDebugPoint(verticalPoint, 0.5)
                
                middlePoint = centerPoint + radius * ((verticalPoint + self.point) / 2.0 - centerPoint) / ((verticalPoint + self.point) / 2.0 - centerPoint).length
                #drawDebugPoint(middlePoint, 0.1)
                
                middleTangent = (self.tangent[0] + Vector((0.0,0.0,-1.0))) / 2.0
                drawArrow(middlePoint, middlePoint + middleTangent)
                
                self.next[0].point = middlePoint
                self.next[0].tangent[0] = middleTangent
                
                verticalNode = node(verticalPointReducedRadius, self.next[0].radius, self.next[0].cotangent, self.clusterIndex, self.ringResolution, self.taper, self.tValGlobal, self.tValBranch, self.branchLength)
                verticalNode.tangent.append(Vector((0.0,0.0,-1.0)))
                
                self.next[0].next.append(verticalNode)
                
                treeGen.report({'INFO'}, f"in hangingBranches(), totalRotationAngle: {totalRotationAngle}")
                newLength = branchLength - radius * totalRotationAngle
                treeGen.report({'INFO'}, f"in hangingBranches(), branchLength: {branchLength}, newBranchLength: {newLength}, totalRotationAngle: {totalRotationAngle}, radius: {radius}")
                
                verticalNode.next.append(node(verticalPointReducedRadius + (branchLength - radius * totalRotationAngle) * Vector((0.0,0.0,-1.0)), self.next[0].radius, self.next[0].cotangent, self.clusterIndex, self.ringResolution, self.taper, self.tValGlobal, self.tValBranch, self.branchLength)) #TODO: tValBranch, cotangent, radius, ...
                
                verticalNode.next[0].tangent.append(Vector((0.0,0.0,-1.0)))
                
                #class node():
                #   def __init__(self, Point, Radius, Cotangent, ClusterIndex, RingResolution, Taper, TvalGlobal, TvalBranch, BranchLength):
        
        
class segment():
    def __init__(self, ClusterIndex, Start, End, StartTangent, EndTangent, StartCotangent, EndCotangent, StartRadius, EndRadius, StartTvalGlobal, EndTvalGlobal, StartTvalBranch, EndTvalBranch, RingResolution, ConnectedToPrevious, BranchLength, LongestBranchLengthInCluster, StartTaper, EndTaper):
        self.clusterIndex = ClusterIndex
        self.start = Start
        self.end = End
        self.startTangent = StartTangent
        self.endTangent = EndTangent
        self.startCotangent = StartCotangent
        self.endCotangent = EndCotangent
        self.startRadius = StartRadius
        self.endRadius = EndRadius
        self.startTvalGlobal = StartTvalGlobal
        self.endTvalGlobal = EndTvalGlobal
        self.startTvalBranch = StartTvalBranch
        self.endTvalBranch = EndTvalBranch
        self.ringResolution = RingResolution
        self.connectedToPrevious = ConnectedToPrevious
        self.branchLength = BranchLength
        self.longestBranchLengthInCluster = LongestBranchLengthInCluster
        self.startTaper = StartTaper
        self.endTaper = EndTaper
        

class splitMode:
    HORIZONTAL = 0
    ROTATE_ANGLE = 1
    ALTERNATING = 2
    
# Operator for saving properties  
class exportProperties(bpy.types.Operator):
    bl_idname = "export.save_properties_file"
    bl_label = "Save Properties"
    
    def execute(self, context):
        props = context.scene  
        filename = props.file_name + ".json"  # Automatically append .json  
        filepath = bpy.path.abspath(f"//{filename}")  # Save to the specified filename  
        save_properties(filepath)
        self.report({'INFO'}, f'Saved properties to {filepath}')
        return {'FINISHED'}

class importProperties(bpy.types.Operator):
    bl_idname = "export.load_properties_file"
    bl_label = "Load Properties"
    
    def execute(self, context):
        props = context.scene  
        filename = props.file_name + ".json"  # Automatically append .json  
        filepath = bpy.path.abspath(f"//{filename}")  # Load from the specified filename  
        load_properties(filepath, context)
        self.report({'INFO'}, f'Loaded properties from {filepath}')
        
        bpy.ops.object.generate_tree()
        return {'FINISHED'}
        
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
            
        dir = context.scene.treeGrowDir
        height = context.scene.treeHeight
        taper = context.scene.taper
        radius = context.scene.branchTipRadius
        stemRingRes = context.scene.stemRingResolution
        
        #normals: mesh overlays (only in edit mode) -> Normals
        context.scene.maxSplitHeightUsed = 0
        
        context.scene.seed += 1
        noise_generator = SimplexNoiseGenerator(self, context.scene.seed)
        #result = noise_generator.coherent_noise(x=1.0, y=2.0, z=3.0)
        #self.report({'INFO'}, f"Generated noise value: {result}, seed: {context.scene.seed}")
        
        #for i in range(0, 200):
        #    noiseX = noise_generator.coherent_noise(x=i / context.scene.noiseScale, y=0.0, z=0.0)
        #    self.report({'INFO'}, f"noiseX: {noiseX}")
        #    v = Vector((i, 0.0, noiseX * 10.0))
        #    drawDebugPoint(v, 0.1)
        #    self.report({'INFO'}, f"noisePoint: {v}")
        
        # test sampleCurve:
        n = 50
        for x in range(0, n - 1):
            point = sampleCurve(self, x / n)
            #drawDebugPoint((x, 0.0, 100.0 * point), 0.1)
        
        if context.active_object is None:
            self.report({'INFO'}, "active object is None!")
            
        if context.active_object is not None and context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            
            nodes = []
            nodeTangents = []
            nodeTangents.append(Vector((0.0,0.0,1.0)))
            nodes.append(node(Vector((0.0,0.0,0.0)), 0.1, Vector((1.0,0.0,0.0)), -1, context.scene.stemRingResolution, context.scene.taper, 0.0, 0.0, height))
            nodes[0].tangent.append(Vector((0.0,0.0,1.0)))
            nodes[0].cotangent = Vector((1.0,0.0,0.0))
            nodes.append(node(dir * height, 0.1, Vector((1.0,0.0,0.0)), -1, context.scene.stemRingResolution, context.scene.taper, 1.0, 0.0, height))
            nodes[1].tangent.append(Vector((0.0,0.0,1.0)))
            nodes[1].cotangent = Vector((1.0,0.0,0.0))
            nodes[0].next.append(nodes[1])
            
            
            if context.scene.nrSplits > 0:
                maxSplitHeightUsed = splitRecursive(nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, context.scene.stemSplitHeightInLevelList, context.scene.splitHeightVariation, context.scene.splitLengthVariation, context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0], context.scene.stemRingResolution, context.scene.curvOffsetStrength, self, nodes[0])
                context.scene.maxSplitHeightUsed = max(context.scene.maxSplitHeightUsed, maxSplitHeightUsed)
            
            
            nodes[0].resampleSpline(nodes[0], self, context.scene.resampleDistance)
            
            nodes[0].applyCurvature(self, 
                                    nodes[0], 
                                    context.scene.treeGrowDir, 
                                    context.scene.treeHeight, 
                                    context.scene.curvatureStart / context.scene.resampleDistance, 
                                    0.0, 
                                    context.scene.curvatureEnd / context.scene.resampleDistance, 
                                    0.0, 
                                    #False, 
                                    #0.0,
                                    -1, 
                                    Vector((0.0,0.0,0.0)), 
                                    0, 
                                    context.scene.maxCurveSteps)
            
            if context.scene.noiseAmplitudeHorizontal > 0.0 or context.scene.noiseAmplitudeVertical > 0.0:
                nodes[0].applyNoise(self, 
                                    noise_generator, 
                                    context.scene.noiseAmplitudeHorizontal,
                                    context.scene.noiseAmplitudeVertical, 
                                    context.scene.noiseAmplitudeGradient, 
                                    context.scene.noiseAmplitudeExponent, 
                                    context.scene.noiseScale, 
                                    nodes[0].point - (nodes[0].next[0].point - nodes[0].point), 
                                    context.scene.treeHeight)
            
            #def applyNoise(
        # self, 
        # treeGen, 
        # noise_generator, 
        # noiseAmplitudeHorizontal,
        # noiseAmplitudeVertical, 
        # noiseAmplitudeGradient, 
        # noiseAmplitudeExponent,
        # noiseScale, 
        # prevPoint, 
        # treeHeight):
      
            
            if context.scene.treeGrowDir == Vector((0.0,0.0,1.0)):
                #self.report({'ERROR'}, "ERROR: when treeGrowDir == (0,0,1)")
                self.report({'INFO'}, "treeGrowDir == (0,0,1)")
                
            self.report({'INFO'}, f"branch clusters: {context.scene.branchClusters}")
            # splitRecursive -> resampleSpline -> applyCurvature
            nodes[0].drawTangentArrows(self)
            
            #context.scene.branchClusterSettingsList
            
            if context.scene.branchClusters > 0:
                addBranches(
                self, 
                self, 
                context.scene.resampleDistance,
                
                context,
                nodes[0], 
                context.scene.branchClusters,
                
                context.scene.branchClusterSettingsList,
                
                #context.scene.nrBranchesList, 
                context.scene.parentClusterBoolListList, 
                
                context.scene.treeGrowDir, 
                context.scene.treeHeight, 
                #context.scene.verticalAngleCrownStartList,
                # 
                #context.scene.verticalAngleCrownEndList, 
                #context.scene.verticalAngleBranchStartList,
                #context.scene.verticalAngleBranchEndList,
                #context.scene.branchAngleModeList,  
                
                #context.scene.rotateAngleCrownStartList,
                #context.scene.rotateAngleCrownEndList,
                #context.scene.rotateAngleBranchStartList,
                #context.scene.rotateAngleBranchEndList,
                
                #context.scene.rotateAngleRangeList,
                #context.scene.useFibonacciAnglesList,
                #context.scene.fibonacciNrList,
                
                context.scene.taper, 
                #context.scene.taperFactorList, 
                #context.scene.ringResolutionList,
                #context.scene.relBranchLengthList, 
                #context.scene.relBranchLengthVariationList,
                
                #context.scene.branchShapeList, 
                #context.scene.nrSplitsPerBranchList, 
                #context.scene.splitsPerBranchVariationList,
                
                #context.scene.branchSplitAngleList, 
                #context.scene.branchSplitPointAngleList, 
                context.scene.branchSplitHeightInLevelList_0, 
                context.scene.branchSplitHeightInLevelList_1, 
                context.scene.branchSplitHeightInLevelList_2, 
                context.scene.branchSplitHeightInLevelList_3, 
                context.scene.branchSplitHeightInLevelList_4, 
                context.scene.branchSplitHeightInLevelList_5, 
                
                
                #context.scene.branchSplitHeightVariationList,
                #context.scene.branchSplitLengthVariationList,
                #context.scene.branchSplitModeList,
                #context.scene.branchSplitRotateAngleList,
                #context.scene.branchSplitAxisVariationList,
                
                #context.scene.branchCurvatureOffsetStrengthList[0],
                #context.scene.branchVarianceList, 
                
                context.scene.hangingBranchesList, 
                #context.scene.branchGlobalCurvatureStartList, 
                #context.scene.branchGlobalCurvatureEndList, 
                noise_generator)
              
            calculateRadius(self, nodes[0], 100.0, context.scene.branchTipRadius)
            segments = []
            nodes[0].getAllSegments(self, nodes[0], segments, False)
            
            addLeaves(self, self, nodes[0], 
                context.scene.treeGrowDir, 
                context.scene.treeHeight, 
                context.scene.leavesDensityList, 
                context.scene.leafSizeList,
                context.scene.leafAspectRatioList,
                context.scene.leafParentClusterBoolListList, 
                context.scene.leafStartHeightGlobalList, 
                context.scene.leafEndHeightGlobalList, 
                context.scene.leafStartHeightClusterList, 
                context.scene.leafEndHeightClusterList, 
                context.scene.leafVerticalAngleBranchStartList, 
                context.scene.leafVerticalAngleBranchEndList, 
                context.scene.leafRotateAngleBranchStartList,
                context.scene.leafRotateAngleBranchEndList,
                context.scene.leafTiltAngleBranchStartList,
                context.scene.leafTiltAngleBranchEndList,
                context.scene.leafAngleModeList, 
                context.scene.leafTypeList, 
                context.scene.leaf_material)
            
            generateVerticesAndTriangles(self, self, context, segments, dir, context.scene.taper, radius, context.scene.ringSpacing, context.scene.stemRingResolution, context.scene.taperFactorList, context.scene.branchTipRadius, context.scene.bark_material)
            
            #context.scene.maxSplitHeightUsed
            if len(context.scene.stemSplitHeightInLevelList) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.stemSplitHeightInLevelList)):
                    context.scene.stemSplitHeightInLevelList.remove(len(context.scene.stemSplitHeightInLevelList) - 1)
                    
            if len(context.scene.stemSplitHeightInLevelList) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.stemSplitHeightInLevelList)):
                    h = context.scene.stemSplitHeightInLevelList.add()
                    
            
            
            if len(context.scene.branchSplitHeightInLevelList_0) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_0)):
                    context.scene.branchSplitHeightInLevelList_0.remove(len(context.scene.branchSplitHeightInLevelList_0) - 1)
                    
            if len(context.scene.branchSplitHeightInLevelList_0) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_0)):
                    h = context.scene.branchSplitHeightInLevelList_0.add()
                  
                  
            
            if len(context.scene.branchSplitHeightInLevelList_1) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_1)):
                    context.scene.branchSplitHeightInLevelList_1.remove(len(context.scene.branchSplitHeightInLevelList_1) - 1)
            
            if len(context.scene.branchSplitHeightInLevelList_1) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_1)):
                    h = context.scene.branchSplitHeightInLevelList_1.add()
              
            
            if len(context.scene.branchSplitHeightInLevelList_2) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_2)):
                    context.scene.branchSplitHeightInLevelList_2.remove(len(context.scene.branchSplitHeightInLevelList_2) - 1)
            
            if len(context.scene.branchSplitHeightInLevelList_2) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_2)):
                    h = context.scene.branchSplitHeightInLevelList_2.add()
              
            if len(context.scene.branchSplitHeightInLevelList_3) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_3)):
                    context.scene.branchSplitHeightInLevelList_3.remove(len(context.scene.branchSplitHeightInLevelList_3) - 1)
            
            if len(context.scene.branchSplitHeightInLevelList_3) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_3)):
                    h = context.scene.branchSplitHeightInLevelList_3.add()
              
              
            if len(context.scene.branchSplitHeightInLevelList_4) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_4)):
                    context.scene.branchSplitHeightInLevelList_4.remove(len(context.scene.branchSplitHeightInLevelList_4) - 1)
            
            if len(context.scene.branchSplitHeightInLevelList_4) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_4)):
                    h = context.scene.branchSplitHeightInLevelList_4.add()
              
              
            if len(context.scene.branchSplitHeightInLevelList_5) > context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_5)):
                    context.scene.branchSplitHeightInLevelList_5.remove(len(context.scene.branchSplitHeightInLevelList_5) - 1)
            
            if len(context.scene.branchSplitHeightInLevelList_5) < context.scene.maxSplitHeightUsed + 1:
                for i in range(context.scene.maxSplitHeightUsed + 1, len(context.scene.branchSplitHeightInLevelList_5)):
                    h = context.scene.branchSplitHeightInLevelList_5.add()
              
            bpy.context.view_layer.objects.active = bpy.data.objects["tree"]
            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
    
def lerp(self, a, b, t):
        return (a + (b - 1) * t)    
def f0(t):
    return (-0.5*t*t*t + t*t - 0.5*t)
def f1(t):
    return (1.5*t*t*t - 2.5*t*t + 1.0)
def f2(t):
    return (-1.5*t*t*t + 2.0*t*t + 0.5*t)
def f3(t):
    return (0.5*t*t*t - 0.5*t*t)
    
def sampleSpline(p0, p1, p2, p3, t):
    return f0(t) * p0 + f1(t) * p1 + f2(t) * p2 + f3(t) * p3
    
def sampleCurve(self, x):
    #self.report({'INFO'}, f"access? {context.scene.treeHeight}") #funkt!
    
    #self.report({'INFO'}, f"sampling curve: x: {x}")
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3] 
    y = 0.0
    #self.report({'INFO'}, f"length: {len(curveElement.points)}, x: {x}")
    #self.report({'INFO'}, f"sampleCurve: len(curveElement.points): {len(curveElement.points)}")
    for n in range(0, len(curveElement.points) - 1):
        
        px = curveElement.points[n].location.x
        py = curveElement.points[n].location.y
        #self.report({'INFO'}, f"begin of loop: n = {n}")
        
        #first segment
        if n == 0:
            if curveElement.points[1].handle_type == "VECTOR":
                #self.report({'INFO'}, "n = 0, linear") 
                p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                p1 = curveElement.points[0].location
                p2 = curveElement.points[1].location
                p3 = curveElement.points[1].location + (curveElement.points[1].location - curveElement.points[0].location)
                #self.report({'INFO'}, f"n = 0, linear: p0: {p0}, p1: {p1}, p2: {p2}, p3: {p3}")
            else:
                p1 = curveElement.points[0].location
                p2 = curveElement.points[1].location
                if curveElement.points[0].handle_type == "AUTO" or curveElement.points[0].handle_type == "AUTO_CLAMPED":
                    if len(curveElement.points) > 2:
                        slope2 = 2.0 * (p2.y - p1.y) / (p2.x - p1.x)
                        #self.report({'INFO'}, f"n = 0, n -> 2 * slope2: {slope2}")
                        #self.report({'INFO'}, f"in n = 0, AUTO: p1: {p1}, p2: {p2}")
                        p0 = mathutils.Vector((p1.x - (p2.x - p1.x) / (1.0 + abs(slope2)), p1.y - slope2 * (p2.x - p1.x)))
                        #self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                    else: # only 2 points -> linear
                        p0 = curveElement.points[0].location - (curveElement.points[1].location - curveElement.points[0].location)
                        #self.report({'INFO'}, f"in n = 0: only 2 points -> linear, p0.x: {p0.x}, p0.y: {p0.y}")
                    
                    if len(curveElement.points) > 2:                            
                        p3 = curveElement.points[2].location
                    else: # linear when only 2 points
                        p3 = p2 + (p2 - p1)
                        p0 = p1 - (p2 - p1)
                        
                        #self.report({'INFO'}, f"in n = 0, AUTO: p0: {p0}")
                        #self.report({'INFO'}, f"in n = 0, AUTO: p3: {p3}")
                else:
                    #self.report({'INFO'}, "n = 0, reflected == 1 * slope")
                    slope1 = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
                    #self.report({'INFO'}, f"n = 0, n -> 2 * slope1: {slope1}")
                    p0 = mathutils.Vector((p2.x + (p2.x - p1.x), p1.y + slope1 * (p2.x - p1.x)))
                    # [0] -> reflected
                    if len(curveElement.points) > 2:
                        # cubic
                        p3 = curveElement.points[2].location
                    else:
                        # 2 points: 0: auto, 1: auto -> linear (== 1 * slope)
                        # linear
                        p3 = p2 + (p2 - p1)
                        #self.report("n = first, p0: {p0}, p1: {p1}, p2: {p2}, p3: {p3}")
            
        #last segment
        if n == len(curveElement.points) - 2:
            if curveElement.points[len(curveElement.points) - 2].handle_type == "VECTOR":
                #self.report({'INFO'}, "n = last, linear")
                p0 = curveElement.points[len(curveElement.points) - 2].location - (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                p1 = curveElement.points[len(curveElement.points) - 2].location
                p2 = curveElement.points[len(curveElement.points) - 1].location
                
                p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
            
            else:
                p1 = curveElement.points[len(curveElement.points) - 2].location
                p2 = curveElement.points[len(curveElement.points) - 1].location
                p3 = curveElement.points[len(curveElement.points) - 1].location + (curveElement.points[len(curveElement.points) - 1].location - curveElement.points[len(curveElement.points) - 2].location)
                #self.report({'INFO'}, "n = last p1 p2 p3")
                if curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO" or curveElement.points[len(curveElement.points) - 1].handle_type == "AUTO_CLAMPED":
                    p0 = curveElement.points[len(curveElement.points) - 3].location
                    #self.report({'INFO'}, "n = last, n -> 2 * slope")
                    slope2 = 2.0 * (p3.y - p2.y) / (p3.x - p2.x)
                    if len(curveElement.points) > 2:
                        p3 = mathutils.Vector((p2.x + (p2.x - p1.x) / (1.0 + abs(slope2)), p3.y + slope2 * (p2.x - p1.x)))
                        #self.report({'INFO'}, "n = last, p3: slope")   
                    else:
                        p3 = p2 + (p2 - p1)
                        #self.report({'INFO'}, f"n = last, p3: mirror, p3.x: {p3.x}, p3.y: {p3.y}")   
                        #self.report({'INFO'}, f"n = last, p3: mirror, p3.x: {p3.x}, p3.y: {p3.y}")   
                else:
                    #self.report({'INFO'}, "n = last, slope")
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
                    #self.report({'INFO'}, "n = middle, n + 1 -> reflected")
                    p0 = curveElement.points[n - 1].location
                    p1 = curveElement.points[n].location
                    p2 = curveElement.points[n + 1].location
                    p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                else:
                    #self.report({'INFO'}, "n = middle, (cubic (clamped)) -> spline!")
                    p0 = curveElement.points[n - 1].location
                    p1 = curveElement.points[n].location
                    p2 = curveElement.points[n + 1].location
                    p3 = curveElement.points[n + 2].location
                            
            if curveElement.points[n].handle_type == "VECTOR":
                if curveElement.points[n + 1].handle_type == "VECTOR":
                    #self.report({'INFO'}, "linear")
                    p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                    p1 = curveElement.points[n].location
                    p2 = curveElement.points[n + 1].location
                    p3 = curveElement.points[n + 1].location + (curveElement.points[n + 1].location - curveElement.points[n].location)
                else:
                    #self.report({'INFO'}, "n = middle, n -> reflected")
                    p0 = curveElement.points[n].location - (curveElement.points[n + 1].location - curveElement.points[n].location)
                    p1 = curveElement.points[n].location
                    p2 = curveElement.points[n + 1].location
                    p3 = curveElement.points[n + 2].location
        
        if p1.x <= x and (p2.x > x or p2.x == 1.0):
            
            tx = (x - p1.x) / (p2.x - p1.x)
            
            px = sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
            py = sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
            
            #self.report({'INFO'}, f"found segment n={n}: p0.x: {p0.x}, p1.x: {p1.x}, p2.x: {p2.x}, p3.x: {p3.x}, px: {px}, x: {x}")
            #self.report({'INFO'}, f"found segment n={n}: p0.y: {p0.y}, p1.y: {p1.y}, p2.y: {p2.y}, p3.y: {p3.y}, py: {py}" )
            
            #ERROR HERE: # found segment n=0: p0.x: -0.5, p1.x: 0.0, p2.x: 0.5, p3.x: 1.0,   x: 0.125
                         # found segment n=0: p0.y:  1.5, p1.y: 1.0, p2.y: 0.5, p3.y: 0.0, ist: py: 0.9375 = 1 - 0.125 / 2 OK
                    #                                                                         -> GeoGebra: x: 0.0625 ERROR HERE
                    #      -> double slope error ??? -> x value scaling error!                -> GeoGebra: y: 0.9375 OK
                    #                                                                           ->  # px not x ???
            
            #self.report({'INFO'}, f"sample point: x: {x}, y: {y}, px: {px}, py: {py}")
            return py
    self.report({'ERROR'}, f"segment not found!, x: {x}")
    return 0.0
    
    
def drawDebugPoint(pos, size, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = size
    bpy.context.active_object.name=name
    
def drawArrow(a, b):
    # Step 1: Create the empty at the position of point A with type 'SINGLE_ARROW'
    bpy.ops.object.empty_add(type='SINGLE_ARROW', location=a)
    empty = bpy.context.object  # Get the newly created empty
    
    # Step 2: Calculate the direction vector from A to B
    direction = b - a
    
    # Step 3: Calculate the rotation to point from A to B
    # Create a rotation matrix that makes the Z-axis of the empty point towards point B
    rotation = direction.to_track_quat('Z', 'Y')  # 'Z' axis points towards B, 'Y' is up
    
    # Apply the rotation to the empty
    empty.rotation_euler = rotation.to_euler()

    # Step 4: Scale the empty based on the distance from A to B
    distance = direction.length
    empty.scale = (distance, distance, distance)  # Scale uniformly along all axes
    
    return empty
    
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
            #self.report({'INFO'}, f"s: {s}, max: {max}, activeNode.taper: {activeNode.taper}") # ERROR HERE: taper = 0 !!!
            sum = max
        
        if len(activeNode.branches) > 0:
            for c in activeNode.branches:
                for n in c:
                    calculateRadius(self, n, sum, branchTipRadius)
                    
        if sum < maxRadius:
            activeNode.radius = sum
            #self.report({'INFO'}, f"activeNode.radius = sum = {sum}")
        else:
            activeNode.radius = maxRadius
            #self.report({'INFO'}, f"activeNode.radius = maxRadius = {maxRadius}")
        return sum
    else:
        activeNode.radius = branchTipRadius
        #self.report({'INFO'}, f"activeNode.radius = branchTipRadius = {branchTipRadius}")
        return branchTipRadius
    

#nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, 0.5, context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0]

def splitRecursive(startNode, nrSplits, splitAngle, splitPointAngle, variance, splitHeightInLevel, splitHeightVariation, splitLengthVariation, stemSplitMode, stemSplitRotateAngle, root_node, stemRingResolution, curvOffsetStrength, self, rootNode):
    #self.report({'INFO'}, f"splitRecursive! nrSplits: {nrSplits}")
    while len(splitHeightInLevel) < nrSplits:
        newHeight = splitHeightInLevel.add()
        newHeight.value = 0.5
    
    
    minSegments = math.ceil(math.log(nrSplits + 1, 2))
    #resampleSpline(root_node, min_segments, 0, 0, 1)

    splitProbabilityInLevel = [0.0] * nrSplits
    expectedSplitsInLevel = [0] * nrSplits
    
    #self.report({'INFO'}, f"nrSplits: {nrSplits}, splitHeightInLevel[0]: {splitHeightInLevel[0].value}")
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
    #self.report({'INFO'}, f"addAmount: {addAmount}, addToLevel: {addToLevel}, maxPossibleSplits: {maxPossibleSplits}")
    if addAmount > 0: # and expectedSplitsInLevel[addToLevel]: + addAmount <= maxPossibleSplits:
        expectedSplitsInLevel[addToLevel] += min(addAmount, maxPossibleSplits - expectedSplitsInLevel[addToLevel])

    splitProbabilityInLevel[addToLevel] = float(expectedSplitsInLevel[addToLevel]) / float(maxPossibleSplits)

    nodesInLevelNextIndex = [[] for _ in range(nrSplits + 1)]
    for n in range(len(startNode.next)):
        nodesInLevelNextIndex[0].append((startNode, n))
        
   # for i in range(nrSplits):
   #     self.report({'INFO'}, f"expectedSplitsInLevel[{i}]: {expectedSplitsInLevel[i]}") # ERROR HERE !!!
    
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
                    #if splitHeight < 0.0 or splitHeight > 1.0:
                        #self.report({'ERROR'}, f"splitHeight out of bounds! splitHeight: {splitHeight}")
                    #self.report({'INFO'}, f"splitRecursive: splitHeight: {splitHeight}")
                    #self.report({'INFO'}, f"splitRecursive(): stemSplitRotateAngle {stemSplitRotateAngle}")
                    maxSplitHeightUsed = max(maxSplitHeightUsed, level)
                    splitNode = split(
                        nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0],
                        nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][1],
                        splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, stemSplitMode, stemSplitRotateAngle, 0.0, stemRingResolution, curvOffsetStrength, self, rootNode)
                    #if splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0]:
                    #    nodeIndices.pop(indexToSplit) # error here !!! -> split at startNode possible!
                         #self.report({'INFO'}, f"in splitRecursive: splitNode == startNode")
                    #else: TEST!
                    nodeIndices.pop(indexToSplit)
                    nodesInLevelNextIndex[level + 1].append((splitNode, 0))
                    nodesInLevelNextIndex[level + 1].append((splitNode, 1))
                    splitsInLevel += 1
                    totalSplitCounter += 1
            safetyCounter += 1
            if safetyCounter > 100:
                self.report({'INFO'}, f"break!")
                break
    return maxSplitHeightUsed
            
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
    #self.report({'INFO'}, f"split! splitHeight: {splitHeight}")
    # Only split if there is a next node at the given index
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
                    calculateSplitData(splitNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
                else:
                    # TODO -> split at new node!!!
                    return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength, self, rootNode)
                    #return startNode
                   # self.report({'INFO'}, f"splitNode == startNode")
                #    if splitNode == rootNode:
                #        calculateSplitData(splitNode, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
               # self.report({'INFO'}, f"split at existing node")
                #return splitNode
            else:
                return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength, self, rootNode) # clusterIndex???
                
    self.report({'INFO'}, f"split failed! nrNodesToTip: {nrNodesToTip}, len(startNode.next): {len(startNode.next)}, nextIndex: {nextIndex}")
    return startNode

def splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength, self, rootNode):
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
    t0 = splitAfterNode.tangent[tangentIndex] # nextIndex + 1 if next.count > 1!!
    t1 = splitAfterNode.next[nextIndex].tangent[0]
    c0 = splitAfterNode.cotangent
    c1 = splitAfterNode.next[nextIndex].cotangent
    r0 = splitAfterNode.radius
    r1 = splitAfterNode.next[nextIndex].radius
    ring_res = splitAfterNode.ringResolution
    taper = splitAfterNode.taper
            
    # Spline interpolation (replace with your own if needed)
    newPoint = sampleSplineT(p0, p1, t0, t1, t)
    newTangent = sampleSplineTangentT(p0, p1, t0, t1, t)
    newCotangent = lerp(c0, c1, t)
    newRadius = lerp(r0, r1, t)
    newTvalGlobal = lerp(splitAfterNode.tValGlobal, splitAfterNode.next[nextIndex].tValGlobal, nrNodesToTip * splitHeight - splitAfterNodeNr)
    
    newTvalBranch = lerp(splitAfterNode.tValBranch, splitAfterNode.next[nextIndex].tValBranch, splitHeight);
    self.report({'INFO'}, f"in split(): splitAfterNode.tValBranch: {splitAfterNode.tValBranch}, splitAfterNode.next[nextIndex].tValBranch: {splitAfterNode.next[nextIndex].tValBranch}, newTvalBranch: {newTvalBranch}")
    
    newNode = node(newPoint, newRadius, newCotangent, splitAfterNode.clusterIndex, ring_res, taper, newTvalGlobal, newTvalBranch, splitAfterNode.branchLength)
    #drawDebugPoint(newPoint, 0.1)
    #self.report({'INFO'}, f"split: newNode.taper: {newNode.taper}")
    newNode.tangent.append(newTangent)
    # Insert new node in the chain
    newNode.next.append(splitAfterNode.next[nextIndex])
    splitAfterNode.next[nextIndex] = newNode
    
    # TODO: splitNode = newNode ???
    
    # ERROR: when splitHeightVariation is large !!!
    
    calculateSplitData(newNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
  #  self.report({'INFO'}, f"did split at new node!")
    return newNode

def calculateSplitData(splitNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, sMode, rotationAngle, stemRingResolution, curvOffsetStrength, self):
    
    n = splitNode
    nodesAfterSplitNode = 0
    
    while n.next:
        nodesAfterSplitNode += 1
        n = n.next[0]

    # Initialize splitAxis
    splitAxis = Vector((0, 0, 0))
    
    self.report({'INFO'}, f"split mode: {sMode}")

    if sMode.value == "HORIZONTAL":
        #splitAxis = splitNode.cotangent
        right = splitNode.tangent[0].cross(Vector((0.0, 0.0, 1.0)))
        drawDebugPoint(splitNode.point + right / 2.0, 0.1)
        splitAxis = right.cross(splitNode.tangent[0]).normalized()
        
        splitAxis = Quaternion(splitNode.tangent[0], random.uniform(-branchSplitAxisVariation, branchSplitAxisVariation)) @ splitAxis
        #drawDebugPoint(splitNode.point + splitAxis / 2.0, 0.1)

    elif sMode.value == "ROTATE_ANGLE":
        splitAxis = splitNode.cotangent.normalized()
        #self.report({'INFO'}, f"splitNode.tangent[0] {splitNode.tangent[0]}")
        ##self.report({'INFO'}, f"rotationAngle {rotationAngle}")
       # self.report({'INFO'}, f"level {level}")
       # self.report({'INFO'}, f"splitAxis {splitAxis}")
        #
        splitAxis = (Quaternion(splitNode.tangent[0], math.radians(rotationAngle) * level) @ splitAxis).normalized()

    else:
        self.report({'INFO'}, f"ERROR: invalid splitMode: {sMode.value}")
        splitAxis = splitNode.cotangent.normalized()
        if level % 2 == 1:
            splitAxis = (Quaternion(splitNode.tangent[0], math.radians(90)) @ splitAxis).normalized()

    splitDirA = (Quaternion(splitAxis, math.radians(splitPointAngle)) @ splitNode.tangent[0]).normalized()
    splitDirB = (Quaternion(splitAxis, -math.radians(splitPointAngle)) @ splitNode.tangent[0]).normalized()

    splitNode.tangent.append(splitDirA)
    splitNode.tangent.append(splitDirB)


    s = splitNode
    previousNodeA = splitNode
    previousNodeB = splitNode
    curv_offset = splitNode.tangent[0].normalized() * (s.next[0].point - s.point).length * (splitAngle / 360.0) * curvOffsetStrength

    for i in range(nodesAfterSplitNode):
        s = s.next[0]
        rel_pos = s.point - splitNode.point

        tangent_a = (Quaternion(splitAxis, math.radians(splitAngle)) @ s.tangent[0]).normalized()
        tangent_b = (Quaternion(splitAxis, -math.radians(splitAngle)) @ s.tangent[0]).normalized()
        cotangent_a = (Quaternion(splitAxis, math.radians(splitAngle)) @ s.cotangent).normalized()
        cotangent_b = (Quaternion(splitAxis, -math.radians(splitAngle)) @ s.cotangent).normalized()

        offset_a = (Quaternion(splitAxis, math.radians(splitAngle)) @ rel_pos)
        offset_a = offset_a * (1.0 + random.uniform(-1.0, 1.0) * splitLengthVariation)
        offset_b = (Quaternion(splitAxis, -math.radians(splitAngle)) @ rel_pos)
        offset_b = offset_b * (1.0 + random.uniform(-1.0, 1.0) * splitLengthVariation)

        # Assuming the class node has a constructor that matches the parameters
        
        
        ring_resolution = stemRingResolution

        nodeA = node(splitNode.point + offset_a + curv_offset, 1.0, cotangent_a, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength)
        nodeA.tangent.append(tangent_a)
        nodeB = node(splitNode.point + offset_b + curv_offset, 1.0, cotangent_b, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength)
        nodeB.tangent.append(tangent_b)

        if i == 0:
            splitNode.next[0] = nodeA # TEMP: switch ab
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

def lerp(a, b, t):
    return a + (b - a) * t

# sampleSplineT and sampleSplineTangentT should be defined as in your script


def addLeaves(self, treeGen, rootNode,        #     TODO: support multiple leaf clusters !!!
        treeGrowDir, 
        treeHeight, 
        leavesDensityList, 
        leafSizeList,
        leafAspectRatioList,
        leafParentClusterBoolListList, 
        leafStartHeightGlobalList, 
        leafEndHeightGlobalList, 
        leafStartHeightClusterList, 
        leafEndHeightClusterList, 
        leafVerticalAngleBranchStartList, 
        leafVerticalAngleBranchEndList, 
        leafRotateAngleBranchStartList,
        leafRotateAngleBranchEndList,
        leafTiltAngleBranchStartList,
        leafTiltAngleBranchEndList,
        leafAngleModeList, 
        leafTypeList, 
        leafMaterial):
            
    for leafClusterIndex in range(0, len(leavesDensityList)):
        treeGen.report({'INFO'}, f"leaf cluster: {leafClusterIndex}")
        
        startNodesNextIndexStartTvalEndTval = []
        branchNodesNextIndexStartTvalEndTval = []
        
        rootNode.getAllStartNodes(
            self, 
            startNodesNextIndexStartTvalEndTval, 
            branchNodesNextIndexStartTvalEndTval,
            -1, 
            leafStartHeightGlobalList[leafClusterIndex].value, # StartHeightGlobal, 
            leafEndHeightGlobalList[leafClusterIndex].value, # EndHeightGlobal, 
            leafStartHeightClusterList[leafClusterIndex].value, # StartHeightCluster, 
            leafEndHeightClusterList[leafClusterIndex].value, # EndHeightCluster, 
            leafParentClusterBoolListList, 
            leafClusterIndex)
            
        #for startNode in startNodesNextIndexStartTvalEndTval:
        #    drawDebugPoint(startNode.startNode.point, 0.1)
            
        if len(startNodesNextIndexStartTvalEndTval) > 0:
            segmentLengths = []
            totalLength = calculateSegmentLengthsAndTotalLength(self, treeGen, 
                                                                startNodesNextIndexStartTvalEndTval, 
                                                                segmentLengths, 
                                                                0.0, # StartHeightGlobal, 
                                                                1.0, # EndHeightGlobal, 
                                                                0.2, # StartHeightCluster, 
                                                                1.0) # EndHeightCluster, 
            
            nrLeaves = totalLength * leavesDensityList[leafClusterIndex].value
            treeGen.report({'INFO'}, f"leafCluster: {leafClusterIndex}: nrLeaves: {nrLeaves}, len(startNodes): {len(startNodesNextIndexStartTvalEndTval)}")
            
            leafFaces = []
            leafVertices = []
            leafUVs = []
            windingAngle = 0.0
            
            for leafIndex in range(0, int(nrLeaves)):
                leafPos = leafIndex * totalLength / nrLeaves
                
                data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, leafPos, treeGrowDir, rootNode, treeHeight, False)
                
                startPoint = data.startPoint
                #treeGen.report({'INFO'}, f"leafClusterIndex: {leafClusterIndex}, startPoint: {startPoint}")
                
                
                startNodeNextIndex = data.startNodeNextIndex
                startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                         data.startNode.next[startNodeNextIndex].point, 
                                                         data.tangent, 
                                                         data.startNode.next[startNodeNextIndex].tangent[0], 
                                                         data.t)
                                                         
                startPointRadius = lerp(data.startNode.radius, data.startNode.next[startNodeNextIndex].radius, data.t)
                                                         
                drawDebugPoint(startPoint, 0.03)
                
                verticalAngle = lerp(leafVerticalAngleBranchStartList[leafClusterIndex].value, leafVerticalAngleBranchEndList[leafClusterIndex].value, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                rotateAngle = lerp(leafRotateAngleBranchStartList[leafClusterIndex].value, leafRotateAngleBranchEndList[leafClusterIndex].value, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                tiltAngle = lerp(leafTiltAngleBranchStartList[leafClusterIndex].value, leafTiltAngleBranchEndList[leafClusterIndex].value, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
    
                offset = 0.0
                factor = math.cos(math.radians(verticalAngle))        
                #if factor != 0.0:
                #    offset = startPointRadius / factor
                offset = startPointRadius    
                
                
                #centerDir = Quaternion(startPointTangent.cross(data.outwardDir), math.radians(-verticalAngle)) @ data.outwardDir # for symmetric!
                                
                right = startPointTangent.cross(Vector((0.0,0.0,1.0)))
                if right.length > 0.001:
                    right = right.normalized()
                else:
                    #vertical
                    right = data.outwardDir
                
                
                #drawArrow(startPoint, startPoint + right)
                
                leafTangent = Quaternion(right, math.radians(verticalAngle)) @ startPointTangent
                leafCotangent = right
                
                #treeGen.report({'INFO'}, f"leafClusterIndex: {leafClusterIndex}, startPointTangent: {startPointTangent}") 
                
                if leafTypeList[leafClusterIndex].value == "SINGLE":
                    if leafAngleModeList[leafClusterIndex].value == "ALTERNATING":
                        axis = right.cross(startPointTangent)
                        if leafIndex % 2 == 0:
                            leafTangent = Quaternion(axis, math.radians(rotateAngle)) @ leafTangent
                            leafCotangent = Quaternion(axis, math.radians(rotateAngle)) @ leafCotangent
                            leafCotangent = Quaternion(leafTangent, math.radians(tiltAngle)) @ leafCotangent
                        else:
                            leafTangent = Quaternion(axis, math.radians(-rotateAngle)) @ leafTangent
                            leafCotangent = Quaternion(axis, math.radians(-rotateAngle)) @ leafCotangent
                            leafCotangent = Quaternion(leafTangent, math.radians(-tiltAngle)) @ leafCotangent
                    
                    if leafAngleModeList[leafClusterIndex].value == "WINDING":
                        axis = startPointTangent
                        leafTangent = Quaternion(axis, math.radians(windingAngle)) @ leafTangent
                        leafCotangent = Quaternion(axis, math.radians(windingAngle)) @ leafCotangent
                        #leafCotangent = Quaternion(leafTangent, math.radians(tiltAngle)) @ leafCotangent #TODO
                        leafCotangent = Quaternion(leafTangent, math.radians(-tiltAngle) * math.sin(math.radians(windingAngle))) @ leafCotangent
                        
                    drawDebugPoint(startPoint + offset * leafTangent, 0.01)
                    
                    leafVertices.append(startPoint - leafCotangent *  leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value / 2.0 + leafTangent * offset)
                    leafVertices.append(startPoint - leafCotangent *  leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value / 2.0 + leafTangent   * (leafSizeList[leafClusterIndex].value + offset))
                    leafVertices.append(startPoint + leafCotangent *  leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value / 2.0 + leafTangent   * (leafSizeList[leafClusterIndex].value + offset))
                    leafVertices.append(startPoint + leafCotangent *  leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value / 2.0 + leafTangent * offset)
                    leafFaces.append((4 * leafIndex, 4 * leafIndex + 1, 4 * leafIndex + 2, 4 * leafIndex + 3))
                    
                    leafUVs.append((0.0,0.0))
                    leafUVs.append((0.0,1.0))
                    leafUVs.append((1.0,1.0))
                    leafUVs.append((1.0,0.0))
                        
                            
                    
                if leafTypeList[leafClusterIndex].value == "OPPOSITE":
                    if leafAngleModeList[leafClusterIndex].value == "ALTERNATING":
                        axis = right.cross(startPointTangent)
                        
                        leafTangentA = Quaternion(axis, math.radians(rotateAngle)) @ leafTangent
                        leafCotangentA = Quaternion(axis, math.radians(rotateAngle)) @ leafCotangent
                        leafCotangentA = Quaternion(leafTangent, math.radians(tiltAngle)) @ leafCotangentA
                        
                        leafTangentB = Quaternion(axis, math.radians(-rotateAngle)) @ leafTangent
                        leafCotangentB = Quaternion(axis, math.radians(-rotateAngle)) @ leafCotangent
                        leafCotangentB = Quaternion(leafTangent, math.radians(-tiltAngle)) @ leafCotangentB
                    
                        drawDebugPoint(startPoint + offset * leafTangentA, 0.01)
                    
                        leafVertices.append(startPoint - leafCotangentA * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentA * offset)
                        leafVertices.append(startPoint - leafCotangentA * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentA * (leafSizeList[leafClusterIndex].value + offset))
                        leafVertices.append(startPoint + leafCotangentA * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentA * (leafSizeList[leafClusterIndex].value + offset))
                        leafVertices.append(startPoint + leafCotangentA * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentA * offset)
                        leafFaces.append((8 * leafIndex, 8 * leafIndex + 1, 8 * leafIndex + 2, 8 * leafIndex + 3))
                        
                        
                        
                        leafVertices.append(startPoint + leafCotangentB * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentB * offset)
                        leafVertices.append(startPoint + leafCotangentB * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentB * (leafSizeList[leafClusterIndex].value + offset))
                        leafVertices.append(startPoint - leafCotangentB * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentB * (leafSizeList[leafClusterIndex].value + offset))
                        leafVertices.append(startPoint - leafCotangentB * leafSizeList[leafClusterIndex].value * leafAspectRatioList[leafClusterIndex].value + leafTangentB * offset)
                        
                        
                        leafFaces.append((8 * leafIndex + 4, 8 * leafIndex + 5, 8 * leafIndex + 6, 8 * leafIndex + 7))
                        
                        leafUVs.append((0.0,0.0))
                        leafUVs.append((0.0,1.0))
                        leafUVs.append((1.0,1.0))
                        leafUVs.append((1.0,0.0))
                         
                        leafUVs.append((0.0,0.0))
                        leafUVs.append((0.0,1.0))
                        leafUVs.append((1.0,1.0))
                        leafUVs.append((1.0,0.0))
                        
                    if leafAngleModeList[leafClusterIndex].value == "WINDING":
                        pass
                         
                
                if leafTypeList[leafClusterIndex].value == "WHORLED":
                    pass
                
                
                windingAngle += rotateAngle
                
                #drawArrow(startPoint, startPoint + leafTangent * leafSizeList[leafClusterIndex].value)
                #drawArrow(startPoint, startPoint + leafCotangent * leafSizeList[leafClusterIndex].value)
                #data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, leafPos, treeGrowDir, rootNode, treeHeight, False)
            
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
        
            #leafMaterial = bpy.data.materials.get("Leaf")
            #if leafMaterial is not None:
            leafObject.data.materials.clear()
            leafObject.data.materials.append(leafMaterial)
                


def addBranches(
self, 
treeGen, 
resampleDistance,

context, #ERROR: when treeGrowDir == (0,0,1) !!
rootNode, 
branchClusters,

branchClusterSettingsList,

#nrBranchesList, 
parentClusterBoolListList, 

treeGrowDir, 
treeHeight, 
#verticalAngleCrownStart, 
#
#verticalAngleCrownEnd, 
#verticalAngleBranchStart,
#verticalAngleBranchEnd,
#
#branchAngleModeList, 

#rotateAngleCrownStartList,
#rotateAngleCrownEndList,
#rotateAngleBranchStartList,
#rotateAngleBranchEndList,
                
#rotateAngleRangeList, 
#useFibonacciAnglesList,
#fibonacciNrList,
taper, 

#taperFactorList, 
#ringResolutionList, # ...TODO... -> use ringResolution! (init with resolution of stem /previous cluster!!!)
#relBranchLengthList,
#relBranchLengthVariationList,
#branchShapeList, 

#nrSplitsPerBranch, 
#splitsPerBranchVariation,
#branchSplitAngle, 

#branchSplitPointAngle, 
branchSplitHeightInLevel, #==branchSplitHeightInLevelList_0
branchSplitHeightInLevelList_1,
branchSplitHeightInLevelList_2,
branchSplitHeightInLevelList_3,
branchSplitHeightInLevelList_4,
branchSplitHeightInLevelList_5, 
                
#branchSplitHeightVariation,
#branchSplitLengthVariation,

#branchSplitMode,
#branchSplitRotateAngle,
#branchSplitAxisVariationList,
#branchCurvOffsetStrength,
#branchVariance, 

hangingBranchesList, 
#curvatureStartGlobalList, 
#curvatureEndGlobalList, 

noiseGenerator):
    
     
    
    #treeGen.report({'INFO'}, f"in add Branches(): len(nrBranchesList): {len(nrBranchesList)}, ")
    #if len(nrBranchesList) > 0 and len(branchesStartHeightGlobalList) > 0:
    for clusterIndex in range(0, branchClusters):
        nrBranches = branchClusterSettingsList[clusterIndex].nrBranches      
        branchesStartHeightGlobal = branchClusterSettingsList[clusterIndex].branchesStartHeightGlobal
        branchesEndHeightGlobal = branchClusterSettingsList[clusterIndex].branchesEndHeightGlobal
        branchesStartHeightCluster = branchClusterSettingsList[clusterIndex].branchesStartHeightCluster
        branchesEndHeightCluster = branchClusterSettingsList[clusterIndex].branchesEndHeightCluster
        
        #treeGen.report({'INFO'}, f"in add Branches() clusterIndex: {clusterIndex}")
        
        startNodesNextIndexStartTvalEndTval = []
        branchNodesNextIndexStartTvalEndTval = []
        branchNodes = []
        c = 0
        if clusterIndex - 1 >= 0:
            c = clusterIndex - 1
        else:
            c = clusterIndex
            
        for i in range(0, branchClusterSettingsList[clusterIndex].nrBranches):
            branchNodesNextIndexStartTvalEndTval.append([])
        
        treeGen.report({'INFO'}, f"calling rootNode.getAllStartNodes(), clusterIndex: {clusterIndex}")
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
            
       #     def getAllStartNodes(
       # self, 
       # treeGen, 
       # startNodesNextIndexStartTvalEndTval, 
       # branchNodesNextIndexStartTvalEndTval, 
       # activeBranchIndex, 
       # startHeightGlobal, 
       # endHeightGlobal, 
       # startHeightCluster, 
       # endHeightCluster, 
       # parentClusterBoolListList, 
       # newClusterIndex):
            
        #if clusterIndex == 1:
        #    for startNode in startNodesNextIndexStartTvalEndTval:
        #        drawDebugPoint(startNode.startNode.point, 0.1)
            
        #treeGen.report({'INFO'}, f"in addBranches(): clusterIndex: {clusterIndex}, len(startNodes): {len(startNodesNextIndexStartTvalEndTval)}, len(branchNodes): {len(branchNodesNextIndexStartTvalEndTval)}")
        
        #for info in startNodesNextIndexStartTvalEndTval:
            #treeGen.report({'INFO'}, f"startNode.point: {info.startNode.point}, startTval: {info.startTval}, endTval: {info.endTval}")
        
        #           def getAllStartNodes(
     #   self, 
     #   treeGen, 
     #   startNodesNextIndexStartTvalEndTval, 
     #   branchNodesNextIndexStartTvalEndTval, 
     #   activeBranchIndex, 
     #   startHeightGlobal, 
     #   endHeightGlobal, 
     #   startHeightCluster, 
     #   endHeightCluster, 
     #   parentClusterBoolListList, 
     #   newClusterIndex):
        
        if len(startNodesNextIndexStartTvalEndTval) > 0:
            segmentLengths = []
           # treeGen.report({'INFO'}, f"len(startNodesNextIndexStartTvalEndTval): {len(startNodesNextIndexStartTvalEndTval)}")
            #for info in startNodesNextIndexStartTvalEndTval:
                #treeGen.report({'INFO'}, f"startTval: {info.startTval}, endTval: {info.endTval}")
            #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex} -> calling calculateSegmentLenghsAndTotalLength(): len(segmentLengths): {len(segmentLengths)}")
            totalLength = calculateSegmentLengthsAndTotalLength(self, treeGen, startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal, branchesEndHeightGlobal, branchesStartHeightCluster, branchesEndHeightCluster)
            #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex}, totalLength: {totalLength}") 
            
            windingAngle = 0.0
            for branchIndex in range(0, nrBranches):
                branchPos = branchIndex * totalLength / nrBranches
                #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex}, branchPos: {branchPos}") 
                
                data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False)
                
                startPoint = data.startPoint
                #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex}, startPoint: {startPoint}")
                drawDebugPoint(startPoint, 0.04)
                
                startNodeNextIndex = data.startNodeNextIndex
                startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                         data.startNode.next[startNodeNextIndex].point, 
                                                         data.tangent, 
                                                         data.startNode.next[startNodeNextIndex].tangent[0], 
                                                         data.t)
                                                         
                branchStartTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                
                globalVerticalAngle = lerp(branchClusterSettingsList[clusterIndex].verticalAngleCrownStart, branchClusterSettingsList[clusterIndex].verticalAngleCrownEnd, data.startNode.tValGlobal)
                
                branchVerticalAngle = lerp(branchClusterSettingsList[clusterIndex].verticalAngleBranchStart, branchClusterSettingsList[clusterIndex].verticalAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                verticalAngle = globalVerticalAngle + branchVerticalAngle
                #treeGen.report({'INFO'}, f"in add Branches: branchStartTvalGlobal: {branchStartTvalGlobal}, globalVerticalAngle: {globalVerticalAngle}, verticalAngle: {verticalAngle}")
                
                globalRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleCrownStart, branchClusterSettingsList[clusterIndex].rotateAngleCrownEnd, branchStartTvalGlobal)
                
                
                branchRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleBranchStart, branchClusterSettingsList[clusterIndex].rotateAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t)) # tValBranch == 0 !!!
                
                #treeGen.report({'INFO'}, f"in add Branches: rotateAngleBranchStartList: {rotateAngleBranchStartList[clusterIndex].value:.3f}, rotateAngleBranchEndList: {rotateAngleBranchEndList[clusterIndex].value:.3f}")
                #treeGen.report({'INFO'}, f"in add Branches: branchRotateAngle: {branchRotateAngle}, data.t: {data.t:.3f}, data.startNode.tValBranch: {data.startNode.tValBranch:.3f}, data.startNode.next[data.startNodeNextIndex].tValBranch: {data.startNode.next[data.startNodeNextIndex].tValBranch:.3f}")
                
                #treeGen.report({'INFO'}, f"in add Branches: clusterIndex: {clusterIndex}, rotateAngleBranchStart: {rotateAngleBranchStartList[clusterIndex].value}, rotateAngleBranchEnd: {rotateAngleBranchEndList[clusterIndex].value}, tValBranch: {data.startNode.tValBranch}, branchRotateAngle: {branchRotateAngle}, globalRotateAngle: {globalRotateAngle}")
                
                #treeGen.report({'INFO'}, f"in add Branches: rotateAngleRange: {rotateAngleRangeList[clusterIndex].value}")
                
                if branchClusterSettingsList[clusterIndex].rotateAngleRange == 0.0:
                    branchClusterSettingsList[clusterIndex].rotateAngleRange = 180.0
                
                
                
                #treeGen.report({'INFO'}, f"in add Branches: outwardDir: {data.outwardDir}")
                #treeGen.report({'INFO'}, f"in add Branches: centerDir: {centerDir}")
                #treeGen.report({'INFO'}, f"in add Branches: angleMode: {branchAngleModeList[0].value}")
                
                #treeGen.report({'INFO'}, f"in add Branches: clusterIndex: {clusterIndex}, branchClusters: {branchClusters}")
                if branchClusterSettingsList[clusterIndex].branchAngleMode.value == "WINDING":
                    
                    centerDir = data.outwardDir # for symmetric!
                    #drawArrow(startPoint, startPoint + data.outwardDir)
                
                
                    #drawArrow(startPoint, startPoint + centerDir * 2.5) #???
                
                    if branchClusterSettingsList[clusterIndex].useFibonacciAngles == True:
                
                        
                        #if rotateAngleRangeList[clusterIndex].value > 0:
                        angle = (windingAngle + 360.0) % 360.0
                        treeGen.report({'INFO'}, f"useFibonacci = true: in add Branches: windingAngle: {windingAngle}, angle: {angle}")
                        #else:
                        #    angle = 0.0
                        right = startPointTangent.cross(Vector((1.0,0.0,0.0))).normalized() # -> most likely vertical
                    else:
                        #treeGen.report({'INFO'}, f"in add Branches: fibonacciNrList[clusterIndex].rotate_angle_range: {fibonacciNrList[clusterIndex].rotate_angle_range}")
                        #treeGen.report({'INFO'}, f"in add Branches: windingAngle: {windingAngle}")
                        if branchClusterSettingsList[clusterIndex].rotateAngleRange <= 0.0:
                            branchClusterSettingsList[clusterIndex].rotateAngleRange = 180.0
                        angle = windingAngle % branchClusterSettingsList[clusterIndex].rotateAngleRange + branchClusterSettingsList[clusterIndex].rotateAngleOffset - branchClusterSettingsList[clusterIndex].rotateAngleRange / 2.0
                        #treeGen.report({'INFO'}, f"in add Branches: angle: {angle}")
                        
                        right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                        
                    treeGen.report({'INFO'}, f"WINDING: right: {right}")
                    axis = right.cross(startPointTangent).normalized()
                    #axis = startPointTangent.cross(data.outwardDir)
                    branchDir = Quaternion(axis, math.radians(-verticalAngle)) @ startPointTangent
                    treeGen.report({'INFO'}, f"WINDING: angle: {angle}, axis startPointTangent: {startPointTangent}, branchDir: {branchDir}")
                    branchDir = Quaternion(startPointTangent, math.radians(angle)) @ branchDir
                    
                # if context.scene.useFibonacciAnglesList[clusterIndex].value == True:
                #     windingAngle += context.scene.fibonacciNrList[clusterIndex].fibonacci_angle
                # else:
                #     windingAngle += rotateAngle
                   
                if branchClusterSettingsList[clusterIndex].branchAngleMode == "SYMMETRIC":
                    centerDir = Quaternion(startPointTangent.cross(data.outwardDir), math.radians(-verticalAngle)) @ data.outwardDir # for symmetric!
                    axis = startPointTangent.cross(centerDir).normalized()
                    
                    rotateAngle = (globalRotateAngle + branchRotateAngle)
                    
                    if branchIndex % 2 == 0:
                        #drawArrow(startPoint, startPoint + startPointTangent)
                        right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                        axis = right.cross(startPointTangent).normalized()
                        branchDir = Quaternion(axis, math.radians(-verticalAngle)) @ startPointTangent
                        #drawArrow(startPoint, startPoint + startPointTangent * 2.0)
                        branchDir = Quaternion(startPointTangent, math.radians(-rotateAngle)) @ branchDir
                    else:
                        #drawArrow(startPoint, startPoint + startPointTangent)
                        right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                        axis = right.cross(startPointTangent).normalized()
                        #drawArrow(startPoint, startPoint + axis * 2.0)
                        branchDir = Quaternion(axis, math.radians(verticalAngle)) @ startPointTangent
                        #drawArrow(startPoint, startPoint + startPointTangent * 2.0)
                        branchDir = Quaternion(startPointTangent, math.radians(rotateAngle)) @ branchDir
                        
                branchCotangent = Vector((0.0, 0.0, 0.0))            
                #There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem
             
                if branchDir.x != 0.0:
                    branchCotangent = Vector((-branchDir.y, branchDir.x, 0.0))
                else:
                    if branchDir.y != 0.0:
                        branchCotangent = Vector((0.0, -branchDir.z, branchDir.y))
                    else:
                        branchCotangent = Vector((branchDir.z, 0.0, -branchDir.y))
    
                startTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                shapeRatioValue = shapeRatio(self, context, startTvalGlobal, branchClusterSettingsList[clusterIndex].branchShape.value)
                branchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * random.uniform(-1.0, 1.0)) * shapeRatioValue
                
                #class node():
                #   def __init__(self, Point, Radius, Cotangent, RingResolution, Taper, TvalGlobal, TvalBranch):
                
                #treeGen.report({'INFO'}, f"in addBranches(): branch node.tValGlobal: {data.startNode.tValGlobal}")
                # ERROR HERE !!  ->  should be start Height!  -> WRONG! do not use data.startNode.tValGlobal!
                
                
                
                branch = node(data.startPoint, 
                              1.0, 
                              branchCotangent, 
                              clusterIndex, 
                              branchClusterSettingsList[clusterIndex].ringResolution, # -> branchClusterSettingsList[clusterIndex].ringResolution
                              taper * branchClusterSettingsList[clusterIndex].taperFactor, 
                              startTvalGlobal, #tValGlobal
                              0.0, 
                              branchLength)
                
                
                #class node():
                #   def __init__(self, 
                #                Point, 
                #                Radius, 
                #                Cotangent, 
                #                ClusterIndex, 
                #                RingResolution, 
                #                Taper, 
                #                TvalGlobal, 
                #                TvalBranch, 
                #                BranchLength):
                #       self.point = Point
                #       self.radius = Radius
                #       self.tangent = []
                #       self.cotangent = Cotangent
                #       self.clusterIndex = ClusterIndex
                #       self.ringResolution = RingResolution
                #       self.taper = Taper
                #       self.tValGlobal = TvalGlobal
                #       self.tValBranch = TvalBranch
                #       self.next = []
                #       self.branches = []
                #       self.branchLength = BranchLength
                
                branch.tangent.append(branchDir)
                branch.tValBranch = 0.0
            
                #branchLength = 0.0
                nextIndex = startNodesNextIndexStartTvalEndTval[data.startNodeIndex].nextIndex
                
                
                
                #treeGen.report({'INFO'}, f"in add Branches: branchLength: {branchLength}, shapeRatio: {shapeRatioValue}")
                
                
                # TODO
                #lengthToTip = data.startNode.lengthToTip()
                #lengthToTop -= data.t * (data.startNode.next[data.startNodeNextIndex].point - data.startNode.point).length
                #if branchLength > lengthToTip:
                #    branchLength = lengthToTip 
            
                #branch = node(data.startPoint, 1.0, branchCotangent, ringResolution, taper, data.startNode.tValGlobal, 0.0)
                
                #treeGen.report({'INFO'}, f"in addBranches(): data.startNode.tValGlobal: {data.startNode.tValGlobal}")
                
                branchNext = node(data.startPoint + branchDir * branchLength, 
                                  1.0, 
                                  branchCotangent, 
                                  clusterIndex, 
                                  branchClusterSettingsList[clusterIndex].ringResolution, 
                                  taper * branchClusterSettingsList[clusterIndex].taperFactor, 
                                  data.startNode.tValGlobal, 
                                  0.0, 
                                  branchLength)
                branchNext.tangent.append(branchDir)
                branchNext.tValBranch = 1.0
                branch.next.append(branchNext)
                
                #drawDebugPoint(data.startPoint + branchDir * branchLength, 0.1)
                
                if len(data.startNode.branches) < startNodeNextIndex + 1:
                    for m in range(len(data.startNode.next)):
                        data.startNode.branches.append([])
                    
                data.startNode.branches[startNodeNextIndex].append(branch)
                branchNodes.append(branch)
                
                if branchClusterSettingsList[clusterIndex].useFibonacciAngles == True:
                    windingAngle += branchClusterSettingsList[clusterIndex].fibonacciNr.fibonacci_angle
                    treeGen.report({'INFO'}, f"in addBranches: windingAngle += {branchClusterSettingsList[clusterIndex].fibonacciNr.fibonacci_angle}")
                else:
                    rotateAngle = (globalRotateAngle + branchRotateAngle) % branchClusterSettingsList[clusterIndex].rotateAngleRange
                    # fibonacciNrList[clusterIndex].rotate_angle_range # branchClusterSettingsList
                    windingAngle += rotateAngle
        
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
                
        
        if hangingBranchesList[clusterIndex].value == False:
            nrSplits = 0
            if branchClusterSettingsList[clusterIndex].nrSplitsPerBranch > 0.0: # [clusterIndex]
                
                
                
                nrSplits = int(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches)
                
                treeGen.report({'INFO'}, f"in add Branches: nrSplits: {nrSplits}")
                length = len(splitHeightInLevelList)
                if length < int(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches):
                    for i in range(length, nrSplits):
                        newHeight = splitHeightInLevelList.add()
                        newHeight = 0.5
                
            maxSplitHeightUsed = splitBranches(treeGen,
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
                                                
                                                branchClusterSettingsList[clusterIndex].branchSplitMode, 
                                                branchClusterSettingsList[clusterIndex].branchSplitRotateAngle,
                                                
                                                branchClusterSettingsList[clusterIndex].ringResolution, 
                                                0.0,#branchCurvOffsetStrength[0], #TODO: variable for each branch cluster... 
                                                branchClusterSettingsList[clusterIndex].branchVariance, 
                                                
                                                branchClusterSettingsList[clusterIndex].branchSplitAxisVariation, 
                                                False, 
                                      
                                                branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                                                branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd)
                                                
                  #      def splitBranches(treeGen, 
                  # rootNode, 
                  # branchCluster, 
                  # nrBranchSplits, # = int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value)
                  #                 # used because branchSplitHeightInLevel needs max possible nrBranchSplits!
                  # 
                  # splitAngle, 
                  # splitPointAngle, 
                  # nrSplitsPerBranch, 
                  # 
                  # splitsPerBranchVariation, 
                  # branchSplitHeightInLevel, # == branchSplitHeightInLevelList_0
                  # branchSplitHeightVariation, 
                  # branchSplitLengthVariation, 
                  # 
                  # branchSplitMode, 
                  # branchSplitRotateAngle, 
                  # 
                  # stemRingResolution, 
                  # curvOffsetStrength, 
                  # variance, 
                  # 
                  # branchSplitAxisVariation, 
                  # hangingBranches,
                  # 
                  # curvatureStartGlobal, 
                  # curvatureEndGlobal):
                                      
            context.scene.maxSplitHeightUsed = max(context.scene.maxSplitHeightUsed, maxSplitHeightUsed)       
                
            for branchNode in branchNodes:
                
                branchNode.resampleSpline(rootNode, treeGen, resampleDistance)
                
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
                                          0, 
                                          context.scene.maxCurveSteps)
                                          
                #def applyCurvature(
        # self, 
        # treeGen, 
        # rootNode, 
        # treeGrowDir, 
        # treeHeight, 
        # curvatureStartGlobal,
        # curvatureStartBranch,
        # curvatureEndGlobal, 
        # curvatureEndBranch,
        # clusterIndex, 
        # branchStartPoint, 
        # curveStep,
        # maxCurveSteps):
                
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
                                      
    #def applyNoise(
        # self, 
        # treeGen, 
        # noise_generator, 
        # noiseAmplitudeHorizontal,
        # noiseAmplitudeVertical, 
        # noiseAmplitudeGradient, 
        # noiseAmplitudeExponent,
        # noiseScale, 
        # prevPoint, 
        # treeHeight):
                                      
                                          
        else: #hangingBranchesList[clusterIndex].value == True:
            for branchNode in branchNodes:
                
                #branchNode.resampleSpline(rootNode, treeGen, resampleDistance)
                
                branchNode.hangingBranches(treeGen, 
                                           branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                                           branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd)
            
                # TODO -> split() -> splitNode.hangingBranches() after each split!
                if nrSplitsPerBranch != None:
                    if len(nrSplitsPerBranch) > 0: # > clusterIndex:
                        if branchClusterSettingsList[clusterIndex].nrSplitsPerBranch > 0.0: # [clusterIndex]
                            
                            maxSplitHeightUsed = splitBranches(treeGen,
                                          rootNode, 
                                          clusterIndex, 
                                          int(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches), 
                                          
                                          branchClusterSettingsList[clusterIndex].branchSplitAngle, 
                                          branchClusterSettingsList[clusterIndex].branchSplitPointAngle, 
                                          branchClusterSettingsList[clusterIndex].nrSplitsPerBranch, 
                                          
                                          branchClusterSettingsList[clusterIndex].splitsPerBranchVariation, 
                                          branchSplitHeightInLevel, # == branchSplitHeightInLevelList_0
                                          branchClusterSettingsList[clusterIndex].branchSplitHeightVariation, 
                                          branchClusterSettingsList[clusterIndex].branchSplitLengthVariation,
                                          
                                          branchClusterSettingsList[clusterIndex].branchSplitMode.value, 
                                          branchClusterSettingsList[clusterIndex].branchSplitRotateAngle,
                                          
                                          branchClusterSettingsList[clusterIndex].ringResolution, 
                                          0.0,#branchCurvOffsetStrength[0], #TODO: variable for each branch cluster... 
                                          branchClusterSettingsList[clusterIndex].branchVariance, 
                                          
                                          branchClusterSettingsList[clusterIndex].branchSplitAxisVariation, 
                                          True, 
                                          
                                          branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                                          branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd)
                                          
                            contexe.scene.maxSplitHeightUsed = max(context.scene.maxSplitHeightUsed, maxSplitHeightUsed)
                
                if branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch > 0.0 or branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch > 0.0:
                    branchNode.applyNoise(treeGen, 
                                          noiseGenerator,
                                          branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchGradient, 
                                          branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch, 
                                          branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch, 
                                          branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchExponent, 
                                          branchClusterSettingsList[clusterIndex].noiseScale, 
                                          branchNode.point - (branchNode.next[0].point - branchNode.point), 
                                          branchLength)
                                      
                #def splitBranches(treeGen, 
                #  rootNode, 
                #  branchCluster, 
                #  nrBranchSplits, # = int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value)
                #                  # used because branchSplitHeightInLevel needs max possible nrBranchSplits!
                #  
                #  splitAngle, 
                #  splitPointAngle, 
                #  nrSplitsPerBranch, 
                #  
                #  splitsPerBranchVariation, 
                #  branchSplitHeightInLevel, # == branchSplitHeightInLevelList_0
                #  branchSplitHeightVariation, 
                #  branchSplitLengthVariation, 
                #  
                #  branchSplitMode, 
                #  branchSplitRotateAngle, 
                #  
                #  stemRingResolution, 
                #  curvOffsetStrength, 
                #  variance, 
                #  
                #  branchSplitAxisVariation, 
                #  hangingBranches,
                #  
                #  curvatureStartGlobal, 
                #  curvatureEndGlobal):
                      
                      
            
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
                  hangingBranches,
                  
                  curvatureStartGlobal, 
                  curvatureEndGlobal):
                      
    allBranchNodes = []
    
    maxSplitHeightInLevelUsed = 0
    
    rootNode.getAllBranchStartNodes(treeGen, allBranchNodes, branchCluster) #0)# ERROR HERE ???
    treeGen.report({'INFO'}, f"in split Branches(): branchCluster: {branchCluster}, nrSplits: {nrBranchSplits}, len(allBranchNodes): {len(allBranchNodes)}, hangingBranches: {hangingBranches}, branchVariance: {variance}")
    
    #################################
    floatSplitsForBranch = [nrSplitsPerBranch for i in range(len(allBranchNodes))]
    splitsForBranch = [0 for i in range(len(allBranchNodes))]
    # -> splitsPerBranchVariation..
    
    branchLengths = []
    branchWeights = []
    totalLength = 0.0
    totalWeight = 0.0
    for i in range(len(allBranchNodes)):
        length = allBranchNodes[i].lengthToTip()
        branchLengths.append(length)
        totalLength += length
        #weight = pow(length, 8.0)
        weight = pow(length, 2.0)
        branchWeights.append(weight)
        totalWeight += weight
    treeGen.report({'INFO'}, f"len(allBranchNodes): {len(allBranchNodes)}")
    for i in range(len(allBranchNodes)):
        treeGen.report({'INFO'}, f"start of loop: i: {i}, len(allBranchNodes): {len(allBranchNodes)}")
        
        treeGen.report({'INFO'}, f"floatSplitsForBranch[i]: {floatSplitsForBranch[i]}, splitsPerBranchVariation: {splitsPerBranchVariation}")
        
        # nrBranchSplits = int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value)
        
        splitsForBranch[i] = int(round(nrBranchSplits * branchWeights[i] / totalWeight + random.uniform(-splitsPerBranchVariation * floatSplitsForBranch[i], splitsPerBranchVariation * floatSplitsForBranch[i])))
        treeGen.report({'INFO'}, f"splitsForBranch[{i}]: {splitsForBranch[i]}")
        
        #TODO: ~branch length...
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
        #if meanLevel == 0:
        #    meanLevel = 1
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
        treeGen.report({'INFO'}, f"i: {i}, len(allBranchNodes): {len(allBranchNodes)}")
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
                treeGen.report({'INFO'}, f"addToLevel: {j} -> break!")
                break
            maxPossibleSplits *= 2
        addAmount = splitsForBranch[i] - totalExpectedSplits
        #self.report({'INFO'}, f"addAmount: {addAmount}, addToLevel: {addToLevel}, maxPossibleSplits: {maxPossibleSplits}")
        if addAmount > 0: # and expectedSplitsInLevel[addToLevel]: + addAmount <= maxPossibleSplits:
            expectedSplitsInLevel[addToLevel] += min(addAmount, maxPossibleSplits - expectedSplitsInLevel[addToLevel])

        splitProbabilityInLevel[addToLevel] = float(expectedSplitsInLevel[addToLevel]) / float(maxPossibleSplits)
        
        for e in expectedSplitsInLevel:
            treeGen.report({'INFO'}, f"expected splits: {e}")
        
        nodesInLevelNextIndex = [[] for _ in range(splitsForBranch[i] + 1)]
        
        for n in range(len(allBranchNodes[i].next)):
            nodesInLevelNextIndex[0].append((allBranchNodes[i], n))
            
        treeGen.report({'INFO'}, f"splitsForBranch[{i}]: {splitsForBranch[i]}, len(splitsForBranch): {len(splitsForBranch)}")
        
        splitCounter = 0
        for level in range(splitsForBranch[i]):
            treeGen.report({'INFO'}, f"in level: {i}")
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
                        if h * splitHeight < 0:
                            splitHeight = max(splitHeight + h * branchSplitHeightVariation, 0.05)
                        else:
                            splitHeight = min(splitHeight + h * branchSplitHeightVariation, 0.95)
                        
                        splitNode = split(
                            nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0],
                            nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][1], 
                            branchSplitHeightInLevel[level].value, 
                            branchSplitLengthVariation,
                            splitAngle,
                            splitPointAngle, 
                            level, 
                            branchSplitMode, 
                            branchSplitRotateAngle, 
                            branchSplitAxisVariation, 
                            stemRingResolution,
                            0.0, #curvOffsetStrength,
                            treeGen, 
                            rootNode)
                        
                        if splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0]:
                            #did not split
                            totalWeight -= branchWeights[indexToSplit]
                            del branchWeights[indexToSplit]
                            del nodeIndices[indexToSplit]
                            treeGen.report({'INFO'}, "did not split!")
                        else:
                            treeGen.report({'INFO'}, f"index to remove: {indexToSplit}, len(nodeIndices): {len(nodeIndices)}, len(branchWeights): {len(branchWeights)}, level: {level}")
                            if maxSplitHeightInLevelUsed < level:
                                maxSplitHeightInLevelUsed = level
                            
                            nodesInLevelNextIndex[level + 1].append((splitNode, 0))
                            nodesInLevelNextIndex[level + 1].append((splitNode, 1))
                            
                            del nodeIndices[indexToSplit]
                            
                            splitsInLevel += 1
                            
    return maxSplitHeightInLevelUsed
    
                   
            
def shapeRatio(self, context, tValGlobal, treeShape):
    if treeShape == "CONICAL":
        return 0.2 + 0.8 * tValGlobal
    if treeShape == "SPHERICAL":
        return 0.2 + 0.8 * math.sin(math.pi * tValGlobal)
    if treeShape == "HEMISPHERICAL":
        return 0.2 + 0.8 * math.sin(0.5 * math.pi * tValGlobal)
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

def calculateSegmentLengthsAndTotalLength(self, treeGen, startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal, branchesEndHeightGlobal, branchesStartHeightCluster, branchesEndHeightCluster):
    #useTvalBranch == False
    totalLength = 0.0
    #treeGen.report({'INFO'}, f"in calculateSegmentLengthsAndTotalLength(): len(startNodesNextIndexStartTvalEndTval): {len(startNodesNextIndexStartTvalEndTval)}")
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
                #treeGen.report({'INFO'}, f"in calculateSegmentLengthsAndTotalLength(): tB_global: {tB_global}, branchesStartHeightGlobal: {branchesStartHeightGlobal} -> continue")
                continue
            if tA_global > branchesEndHeightGlobal:
                #treeGen.report({'INFO'}, f"in calculateSegmentLengthsAndTotalLength(): tB_global: {tB_global}, branchesEndHeightGlobal: {branchesEndHeightGlobal} -> continue")
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
        #treeGen.report({'INFO'}, f"in calculateSegmentLengthsAndTotalLength(): adding length: {segmentLengthAbove}")
        segmentLengths.append(segmentLengthAbove)
        totalLength += segmentLengthAbove
        
        #treeGen.report({'INFO'}, f"in calculateSegmentLengthsAndTotalLength(): adding length: {segmentLengthAbove}")
        
        
        # t-global only influences segmentLengths if segment is in stem! -> else only use t-branch !!!
        
        # TODO: hide branchesStartHeightCluster in BranchCluster 0 (and all clusters that only have stem as parent)!!!
        
            
    return totalLength


def generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, calledFromAddLeaves):
    accumLength = 0.0
    startNodeIndex = 0
    tVal = 0.0
    
    #self.report({'INFO'}, f"in generateStartPointData: branchPos: {branchPos}, len(SegmentLengths): {len(segmentLengths)}")
    
    for i in range(len(segmentLengths)):
        #self.report({'INFO'}, f"in generateStartPointData: segmentLengths[{i}]: {segmentLengths[i]}")
        if accumLength + segmentLengths[i] >= branchPos:
            startNodeIndex = i
            segStart = accumLength
            segLen = segmentLengths[i]
            #self.report({'INFO'}, f"in generateStartPointData: segmentLength: {segLen}") #OK
            if segLen > 0.0:
                tVal = (branchPos - segStart) / segLen
                #branchPos: [0 .. totalLength]
                #self.report({'INFO'}, f"in generateStartPointData: tVal: {tVal}")
            
            startTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].startTval
            endTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].endTval
            #self.report({'INFO'}, f"in generateStartPointData: startTval: {startTval}, endTval:{endTval}, segmentLength: {segmentLengths[i]}") 
            # startTval: 0.0, endTval:0.2, segmentLength: 6.18
            tVal = startTval + tVal * (endTval - startTval)
            break
        accumLength += segmentLengths[i]
        
    startNodeNextIndex = startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex
    nStart = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode
    tangent = (0.0, 0.0, 0.0)
    
    if len(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next) > 1:
        tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[startNodeNextIndex + 1]
    else:
        tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[0]
    
    startPoint = sampleSplineT(
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point,
        tangent,
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].tangent[0], 
        tVal)
    
    nextTangent = (treeGrowDir.normalized() * treeHeight - (rootNode.point + rootNode.tangent[0] * (treeGrowDir.normalized() * treeHeight - rootNode.point).length * (1.5 / 3.0))).normalized()
    
    centerPoint = sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0, 0.0, 1.0)), nextTangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);
    
    startPointCotangent = lerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent, 
                               startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, 
                               tVal)
    
    #outwardDir = lerp(
    #startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
    #startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, tVal) - centerPoint
    
    outwardDir = lerp(
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal) - centerPoint
    
       
    #treeGen.report({'INFO'}, f"in generateStartPointData: startNode.point: {startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point}")
    #treeGen.report({'INFO'}, f"in generateStartPointData: startNode.next[startNodeNextIndex].point: {startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point}")
    
    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = lerp(
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent,
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, 
            tVal)
            
        #self.report({'INFO'}, "in add Branches(): outwardDir is zero [0]")
        #tan index split! ERROR HERE !!!
        
    outwardDir.z = 0.0

    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = lerp(
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent,
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent,
            tVal)
        #self.report({'INFO'}, "in add Branches(): outwardDir is zero [1]")
        # print("outward_dir is zero, using cotangent: ", outward_dir)
    outwardDir = outwardDir.normalized()
    
    #self.report({'INFO'}, f"in generateStartPointData: startPoint: {startPoint}")
    #self.report({'INFO'}, f"in generateStartPointData: outwardDir: {outwardDir}")
    
    #drawDebugPoint(startPoint, 0.1)
    #drawDebugPoint(startPoint + outwardDir, 0.1)
    
    #self.report({'INFO'}, f"in add Branches(): startPoint: {startPoint}, outwardDir: {outwardDir}")
    #self.report({'INFO'}, f"in add Branches(): centerPoint: {centerPoint}")
    
    return startPointData(startPoint, tVal, outwardDir, nStart, startNodeIndex, startNodeNextIndex, tVal, tangent, startPointCotangent)

    #class startPointData():
    #def __init__(self, StartPoint, StartPointTvalGlobal, OutwardDir, StartNode, StartNodeIndex, StartNodeNextIndex, T, Tangent, Cotangent):
    
    # treeGen.report({'INFO'}, f"in addBranches(): branch node.tValGlobal: {data.startNode.tValGlobal}")
    # ERROR HERE !!  ->  should be start Height!
                
    


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
    return (-3.0 * (1.0 - t)**2.0 * start + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * end).normalized()

def lerp(a, b, t):
    return a + (b - a) * t
    
    
    
def generateVerticesAndTriangles(self, treeGen, context, segments, dir, taper, radius, ringSpacing, stemRingRes, taperFactor, branchTipRadius, barkMaterial):
    vertices = []
    faces = []
    
    offset = 0
    counter = 0
    
    startSection = 0
    
    for s in range(0, len(segments)):
        segmentLength = (segments[s].end - segments[s].start).length
        self.report({'INFO'}, f"in generateVerticesAndTriangles: segmentLength: {segmentLength}")
        if segmentLength > 0:
            sections = round(segmentLength / ringSpacing)
            if sections <= 0:
                sections = 1
            branchRingSpacing = segmentLength / sections
            
            if s > 0:
                if segments[s].connectedToPrevious == True and segments[s - 1].connectedToPrevious == False: # only on first segment 
                    #-> later connected segments: dont subtract stemRingRes again!
                    startSection = 1
                    offset -= stemRingRes # ERROR HERE (???)
                    self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == True, offset: {offset}, startSection = 1") 
                    if segments[s - 1].connectedToPrevious == True:
                        self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == True, offset: {offset}")
                if segments[s].connectedToPrevious == True and segments[s - 1].connectedToPrevious == True:
                    self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == True, previous.connectedToPrevious == True, offset: {offset}")
                    startSection = 1
                
                if segments[s].connectedToPrevious == False:
                    startSection = 0
                    offset = len(vertices)
                    self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == False, offset: {offset}, startSections = 0")
            else:
                self.report({'INFO'}, f"in generateVerticesAndTriangles: offset: {offset}")
                
            controlPt1 = segments[s].start + segments[s].startTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
            controlPt2 = segments[s].end - segments[s].endTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
        
            for section in range(startSection, sections + 1):
                pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections)
                tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections).normalized()
                dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / sections)
                dirB = (tangent.cross(dirA)).normalized()
                dirA = (dirB.cross(tangent)).normalized()
                
                #curveT_s = lerp(segments[s].startTvalGlobal, segments[s].endTvalGlobal, section / sections)
                #curveT_s1 = lerp(segments[s].startTvalGlobal, segments[s].endTvalGlobal, (section + 1) / sections)
                #tVal = lerp(curveT_s, curveT_s1, section / sections)
                
                #tVal = curveT_s
                #treeGen.report({'INFO'}, f"cluster: {segments[s].clusterIndex}: segments[{s}].startTvalBranch: {segments[s].startTvalBranch}")
                #treeGen.report({'INFO'}, f"cluster: {segments[s].clusterIndex}: segments[{s}].endTvalBranch: {segments[s].endTvalBranch}")
                
                #treeGen.report({'INFO'}, f"in generateVerticesAndTriangles(): segments[s].startTvalGlobal: {segments[s].startTvalGlobal}, segments[s].endTvalGlobal: {segments[s].endTvalGlobal}")
                tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / sections)
                # tVal: [0...1] along ALL segments! (OK, only 1 segment)
                
                tValBranch = segments[s].startTvalBranch + (segments[s].endTvalBranch - segments[s].startTvalBranch) * (section / sections)
                tValGlobal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].endTvalGlobal) * (section / sections)
                if segments[s].clusterIndex == -1:
                    #radius = sampleCurve(treeGen, tVal)
                    
                    taper = lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                    startRadius = segments[s].startRadius
                    endRadius = segments[s].endRadius
                    linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                    normalizedCurve = (1.0 - branchTipRadius) * tVal + sampleCurve(treeGen, tVal)
                    
                    radius = linearRadius * normalizedCurve
                else:
                    #treeGen.report({'INFO'}, f"taperFactor: {context.scene.taperFactorList[segments[s].clusterIndex].value}, tValBranch: {tValBranch}")
                    
                    #in node: node.taper = taper * taperFactor
                    
                    #radius = sampleCurve(treeGen, tValBranch) 
                    
                    taper = lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                    
                    startRadius = segments[s].startRadius
                    endRadius = segments[s].endRadius
                    
                    linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                    
                    normalizedCurve = (1.0 - branchTipRadius) * tValBranch + sampleCurve(treeGen, tValBranch) * context.scene.taperFactorList[segments[s].clusterIndex].value
                    
                    radius = linearRadius * normalizedCurve
                    
                    #branchLengthToTip = segments[s].branchLength * (1.0 - tValBranch)
                    #newTval = 1.0 - branchLengthToTip / segments[s].longestBranchLengthInCluster + tValBranch * (branchLengthToTip / segments[s].longestBranchLengthInCluster)
                    
                    
                    #radius = sampleCurve(treeGen, tValBranch) * context.scene.taperFactorList[segments[s].clusterIndex].value
                
                #ERROR HERE: # found segment n=0: p0.x: -0.5, p1.x: 0.0, p2.x: 0.5, p3.x: 1.0, x: 0.125
                             # found segment n=0: p0.y: 1.5, p1.y: 1.0, p2.y: 0.5, p3.y: 0.0, ist: py: 0.9375 = 1 - 0.125 / 2 OK
                    #                                                                         -> GeoGebra: x: 0.0625 ERROR HERE
                    #      -> double slope error ??? -> x value scaling error!                -> GeoGebra: y: 0.9375 OK
                
                #treeGen.report({'INFO'}, f"tVal: {tVal}, radius: {radius}, section: {section}, sections: {sections}")
                
                # if segments[s].clusterIndex == -1:
                #     radius = context.scene.taper * context.scene.treeHeight * radius
                # else:
                #     radius = taperFactor[segments[s].clusterIndex].value * lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing)) # TODO: taper curve for branches...
                
                #treeGen.report({'INFO'}, f"segments[s].ringResolution: {segments[s].ringResolution}")
                for i in range(0, segments[s].ringResolution):
                    angle = (2 * math.pi * i) / segments[s].ringResolution
                    x = math.cos(angle)
                    y = math.sin(angle)
                    
                    v = pos + dirA * radius * math.cos(angle) + dirB * radius * math.sin(angle)
                    
                    
                    #v = pos + dirA * lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing)) * math.cos(angle) + dirB * lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing)) * math.sin(angle)
                    
                    vertices.append(v)
                    #self.report({'INFO'}, f"in generateVerticesAndTriangles: len(vertices):  {len(vertices)}, startSection: {startSection}")
                    
                    counter += 1
            #self.report({'INFO'}, f"in generateVerticesAndTriangles: sections: {sections}")
            for c in range(0, sections): 
                #self.report({'INFO'}, f"section {c}")
                for j in range(0, segments[s].ringResolution):
                    faces.append((offset + c * (segments[s].ringResolution) + j,
                        offset + c * (segments[s].ringResolution) + (j + 1) % (segments[s].ringResolution), 
                        offset + c * (segments[s].ringResolution) + segments[s].ringResolution  + (j + 1) % (segments[s].ringResolution), 
                        offset + c * (segments[s].ringResolution) + segments[s].ringResolution  + j))
                    #self.report({'INFO'}, f"quad start index: {offset + c * (segments[s].ringResolution) + j}")
            
            offset += counter
            counter = 0
        
            
    
    meshData = bpy.data.meshes.new("treeMesh")
    meshData.from_pydata(vertices, [], faces)
    meshData.update()
    
    for polygon in meshData.polygons:
        polygon.use_smooth = True
    
    name = "tree"
    if name in bpy.data.objects:
        bpy.data.objects[name].data = meshData
        treeObject = bpy.data.objects[name]
        treeObject.select_set(True)
        self.report({'INFO'}, "object 'tree' found!")
    else:
        treeObject = bpy.data.objects.new("tree", meshData)
        bpy.context.collection.objects.link(treeObject)
        treeObject.select_set(True)
        self.report({'INFO'}, "no object 'tree' found!")
        
    #barkMaterial = bpy.data.materials.get("Bark")
    #if barkMaterial is not None:
    treeObject.data.materials.clear()
    treeObject.data.materials.append(barkMaterial)
                
class SimplexNoiseGenerator():
    def __init__(self, treeGen, seed=None):
        self.onethird = 1.0 / 3.0
        self.onesixth = 1.0 / 6.0

        # Initialize all required variables as instance variables
        self.A = [0, 0, 0]
        self.s = 0.0
        self.u = 0.0
        self.v = 0.0
        self.w = 0.0
        self.i = 0
        self.j = 0
        self.k = 0

        # Initialize the permutation table (T)
        if seed is None:
            self.T = [int((x * 0x10000) % 0xFFFFFFFF) for x in range(8)]
        else:
            #self.T = [int(val) for val in seed.split()]
            expandedSeed = []
            random.seed(seed) # set the seed
            self.T = [random.randint(0, 2**31 - 1) for _ in range(8)]
            
            for t in self.T:
                treeGen.report({'INFO'}, f"T: {t}")

    def coherent_noise(self, x, y, z, octaves=2, multiplier=25, amplitude=0.5, lacunarity=2, persistence=0.9):
        v3 = mathutils.Vector([x, y, z]) / multiplier
        val = 0.0
        for n in range(octaves):
            val += self.noise(v3.x, v3.y, v3.z) * amplitude
            v3 *= lacunarity
            amplitude *= persistence
        return val

    def noise(self, x, y, z):
        self.s = (x + y + z) * self.onethird
        self.i = self.fastfloor(x + self.s)
        self.j = self.fastfloor(y + self.s)
        self.k = self.fastfloor(z + self.s)

        self.s = (self.i + self.j + self.k) * self.onesixth
        self.u = x - self.i + self.s
        self.v = y - self.j + self.s
        self.w = z - self.k + self.s

        # Reset A at the start of each noise calculation
        self.A = [0, 0, 0]

        if self.u >= self.w:
            if self.u >= self.v:
                hi = 0
            else:
                hi = 1
        else:
            if self.v >= self.w:
                hi = 1
            else:
                hi = 2
                
        if self.u < self.w:
            if self.u < self.v:
                lo = 0
            else:
                lo = 1
        else:
            if self.v < self.w:
                lo = 1
            else:
                lo = 2
        
        return self.kay(hi) + self.kay(3 - hi - lo) + self.kay(lo) + self.kay(0)

    def kay(self, a):
        self.s = (self.A[0] + self.A[1] + self.A[2]) * self.onesixth
        x = self.u - self.A[0] + self.s
        y = self.v - self.A[1] + self.s
        z = self.w - self.A[2] + self.s
        t = 0.6 - x * x - y * y - z * z

        h = self.shuffle(self.i + self.A[0], self.j + self.A[1], self.k + self.A[2])
        self.A[a] += 1
        if t < 0:
            return 0
        b5 = h >> 5 & 1
        b4 = h >> 4 & 1
        b3 = h >> 3 & 1
        b2 = h >> 2 & 1
        b1 = h & 3

        p, q, r = self.get_pqr(b1, x, y, z)

        if b5 == b3:
            p = -p
        if b5 == b4:
            q = -q
        if b5 != (b4 ^ b3):
            r = -r
        t *= t
        if b1 == 0:
            return 8 * t * t * (p + q + r)
        if b2 == 0:
            return 8 * t * t * (q + r)
        return 8 * t * t * r

    def get_pqr(self, b1, x, y, z):
        if b1 == 1:
            p, q, r = x, y, z
        elif b1 == 2:
            p, q, r = y, z, x
        else:
            p, q, r = z, x, y
        return p, q, r

    def shuffle(self, i, j, k):
        return self.bb(i, j, k, 0) + self.bb(j, k, i, 1) + self.bb(k, i, j, 2) + self.bb(i, j, k, 3) + \
               self.bb(j, k, i, 4) + self.bb(k, i, j, 5) + self.bb(i, j, k, 6) + self.bb(j, k, i, 7)

    def bb(self, i, j, k, B):
        return self.T[self.b(i, B) << 2 | self.b(j, B) << 1 | self.b(k, B)]

    def b(self, N, B):
        return N >> B & 1

    def fastfloor(self, n):
        return int(n) if n > 0 else int(n) - 1


def update_fibonacci_numbers(self):
    fn0 = 1.0
    fn1 = 1.0
    self.rotate_angle_range = 360.0
    if self.fibonacci_nr > 2:
        for n in range(2, self.fibonacci_nr + 1):
            temp = fn0 + fn1
            fn0 = fn1
            fn1 = temp
    self.fibonacci_angle = 360.0 * (1.0 - fn0 / fn1)
    
    
class fibonacciProps(bpy.types.PropertyGroup):
    fibonacci_nr: bpy.props.IntProperty(name = "fibonacciNr", default=3, min=3, 
        update = lambda self, context:update_fibonacci_numbers(self))
        
    fibonacci_angle: bpy.props.FloatProperty(name="", default=0.0, options={'HIDDEN'})
    
    use_fibonacci: bpy.props.BoolProperty(name = "useFibonacci", default=False,
        update = lambda self, context:update_fibonacci_numbers(self)) ##########  -> both in one propertyGroup!
        
    #rotate_angle_range: bpy.props.FloatProperty(name="", default=0.0, min=0.0)
    #rotate_angle_offset: bpy.props.FloatProperty(name="", default=0.0)
        

    
    # fn0 = 1.0
    # fn1 = 1.0
    # if scene.fibonacciNrList[i].value > 2:
    #     for n in range(2, scene.fibonacciNrList[i].value + 1):
    #         temp = fn0 + fn1
    #         fn0 = fn1
    #         fn1 = temp
    # scene.rotateAngleCrownStartList[i].value = 360.0 * (1.0 - fn0 / fn1) #TODO 

class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=10) # reuse for all ints (?)
    
class intPropL(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=200)

class posIntProp3(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "posIntProp3", default=3, min=3, soft_max=12)

class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0) # reuse for all floats (?)
    
class posFloatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0, min=0)
    
class posFloatPropDefault1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0)
    
class posFloatPropSoftMax2(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default = 1.0, min = 0, soft_max=2.0)
    
class posFloatPropSoftMax1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0, soft_max=1.0)

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
            ('CYLINDRICAL', "Cylindrical", "A cylinder-shaped tree."),
            ('TAPERED_CYLINDRICAL', "Tapered Cylindrical", "A cylinder that tapers towards the top."),
            ('FLAME', "Flame", "A flame-shaped tree."),
            ('INVERSE_CONICAL', "Inverse Conical", "An upside-down cone-shaped tree."),
            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
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
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.parentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

class toggleLeafBool(bpy.types.Operator):
    bl_idname = "scene.toggle_leaf_bool"
    bl_label = "Toggle Leaf Bool"
    bl_description = "At least one item has to be true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.leafParentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

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
    
class branchClusterSettings(bpy.types.PropertyGroup):
    branchClusterBoolList: bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    nrBranches: bpy.props.IntProperty(name = "Number of branches", default = 0, min = 0)
    nrBranchesIndex: bpy.props.IntProperty(name = "nrBranchesListIndex", default=0)
    branchShape: bpy.props.PointerProperty(type = treeShapeEnumProp)
    relBranchLength: bpy.props.FloatProperty(name = "Relative branch length", default = 1.0, min = 0.0, max = 1.0)
    relBranchLengthVariation: bpy.props.FloatProperty(name = "Relative branch length variation", default = 0.0, min = 0.0, soft_max = 1.0)
    taperFactor: bpy.props.FloatProperty(name = "Taper factor", default = 1.0, min = 0.0, soft_max = 1.0)
    ringResolution: bpy.props.IntProperty(name = "Ring resolution", default = 6, min = 3)
    branchesStartHeightGlobal: bpy.props.FloatProperty(name = "Branches start height global", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightGlobal: bpy.props.FloatProperty(name = "Branches end height global", default = 0.0, min = 0.0, max = 1.0)
    branchesStartHeightCluster: bpy.props.FloatProperty(name = "Branches start height cluster", default = 0.0, min = 0.0, max = 1.0)
    branchesEndHeightCluster: bpy.props.FloatProperty(name = "Branches end height cluster", default = 0.0, min = 0.0, max = 1.0)
    
    #bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    #bpy.types.Scene.nrBranchesList = bpy.props.CollectionProperty(type=intProp)
    #bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    #bpy.types.Scene.branchShapeList = bpy.props.CollectionProperty(type=treeShapeEnumProp)
    #bpy.types.Scene.relBranchLengthList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    #bpy.types.Scene.relBranchLengthVariationList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1Default0)
    #bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    #bpy.types.Scene.ringResolutionList = bpy.props.CollectionProperty(type=posIntProp3)
    #bpy.types.Scene.branchesStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchesEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    
    noiseAmplitudeHorizontalBranch: bpy.props.FloatProperty(name = "Noise amplitude horizontal", default = 0.0, min = 0.0)
    noiseAmplitudeVerticalBranch: bpy.props.FloatProperty(name = "Noise amplitude vertical", default = 0.0, min = 0.0)
    noiseAmplitudeBranchGradient: bpy.props.FloatProperty(name = "Noise amplitude gradient", default = 0.0, min = 0.0)
    noiseAmplitudeBranchExponent: bpy.props.FloatProperty(name = "Noise amplitude exponent", default = 1.0, min = 0.0)
    noiseScale: bpy.props.FloatProperty(name = "Noise scale", default = 1.0, min = 0.0)
    
    #bpy.types.Scene.noiseAmplitudeHorizontalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.noiseAmplitudeVerticalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.noiseAmplitudeBranchGradientList = bpy.props.CollectionProperty(type=posFloatProp)    
    #bpy.types.Scene.noiseAmplitudeBranchExponentList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    #bpy.types.Scene.noiseScaleList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    
    verticalAngleCrownStart: bpy.props.FloatProperty(name = "Vertical angle crown start")
    verticalAngleCrownEnd: bpy.props.FloatProperty(name = "Vertical angle crown end")
    verticalAngleBranchStart: bpy.props.FloatProperty(name = "Vertical angle branch start")
    verticalAngleBranchEnd: bpy.props.FloatProperty(name = "Vertical angle branch end")
    branchAngleMode: bpy.props.PointerProperty(type = angleModeEnumProp)
    useFibonacciAngles: bpy.props.BoolProperty(name = "Use Fibonacci angles")
    fibonacciNr: bpy.props.PointerProperty(type = fibonacciProps)
    rotateAngleRange: bpy.props.FloatProperty(name = "Rotate angle range") # -> no longer in fibonacciProps!
    rotateAngleOffset: bpy.props.FloatProperty(name = "Rotate angle offset") # -> no longer in fibonacciProps!
    
    rotateAngleCrownStart: bpy.props.FloatProperty(name = "Rotate angle crown start")
    rotateAngleCrownEnd: bpy.props.FloatProperty(name = "Rotate angle crown end")
    rotateAngleBranchStart: bpy.props.FloatProperty(name = "Rotate angle branch start")
    rotateAngleBranchEnd: bpy.props.FloatProperty(name = "Rotate angle branch end")
    
    hangingBranches: bpy.props.BoolProperty(name = "Hanging branches")
    branchGlobalCurvatureStart: bpy.props.FloatProperty(name = "Branch global curvature start")
    branchGlobalCurvatureEnd: bpy.props.FloatProperty(name = "Branch global curvature end")
    branchCurvatureStart: bpy.props.FloatProperty(name = "Branch curvature start")
    branchCurvatureEnd: bpy.props.FloatProperty(name = "Branch curvature end")
    branchCurvatureOffsetStrength: bpy.props.FloatProperty(name = "Branch curvature offset", min = 0.0)
    
    #bpy.types.Scene.verticalAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.verticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchAngleModeList = bpy.props.CollectionProperty(type=angleModeEnumProp)
    #bpy.types.Scene.useFibonacciAnglesList = bpy.props.CollectionProperty(type=boolProp)
    #bpy.types.Scene.fibonacciNrList = bpy.props.CollectionProperty(type=fibonacciProps)
    #bpy.types.Scene.rotateAngleRangeList = bpy.props.CollectionProperty(type=floatProp)
    
    #bpy.types.Scene.rotateAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.rotateAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    
    #bpy.types.Scene.hangingBranchesList = bpy.props.CollectionProperty(type=boolProp)
    #bpy.types.Scene.branchGlobalCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchGlobalCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchCurvatureOffsetStrengthList = bpy.props.CollectionProperty(type=posFloatProp)
    
    nrSplitsPerBranch: bpy.props.FloatProperty(name = "Nr splits per branch", default = 0.0, min = 0.0)
    branchSplitMode: bpy.props.PointerProperty(type=splitModeEnumProp)
    branchSplitRotateAngle: bpy.props.FloatProperty(name = "Branch split rotate angle")
    branchSplitAxisVariation: bpy.props.FloatProperty(name = "Branch split axis variation", min = 0.0)
    
    branchSplitAngle: bpy.props.FloatProperty(name = "Branch split angle", min = 0.0)
    branchSplitPointAngle: bpy.props.FloatProperty(name = "Branch split point angle", min = 0.0)
    
    splitsPerBranchVariation: bpy.props.FloatProperty(name = "Splits per branch variation", min = 0.0, max = 1.0)
    branchVariance: bpy.props.FloatProperty(name = "Branch varianace", default = 0.0, min = 0.0, max = 1.0)
    branchSplitHeightVariation: bpy.props.FloatProperty(name = "Branch split height variation", default = 0.0, min = 0.0, max = 1.0)
    branchSplitLengthVariation: bpy.props.FloatProperty(name = "Branch split length variation", default = 0.0, min = 0.0, max = 1.0)
    
    #bpy.types.Scene.branchSplitModeList = bpy.props.CollectionProperty(type=splitModeEnumProp)
    #bpy.types.Scene.branchVarianceList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitRotateAngleList = bpy.props.CollectionProperty(type=floatProp)
    #bpy.types.Scene.branchSplitAxisVariationList = bpy.props.CollectionProperty(type=posFloatProp)
    
    #bpy.types.Scene.branchSplitAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.branchSplitPointAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    
    #bpy.types.Scene.nrSplitsPerBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    #bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp01)
    #bpy.types.Scene.branchSplitLengthVariationList = bpy.props.CollectionProperty(type=floatProp01)
    
    branchSplitHeightInLevelListList: bpy.props.PointerProperty(type=floatListProp01)
    branchSplitHeightInLevelListIndex: bpy.props.IntProperty(default = 0)
    showBranchSplitHeights: bpy.props.BoolProperty(name = "Show / hide split levels", default = True)
    
    #bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_0 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_0 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_1 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_1 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_2 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_2 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_3 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_3 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_4 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_4 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.branchSplitHeightInLevelList_5 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex_5 = bpy.props.IntProperty(default = 0)
    #bpy.types.Scene.showBranchSplitHeights = bpy.props.CollectionProperty(type=boolProp)
    
    #Yes, it’s possible to reuse properties (including EnumProperty values) across multiple PropertyGroup classes in Blender. You can define an EnumProperty or any other property in one PropertyGroup, and then use that property in multiple other PropertyGroup classes by referencing it.
    #shared_enum: bpy.props.PointerProperty(type=SharedEnumPropertyGroup)
    
    
    #value: bpy.props.CollectionProperty(name = "floatListProperty", type=floatProp)
    #bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    #treeShapeEnumProp
        
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
        
        
    
class addStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_stem_split_level"
    bl_label = "Add split level"
    
    def execute(self, context):
        context.scene.showStemSplitHeights = True
        newSplitHeight = context.scene.stemSplitHeightInLevelList.add()
        newSplitHeight.value = 0.5
        context.scene.stemSplitHeightInLevelListIndex = len(context.scene.stemSplitHeightInLevelList) - 1
        return {'FINISHED'}

class addBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_branch_split_level"
    bl_label = "Add split level"
    level: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.showBranchSplitHeights[self.level].value = True
        
        newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value.add()
        newSplitHeight = 0.5
        if self.level == 0:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_0.add()
            newSplitHeight.value = 0.5
        if self.level == 1:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_1.add()
            newSplitHeight.value = 0.5
        if self.level == 2:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_2.add()
            newSplitHeight.value = 0.5
        if self.level == 3:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_3.add()
            newSplitHeight.value = 0.5
        if self.level == 4:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_4.add()
            newSplitHeight.value = 0.5
        if self.level == 5:
            newSplitHeight = context.scene.branchSplitHeightInLevelList_5.add()
            newSplitHeight.value = 0.5
        
        
        if self.level > 5:
            newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value
            newSplitHeight = 0.5
            return {'FINISHED'}
        
        #context.scene.branchSplitHeightInLevelListIndex[len(context.scene.branchSplitHeightInLevelListIndex) - 1].value = 0
        return {'FINISHED'}
    
class removeStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_stem_split_level"
    bl_label = "Remove split level"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.showStemSplitHeights = True
        if len(context.scene.stemSplitHeightInLevelList) > 0:
            context.scene.stemSplitHeightInLevelList.remove(len(context.scene.stemSplitHeightInLevelList) - 1)
            
        
        return {'FINISHED'}

class removeBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_branch_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        context.scene.showBranchSplitHeights[self.level].value = True
        if self.level == 0:
            if len(context.scene.branchSplitHeightInLevelList_0) > 0:
                context.scene.branchSplitHeightInLevelList_0.remove(context.scene.branchSplitHeightInLevelListIndex_0)
                #context.scene.branchSplitHeightInLevelListIndex_0 -= 1
        if self.level == 1:
            if len(context.scene.branchSplitHeightInLevelList_1) > 0:
                context.scene.branchSplitHeightInLevelList_1.remove(len(context.scene.branchSplitHeightInLevelList_1) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_1 -= 1
        if self.level == 2:
            if len(context.scene.branchSplitHeightInLevelList_2) > 0:
                context.scene.branchSplitHeightInLevelList_2.remove(len(context.scene.branchSplitHeightInLevelList_2) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_2 -= 1
        if self.level == 3:
            if len(context.scene.branchSplitHeightInLevelList_3) > 0:
                context.scene.branchSplitHeightInLevelList_3.remove(len(context.scene.branchSplitHeightInLevelList_3) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_3 -= 1
        if self.level == 4:
            if len(context.scene.branchSplitHeightInLevelList_4) > 0:
                context.scene.branchSplitHeightInLevelList_4.remove(len(context.scene.branchSplitHeightInLevelList_4) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_4 -= 1
        if self.level == 5:
            if len(context.scene.branchSplitHeightInLevelList_5) > 0:
                context.scene.branchSplitHeightInLevelList_5.remove(len(context.scene.branchSplitHeightInLevelList_4) - 1)
                #context.scene.branchSplitHeightInLevelListIndex_5 -= 1
        if self.level > 5:
            context.scene.branchSplitHeightInLevelListList[self.level].value.remove(len(context.scene.branchSplitHeightInLevelListList[self.level].value) - 1)
            
               #context.scene.branchSplitModeList.remove(len(context.scene.branchSplitModeList) - 1)         
        #self.report({'INFO'}, f"remove split level")
        return {'FINISHED'}
    
class addItem(bpy.types.Operator): # add branch cluster
    bl_idname = "scene.add_list_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.branchClusters += 1
        
        branchSettings = context.scene.branchClusterSettingsList.add()
        branchSettings.nrBranches = 2
        # ...
        
        nrBranches = context.scene.nrBranchesList.add()
        nrBranches.value = 2       # default for nrBranches!
        
        parentClusterBoolListList = context.scene.parentClusterBoolListList.add()
        for b in range(0, context.scene.branchClusters):
            parentClusterBoolListList.value.add()
        parentClusterBoolListList.value[0].value = True
        
        #boolListItem = scene.leafParentClusterBoolListList[cluster_index].value
        for leafParentClusterList in context.scene.leafParentClusterBoolListList:
            leafParentClusterList.value.add()
        
        branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
                
        branchSplitMode = context.scene.branchSplitModeList.add()  # TODO (???) #branchSplitMode...
        branchVariance = context.scene.branchVarianceList.add()
        branchSplitRotateAngle = context.scene.branchSplitRotateAngleList.add()
        branchSplitRotateAngle.value = 0.0
        branchSplitAxisVariation = context.scene.branchSplitAxisVariationList.add()
        branchSplitAxisVariation.value = 0.0
        branchSplitAngle = context.scene.branchSplitAngleList.add()
        branchSplitAngle.value = 0.0
        branchSplitPointAngle = context.scene.branchSplitPointAngleList.add()
        branchSplitPointAngle.value = 0.0
        branchShape = context.scene.branchShapeList.add()
        relBranchLength = context.scene.relBranchLengthList.add()
        relBranchLength.value = 1.0
        relBranchLengthVariation = context.scene.relBranchLengthVariationList.add()
        taperFactor = context.scene.taperFactorList.add()
        taperFactor.value = 1.0
        ringResolution = context.scene.ringResolutionList.add()
        
        showNoiseSettings = context.scene.showNoiseSettings.add()
        showNoiseSettings.value = True
        
        noiseAmplitudeBranchGradient = context.scene.noiseAmplitudeBranchGradientList.add()
        noiseAmplitudeBranchGradient = 1.0
        noiseAmplitudeHorizontalBranch = context.scene.noiseAmplitudeHorizontalBranchList.add()
        noiseAmplitudeHorizontalBranch = 0.0
        noiseAmplitudeVerticalBranch = context.scene.noiseAmplitudeVerticalBranchList.add()
        noiseAmplitudeVerticalBranch = 0.0
        noiseAmplitudeExponent = context.scene.noiseAmplitudeBranchExponentList.add()
        noiseAmplitudeExponent = 1.0
        noiseScale = context.scene.noiseScaleList.add()
        noiseScale = 1.0
        
        # TODO (?????)
        #
        #if context.scene.branchClusters == 1:
        #    ringResolution.value = context.scene.stemRingResolution
        #else:
        #    ringResolution.value = context.scene.ringResolution[context.scene.branchClusters -  2].value
        
        
        #verticalRange = context.scene.verticalRangeList.add()
        #verticalRange.value = 0.0
        showAngleSetting = context.scene.showAngleSettings.add()
        showAngleSetting.value = True
        showSplitSettings = context.scene.showSplitSettings.add()
        showSplitSettings.value = True
        verticalAngleCrownStart = context.scene.verticalAngleCrownStartList.add()
        #verticalAngleCrownStart.value = 0.0
        #verticalAngleCrownStart.show_angle_settings = True
        verticalAngleCrownEnd = context.scene.verticalAngleCrownEndList.add()
        verticalAngleCrownEnd.value = 0.0
        verticalAngleBranchStart = context.scene.verticalAngleBranchStartList.add()
        verticalAngleBranchStart.value = 0.0
        verticalAngleBranchEnd = context.scene.verticalAngleBranchEndList.add()
        verticalAngleBranchEnd.value = 0.0
        branchAngleMode = context.scene.branchAngleModeList.add()
        useFibonacciAnglesList = context.scene.useFibonacciAnglesList.add()
        fibonacciNrList = context.scene.fibonacciNrList.add()
        fibonacciNrList.value = 3
        rotateAngleCrownStart = context.scene.rotateAngleCrownStartList.add()
        rotateAngleCrownStart = 0.0
        rotateAngleCrownEnd = context.scene.rotateAngleCrownEndList.add()
        rotateAngleCrownEnd = 0.0
        rotateAngleBranchStart = context.scene.rotateAngleBranchStartList.add()
        rotateAngleBranchStart = 0.0
        rotateAngleBranchEnd = context.scene.rotateAngleBranchEndList.add()
        rotateAngleBranchEnd = 0.0
        
        
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
        hangingBranches = context.scene.hangingBranchesList.add()
        hangingBranches = False
        branchGlobalCurvatureStart = context.scene.branchGlobalCurvatureStartList.add()
        branchGlobalCurvatureStart.value = 0.0
        branchGlobalCurvatureEnd = context.scene.branchGlobalCurvatureEndList.add()
        branchGlobalCurvatureEnd.value = 0.0
        branchCurvatureStart = context.scene.branchCurvatureStartList.add()
        branchCurvatureStart.value = 0.0
        branchCurvatureEnd = context.scene.branchCurvatureEndList.add()
        branchCurvatureEnd.value = 0.0
        branchCurvatureOffsetStrength = context.scene.branchCurvatureOffsetStrengthList.add()
        branchCurvatureOffsetStrength.value = 0.0
        nrSplitsPerBranch = context.scene.nrSplitsPerBranchList.add()
        nrSplitsPerBranch.value = 0.0
        splitsPerBranchVariation = context.scene.splitsPerBranchVariationList.add()
        splitsPerBranchVariation.value = 0.0
        branchSplitHeightVariation = context.scene.branchSplitHeightVariationList.add()
        branchSplitHeightVariation.value = 0.0
        branchSplitLengthVariation = context.scene.branchSplitLengthVariationList.add()
        branchSplitLengthVariation.value = 0.0
        branchSplitHeightInLevelListListItem = context.scene.branchSplitHeightInLevelListList.add()
        showBranchSplitHeight = context.scene.showBranchSplitHeights.add()
        showBranchSplitHeight = True
        
        # ---> hardcode 20 lists -> tempplateList ( no nested List!, bakcfall: old UI...)
        # ---> call getNestedList() at beginning of updateTree()
        
        
        
        
        
        
        
        
        
        
        #branchSplitHeightInLevelListIndex = context.scene.branchSplitHeightInLevelListIndex.add()
                
        
        #bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)-----------ok
        #bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.propy.CollectionProperty(type=intProp) -----------ok
        
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
        
        for leafParentClusterList in context.scene.leafParentClusterBoolListList:
            if len(leafParentClusterList.value) > 1:
                leafParentClusterList.value.remove(len(leafParentClusterList.value) - 1)
                
                allFalse = True
                for b in leafParentClusterList.value:
                    if b.value == True:
                        allFalse = False
                if allFalse == True:
                    leafParentClusterList.value[0].value = True
        
        context.scene.branchSplitModeList.remove(len(context.scene.branchSplitModeList) - 1)
        context.scene.branchVarianceList.remove(len(context.scene.branchVarianceList) - 1)
        context.scene.branchSplitRotateAngleList.remove(len(context.scene.branchSplitRotateAngleList) - 1)
        context.scene.branchSplitAxisVariationList.remove(len(context.scene.branchSplitAxisVariationList) - 1)
        context.scene.branchSplitAngleList.remove(len(context.scene.branchSplitAngleList) - 1)
        context.scene.branchSplitPointAngleList.remove(len(context.scene.branchSplitPointAngleList) - 1)
        context.scene.branchShapeList.remove(len(context.scene.branchShapeList) - 1)
        context.scene.relBranchLengthList.remove(len(context.scene.relBranchLengthList) - 1)
        context.scene.relBranchLengthVariationList.remove(len(context.scene.relBranchLengthVariationList) - 1)
        context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
        context.scene.ringResolutionList.remove(len(context.scene.ringResolutionList) - 1)
        
        context.scene.showNoiseSettings.remove(len(context.scene.showNoiseSettings) - 1)
        context.scene.noiseAmplitudeBranchGradientList.remove(len(context.scene.noiseAmplitudeBranchGradientList) - 1)
        
        context.scene.noiseAmplitudeHorizontalBranchList.remove(len(context.scene.noiseAmplitudeHorizontalBranchList) - 1)
        context.scene.noiseAmplitudeVerticalBranchList.remove(len(context.scene.noiseAmplitudeVerticalBranchList) - 1)
        context.scene.noiseAmplitudeBranchExponentList.remove(len(context.scene.noiseAmplitudeBranchExponentList) - 1)
        context.scene.noiseScaleList.remove(len(context.scene.noiseScaleList) - 1)
        
        context.scene.showAngleSettings.remove(len(context.scene.showAngleSettings) - 1)
        context.scene.showSplitSettings.remove(len(context.scene.showSplitSettings) - 1)
        context.scene.verticalAngleCrownStartList.remove(len(context.scene.verticalAngleCrownStartList) - 1)
        context.scene.verticalAngleCrownEndList.remove(len(context.scene.verticalAngleCrownEndList) - 1)
        context.scene.verticalAngleBranchStartList.remove(len(context.scene.verticalAngleBranchStartList) - 1)
        context.scene.verticalAngleBranchEndList.remove(len(context.scene.verticalAngleBranchEndList) - 1)
        context.scene.branchAngleModeList.remove(len(context.scene.branchAngleModeList) - 1)
        context.scene.useFibonacciAnglesList.remove(len(context.scene.useFibonacciAnglesList) - 1)
        context.scene.fibonacciNrList.remove(len(context.scene.fibonacciNrList) - 1)
        
        context.scene.rotateAngleCrownStartList.remove(len(context.scene.rotateAngleCrownStartList) - 1)
        context.scene.rotateAngleCrownEndList.remove(len(context.scene.rotateAngleCrownEndList) - 1)
        context.scene.rotateAngleBranchStartList.remove(len(context.scene.rotateAngleBranchStartList) - 1)
        context.scene.rotateAngleBranchEndList.remove(len(context.scene.rotateAngleBranchEndList) - 1)
        
        context.scene.branchesStartHeightGlobalList.remove(len(context.scene.branchesStartHeightGlobalList) - 1)
        context.scene.branchesEndHeightGlobalList.remove(len(context.scene.branchesEndHeightGlobalList) - 1)
        context.scene.branchesStartHeightClusterList.remove(len(context.scene.branchesStartHeightClusterList) - 1)
        context.scene.branchesEndHeightClusterList.remove(len(context.scene.branchesEndHeightClusterList) - 1)
        context.scene.hangingBranchesList.remove(len(context.scene.hangingBranchesList) - 1)
        context.scene.branchGlobalCurvatureStartList.remove(len(context.scene.branchGlobalCurvatureStartList) - 1)
        context.scene.branchGlobalCurvatureEndList.remove(len(context.scene.branchGlobalCurvatureEndList) - 1)
        context.scene.branchCurvatureStartList.remove(len(context.scene.branchCurvatureStartList) - 1)
        context.scene.branchCurvatureEndList.remove(len(context.scene.branchCurvatureEndList) - 1)
        context.scene.branchCurvatureOffsetStrengthList.remove(len(context.scene.branchCurvatureOffsetStrengthList) - 1)
        context.scene.nrSplitsPerBranchList.remove(len(context.scene.nrSplitsPerBranchList) - 1)
        context.scene.splitsPerBranchVariationList.remove(len(context.scene.splitsPerBranchVariationList) - 1)
        context.scene.branchSplitHeightVariationList.remove(len(context.scene.branchSplitHeightVariationList) - 1)
        context.scene.branchSplitLengthVariationList.remove(len(context.scene.branchSplitLengthVariationList) - 1)
        context.scene.branchSplitHeightInLevelListList.remove(len(context.scene.branchSplitHeightInLevelListList) - 1)
        
        #context.scene.branchSplitHeightInLevelListIndex.remove(len(context.scene.branchSplitHeightInLevelListIndex) - 1)
                
        
            
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
        
        layout.prop(context.scene, "file_name")  # String input for file name
        
        layout.operator("export.save_properties_file", text="Save Properties")
        layout.operator("export.load_properties_file", text="Load Properties")
        
        row = layout.row()
        row.label(icon = 'COLORSET_12_VEC')
        
        row.operator("object.generate_tree", text="Generate Tree")
        
        if context.scene.my_tool.is_running:
            layout.label(text="Task in progress...")
            layout.prop(scene.my_tool, "progress", text="Progress")
        else:
            layout.label(text="Task Complete!")
            
            
class MyToolProperties(bpy.types.PropertyGroup):
    progress: bpy.props.FloatProperty(
        name="Progress",
        description="Progress of the long-running task",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE'
    )
    is_running: bpy.props.BoolProperty(
        name="Is Running",
        default=False
    )
        
    
class treeSettings(bpy.types.Panel):
    bl_label = "Tree Settings"
    bl_idname = "PT_TreeSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text="Select Brak Material:")
        row.prop_search(context.scene, "bark_material", bpy.data, "materials", text="")
        
        row = layout.row()
        row.label(text="Select Leaf Material:")
        row.prop_search(context.scene, "leaf_material", bpy.data, "materials", text="")
        
        row = layout.row()
        layout.prop(context.scene, "treeHeight")
        row = layout.row()
        layout.prop(context.scene, "treeGrowDir")
        row = layout.row()
        layout.prop(context.scene, "taper")
        row = layout.row()
        layout.operator("scene.reset_curves", text="Reset taper curve")
        row = layout.row()
        layout.template_curve_mapping(taperCurveData('taperMapping'), "mapping")
        row = layout.row()
        layout.prop(context.scene, "branchTipRadius")
        row = layout.row()
        layout.prop(context.scene, "ringSpacing")
        row = layout.row()
        layout.prop(context.scene, "stemRingResolution")
        row = layout.row()
        layout.prop(context.scene, "resampleDistance")
        
        

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
        layout.prop(context.scene, "noiseAmplitudeVertical")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeHorizontal")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeGradient")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeExponent")
        row = layout.row()
        layout.prop(context.scene, "noiseScale")
        row = layout.row()
        layout.prop(context.scene, "seed")

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
        layout.prop(context.scene, "curvatureStart")
        row = layout.row()
        layout.prop(context.scene, "curvatureEnd")
        row = layout.row()
        layout.prop(context.scene, "maxCurveSteps")
        
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
        layout.prop(context.scene, "nrSplits")
        
        row = layout.row()
        layout.prop(context.scene, "variance", slider=True)
        row = layout.row()
        #layout.prop(context.scene, "stemSplitMode")
        split = row.split(factor=0.5)
        split.label(text="Stem split mode")
        split.prop(context.scene, "stemSplitMode", text="")
        mode = scene.stemSplitMode
        if mode == "ROTATE_ANGLE":
            row = layout.row()
            layout.prop(context.scene, "stemSplitRotateAngle")
        row = layout.row()
        layout.prop(context.scene, "curvOffsetStrength")
        
        box = layout.box()
        row = box.row()
        
        #box.prop(scene.branchClusterBoolListList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterBoolListList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
            
        
        row.prop(context.scene, "showStemSplitHeights", icon="TRIA_DOWN" if context.scene.showStemSplitHeights else "TRIA_RIGHT", emboss=False, text="")
        
        row.operator("scene.add_stem_split_level", text="Add split level")
        row.operator("scene.remove_stem_split_level", text="Remove").index = scene.stemSplitHeightInLevelListIndex
        if context.scene.showStemSplitHeights == True:
            row = layout.row()
            row.template_list("UL_stemSplitLevelList", "", scene, "stemSplitHeightInLevelList", scene, "stemSplitHeightInLevelListIndex")
                        
        #j = 0
        #for splitLevel in context.scene.stemSplitHeightInLevelList:
        #    box.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
        #    j += 1
            
            
        #box.template_list("UI_UL_list", "stemSplitHeightInLevelList", context.scene, "stemSplitHeightInLevelList", context.scene.stemSplitHeightInLevelList,  0)
        #box.template_list("myList", "stemSplitHeightInLevelList", context.scene, "stemSplitHeightInLevelListIndex", active_propname, *, item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)
        #row = box.row()
        
        
        row = layout.row()
        layout.prop(context.scene, "splitHeightVariation")
        row = layout.row()
        layout.prop(context.scene, "splitLengthVariation")
        row = layout.row()
        layout.prop(context.scene, "stemSplitAngle")
        row = layout.row()
        layout.prop(context.scene, "stemSplitPointAngle")
        row = layout.row()


def taperNodeTree():
    if 'taperNodeGroup' not in bpy.data.node_groups:
        taperCurveNodeGroup = bpy.data.node_groups.new('taperNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['taperNodeGroup'].nodes

taper_node_mapping = {}

def taperCurveData(taperCurve):
    if taperCurve not in taper_node_mapping:
        TaperNodeTree = taperNodeTree().new('ShaderNodeRGBCurve')
        taper_node_mapping[taperCurve] = TaperNodeTree.name
        
        #resetTaperCurve()
        
    nodeTree = taperNodeTree()[taper_node_mapping[taperCurve]]
    
    
    return nodeTree

class resetCurvesButton(bpy.types.Operator):
    bl_idname = "scene.reset_curves"
    bl_label = "initialise"
    
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        nrCurves = len(nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves)
        #self.report({'INFO'}, f"nrCurves: {nrCurves}")
        curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
        
        #initialise values
        resetTaperCurve()
        return {'FINISHED'}
    
def reset_taper_curve_deferred():
    bpy.ops.scene.reset_curves()
    return None
    
    
def resetTaperCurve():
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    if not nodeGroups:
        return
    curveNode = nodeGroups.nodes.get(taper_node_mapping.get('taperMapping'))
    if not curveNode:
        return
    curveElement = curveNode.mapping.curves[3]
    # Initialise values
    curveElement.points[0].location = (0.0, 1.0)
    curveElement.points[1].location = (1.0, 0.0)
    curveElement.points[0].handle_type = "VECTOR"
    curveElement.points[1].handle_type = "VECTOR"
    if len(curveElement.points) > 2:
        for i in range(2, len(curveElement.points)):
            curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
    curveNode.mapping.update()
    

class sampleCruvesButton(bpy.types.Operator):
    bl_idname = "scene.sample_curves"
    bl_label = "evaluate"
    
    
    
    def execute(self, context):
        #self.report({'INFO'}, "sampling curve in sampleCurvesButton -> execute")
        x = 0.75
        sampleCurve(self, x)
        return {'FINISHED'}
    
# def draw_parent_cluster_bools(layout, scene, cluster_index):
#    boolListItem = scene.parentClusterBoolListList[cluster_index].value
#    
#    boolCount = 0
#    for j, boolItem in enumerate(boolListItem):
#        split = layout.split(factor=0.6)
#        #row = box.row()
#        if boolCount == 0:
#            split.label(text=f"Stem")
#            boolCount += 1
#        else:
#            split.label(text=f"Branch cluster {boolCount - 1}")
#            boolCount += 1
#            
#        rightColumn = split.column(align=True)
#        row = rightColumn.row(align=True)
#        row.alignment = 'CENTER'              # align to center
#        
#        op = row.operator("scene.toggle_bool", text="", depress=boolItem.value)
#        op.list_index = cluster_index
#        op.bool_index = j
    
def draw_leaf_cluster_bools(layout, scene, cluster_index, leafParentClusterBool):
    boolListItem = scene.leafParentClusterBoolListList[cluster_index].value
    
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
            
        rightColumn = split.column(align=True)
        row = rightColumn.row(align=True)
        row.alignment = 'CENTER'              # align to center
        
        op = row.operator("scene.toggle_bool", text="", depress=boolItem.value)
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
        row = layout.row()
    
        for i, outer in enumerate(scene.parentClusterBoolListList):
            box = layout.box()
            box.prop(scene.branchClusterBoolListList[i], "show_branch_cluster", icon="TRIA_DOWN" if scene.branchClusterBoolListList[i].show_branch_cluster else "TRIA_RIGHT", emboss=False, text=f"Branch cluster {i}", toggle=True)
            
            
            row = layout.row()
            row.prop(outer, "show_branch_cluster", icon="TRIA_DOWN", emboss=False, text=f"Branch cluster", toggle=True)
            
            if scene.branchClusterBoolListList[i].show_branch_cluster:
                box1 = box.box()
                row = box1.row()
                
                row.prop(outer, "show_cluster", icon="TRIA_DOWN" if outer.show_cluster else "TRIA_RIGHT", emboss=False, text=f"Parent clusters", toggle=True)
                
                if outer.show_cluster:
                    if i < len(context.scene.nrBranchesList):
                        
                        draw_parent_cluster_bools(box1, scene, i) 
                        
                        parentClusterBoolListList = context.scene.parentClusterBoolListList
                    
                if i < len(scene.branchClusterSettingsList):
                    split = box.split(factor=0.6)
                    split.label(text="Number of branches")
                    split.prop(scene.branchClusterSettingsList[i], "nrBranches", text="")
            
            #    if i < len(scene.nrBranchesList):
            #        split = box.split(factor=0.6)
            #        split.label(text="Number of branches")
            #        split.prop(scene.nrBranchesList[i], "value", text="")#, slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Branch shape")
                    split.prop(scene.branchClusterSettingsList[i].branchShape, "value", text="")
                
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLength", text="", slider=True)
                    
                    split = box.split(factor=0.6)
                    split.label(text="Relative branch length variation")
                    split.prop(scene.branchClusterSettingsList[i], "relBranchLengthVariation", text="", slider=True)
                
                    split = box.split(factor=0.6)
                    split.label(text="Taper factor")
                    split.prop(scene.branchClusterSettingsList[i], "taperFactor", text="", slider=True)
                
                    split = box.split(factor=0.6)
                    split.label(text="Ring resolution")
                    split.prop(scene.branchClusterSettingsList[i], "ringResolution", text="")
                
                    split = box.split(factor=0.6)
                    split.label(text="Branches start height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightGlobal", text="", slider=True)
            
                    split = box.split(factor=0.6)
                    split.label(text="Branches end height global")
                    split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightGlobal", text="", slider=True)
                
                    split = box.split(factor=0.6)
                    split.label(text="Branches start height cluster")
                    split.prop(scene.branchClusterSettingsList[i], "branchesStartHeightCluster", text="", slider=True)
            
                    split = box.split(factor=0.6)
                    split.label(text="Branches end height cluster")
                    split.prop(scene.branchClusterSettingsList[i], "branchesEndHeightCluster", text="", slider=True)
            
            split = box.split(factor=0.6)
            #if len(scene.showNoiseSettings) <= i:
            #    split.label(text=f"ERROR: len(showNoiseSettings): {len(scene.showNoiseSettings)}")
            #else:
            split.prop(scene.showNoiseSettings[i], "value", icon="TRIA_DOWN" if scene.showNoiseSettings[i].value else "TRIA_RIGHT", emboss=False, text="Noise settings", toggle=True)
                
            if scene.showNoiseSettings[i].value:
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
            if len(scene.showAngleSettings) <= i:
                split.label(text=f"ERROR: len(showAngleSettings): {len(scene.showAngleSettings)}")
            else:
                split.prop(scene.showAngleSettings[i], "value", icon="TRIA_DOWN" if scene.showAngleSettings[i].value else "TRIA_RIGHT", emboss=False, text="Angle settings", toggle=True)
           
                
            
                if scene.showAngleSettings[i].value:
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
                
                    split = box1.split(factor=0.6)
                    split.label(text="Branch angle mode")
                    if i < len(scene.branchAngleModeList):
                        split.prop(scene.branchClusterSettingsList[i].branchAngleMode, "value", text="")
                        
                        #split.prop(scene.branchClusterSettingsList[i].branchSplitMode, "value", text="")
                        #mode = scene.branchClusterSettingsList[i].branchSplitMode
                    
                    box2 = box1.box()
                    split = box2.split(factor=0.6)
                    
                    #split.prop(scene.branchClusterSettingsList[i].branchShape, "value", text="")
                    
                    if i < len(scene.branchAngleModeList):
                        if scene.branchAngleModeList[i].value == 'WINDING':
                            split.label(text="Use Fibonacci angles")
                            split.prop(scene.branchClusterSettingsList[i], "useFibonacciAngles", text="")
                            if scene.branchClusterSettingsList[i].useFibonacciAngles == True:
                            
                                split = box2.split(factor=0.6)
                                split.label(text="Fibonacci number")
                                split.prop(scene.branchClusterSettingsList[i].fibonacciNr, "fibonacci_nr", text="")
                                #split.prop(scene.fibonacciNrList[i], "fibonacci_nr", text="")
                                
                                # in branchClusterSettings: 
                                #   useFibonacciAngles: bpy.props.BoolProperty(name = "Use Fibonacci angles")
                                #   fibonacciNr: bpy.props.PointerProperty(type = fibonacciProps)
                                
                                
                                # class fibonacciProps(bpy.types.PropertyGroup):
                                #   fibonacci_nr: bpy.props.IntProperty(name = "fibonacciNr", default=3, min=3, 
                                #   update = lambda self, context:update_fibonacci_numbers(self))
        
                                #   fibonacci_angle: bpy.props.FloatProperty(name="", default=0.0, options={'HIDDEN'})
    
                                #   use_fibonacci: bpy.props.BoolProperty(name = "useFibonacci", default=False,
                                #   update = lambda self, context:update_fibonacci_numbers(self)) ##########  -> both in one propertyGroup!
       
                                
                                split1 = box2.split(factor=0.6)
                                split1.label(text="Angle:")
                                split1.label(text=f"{scene.branchClusterSettingsList[i].fibonacciNr.fibonacci_angle:.2f}°")
                            
                        if scene.branchClusterSettingsList[i].useFibonacciAngles == False or scene.branchClusterSettingsList[i].branchAngleMode.value == 'SYMMETRIC':
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
                        
                        box3 = box1.box()
                        #split = box3.split(factor=0.6)
                        #split.label(text="Hanging branches")
                        #if i < len(scene.hangingBranchesList):
                        #    split.prop(scene.hangingBranchesList[i], "value", text="")
                        
                        if scene.hangingBranchesList[i].value == True:
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature start")
                            split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureStart", text="")
                            
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature end")
                            split.prop(scene.branchClusterSettingsList[i], "branchGlobalCurvatureEnd", text="")
                        else:
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
                split.prop(scene.showSplitSettings[i], "value", icon="TRIA_DOWN" if scene.showSplitSettings[i].value else "TRIA_RIGHT", emboss=False, text="Split settings", toggle=True)
                
                if scene.showSplitSettings[i].value:
                    box2 = box.box()
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Nr splits per branch")
                    split.prop(scene.branchClusterSettingsList[i], "nrSplitsPerBranch", text="")
                    
                    #split.prop(scene.branchClusterSettingsList[i].branchShape, "value", text="")
                
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
                            row.template_list("UL_branchSplitLevelListLevel_0", "", scene, "branchSplitHeightInLevelList_0", scene, "branchSplitHeightInLevelListIndex_0")
                        if i == 1:
                            row.template_list("UL_branchSplitLevelListLevel_1", "", scene, "branchSplitHeightInLevelList_1", scene, "branchSplitHeightInLevelListIndex_1")
                        if i == 2:
                            row.template_list("UL_branchSplitLevelListLevel_2", "", scene, "branchSplitHeightInLevelList_2", scene, "branchSplitHeightInLevelListIndex_2")
                        if i == 3:
                            row.template_list("UL_branchSplitLevelListLevel_3", "", scene, "branchSplitHeightInLevelList_3", scene, "branchSplitHeightInLevelListIndex_3")
                        if i == 4:
                            row.template_list("UL_branchSplitLevelListLevel_4", "", scene, "branchSplitHeightInLevelList_4", scene, "branchSplitHeightInLevelListIndex_4")
                        if i == 5:
                            row.template_list("UL_branchSplitLevelListLevel_5", "", scene, "branchSplitHeightInLevelList_5", scene, "branchSplitHeightInLevelListIndex_5")
                        if i > 5:
                            j = 0
                            for splitLevel in context.scene.branchClusterSettingsList[i].branchSplitHeightInLevelList:
                                box2.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
                                j += 1

class addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.leafClusters += 1
        
        showLeafSettings = context.scene.showLeafSettings.add()
        showLeafSettings.value = True
        
        nrLeaves = context.scene.leavesDensityList.add()
        leafSize = context.scene.leafSizeList.add()
        leafAspectRatio = context.scene.leafAspectRatioList.add()
        leafAngleMode = context.scene.leafAngleModeList.add()
        leafType = context.scene.leafTypeList.add()
        leafStartHeightGlobal = context.scene.leafStartHeightGlobalList.add()
        leafEndHeightGlobal = context.scene.leafEndHeightGlobalList.add()
        leafEndHeightGlobal.value = 1.0
        leafStartHeightCluster = context.scene.leafStartHeightClusterList.add()
        leafEndHeightCluster = context.scene.leafEndHeightClusterList.add()
        leafEndHeightCluster.value = 1.0
        
        leafVerticalAngleBranchStart = context.scene.leafVerticalAngleBranchStartList.add()
        leafVerticalAngleBranchStart.value = 0.0
        leafVerticalAngleBranchEnd = context.scene.leafVerticalAngleBranchEndList.add()
        leafVerticalAngleBranchEnd.value = 0.0
        
        leafRotateAngleBranchStartList = context.scene.leafRotateAngleBranchStartList.add()
        leafRotateAngleBranchStartList = 0.0
        leafRotateAngleBranchEndList = context.scene.leafRotateAngleBranchEndList.add()
        leafRotateAngleBranchEndList = 0.0
        
        leafTiltAngleBranchStartList = context.scene.leafTiltAngleBranchStartList.add()
        leafTiltAngleBranchStartList = 0.0
        leafTiltAngleBranchEndList = context.scene.leafTiltAngleBranchEndList.add()
        leafTiltAngleBranchEndList = 0.0
        
        leafParentClusterBoolListList = context.scene.leafParentClusterBoolListList.add()
        stemBool = context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value.add()
        stemBool = True
                
        for b in range(0, context.scene.branchClusters):
            self.report({'INFO'}, f"adding leaf cluster")
            context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value.add()
            self.report({'INFO'}, f"len(leafParentClusterBoolListList): {len(context.scene.leafParentClusterBoolListList)}")
        
        leafParentClusterBoolListList.value[0].value = True
        
        # parentClusterBoolListList = context.scene.parentClusterBoolListList.add()
        # for b in range(0, context.scene.branchClusters):
        #     parentClusterBoolListList.value.add()
        # parentClusterBoolListList.value[0].value = True
        
        return {'FINISHED'}
        
class removeLeafItem(bpy.types.Operator):
    bl_idname = "scene.remove_leaf_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context): 
        context.scene.leafClusters -= 1
        
        if len(context.scene.showLeafSettings) > 0:
            context.scene.showLeafSettings.remove(len(context.scene.showLeafSettings) - 1)
        
        if len(context.scene.leavesDensityList) > 0:
            context.scene.leavesDensityList.remove(len(context.scene.leavesDensityList) - 1)
        if len(context.scene.leafSizeList) > 0:
            context.scene.leafSizeList.remove(len(context.scene.leafSizeList) - 1)
        if len(context.scene.leafAspectRatioList) > 0:
            context.scene.leafAspectRatioList.remove(len(context.scene.leafAspectRatioList) - 1)
        if len(context.scene.leafAngleModeList) > 0:
            context.scene.leafAngleModeList.remove(len(context.scene.leafAngleModeList) - 1)
        if len(context.scene.leafTypeList) > 0:
            context.scene.leafTypeList.remove(len(context.scene.leafTypeList) - 1)
        if len(context.scene.leafStartHeightGlobalList) > 0:
            context.scene.leafStartHeightGlobalList.remove(len(context.scene.leafStartHeightGlobalList) - 1)
        if len(context.scene.leafEndHeightGlobalList) > 0:
            context.scene.leafEndHeightGlobalList.remove(len(context.scene.leafEndHeightGlobalList) - 1)
        if len(context.scene.leafStartHeightClusterList) > 0:
            context.scene.leafStartHeightClusterList.remove(len(context.scene.leafStartHeightClusterList) - 1)
        if len(context.scene.leafEndHeightClusterList) > 0:
            context.scene.leafEndHeightClusterList.remove(len(context.scene.leafEndHeightClusterList) - 1)
        
        if len(context.scene.leafVerticalAngleBranchStartList) > 0:
            context.scene.leafVerticalAngleBranchStartList.remove(len(context.scene.leafVerticalAngleBranchStartList) - 1)
        if len(context.scene.leafVerticalAngleBranchEndList) > 0:
            context.scene.leafVerticalAngleBranchEndList.remove(len(context.scene.leafVerticalAngleBranchEndList) - 1)
        
        if len(context.scene.leafRotateAngleBranchStartList) > 0:
            context.scene.leafRotateAngleBranchStartList.remove(len(context.scene.leafRotateAngleBranchStartList) - 1)
        if len(context.scene.leafRotateAngleBranchEndList) > 0:
            context.scene.leafRotateAngleBranchEndList.remove(len(context.scene.leafRotateAngleBranchEndList) - 1)
        
        if len(context.scene.leafTiltAngleBranchStartList) > 0:
            context.scene.leafTiltAngleBranchStartList.remove(len(context.scene.leafTiltAngleBranchStartList) - 1)
        if len(context.scene.leafTiltAngleBranchEndList) > 0:
            context.scene.leafTiltAngleBranchEndList.remove(len(context.scene.leafTiltAngleBranchEndList) - 1)
        
        if len(context.scene.leafParentClusterBoolListList) > 0:
            listToClear = context.scene.leafParentClusterBoolListList[len(context.scene.leafParentClusterBoolListList) - 1].value
            lenToClear = len(listToClear)
            for i in range(0, lenToClear):
                listToClear.remove(len(listToClear) - 1)
            context.scene.leafParentClusterBoolListList.remove(len(context.scene.leafParentClusterBoolListList) - 1)
            
        self.report({'INFO'}, f"len(leafParentClusterBoolListList): {len(context.scene.leafParentClusterBoolListList)}")
        
        # if len(context.scene.parentClusterBoolListList) > 0:
        #     listToClear = context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value
        #     lenToClear = len(listToClear)
        #     for i in range(0, lenToClear):
        #         context.scene.parentClusterBoolListList[len(context.scene.parentClusterBoolListList) - 1].value.remove(len(context.scene.parentClusterBoolListList[i].value) - 1)
        #     context.scene.parentClusterBoolListList.remove(len(context.scene.parentClusterBoolListList) - 1)
        
            
        
        return {'FINISHED'}
        
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
        row.operator("scene.add_leaf_item", text="Add")
        row.operator("scene.remove_leaf_item", text="Remove").index = context.scene.leavesDensityListIndex
        row = layout.row()
        
        for i, outer in enumerate(scene.showLeafSettings):
            
            box = layout.box()
            box.prop(scene.showLeafSettings[i], "value", icon="TRIA_DOWN" if scene.showLeafSettings[i].value else "TRIA_RIGHT", emboss=False, text=f"Leaf cluster {i}", toggle=True)
            
            if scene.showLeafSettings[i].value:
                split = box.split(factor=0.6)
                split.label(text="Leaf density")
                split.prop(scene.leavesDensityList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf size")
                split.prop(scene.leafSizeList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf aspect ratio")
                split.prop(scene.leafAspectRatioList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf start height global")
                split.prop(scene.leafStartHeightGlobalList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf end height global")
                split.prop(scene.leafEndHeightGlobalList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf start height cluster")
                split.prop(scene.leafStartHeightClusterList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf end height cluster")
                split.prop(scene.leafEndHeightClusterList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Leaf type")
                split.prop(scene.leafTypeList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Leaf angle mode")
                split.prop(scene.leafAngleModeList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Vertical angle branch start")
                split.prop(scene.leafVerticalAngleBranchStartList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Vertical angle branch end")
                split.prop(scene.leafVerticalAngleBranchEndList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Rotate angle branch start")
                split.prop(scene.leafRotateAngleBranchStartList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Rotate angle branch end")
                split.prop(scene.leafRotateAngleBranchEndList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Tilt angle branch start")
                split.prop(scene.leafTiltAngleBranchStartList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Tilt angle branch end")
                split.prop(scene.leafTiltAngleBranchEndList[i], "value", text="")
                
                
                
                
                
                
                box1 = box.box()
                draw_leaf_cluster_bools(box1, scene, i, scene.leafParentClusterBoolListList[i])
                        
            
            
def register():
    #save and load
    bpy.utils.register_class(importProperties)
    bpy.utils.register_class(exportProperties)
    
    
    
    bpy.utils.register_class(MyToolProperties)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyToolProperties)

    
    #properties
    bpy.utils.register_class(treeShapeEnumProp)
    bpy.utils.register_class(splitModeEnumProp)
    bpy.utils.register_class(angleModeEnumProp)
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(intPropL)
    bpy.utils.register_class(posIntProp3)
    bpy.utils.register_class(fibonacciProps)
    bpy.utils.register_class(floatProp)
    bpy.utils.register_class(posFloatProp)
    bpy.utils.register_class(posFloatPropDefault1)
    bpy.utils.register_class(floatProp01)
    bpy.utils.register_class(floatProp01default0p5)
    bpy.utils.register_class(posFloatPropSoftMax1)
    bpy.utils.register_class(posFloatPropSoftMax1Default0)
    bpy.utils.register_class(posFloatPropSoftMax2)
    bpy.utils.register_class(floatListProp)
    bpy.utils.register_class(floatListProp01)
    bpy.utils.register_class(boolProp)
    bpy.utils.register_class(parentClusterBoolListProp)
    bpy.utils.register_class(branchClusterBoolListProp)
    bpy.utils.register_class(leafParentClusterBoolListProp)
    bpy.utils.register_class(leafAngleModeEnumProp)
    bpy.utils.register_class(leafTypeEnumProp)
    
    bpy.utils.register_class(branchClusterSettings)
    
    #operators
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(toggleLeafBool)
    bpy.utils.register_class(addStemSplitLevel)
    bpy.utils.register_class(removeStemSplitLevel)
    bpy.utils.register_class(addBranchSplitLevel)
    bpy.utils.register_class(removeBranchSplitLevel)
    bpy.utils.register_class(generateTree)
    bpy.utils.register_class(resetCurvesButton)
    bpy.utils.register_class(sampleCruvesButton)
    bpy.utils.register_class(addLeafItem)
    bpy.utils.register_class(removeLeafItem)
    
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(treeSettings)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(angleSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(branchSettings)
    bpy.utils.register_class(leafSettings)
    
    #bpy.utils.register_class(parentClusterPanel)
    
    #UILists
    bpy.utils.register_class(UL_stemSplitLevelList)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_5)
          
    #collections
    
    bpy.types.Scene.branchClusterSettingsList = bpy.props.CollectionProperty(type=branchClusterSettings)
    
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.showStemSplitHeights = bpy.props.BoolProperty(
        name = "Show/hide stem split heights",
        default = True
    )
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.file_name = bpy.props.StringProperty(name="File Name", default="my_tree_properties")
    
    bpy.types.Scene.showNoiseSettings = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.showAngleSettings = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.showSplitSettings = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.showLeafSettings = bpy.props.CollectionProperty(type=boolProp)
    
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.parentClusterBoolListList = bpy.props.CollectionProperty(type=parentClusterBoolListProp)
    bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    bpy.types.Scene.nrBranchesList = bpy.props.CollectionProperty(type=intProp)
    bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    bpy.types.Scene.branchSplitModeList = bpy.props.CollectionProperty(type=splitModeEnumProp)
    bpy.types.Scene.branchVarianceList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitRotateAngleList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitAxisVariationList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.rotateAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.rotateAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.rotateAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.rotateAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.branchSplitPointAngleList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.branchShapeList = bpy.props.CollectionProperty(type=treeShapeEnumProp)
    bpy.types.Scene.relBranchLengthList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    bpy.types.Scene.relBranchLengthVariationList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1Default0)
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    bpy.types.Scene.ringResolutionList = bpy.props.CollectionProperty(type=posIntProp3)
    bpy.types.Scene.noiseAmplitudeBranchGradientList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.noiseAmplitudeVerticalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.noiseAmplitudeHorizontalBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.noiseAmplitudeBranchExponentList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    bpy.types.Scene.noiseScaleList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    bpy.types.Scene.verticalAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchAngleModeList = bpy.props.CollectionProperty(type=angleModeEnumProp)
    bpy.types.Scene.useFibonacciAnglesList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.fibonacciNrList = bpy.props.CollectionProperty(type=fibonacciProps)
    bpy.types.Scene.rotateAngleRangeList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchesStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.hangingBranchesList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.branchGlobalCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchGlobalCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchCurvatureStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchCurvatureEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchCurvatureOffsetStrengthList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.nrSplitsPerBranchList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitLengthVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_0 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_0 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_1 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_1 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_2 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_2 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_3 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_3 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_4 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_4 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_5 = bpy.props.CollectionProperty(type=floatProp01default0p5)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_5 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.showBranchSplitHeights = bpy.props.CollectionProperty(type=boolProp)
    
    bpy.types.Scene.leavesDensityList = bpy.props.CollectionProperty(type=posFloatProp)
    bpy.types.Scene.leavesDensityListIndex = bpy.props.IntProperty(default=0)
    bpy.types.Scene.leafSizeList = bpy.props.CollectionProperty(type=posFloatPropDefault1)
    bpy.types.Scene.leafAspectRatioList = bpy.props.CollectionProperty(type=posFloatPropSoftMax2)
    bpy.types.Scene.leafAngleModeList = bpy.props.CollectionProperty(type=leafAngleModeEnumProp)
    bpy.types.Scene.leafTypeList = bpy.props.CollectionProperty(type=leafTypeEnumProp)
    bpy.types.Scene.leafStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.leafEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.leafStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.leafEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.leafVerticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.leafVerticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.leafRotateAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.leafRotateAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.leafTiltAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.leafTiltAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    
    bpy.types.Scene.bark_material = bpy.props.PointerProperty(type=bpy.types.Material)
    bpy.types.Scene.leaf_material = bpy.props.PointerProperty(type=bpy.types.Material)
    
    bpy.types.Scene.maxSplitHeightUsed = bpy.props.IntProperty(default = 0)
    
    #leafParentClusterBoolListProp
    bpy.types.Scene.leafParentClusterBoolListList = bpy.props.CollectionProperty(type=leafParentClusterBoolListProp)
    
    # bpy.props.CollectionProperty(type=intProp)
        
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
        min = 0.001
    )
    bpy.types.Scene.noiseAmplitudeHorizontal = bpy.props.FloatProperty(
        name = "Noise Amplitude Horizontal",
        description = "Noise amplitude horizontal",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeVertical = bpy.props.FloatProperty(
        name = "Noise Amplitude Vertical",
        description = "Noise amplitude vertical",
        default = 0.0,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeGradient = bpy.props.FloatProperty(
        name = "Noise Amplitude Gradient",
        description = "Gradient of noise Amplitude at the base of the tree",
        default = 0.1,
        min = 0.0
    )
    bpy.types.Scene.noiseAmplitudeExponent = bpy.props.FloatProperty(
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
    bpy.types.Scene.seed = bpy.props.IntProperty(
        name = "Seed",
        description = "Noise generator seed"
    )
    bpy.types.Scene.curvatureStart = bpy.props.FloatProperty(
        name = "Curvature Start",
        description = "Curvature at start of branches",
        default = 0.0
    )
    bpy.types.Scene.curvatureEnd = bpy.props.FloatProperty(
        name = "Curvature End",
        description = "Curvature at end of branches",
        default = 0.0
    )
    bpy.types.Scene.maxCurveSteps = bpy.props.IntProperty(
        name = "Max Curve Steps",
        description = "debug max curve steps",
        default = 10,
        min = 0
    )
    #bpy.types.Scene.shyBranchesMaxDistance = bpy.props.FloatProperty(
    #    name = "Shy Branches Max Distance",
    #    description = "Maximum distance for shy branches",
    #    default = 0.1,
    #    min = 0.0
    #)
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
        min = 0.0,
        max = 1.0
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
    bpy.types.Scene.splitLengthVariation = bpy.props.FloatProperty(
        name = "Split Length Variation",
        description = "Variation in split length",
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
            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
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
    bpy.types.Scene.resampleDistance = bpy.props.FloatProperty(
        name = "Resample Distance", 
        description = "Distance between nodes",
        default = 10.0,
        min = 0.0
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
            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
            ('HORIZONTAL', "Horizontal", "Split horizontally"),
        ],
        default='ROTATE_ANGLE',
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
    # branchCurvatureOffsetStrength
    bpy.types.Scene.branchCurvatureOffsetStrength = bpy.props.FloatVectorProperty(
        name="Branch Curvature Offset",
        description="Branch curvature offset strength",
        size = 1,
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
    
    bpy.types.Scene.leafClusters = bpy.props.IntProperty(
        name = "Leaf Clusters",
        description = "Number of leaf clusters",
        default = 0,
        min = 0
    )
    
    bpy.app.timers.register(reset_taper_curve_deferred, first_interval=0.1)
    #bpy.ops.scene.reset_curves()


    #data = {
    #    "treeHeight": props.treeHeight,
    #    "treeGrowDir": list(props.treeGrowDir),  
    #    "taper": props.taper,
    #    "taperCurvePoints": controlPts,
    #    "taperCurveHandleTypes": handleTypes,
    #    "branchTipRadius": props.branchTipRadius,
    #    "ringSpacing": props.ringSpacing,
    #    "stemRingResolution": props.stemRingResolution,
    #    "resampleDistance": props.resampleDistance,
    #    
    #    "noiseAmplitude": props.noiseAmplitude,
    #    "noiseAmplitudeGradient": props.noiseAmplitudeGradient,
    #    "noiseAmplitudeExponent": props.noiseAmplitudeExponent,
    #    "noiseScale": props.noiseScale,
    #    
    #    "curvatureStart": props.curvatureStart,
    #    "curvatureEnd": props.curvatureEnd,
    #    "maxCurveSteps": props.maxCurveSteps,
    #    
    #    "nrSplits": props.nrSplits, 
    #    "variance": props.variance,
    #    "stemSplitMode": props.stemSplitMode,
    #    "stemSplitRotateAngle": props.stemSplitRotateAngle,
    #    "curvOffsetStrength": props.curvOffsetStrength,
    #    
    #    "branchSplitHeightInLevelListIndex": props.branchSplitHeightInLevelListIndex,
    #    
    #    **{f"branchSplitHeightInLevelList_{i}": [item.value for item in getattr(props, f"branchSplitHeightInLevelList_{i}")]
    #       for i in range(6)},
    #    **{f"branchSplitHeightInLevelListIndex_{i}": getattr(props, f"branchSplitHeightInLevelListIndex_{i}")
    #       for i in range(6)},
    #       
    #    "splitHeightVariation": props.splitHeightVariation,
    #    "splitLengthVariation": props.splitLengthVariation,
    #    "stemSplitAngle": props.stemSplitAngle,
    #    "stemSplitPointAngle": props.stemSplitPointAngle,
    #    
    #    "branchClusters": props.branchClusters,
    #    
    #    "nrBranchesList": [props.nrBranchesList[i].value for i in range(0, props.branchClusters)],
    #    #"nrBranchesList": [item.value for item in props.nrBranchesList],
    #    
    #    #"parentClusterBoolList": [item.value for item in props.parentClusterBoolList],#TODO
    #    #"parentClusterBoolListList": [item.value for item in props.parentClusterBoolListList],
    #    #"branchClusterBoolListList": [item.value for item in props.branchClusterBoolListList],
    #    #"nrBranchesListIndex": props.nrBranchesListIndex,
    #    
    #    "parentClusterBoolListList": [[list(i.value for i in item.value)] for item in props.parentClusterBoolListList],
    #    
    #    "branchSplitModeList": [item.value for item in props.branchSplitModeList],
    #    "branchVarianceList": [item.value for item in props.branchVarianceList],
    #    "branchSplitRotateAngleList": [item.value for item in props.branchSplitRotateAngleList],
    #    "branchSplitAxisVariationList": [item.value for item in props.branchSplitAxisVariationList],
    #    "rotateAngleCrownStartList": [item.value for item in props.rotateAngleCrownStartList],
    #    "rotateAngleCrownEndList": [item.value for item in props.rotateAngleCrownEndList],
    #    "rotateAngleBranchStartList": [item.value for item in props.rotateAngleBranchStartList],
    #    "rotateAngleBranchEndList": [item.value for item in props.rotateAngleBranchEndList],
    #    "branchSplitAngleList": [item.value for item in props.branchSplitAngleList],
    #    "branchSplitPointAngleList": [item.value for item in props.branchSplitPointAngleList],
    #    "branchShapeList": [item.value for item in props.branchShapeList],
    #    "relBranchLengthList": [item.value for item in props.relBranchLengthList],
    #    "relBranchLengthVariationList": [item.value for item in props.relBranchLengthVariationList],
    #    "taperFactorList": [item.value for item in props.taperFactorList],
    #    "ringResolutionList": [item.value for item in props.ringResolutionList],
    #    "verticalAngleCrownStartList": [item.value for item in props.verticalAngleCrownStartList],
    #    "verticalAngleCrownEndList": [item.value for item in props.verticalAngleCrownEndList],
    #    "verticalAngleBranchStartList": [item.value for item in props.verticalAngleBranchStartList],
    #    "verticalAngleBranchEndList": [item.value for item in props.verticalAngleBranchEndList],
    #    "branchAngleModeList": [item.value for item in props.branchAngleModeList],
    #    "useFibonacciAnglesList": [item.value for item in props.useFibonacciAnglesList],
    #    "rotateAngleList": [item.value for item in props.rotateAngleList],
    #    "rotateAngleRangeList": [item.value for item in props.rotateAngleRangeList],
    #    "branchesStartHeightGlobalList": [item.value for item in props.branchesStartHeightGlobalList],
    #    "branchesEndHeightGlobalList": [item.value for item in props.branchesEndHeightGlobalList],
    #    "branchesStartHeightClusterList": [item.value for item in props.branchesStartHeightClusterList],
    #    "branchesEndHeightClusterList": [item.value for item in props.branchesEndHeightClusterList],
    #    "hangingBranchesList": [item.value for item in props.hangingBranchesList],
    #    "branchGlobalCurvatureStartList": [item.value for item in props.branchGlobalCurvatureStartList],
    #    "branchGlobalCurvatureEndList": [item.value for item in props.branchGlobalCurvatureEndList],
    #    "branchCurvatureStartList": [item.value for item in props.branchCurvatureStartList],
    #    "branchCurvatureEndList": [item.value for item in props.branchCurvatureEndList],
    #    "branchCurvatureOffsetStrengthList": [item.value for item in props.branchCurvatureOffsetStrengthList],
    #    "nrSplitsPerBranchList": [item.value for item in props.nrSplitsPerBranchList],
    #    "splitsPerBranchVariationList": [item.value for item in props.splitsPerBranchVariationList],
    #    "branchSplitHeightVariationList": [item.value for item in props.branchSplitHeightVariationList],
    #    
    #    
    #    "branchSplitHeightInLevelList_0": [item.value for item in props.branchSplitHeightInLevelList_0],
    #    "branchSplitHeightInLevelListIndex_0": props.branchSplitHeightInLevelListIndex_0,
    #    "branchSplitHeightInLevelList_1": [item.value for item in props.branchSplitHeightInLevelList_1],
    #    "branchSplitHeightInLevelListIndex_1": props.branchSplitHeightInLevelListIndex_1,
    #    "branchSplitHeightInLevelList_2": [item.value for item in props.branchSplitHeightInLevelList_2],
    #    "branchSplitHeightInLevelListIndex_2": props.branchSplitHeightInLevelListIndex_2,
    #    "branchSplitHeightInLevelList_3": [item.value for item in props.branchSplitHeightInLevelList_3],
    #    "branchSplitHeightInLevelListIndex_3": props.branchSplitHeightInLevelListIndex_3,
    #    "branchSplitHeightInLevelList_4": [item.value for item in props.branchSplitHeightInLevelList_4],
    #    "branchSplitHeightInLevelListIndex_4": props.branchSplitHeightInLevelListIndex_4,
    #    "branchSplitHeightInLevelList_5": [item.value for item in props.branchSplitHeightInLevelList_5],
    #    "branchSplitHeightInLevelListIndex_5": props.branchSplitHeightInLevelListIndex_5
    #    
    #}
    
def save_properties(filePath):
    props = bpy.context.scene
    
    controlPts = []
    handleTypes = []
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
    for n in range(0, len(curveElement.points)):
        controlPts.append(list(curveElement.points[n].location))
        handleTypes.append(curveElement.points[n].handle_type)
    
    nestedBranchList = []
    for cluster in props.parentClusterBoolListList:
        innerList = []
        for boolProp in cluster.value:
            innerList.append(boolProp.value)
        nestedBranchList.append(innerList)
        
    nestedLeafList = []
    for cluster in props.leafParentClusterBoolListList:
        innerLeafList = []
        for boolProp in cluster.value:
            innerLeafList.append(boolProp.value)
        nestedLeafList.append(innerLeafList)
    
    
    data = {
        "treeHeight": props.treeHeight,
        "treeGrowDir": list(props.treeGrowDir),
        "taper": props.taper,
        
        "taperCurvePoints": [list(pt.location) for pt in bpy.data.node_groups.get('taperNodeGroup').nodes[taper_node_mapping['taperMapping']].mapping.curves[3].points],
        "taperCurveHandleTypes": [pt.handle_type for pt in bpy.data.node_groups.get('taperNodeGroup').nodes[taper_node_mapping['taperMapping']].mapping.curves[3].points],
    
        "branchTipRadius": props.branchTipRadius,
        "ringSpacing": props.ringSpacing,
        "stemRingResolution": props.stemRingResolution,
        "resampleDistance": props.resampleDistance,
    
        "noiseAmplitudeVertical": props.noiseAmplitudeVertical,
        "noiseAmplitudeHorizontal": props.noiseAmplitudeHorizontal,
        "noiseAmplitudeGradient": props.noiseAmplitudeGradient,
        "noiseAmplitudeExponent": props.noiseAmplitudeExponent,
        "noiseScale": props.noiseScale,
        "seed": props.seed,
        
        "curvatureStart": props.curvatureStart,
        "curvatureEnd": props.curvatureEnd,
        "maxCurveSteps": props.maxCurveSteps,
        
        "nrSplits": props.nrSplits,
        "variance": props.variance,
        "stemSplitMode": props.stemSplitMode,
        "stemSplitRotateAngle": props.stemSplitRotateAngle,
        "curvOffsetStrength": props.curvOffsetStrength,
        
        "stemSplitHeightInLevelList": [item.value for item in props.stemSplitHeightInLevelList],
        "stemSplitHeightInLevelListIndex": props.stemSplitHeightInLevelListIndex,
            
        "splitHeightVariation": props.splitHeightVariation,
        "splitLengthVariation": props.splitLengthVariation,
        "stemSplitAngle": props.stemSplitAngle,
        "stemSplitPointAngle": props.stemSplitPointAngle,
    
        "branchClusters": props.branchClusters,
        "showBranchClusterList": [props.branchClusterBoolListList[i].show_branch_cluster for i in range(props.branchClusters)],
        "showParentClusterList": [props.parentClusterBoolListList[i].show_cluster for i in range(props.branchClusters)],
    
        #parentClusterBoolListList
        "parentClusterBoolListList": nestedBranchList,
        
        "nrBranchesList": [props.nrBranchesList[i].value for i in range(props.branchClusters)],
        "branchShapeList": [props.branchShapeList[i].value for i in range(props.branchClusters)],
        "relBranchLengthList": [props.relBranchLengthList[i].value for i in range(props.branchClusters)],
        "relBranchLengthVariationList": [props.relBranchLengthVariationList[i].value for i in range(props.branchClusters)],
        "taperFactorList": [props.taperFactorList[i].value for i in range(props.branchClusters)],
        "ringResolutionList": [props.ringResolutionList[i].value for i in range(props.branchClusters)],
        "branchesStartHeightGlobalList": [props.branchesStartHeightGlobalList[i].value for i in range(props.branchClusters)],
        "branchesEndHeightGlobalList": [props.branchesEndHeightGlobalList[i].value for i in range(props.branchClusters)],
        "branchesStartHeightClusterList": [props.branchesStartHeightClusterList[i].value for i in range(props.branchClusters)],
        "branchesEndHeightClusterList": [props.branchesEndHeightClusterList[i].value for i in range(props.branchClusters)],
        
        "showNoiseSettingsList": [props.showNoiseSettings[i].value for i in range(props.branchClusters)],
        
        "noiseAmplitudeHorizontalList": [props.noiseAmplitudeHorizontalBranchList[i].value for i in range(props.branchClusters)],
        "noiseAmplitudeVerticalList": [props.noiseAmplitudeVerticalBranchList[i].value for i in range(props.branchClusters)],
        "noiseAmplitudeGradientList": [props.noiseAmplitudeBranchGradientList[i].value for i in range(props.branchClusters)],
        "noiseAmplitudeExponentList": [props.noiseAmplitudeBranchExponentList[i].value for i in range(props.branchClusters)],
        "noiseScaleList": [props.noiseScaleList[i].value for i in range(props.branchClusters)],
        
        "showAngleSettingsList": [props.showAngleSettings[i].value for i in range(props.branchClusters)],
        
        "verticalAngleCrownStartList": [props.verticalAngleCrownStartList[i].value for i in range(props.branchClusters)],
        "verticalAngleCrownEndList": [props.verticalAngleCrownEndList[i].value for i in range(props.branchClusters)],
        "verticalAngleBranchStartList": [props.verticalAngleBranchStartList[i].value for i in range(props.branchClusters)],
        "verticalAngleBranchEndList": [props.verticalAngleBranchEndList[i].value for i in range(props.branchClusters)],
        "branchAngleModeList": [props.branchAngleModeList[i].value for i in range(props.branchClusters)],
        "useFibonacciAnglesList": [props.useFibonacciAnglesList[i].value for i in range(props.branchClusters)],
        "fibonacciNr": [props.fibonacciNrList[i].fibonacci_nr for i in range(props.branchClusters)],
        "rotateAngleRangeList": [props.fibonacciNrList[i].rotate_angle_range for i in range(props.branchClusters)],
        "rotateAngleOffsetList": [props.fibonacciNrList[i].rotate_angle_offset for i in range(props.branchClusters)],
        
        "rotateAngleCrownStartList": [props.rotateAngleCrownStartList[i].value for i in range(props.branchClusters)],
        "rotateAngleCrownEndList": [props.rotateAngleCrownEndList[i].value for i in range(props.branchClusters)],
        "rotateAngleBranchStartList": [props.rotateAngleBranchStartList[i].value for i in range(props.branchClusters)],
        "rotateAngleBranchEndList": [props.rotateAngleBranchEndList[i].value for i in range(props.branchClusters)],
        
        "branchGlobalCurvatureStartList": [props.branchGlobalCurvatureStartList[i].value for i in range(props.branchClusters)],
        "branchGlobalCurvatureEndList": [props.branchGlobalCurvatureEndList[i].value for i in range(props.branchClusters)],
        "branchCurvatureStartList": [props.branchCurvatureStartList[i].value for i in range(props.branchClusters)],
        "branchCurvatureEndList": [props.branchCurvatureEndList[i].value for i in range(props.branchClusters)],
        "branchCurvatureOffsetStrengthList": [props.branchCurvatureOffsetStrengthList[i].value for i in     range(props.branchClusters)],
        
        "showSplitSettingsList": [props.showSplitSettings[i].value for i in range(props.branchClusters)],
        
        "nrSplitsPerBranchList": [props.nrSplitsPerBranchList[i].value for i in range(props.branchClusters)],
        "branchSplitModeList": [props.branchSplitModeList[i].value for i in range(props.branchClusters)],
        "branchSplitRotateAngleList": [props.branchSplitRotateAngleList[i].value for i in range(props.branchClusters)],
        "branchSplitAxisVariationList": [props.branchSplitAxisVariationList[i].value for i in range(props.branchClusters)],
        
        "branchSplitAngleList": [props.branchSplitAngleList[i].value for i in range(props.branchClusters)],
        "branchSplitPointAngleList": [props.branchSplitPointAngleList[i].value for i in range(props.branchClusters)],
        
        "splitsPerBranchVariationList": [props.splitsPerBranchVariationList[i].value for i in range(props.branchClusters)],
        "branchVarianceList": [props.branchVarianceList[i].value for i in range(props.branchClusters)],
        "branchSplitHeightVariationList": [props.branchSplitHeightVariationList[i].value for i in range(props.branchClusters)],
        "branchSplitLengthVariationList": [props.branchSplitLengthVariationList[i].value for i in range(props.branchClusters)],
        "hangingBranchesList": [props.hangingBranchesList[i].value for i in range(props.branchClusters)],
        
        "showBranchSplitHeights": [props.showBranchSplitHeights[i].value for i in range(props.branchClusters)],
        
        "branchSplitHeightInLevelListIndex": props.branchSplitHeightInLevelListIndex,
        
        "branchSplitHeightInLevelList_0": [props.branchSplitHeightInLevelList_0[i].value for i in range(0, bpy.context.scene.maxSplitHeightUsed)],
        "branchSplitHeightInLevelListIndex_0": props.branchSplitHeightInLevelListIndex_0,
        
        "branchSplitHeightInLevelList_1": [item.value for item in props.branchSplitHeightInLevelList_1],
        "branchSplitHeightInLevelListIndex_1": props.branchSplitHeightInLevelListIndex_1,
        
        "branchSplitHeightInLevelList_2": [item.value for item in props.branchSplitHeightInLevelList_2],
        "branchSplitHeightInLevelListIndex_2": props.branchSplitHeightInLevelListIndex_2,
        
        "branchSplitHeightInLevelList_3": [item.value for item in props.branchSplitHeightInLevelList_3],
        "branchSplitHeightInLevelListIndex_3": props.branchSplitHeightInLevelListIndex_3,
        
        "branchSplitHeightInLevelList_4": [item.value for item in props.branchSplitHeightInLevelList_4],
        "branchSplitHeightInLevelListIndex_4": props.branchSplitHeightInLevelListIndex_4,
        
        "branchSplitHeightInLevelList_5": [item.value for item in props.branchSplitHeightInLevelList_5],
        "branchSplitHeightInLevelListIndex_5": props.branchSplitHeightInLevelListIndex_5,
        
        "showLeafSettings": [item.value for item in props.showLeafSettings],
        
        "leavesDensityList": [item.value for item in props.leavesDensityList],
        "leafSizeList": [item.value for item in props.leafSizeList],
        "leafAspectRatioList": [item.value for item in props.leafAspectRatioList],
        "leafStartHeightGlobalList": [item.value for item in props.leafStartHeightGlobalList],
        "leafEndHeightGlobalList": [item.value for item in props.leafEndHeightGlobalList],
        "leafStartHeightClusterList": [item.value for item in props.leafStartHeightClusterList],
        "leafEndHeightClusterList": [item.value for item in props.leafEndHeightClusterList],
        "leafTypeList": [item.value for item in props.leafTypeList],
        "leafAngleModeList": [item.value for item in props.leafAngleModeList],
        
        "leafVerticalAngleBranchStartList": [item.value for item in props.leafVerticalAngleBranchStartList],
        "leafVerticalAngleBranchEndList": [item.value for item in props.leafVerticalAngleBranchEndList],
        "leafRotateAngleBranchStartList": [item.value for item in props.leafRotateAngleBranchStartList],
        "leafRotateAngleBranchEndList": [item.value for item in props.leafRotateAngleBranchEndList],
        "leafTiltAngleBranchStartList": [item.value for item in props.leafTiltAngleBranchStartList],
        "leafTiltAngleBranchEndList": [item.value for item in props.leafTiltAngleBranchEndList],
        #TODO: parentClusterBoolListList
        "showLeafClusterList": [props.leafParentClusterBoolListList[i].show_leaf_cluster for  i in range(len(props.leafParentClusterBoolListList))],
        "leafParentClusterBoolListList": nestedLeafList
    }

    with open(filePath, 'w') as f:
        json.dump(data, f)
        
        
def load_properties(filepath, context):
    with open(filepath, 'r') as f:
        data = json.load(f)
        props = context.scene
                
        props.treeHeight = data.get("treeHeight", props.treeHeight)
        treeGrowDir = data.get("treeGrowDir", props.treeGrowDir)
        if isinstance(treeGrowDir, list) and len(treeGrowDir) == 3:
            props.treeGrowDir = treeGrowDir
        props.taper = data.get("taper", props.taper)
        
        controlPts = []
        controlPts = data.get("taperCurvePoints", controlPts)
        handleTypes = []
        handleTypes = data.get("taperCurveHandleTypes", handleTypes)
        nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
        
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
        curveElement.points[0].location = controlPts[0]
        curveElement.points[0].handle_type = handleTypes[0]
        curveElement.points[1].location = controlPts[1]
        curveElement.points[1].handle_type = handleTypes[0]
        if len(controlPts) > 2:
            for i in range(2, len(controlPts)):
                curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                curveElement.points[len(curveElement.points) - 1].location.x = controlPts[i][0]
                curveElement.points[len(curveElement.points) - 1].location.y = controlPts[i][1]
                
                curveElement.points[len(curveElement.points) - 1].handle_type = handleTypes[i]
        nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.update()
        
        props.branchTipRadius = data.get("branchTipRadius", props.branchTipRadius)
        props.ringSpacing = data.get("ringSpacing", props.ringSpacing)
        props.stemRingResolution = data.get("stemRingResolution", props.stemRingResolution)
        props.resampleDistance = data.get("resampleDistance", props.resampleDistance)
        
        props.noiseAmplitudeVertical = data.get("noiseAmplitudeVertical", props.noiseAmplitudeVertical)
        props.noiseAmplitudeHorizontal = data.get("noiseAmplitudeHorizontal", props.noiseAmplitudeHorizontal)
        props.noiseAmplitudeGradient = data.get("noiseAmplitudeGradient", props.noiseAmplitudeGradient)
        props.noiseAmplitudeExponent = data.get("noiseAmplitudeExponent", props.noiseAmplitudeExponent)
        props.noiseScale = data.get("noiseScale", props.noiseScale)
        props.seed = data.get("seed", props.seed)
        
        props.curvatureStart = data.get("curvatureStart", props.curvatureStart)
        props.curvatureEnd = data.get("curvatureEnd", props.curvatureEnd)
        props.maxCurveSteps = data.get("maxCurveSteps", props.maxCurveSteps)
        
        props.nrSplits = data.get("nrSplits", props.nrSplits)
        props.variance = data.get("variance", props.variance)
        props.stemSplitMode = data.get("stemSplitMode", props.stemSplitMode)
        props.stemSplitRotateAngle = data.get("stemSplitRotateAngle", props.stemSplitRotateAngle)
        props.curvOffsetStrength = data.get("curvOffsetStrength", props.curvOffsetStrength)
        
        for value in data.get("stemSplitHeightInLevelList", []):
            item = props.stemSplitHeightInLevelList.add()
            item.value = value
        props.stemSplitHeightInLevelListIndex = data.get("stemSplitHeightInLevelListIndex", props.stemSplitHeightInLevelListIndex)
                
        props.splitHeightVariation = data.get("splitHeightVariation", props.splitHeightVariation)
        props.splitLengthVariation = data.get("splitLengthVariation", props.splitLengthVariation)
        props.stemSplitAngle = data.get("stemSplitAngle", props.stemSplitAngle)
        props.stemSplitPointAngle = data.get("stemSplitPointAngle", props.stemSplitPointAngle)
        
        props.branchClusters = data.get("branchClusters", props.branchClusters)
        
        for value in data.get("nrBranchesList", []):
            item = props.nrBranchesList.add()
            item.value = value
            
        for value in data.get("branchShapeList", []):
            item = props.branchShapeList.add()
            item.value = value
            
        for value in data.get("relBranchLengthList", []):
            item = props.relBranchLengthList.add()
            item.value = value
            
        for value in data.get("relBranchLengthVariationList", []):
            item = props.relBranchLengthVariationList.add()
            item.value = value
            
        for value in data.get("taperFactorList", []):
            item = props.taperFactorList.add()
            item.value = value
        
        for value in data.get("ringResolutionList", []):
            item = props.ringResolutionList.add()
            item.value = value
        
        for value in data.get("branchesStartHeightGlobalList", []):
            item = props.branchesStartHeightGlobalList.add()
            item.value = value
            
        for value in data.get("branchesEndHeightGlobalList", []):
            item = props.branchesEndHeightGlobalList.add()
            item.value = value
            
        for value in data.get("branchesStartHeightClusterList", []):
            item = props.branchesStartHeightClusterList.add()
            item.value = value
            
        for value in data.get("branchesEndHeightClusterList", []):
            item = props.branchesEndHeightClusterList.add()
            item.value = value
        
        for value in data.get("noiseAmplitudeHorizontalBranchList", []):
            item = props.noiseAmplitudeHorizontalBranchList.add()
            item.value = value
        
        for value in data.get("noiseAmplitudeVerticalBranchList", []):
            item = props.noiseAmplitudeVerticalBranchList.add()
            item.value = value
        
        for value in data.get("noiseAmplitudeBranchGradientList", []):
            item = props.noiseAmplitudeBranchGradientList.add()
            item.value = value
            
        for value in data.get("noiseAmplitudeBranchExponentList", []):
            item = props.noiseAmplitudBranchExponentList.add()
            item.value = value
            
        for value in data.get("noiseScaleList", []):
            item = props.noiseScaleList.add()
            item.value = value
            
        
        for value in data.get("verticalAngleCrownStartList", []):
            item = props.verticalAngleCrownStartList.add()
            item.value = value
            
        for value in data.get("verticalAngleCrownEndList", []):
            item = props.verticalAngleCrownEndList.add()
            item.value = value
            
        for value in data.get("verticalAngleBranchStartList", []):
            item = props.verticalAngleBranchStartList.add()
            item.value = value
            
        for value in data.get("verticalAngleBranchEndList", []):
            item = props.verticalAngleBranchEndList.add()
            item.value = value
        
        
        for value in data.get("branchAngleModeList", []):
            item = props.branchAngleModeList.add()
            item.value = value
            
        # "useFibonacciAnglesList": [props.useFibonacciAnglesList[i].value for i in range(props.branchClusters)],
        # "fibonacciNr": [props.fibonacciNrList[i].fibonacci_nr for i in range(props.branchClusters)],
        # "rotateAngleRangeList": [props.fibonacciNrList[i].rotate_angle_range for i in range(props.branchClusters)],
        # "rotateAngleOffsetList": [props.fibonacciNrList[i].rotate_angle_offset for i in range(props.branchClusters)],
        
        for value in data.get("useFibonacciAnglesList", []):
            item = props.useFibonacciAnglesList.add()
            item.value = value
            
        for value in data.get("fibonacciNr", []):
            item = props.fibonacciNrList.add()
            item.fibonacci_nr = value
        
        fibIndex = 0
        for value in data.get("rotateAngleRangeList", []):
            item = props.fibonacciNrList[fibIndex]
            item.rotate_angle_range = value
            fibIndex += 1
            
        fibIndex = 0
        for value in data.get("rotateAngleOffsetList", []):
            item = props.fibonacciNrList[fibIndex]
            item.rotate_angle_offset = value
            fibIndex += 1
        
        
        for value in data.get("rotateAngleCrownStartList", []):
            item = props.rotateAngleCrownStartList.add()
            item.value = value
            
        for value in data.get("rotateAngleCrownEndList", []):
            item = props.rotateAngleCrownEndList.add()
            item.value = value
            
        for value in data.get("rotateAngleBranchStartList", []):
            item = props.rotateAngleBranchStartList.add()
            item.value = value
            
        for value in data.get("rotateAngleBranchEndList", []):
            item = props.rotateAngleBranchEndList.add()
            item.value = value
            
            
        for value in data.get("branchGlobalCurvatureStartList", []):
            item = props.branchGlobalCurvatureStartList.add()
            item.value = value
            
        for value in data.get("branchGlobalCurvatureEndList", []):
            item = props.branchGlobalCurvatureEndList.add()
            item.value = value
        
        for value in data.get("branchCurvatureStartList", []):
            item = props.branchCurvatureStartList.add()
            item.value = value
           
        for value in data.get("branchCurvatureEndList", []):
            item = props.branchCurvatureEndList.add()
            item.value = value
        
        for value in data.get("branchCurvatureOffsetStrengthList", []):
            item = props.branchCurvatureOffsetStrengthList.add()
            item.value = value
        
        
        
        for value in data.get("nrSplitsPerBranchList", []):
            item = props.nrSplitsPerBranchList.add()
            item.value = value
            
        for value in data.get("branchSplitModeList", []):
            item = props.branchSplitModeList.add()
            item.value = value
            
        for value in data.get("branchSplitRotateAngleList", []):
            item = props.branchSplitRotateAngleList.add()
            item.value = value
            
        for value in data.get("branchSplitAxisVariationList", []):
            item = props.branchSplitAxisVariationList.add()
            item.value = value
        
        
            
            
        for value in data.get("branchSplitAngleList", []):
            item = props.branchSplitAngleList.add()
            item.value = value
            
        for value in data.get("branchSplitPointAngleList", []):
            item = props.branchSplitPointAngleList.add()
            item.value = value
                        
        
        for value in data.get("splitsPerBranchVariationList", []):
            item = props.splitsPerBranchVariationList.add()
            item.value = value
            
        for value in data.get("branchVarianceList", []):
            item = props.branchVarianceList.add()
            item.value = value
        
        for value in data.get("branchSplitHeightVariationList", []):
            item = props.branchSplitHeightVariationList.add()
            item.value = value
        
        for value in data.get("branchSplitLengthVariationList", []):
            item = props.branchSplitLengthVariationList.add()
            item.value = value
        
        for value in data.get("hangingBranchesList", []):
            item = props.hangingBranchesList.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex = data.get("branchSplitHeightInLevelListIndex", props.branchSplitHeightInLevelListIndex)
            
        for value in data.get("branchSplitHeightInLevelList_0", []):
            item = props.branchSplitHeightInLevelList_0.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_0 = data.get("branchSplitHeightInLevelListIndex_0", props.branchSplitHeightInLevelListIndex_0)
        
        for value in data.get("branchSplitHeightInLevelList_1", []):
            item = props.branchSplitHeightInLevelList_1.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_1 = data.get("branchSplitHeightInLevelListIndex_1", props.branchSplitHeightInLevelListIndex_1)
        
        for value in data.get("branchSplitHeightInLevelList_2", []):
            item = props.branchSplitHeightInLevelList_0.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_2 = data.get("branchSplitHeightInLevelListIndex_2", props.branchSplitHeightInLevelListIndex_2)
        
        for value in data.get("branchSplitHeightInLevelList_3", []):
            item = props.branchSplitHeightInLevelList_3.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_3 = data.get("branchSplitHeightInLevelListIndex_3", props.branchSplitHeightInLevelListIndex_3)
        
        for value in data.get("branchSplitHeightInLevelList_4", []):
            item = props.branchSplitHeightInLevelList_4.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_4 = data.get("branchSplitHeightInLevelListIndex_4", props.branchSplitHeightInLevelListIndex_4)
        
        for value in data.get("branchSplitHeightInLevelList_5", []):
            item = props.branchSplitHeightInLevelList_5.add()
            item.value = value
            
        props.branchSplitHeightInLevelListIndex_5 = data.get("branchSplitHeightInLevelListIndex_5", props.branchSplitHeightInLevelListIndex_5)
        
        for value in data.get("leavesDensityList", []):
            item = props.leavesDensityList.add()
            item.value = value
            
        for value in data.get("leafSizeList", []):
            item = props.leafSizeList.add()
            item.value = value
            
        for value in data.get("leafAspectRatioList", []):
            item = props.leafAspectRatioList.add()
            item.value = value
           
        for value in data.get("leafStartHeightGlobalList", []):
            item = props.leafStartHeightGlobalList.add()
            item.value = value
           
        for value in data.get("leafEndHeightGlobalList", []):
            item = props.leafEndHeightGlobalList.add()
            item.value = value
              
        for value in data.get("leafStartHeightClusterList", []):
            item = props.leafStartHeightClusterList.add()
            item.value = value
            
        for value in data.get("leafEndHeightClusterList", []):
            item = props.leafEndHeightClusterList.add()
            item.value = value
            
        for value in data.get("leafTypeList", []):
            item = props.leafTypeList.add()
            item.value = value
            
        for value in data.get("leafAngleModeList", []):
            item = props.leafAngleModeList.add()
            item.value = value
            
        for value in data.get("leafVerticalAngleBranchStartList", []):
            item = props.leafVerticalAngleBranchStartList.add()
            item.value = value
            
        for value in data.get("leafVerticalAngleBranchEndList", []):
            item = props.leafVerticalAngleBranchEndList.add()
            item.value = value
           
        for value in data.get("leafRotateAngleBranchStartList", []):
            item = props.leafRotateAngleBranchStartList.add()
            item.value = value
         
        for value in data.get("leafRotateAngleBranchEndList", []):
            item = props.leafRotateAngleBranchEndList.add()
            item.value = value
        
        for value in data.get("leafTiltAngleBranchStartList", []):
            item = props.leafTiltAngleBranchStartList.add()
            item.value = value
        
        for value in data.get("leafTiltAngleBranchEndList", []):
            item = props.leafTiltAngleBranchEndList.add()
            item.value = value
        
        
        
        #generateTree()
        #-----------------------
        #"nrBranchesList": [props.nrBranchesList[i].value for i in range(0, props.branchClusters)],
        
        #"branchSplitModeList": [item.value for item in props.branchSplitModeList],
        #"branchVarianceList": [item.value for item in props.branchVarianceList],
        #"branchSplitRotateAngleList": [item.value for item in props.branchSplitRotateAngleList],
        #"branchSplitAngleList": [item.value for item in props.branchSplitAngleList],
        #"branchSplitPointAngleList": [item.value for item in props.branchSplitPointAngleList],
        #"branchShapeList": [item.value for item in props.branchShapeList],
        #"relBranchLengthList": [item.value for item in props.relBranchLengthList],
        #"taperFactorList": [item.value for item in props.taperFactorList],
        #"verticalAngleCrownStartList": [item.value for item in props.verticalAngleCrownStartList],
        #"verticalAngleCrownEndList": [item.value for item in props.verticalAngleCrownEndList],
        #"verticalAngleBranchStartList": [item.value for item in props.verticalAngleBranchStartList],
        #"verticalAngleBranchEndList": [item.value for item in props.verticalAngleBranchEndList],
        #"branchAngleModeList": [item.value for item in props.branchAngleModeList],
        #"rotateAngleList": [item.value for item in props.rotateAngleList],
        #"rotateAngleRangeList": [item.value for item in props.rotateAngleRangeList],
        #"branchesStartHeightGlobalList": [item.value for item in props.branchesStartHeightGlobalList],
        #"branchesEndHeightGlobalList": [item.value for item in props.branchesEndHeightGlobalList],
        #"branchesStartHeightClusterList": [item.value for item in props.branchesStartHeightClusterList],
        #"branchesEndHeightClusterList": [item.value for item in props.branchesEndHeightClusterList],
        #"branchCurvatureList": [item.value for item in props.branchCurvatureList],
        #"branchCurvatureOffsetStrengthList": [item.value for item in props.branchCurvatureOffsetStrengthList],
        #"nrSplitsPerBranchList": [item.value for item in props.nrSplitsPerBranchList],
        #"splitsPerBranchVariationList": [item.value for item in props.splitsPerBranchVariationList],
        #"branchSplitHeightVariationList": [item.value for item in props.branchSplitHeightVariationList],
        
        
    
    
    
def unregister():
    
    #properties
    #bpy.utils.unregister_class(treeShapeEnumProp)
    #bpy.utils.unregister_class(splitModeEnumProp)
    #bpy.utils.unregister_class(angleModeEnumProp)
    #bpy.utils.unregister_class(intProp)
    #bpy.utils.unregister_class(floatProp)
    #bpy.utils.unregister_class(posFloatProp)
    #bpy.utils.unregister_class(floatProp01)
    #bpy.utils.unregister_class(floatListProp)
    #bpy.utils.unregister_class(boolProp)
    #bpy.utils.unregister_class(parentClusterBoolListProp)
    
    #UILists
    bpy.utils.unregister_class(UL_stemSplitLevelList)
    
    #operators
    #bpy.utils.unregister_class(addItem)
    #bpy.utils.unregister_class(removeItem)
    #bpy.utils.unregister_class(addBranchSplitLevel)
    #bpy.utils.unregister_class(removeBranchSplitLevel)
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
    #del bpy.types.Scene.noiseAmplitude
    #del bpy.types.Scene.noiseAmplitudeGradient
    #del bpy.types.Scene.noiseAmplitudeExponent
    #del bpy.types.Scene.noiseScale
    #del bpy.types.Scene.splitCurvature
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