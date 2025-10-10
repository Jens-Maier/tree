# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import json
import os
import bmesh

class startNodeInfo():
    def __init__(self, StartNode, NextIndex, StartTval, EndTval, StartTvalGlobal, EndTvalGlobal):
        self.startNode = StartNode
        self.nextIndex = NextIndex
        self.startTval = StartTval
        self.endTval = EndTval
        self.startTvalGlobal = StartTvalGlobal
        self.endTvalGlobal = EndTvalGlobal
        
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
        self.rotateAngleRange = 0.0
        
class dummyStartPointData():
    def __init__(self):
        self.dummyStartPoints = [] # for all other stems at same height as startPoint
        
        
class rotationStep():
    def __init__(self, RotationPoint, Curvature, CurveAxis, IsLast):
       self.rotationPoint = RotationPoint
       self.curvature = Curvature
       self.curveAxis = CurveAxis
       self.isLast = IsLast

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
                     
                        startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, startTvalSegment, endTvalSegment, segmentStartGlobal, segmentEndGlobal))
        
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
                                startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, startTval, endTval, segStart, segEnd))
                                
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
                               
                
        for b in self.branches:
            branchNodesNextIndexStartTvalEndTval.append([])
            for n in b:
                for i in range(0, len(n.next)):
                    branchNodesNextIndexStartTvalEndTval[len(branchNodesNextIndexStartTvalEndTval) - 1].append(startNodeInfo(n, i, 0.0, 1.0, 0.0, 1.0))
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
                            parallelPoints.append(sampleSplineT(self.point, n.point, self.tangent[i + 1], n.tangent[0], tVal))
                        if len(self.next) == 1:
                            #treeGen.report({'INFO'}, "in getAllParallelStartPoints() appinding point 1")
                            parallelPoints.append(sampleSplineT(self.point, n.point, self.tangent[0], n.tangent[0], tVal))
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
                return pow(lerp(0.0, amplitude, position / gradient), exponent)
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
                nextRotationSteps.append(rotationStep(self.point, angle, axis, True))
            if len(self.next) == 2 and n == 0:
                nextRotationSteps.append(rotationStep(self.point, angleA, axis, True))
            if len(self.next) == 2 and n == 1:
                nextRotationSteps.append(rotationStep(self.point, angleB, axis, True))
            
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
            
            centerPoint = sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0,0.0,1.0)), nextTangent, self.tValGlobal)
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
            
        globalCurvature = lerp(curvatureStartGlobal, curvatureEndGlobal, self.tValGlobal)
        branchCurvature = lerp(curvatureStartBranch, curvatureEndBranch, self.tValBranch)
        
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
                rotationSteps.append(rotationStep(self.point, curvature * sectionLength * reducedCurveStepFactor, curveAxis, isLast))
            else:
                rotationSteps.append(rotationStep(self.point, curvature * sectionLength, curveAxis, isLast))
        
        
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
    
    def resampleSpline(self, rootNode, treeGen, resampleDistance):
        treeGen.report({'INFO'}, f"in resampleSpline: point: {self.point}")
        treeGen.report({'INFO'}, f"in resampleSpline: next[0].point: {self.next[0].point}")
        treeGen.report({'INFO'}, f"in resampleSpline: resampleDistance: {resampleDistance}")
        treeGen.report({'INFO'}, f"in resampleSpline: len(self.next): {len(self.next)}")
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
 
 
class segment():
    def __init__(self, ClusterIndex, Start, End, FirstTangent, StartTangent, EndTangent, StartCotangent, EndCotangent, StartRadius, EndRadius, StartTvalGlobal, EndTvalGlobal, StartTvalBranch, EndTvalBranch, RingResolution, ConnectedToPrevious, BranchLength, LongestBranchLengthInCluster, StartTaper, EndTaper):
        self.clusterIndex = ClusterIndex
        self.start = Start
        self.end = End
        self.firstTangent = FirstTangent
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
                for i in range(context.scene.treeSettings.maxSplitHeightUsed + 1, len(context.scene.stemSplitHeightInLevelList)):
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



class floatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=0)

def myNodeTree():
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    return bpy.data.node_groups['CurveNodeGroup'].nodes

curve_node_mapping = {}
taper_node_mapping = {}

def myCurveData(curve_name):
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        curve_node_mapping[curve_name] = cn.name
    nodeTree = myNodeTree()[curve_node_mapping[curve_name]]
    return nodeTree

class resetCurvesButton(bpy.types.Operator):
    bl_idname = "scene.reset_curves"
    bl_label = "Reset"
    
    def execute(self, context):
        nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
        nrCurves = len(nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves)
        curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
        
        resetTaperCurve()
        return {'FINISHED'}

def ensure_stem_curve_node():
    curve_name = "Stem"
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        curve_node_mapping[curve_name] = cn.name
    return curve_name

def ensure_branch_curve_node(idx):
    curve_name = f"BranchCluster_{idx}"
    if 'CurveNodeGroup' not in bpy.data.node_groups:
        bpy.data.node_groups.new('CurveNodeGroup', 'ShaderNodeTree')
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        #cn.label = curve_name
        curve_node_mapping[curve_name] = cn.name
    return curve_name


def drawDebugPoint(pos, size, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = size
    bpy.context.active_object.name=name


class AddBranchClusterButton(bpy.types.Operator):
    bl_idname = "scene.add_branch_cluster"
    bl_label = "Add Branch Cluster"

    def execute(self, context):
        context.scene.nrBranchClusters += 1
        idx = context.scene.nrBranchClusters - 1
        ensure_branch_curve_node(idx)
        self.report({'INFO'}, f"Added branch cluster {idx}")
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


    
class BranchSettings(bpy.types.Panel):
    bl_label = "Branch Settings"
    bl_idname = "PT_branchSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        
        #layout.template_curve_mapping(myCurveData('Stem'), "mapping")
        
        #layout.prop(context.scene, "evaluate", slider=True)
        #layout.operator("scene.evaluate_button", text="Evaluate").x = context.scene.evaluate
        #layout.operator("scene.init_button", text="Initialise")
        #layout.template_curve_mapping(taperCurveData('taperMapping'), "mapping")
        
        # FUNKT!
        #layout.prop(context.scene, "nrBranchClusters")
        #layout.operator("scene.add_branch_cluster", text="Add Branch Cluster")
        #for i in range(0, context.scene.nrBranchClusters):
        #    curve_name = ensure_branch_curve_node(i)
        #    box = layout.box()
        #    box.label(text=f"Branch Cluster {i}")
        #    curve_node = myCurveData(curve_name)
        #    box.template_curve_mapping(curve_node, "mapping")
        #    op = box.operator("scene.evaluate_branch_cluster", text="Evaluate")
        #    op.idx = i
        #    reset = box.operator("scene.reset_branch_cluster_curve", text="Reset")
        #    reset.idx = i
        
        #layout = self.layout
        #obj = context.object
        scene = context.scene
        bl_parent_id = 'PT_TreeGen'
        bl_optione = {'DEFAULT_CLOSED'}
        
        
        row = layout.row(align = True)
        row.operator("scene.add_list_item", text="Add")
        row.operator("scene.remove_list_item", text="Remove")
        
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
                    #if scene.branchClusterSettingsList[i].useTaperCurve == True:
                    #    # reset | hide
                    #    row = box.row()
                    #    row.operator("scene.reset_curves_cluster", text="Reset taper curve").level = i
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
                        curve_name = ensure_branch_curve_node(i)
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
    
def sampleCurveStem(self, x):
    ensure_stem_curve_node()
    
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
    
    ensure_stem_curve_node()
    nodeGroups = bpy.data.node_groups.get('CurveNodeGroup') #taperNodeGroup')
    curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] #'Stem'
    #self.report({'INFO'}, "sample spline: ")
    #for p in curveElement.points:
    #    self.report({'INFO'}, f"stem: point: {p.location}")
        
    y = 0.0
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
            
            px = sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
            py = sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
            
            #self.report({'INFO'}, f"stem: sample point: x: {x}, y: {y}, px: {px}, py: {py}")
            return py
    self.report({'ERROR'}, f"segment not found!, x: {x}")
    return 0.0

def sampleCurveBranch(self, x, clusterIndex):
    
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
    
    curve_name = ensure_branch_curve_node(clusterIndex)
    
    nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
    curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
    y = 0.0
    
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
            
            px = sampleSpline(p0.x, p1.x, p2.x, p3.x, tx)
            py = sampleSpline(p0.y, p1.y, p2.y, p3.y, tx)
            
            return py
                
    return 0.0
    

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
    
    newPoint = sampleSplineT(p0, p1, t0, t1, t)
    newTangent = sampleSplineTangentT(p0, p1, t0, t1, t)
    newCotangent = lerp(c0, c1, t)
    newRadius = lerp(r0, r1, t)
    newTvalGlobal = lerp(splitAfterNode.tValGlobal, splitAfterNode.next[nextIndex].tValGlobal, nrNodesToTip * splitHeight - splitAfterNodeNr)
    
    newTvalBranch = lerp(splitAfterNode.tValBranch, splitAfterNode.next[nextIndex].tValBranch, splitHeight);
        
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

def lerp(a, b, t):
    return a + (b - a) * t


class SimplexNoiseGenerator():
    def __init__(self, treeGen, seed=None):
        self.onethird = 1.0 / 3.0
        self.onesixth = 1.0 / 6.0

        self.A = [0, 0, 0]
        self.s = 0.0
        self.u = 0.0
        self.v = 0.0
        self.w = 0.0
        self.i = 0
        self.j = 0
        self.k = 0

        # permutation table (T)
        if seed is None:
            self.T = [int((x * 0x10000) % 0xFFFFFFFF) for x in range(8)]
        else:
            expandedSeed = []
            random.seed(seed)
            self.T = [random.randint(0, 2**31 - 1) for _ in range(8)]
            

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
                
                data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, leafPos, treeGrowDir, rootNode, treeHeight, False)
                
                startPoint = data.startPoint
                
                startNodeNextIndex = data.startNodeNextIndex
                startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                         data.startNode.next[startNodeNextIndex].point, 
                                                         data.tangent, 
                                                         data.startNode.next[startNodeNextIndex].tangent[0], 
                                                         data.t)
                                                         
                startPointRadius = lerp(data.startNode.radius, data.startNode.next[startNodeNextIndex].radius, data.t)
                
                verticalAngle = lerp(leafClusterSettingsList[leafClusterIndex].leafVerticalAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafVerticalAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                rotateAngle = lerp(leafClusterSettingsList[leafClusterIndex].leafRotateAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafRotateAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                tiltAngle = lerp(leafClusterSettingsList[leafClusterIndex].leafTiltAngleBranchStart, leafClusterSettingsList[leafClusterIndex].leafTiltAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
    
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
                        whorledLeafCotangent = Quaternion(whorledLeafTangent, tiltAngle * math.sin(windingAngle + i * whorlAngle)) @ whorledLeafCotangent
                        
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


def findClosestVectors(treeGen, vectors, target_vector):
    
    def get_angle(v):
        angle = math.atan2(v[1], v[0])
        return (angle + 2.0 * math.pi) % (2.0 * math.pi)
    
    target_angle = get_angle(target_vector)
    
    min_clockwise_diff = float(2.0 * math.pi)
    closest_clockwise_vector = None

    min_anticlockwise_diff = float(2.0 * math.pi)
    closest_anticlockwise_vector = None

    for v in vectors:
        vector_angle = get_angle(v)

        # Calculate clockwise difference
        # This handles the wrap-around from 0 to 360
        clockwise_diff = (target_angle - vector_angle + 2.0 * math.pi) % (2.0 * math.pi)
        if clockwise_diff < min_clockwise_diff and clockwise_diff != 0:
            min_clockwise_diff = clockwise_diff
            closest_clockwise_vector = v

        # Calculate anticlockwise difference
        # This also handles the wrap-around
        anticlockwise_diff = (vector_angle - target_angle + 2.0 * math.pi) % (2.0 * math.pi)
        if anticlockwise_diff < min_anticlockwise_diff and anticlockwise_diff != 0:
            min_anticlockwise_diff = anticlockwise_diff
            closest_anticlockwise_vector = v
    
    #treeGen.report({'INFO'}, f"min anticlockwise diff: {min_anticlockwise_diff}")
    #treeGen.report({'INFO'}, f"min clockwise diff: {min_clockwise_diff}")
    
    # Handle the case where the target vector is not found in the list, but one of the vectors is the same.
    if closest_clockwise_vector is None:
        closest_clockwise_vector = closest_anticlockwise_vector
    if closest_anticlockwise_vector is None:
        closest_anticlockwise_vector = closest_clockwise_vector
        
    clockwise_angle_range = min_clockwise_diff / 2.0
    anticlockwise_angle_range = min_anticlockwise_diff / 2.0
    #treeGen.report({'INFO'}, f"clockwise_angle_range: {clockwise_angle_range}")
    #treeGen.report({'INFO'}, f"anticlockwise_angle_range: {anticlockwise_angle_range}")
    
    half_closest_clockwise_vector = Quaternion(Vector((0.0,0.0,1.0)), -clockwise_angle_range) @ target_vector
    half_closest_anticlockwise_vector = Quaternion(Vector((0.0,0.0,1.0)), anticlockwise_angle_range) @ target_vector
    
    return closest_clockwise_vector, closest_anticlockwise_vector, half_closest_clockwise_vector, half_closest_anticlockwise_vector, clockwise_angle_range, anticlockwise_angle_range


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
                startPointData.append(generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False))
            
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
                (dummyData, centerPoint) = generateDummyStartPointData(treeGen, rootNode, data)
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
                
                (cwVector, acwVector, halfCwVector, halfAcwVector, halfAngleCW, halfAngleACW) = findClosestVectors(treeGen, directions, startPointData[n].outwardDir) # -> adaptive rotate angle range !!!
                
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
                
                data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False)
                
                startPoint = data.startPoint
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
                
                globalRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleCrownStart, branchClusterSettingsList[clusterIndex].rotateAngleCrownEnd, branchStartTvalGlobal)
                
                branchRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleBranchStart, branchClusterSettingsList[clusterIndex].rotateAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t)) # tValBranch == 0 !!!
                
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
        
                startTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                startTvalBranch = lerp(data.startNode.tValBranch, data.startNode.next[startNodeNextIndex].tValBranch, data.t)
                treeShapeRatioValue = shapeRatio(self, context, startTvalGlobal, branchClusterSettingsList[clusterIndex].treeShape.value)
                 
                branchShapeRatioValue = shapeRatio(self, context, startTvalBranch, branchClusterSettingsList[clusterIndex].branchShape.value)
                
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
                    whorlCount = int(round(lerp(branchClusterSettingsList[clusterIndex].branchWhorlCountStart, branchClusterSettingsList[clusterIndex].branchWhorlCountEnd, startTvalGlobal)))
                    
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


def generateDummyStartPointData(treeGen, rootNode, startPointDatum):
    
    #treeGen.report({'INFO'}, "in generateDummyStartPointData()")
    parallelPoints = []
    rootNode.getAllParallelStartPoints(treeGen, startPointDatum.startPointTvalGlobal, startPointDatum.startNode, parallelPoints)
    
    dummyStartPointData = []
    centerPoint = Vector(startPointDatum.startPoint)
    n = 1
    for p in parallelPoints:
        centerPoint += p
        n += 1
    centerPoint = centerPoint / n
    
    for p in parallelPoints:
        dummyStartPointData.append(startPointData(p, startPointDatum.startPointTvalGlobal, Vector((0.0,0.0,0.0)), None, 0, 0, 0, Vector((0.0,0.0,0.0)), Vector((0.0,0.0,0.0))))
    
    return (dummyStartPointData, centerPoint)


def generateStartPointData(self, 
                           startNodesNextIndexStartTvalEndTval, 
                           segmentLengths, 
                           branchPos, 
                           treeGrowDir, 
                           rootNode, 
                           treeHeight, 
                           calledFromAddLeaves):
    self.report({'INFO'}, "---------------------------------------------")
    self.report({'INFO'}, "in generateStartPointData()")
    accumLength = 0.0
    startNodeIndex = 0
    tVal = 0.0
    tValGlobal = 0.0
    
    for i in range(len(segmentLengths)):
        if accumLength + segmentLengths[i] >= branchPos:
            startNodeIndex = i
            segStart = accumLength
            segLen = segmentLengths[i]
            if segLen > 0.0:
                tVal = (branchPos - segStart) / segLen
            
            startTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].startTval
            endTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].endTval
            startNode = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode
            nextNode = startNode.next[startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex]
            
            tVal = startTval + tVal * (endTval - startTval)
            startPointTvalGlobal = startNode.tValGlobal + tVal * (nextNode.tValGlobal - startNode.tValGlobal)
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
    
    outwardDir = lerp(
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal) - centerPoint
    
    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent
        
    outwardDir.z = 0.0

    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent
        
    outwardDir = outwardDir.normalized()
    
    self.report({'INFO'}, f"in generateStartPointData(): outwardDir: {outwardDir}")
    return startPointData(startPoint, startPointTvalGlobal, outwardDir, nStart, startNodeIndex, startNodeNextIndex, tVal, tangent, startPointCotangent)


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
    
    offset = 0
    counter = 0
    
    startSection = 0
    
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
                pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections)
                tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections).normalized()
                
                if section == 0:
                    tangent = segments[s].firstTangent
                
                dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / sections)
                dirB = (tangent.cross(dirA)).normalized()
                dirA = (dirB.cross(tangent)).normalized()
                
                tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / sections)
                
                tValBranch = segments[s].startTvalBranch + (segments[s].endTvalBranch - segments[s].startTvalBranch) * (section / sections)
                tValGlobal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].endTvalGlobal) * (section / sections)
                if segments[s].clusterIndex == -1:
                    taper = lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                    startRadius = segments[s].startRadius
                    endRadius = segments[s].endRadius
                    linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                    normalizedCurve = (1.0 - branchTipRadius) * tVal + sampleCurveStem(treeGen, tVal)
                    
                    radius = linearRadius * normalizedCurve
                else:
                    taper = lerp(segments[s].startTaper, segments[s].endTaper, section / sections)
                    startRadius = segments[s].startRadius
                    endRadius = segments[s].endRadius
                    linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing))
                    normalizedCurve = (1.0 - branchTipRadius) * tValBranch + sampleCurveBranch(treeGen, tValBranch, segments[s].clusterIndex) * context.scene.taperFactorList[segments[s].clusterIndex].taperFactor 
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
            
            for c in range(0, sections): 
                for j in range(0, segments[s].ringResolution):
                    faces.append((offset + c * (segments[s].ringResolution + 1) + j,
                                  offset + c * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1), 
                                  offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + (j + 1) % (segments[s].ringResolution + 1), 
                                  offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + j))
                        
            offset += counter
            counter = 0
        
    meshData = bpy.data.meshes.new("treeMesh")
    meshData.from_pydata(vertices, [], faces)
    
    ############################################################
    #mesh.calc_normals_split()
    
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
    
    bpy.ops.object.shade_auto_smooth(angle=0.8)
    
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

def update_fibonacci_numbers(self):
    fn0 = 1.0
    fn1 = 1.0
    self.rotate_angle_range = 2.0 * math.pi
    if self.fibonacci_nr > 2:
        for n in range(2, self.fibonacci_nr + 1):
            temp = fn0 + fn1
            fn0 = fn1
            fn1 = temp
    self.fibonacci_angle = 2.0 * math.pi * (1.0 - fn0 / fn1)
    
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
        row.prop(context.scene.treePreset, "value", text="")
        row = layout.row()
        row.operator("export.load_preset", text="Load Preset")
        
        row = layout.row()
        row.label(icon = 'COLORSET_12_VEC')
        row.operator("object.generate_tree", text="Generate Tree")
        
    
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
        layout.operator("scene.reset_curves", text="Reset taper curve")
        
        row = layout.row()
        #layout.template_curve_mapping(taperCurveData('taperMapping'), "mapping")
        layout.template_curve_mapping(myCurveData('Stem'), "mapping")
        
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
        row.operator("scene.remove_stem_split_level", text="Remove").index = scene.treeSettings.stemSplitHeightInLevelListIndex
        if context.scene.treeSettings.showStemSplitHeights == True:
            row = layout.row()
            row.template_list("UL_stemSplitLevelList", "", scene.treeSettings, "stemSplitHeightInLevelList", scene.treeSettings, "stemSplitHeightInLevelListIndex")
        
        row = layout.row()
        layout.prop(context.scene.treeSettings, "splitHeightVariation")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "splitLengthVariation")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemSplitAngle")
        row = layout.row()
        layout.prop(context.scene.treeSettings, "stemSplitPointAngle")
        row = layout.row()

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


def load_properties(filePath, context):
    with open(filePath, 'r') as f:
        data = json.load(f)
        props = context.scene
        init_properties(data, props)

def load_preset(preset, context, self):
    if preset == 'TREE1':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.14000000059604645, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"], ["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 1.2300000190734863, "noiseAmplitudeHorizontal": 1.2000000476837158, "noiseAmplitudeGradient": 0.35999998450279236, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 0.3100000321865082, "seed": 1484, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 1, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125], "stemSplitHeightInLevelListIndex": 0, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.07000000029802322, "stemSplitPointAngle": 0.25999999046325684, "branchClusters": 2, "showBranchClusterList": [true, true], "showParentClusterList": [true, true], "parentClusterBoolListList": [[true], [false, true]], "nrBranchesList": [37, 68], "treeShapeList": ["INVERSE_HEMISPHERICAL", "INVERSE_HEMISPHERICAL"], "branchShapeList": ["CYLINDRICAL", "CYLINDRICAL"], "branchTypeList": ["SINGLE", "SINGLE"], "branchWhorlCountStartList": [12, 3], "branchWhorlCountEndList": [3, 3], "relBranchLengthList": [0.5138890147209167, 0.2569444477558136], "relBranchLengthVariationList": [0.0694444477558136, 0.0], "taperFactorList": [0.8402778506278992, 0.8402777910232544], "useTaperCurveList": [false, false], "ringResolutionList": [6, 5], "branchesStartHeightGlobalList": [0.1666666716337204, 0.0], "branchesEndHeightGlobalList": [0.9166666865348816, 1.0], "branchesStartHeightClusterList": [0.0, 0.0416666679084301], "branchesEndHeightClusterList": [0.875, 0.340277761220932], "branchesStartPointVariationList": [0.0, 0.0], "showNoiseSettingsList": [true, true], "noiseAmplitudeHorizontalList": [0.0, 0.0], "noiseAmplitudeVerticalList": [0.0, 0.0], "noiseAmplitudeGradientList": [0.0, 0.0], "noiseAmplitudeExponentList": [1.0, 1.0], "noiseScaleList": [1.0, 1.0], "showAngleSettingsList": [true, true], "verticalAngleCrownStartList": [1.2400000095367432, 0.7850000262260437], "verticalAngleCrownEndList": [0.44999998807907104, 0.7850000262260437], "verticalAngleBranchStartList": [0.0, 0.0], "verticalAngleBranchEndList": [0.0, 0.0], "branchAngleModeList": ["WINDING", "SYMMETRIC"], "useFibonacciAnglesList": [false, true], "fibonacciNr": [40, 5], "rotateAngleRangeList": [6.2831854820251465, 3.140000104904175], "rotateAngleOffsetList": [1.5700000524520874, 0.0], "rotateAngleCrownStartList": [2.480001211166382, -0.17000000178813934], "rotateAngleCrownEndList": [2.480001211166382, -0.23999999463558197], "rotateAngleBranchStartList": [0.0, 0.0], "rotateAngleBranchEndList": [0.0, 0.0], "rotateAngleRangeFactorList": [1.0, 1.0], "reducedCurveStepCutoffList": [0.0, 0.0], "reducedCurveStepFactorList": [0.0, 0.0], "branchGlobalCurvatureStartList": [0.0, 0.0], "branchGlobalCurvatureEndList": [0.0, 0.0], "branchCurvatureStartList": [-0.057999998331069946, 0.012000000104308128], "branchCurvatureEndList": [0.03999999910593033, 0.024000000208616257], "branchCurvatureOffsetStrengthList": [0.0, 0.0], "showSplitSettingsList": [true, true], "nrSplitsPerBranchList": [7.980000019073486, 2.369999885559082], "branchSplitModeList": ["HORIZONTAL", "HORIZONTAL"], "branchSplitRotateAngleList": [0.0, 0.0], "branchSplitAxisVariationList": [0.5399997234344482, 0.44999998807907104], "branchSplitAngleList": [0.25999999046325684, 0.27000001072883606], "branchSplitPointAngleList": [0.17000000178813934, 0.17000000178813934], "splitsPerBranchVariationList": [0.0, 0.0], "branchVarianceList": [0.0, 0.0], "outwardAttractionList": [0.0, 0.0], "branchSplitHeightVariationList": [0.38129496574401855, 0.0], "branchSplitLengthVariationList": [0.1366906315088272, 0.0], "showBranchSplitHeights": [false, true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.2371794879436493, 0.2756410241127014, 0.3333333134651184, 0.5], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [0.5458715558052063, 0.3205128014087677, 0.23076921701431274], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props)
        
    if preset == 'TREE2':
        f = '{"treeHeight": 5.0, "treeGrowDir": [0.0, 0.0, 1.0], "taper": 0.15000000596046448, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 0.0], [1.0, 1.0]]], "clusterTaperCurveHandleTypes": [["AUTO", "AUTO"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 0.10000000149011612, "stemRingResolution": 16, "resampleDistance": 0.4599999785423279, "noiseAmplitudeVertical": 0.0, "noiseAmplitudeHorizontal": 0.0, "noiseAmplitudeGradient": 0.7799999713897705, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 1.0, "seed": 832, "curvatureStart": 0.0, "curvatureEnd": 0.03400000184774399, "nrSplits": 3, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5], "stemSplitHeightInLevelListIndex": 0, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.33000001311302185, "stemSplitPointAngle": 0.25999999046325684, "branchClusters": 1, "showBranchClusterList": [true], "showParentClusterList": [true], "parentClusterBoolListList": [[true]], "nrBranchesList": [30], "treeShapeList": ["CONICAL"], "branchShapeList": ["INVERSE_CONICAL"], "branchTypeList": ["SINGLE"], "branchWhorlCountStartList": [3], "branchWhorlCountEndList": [3], "relBranchLengthList": [1.0], "relBranchLengthVariationList": [0.0], "taperFactorList": [0.7361111044883728], "useTaperCurveList": [false], "ringResolutionList": [6], "branchesStartHeightGlobalList": [0.4652777314186096], "branchesEndHeightGlobalList": [0.8680555820465088], "branchesStartHeightClusterList": [0.0], "branchesEndHeightClusterList": [1.0], "branchesStartPointVariationList": [0.0], "showNoiseSettingsList": [true], "noiseAmplitudeHorizontalList": [0.0], "noiseAmplitudeVerticalList": [0.0], "noiseAmplitudeGradientList": [0.0], "noiseAmplitudeExponentList": [1.0], "noiseScaleList": [1.0], "showAngleSettingsList": [true], "verticalAngleCrownStartList": [-0.7699999809265137], "verticalAngleCrownEndList": [-0.6800000071525574], "verticalAngleBranchStartList": [0.0], "verticalAngleBranchEndList": [0.0], "branchAngleModeList": ["WINDING"], "useFibonacciAnglesList": [false], "fibonacciNr": [3], "rotateAngleRangeList": [3.6600000858306885], "rotateAngleOffsetList": [-1.5700000524520874], "rotateAngleCrownStartList": [4.429999828338623], "rotateAngleCrownEndList": [5.300000190734863], "rotateAngleBranchStartList": [0.0], "rotateAngleBranchEndList": [0.0], "rotateAngleRangeFactorList": [1.0], "reducedCurveStepCutoffList": [0.0], "reducedCurveStepFactorList": [0.0], "branchGlobalCurvatureStartList": [0.0], "branchGlobalCurvatureEndList": [0.0], "branchCurvatureStartList": [0.0], "branchCurvatureEndList": [-0.061000000685453415], "branchCurvatureOffsetStrengthList": [0.0], "showSplitSettingsList": [true], "nrSplitsPerBranchList": [1.0], "branchSplitModeList": ["HORIZONTAL"], "branchSplitRotateAngleList": [0.0], "branchSplitAxisVariationList": [0.0], "branchSplitAngleList": [0.4359999895095825], "branchSplitPointAngleList": [0.4359999895095825], "splitsPerBranchVariationList": [0.0], "branchVarianceList": [0.0], "outwardAttractionList": [0.11510791629552841], "branchSplitHeightVariationList": [0.0], "branchSplitLengthVariationList": [0.17266187071800232], "showBranchSplitHeights": [true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props)
        
    if preset == 'MAPLE':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.14000000059604645, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"], ["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 1.2300000190734863, "noiseAmplitudeHorizontal": 1.2000000476837158, "noiseAmplitudeGradient": 0.35999998450279236, "noiseAmplitudeExponent": 1.0299999713897705, "noiseScale": 0.3100000321865082, "seed": 1552, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 2, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5], "stemSplitHeightInLevelListIndex": 1, "splitHeightVariation": 0.0, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.07119999825954437, "stemSplitPointAngle": 0.27379998564720154, "branchClusters": 2, "showBranchClusterList": [true, true], "showParentClusterList": [true, true], "parentClusterBoolListList": [[true], [false, true]], "nrBranchesList": [37, 68], "treeShapeList": ["INVERSE_HEMISPHERICAL", "INVERSE_HEMISPHERICAL"], "branchShapeList": ["CYLINDRICAL", "CYLINDRICAL"], "branchTypeList": ["SINGLE", "SINGLE"], "branchWhorlCountStartList": [12, 3], "branchWhorlCountEndList": [3, 3], "relBranchLengthList": [0.5138890147209167, 0.2569444477558136], "relBranchLengthVariationList": [0.0694444477558136, 0.0], "taperFactorList": [0.8402778506278992, 0.8402777910232544], "useTaperCurveList": [false, false], "ringResolutionList": [6, 5], "branchesStartHeightGlobalList": [0.19351230561733246, 0.0], "branchesEndHeightGlobalList": [0.9166666865348816, 1.0], "branchesStartHeightClusterList": [0.0, 0.05508948862552643], "branchesEndHeightClusterList": [0.875, 0.340277761220932], "branchesStartPointVariationList": [0.0, 0.0], "showNoiseSettingsList": [true, true], "noiseAmplitudeHorizontalList": [0.0, 0.0], "noiseAmplitudeVerticalList": [0.0, 0.0], "noiseAmplitudeGradientList": [0.0, 0.0], "noiseAmplitudeExponentList": [1.0, 1.0], "noiseScaleList": [1.0, 1.0], "showAngleSettingsList": [true, true], "verticalAngleCrownStartList": [0.879800021648407, 0.7850000262260437], "verticalAngleCrownEndList": [0.5440000295639038, 0.7850000262260437], "verticalAngleBranchStartList": [0.0, 0.0], "verticalAngleBranchEndList": [0.0, 0.0], "branchAngleModeList": ["WINDING", "SYMMETRIC"], "useFibonacciAnglesList": [false, true], "fibonacciNr": [40, 5], "rotateAngleRangeList": [6.28000020980835, 6.28000020980835], "rotateAngleOffsetList": [1.5700000524520874, 0.0], "rotateAngleCrownStartList": [1.2209999561309814, -0.1745000034570694], "rotateAngleCrownEndList": [1.2389999628067017, -0.22599999606609344], "rotateAngleBranchStartList": [0.0, 0.0], "rotateAngleBranchEndList": [0.0, 0.0], "rotateAngleRangeFactorList": [1.0, 1.0], "reducedCurveStepCutoffList": [0.010000020265579224, 0.0], "reducedCurveStepFactorList": [0.0, 0.0], "branchGlobalCurvatureStartList": [0.0, 0.0], "branchGlobalCurvatureEndList": [0.0, 0.0], "branchCurvatureStartList": [-0.05700000002980232, 0.011300000362098217], "branchCurvatureEndList": [0.040800001472234726, 0.026100000366568565], "branchCurvatureOffsetStrengthList": [0.0, 0.0], "showSplitSettingsList": [true, true], "nrSplitsPerBranchList": [7.980000019073486, 2.369999885559082], "branchSplitModeList": ["HORIZONTAL", "HORIZONTAL"], "branchSplitRotateAngleList": [0.0, 0.0], "branchSplitAxisVariationList": [0.5399997234344482, 0.44999998807907104], "branchSplitAngleList": [0.2660999894142151, 0.2661600112915039], "branchSplitPointAngleList": [0.17880000174045563, 0.17890000343322754], "splitsPerBranchVariationList": [0.0, 0.0], "branchVarianceList": [0.0, 0.0], "outwardAttractionList": [0.0, 0.0], "branchSplitHeightVariationList": [0.38129496574401855, 0.0], "branchSplitLengthVariationList": [0.1366906315088272, 0.0], "showBranchSplitHeights": [true, true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.2300613522529602, 0.4166666567325592, 0.2300613522529602, 0.4166666567325592], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [0.5458715558052063, 0.3205128014087677, 0.23076921701431274], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[false, true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props)
        
    if preset == 'SILVER_BIRCH':
        f = '{"treeHeight": 10.0, "treeGrowDir": [0.0010000000474974513, 0.0, 1.0], "taper": 0.11999999731779099, "taperCurvePoints": [[0.0, 1.0], [1.0, 0.0]], "taperCurveHandleTypes": ["VECTOR", "VECTOR"], "clusterTaperCurvePoints": [[[0.0, 1.0], [1.0, 0.0]]], "clusterTaperCurveHandleTypes": [["VECTOR", "VECTOR"]], "branchTipRadius": 0.0020000000949949026, "ringSpacing": 2.0, "stemRingResolution": 16, "resampleDistance": 0.5, "noiseAmplitudeVertical": 0.0, "noiseAmplitudeHorizontal": 0.0, "noiseAmplitudeGradient": 0.0, "noiseAmplitudeExponent": 0.0, "noiseScale": 1.0, "seed": 1787, "curvatureStart": 0.0, "curvatureEnd": 0.0, "nrSplits": 0, "variance": 0.0, "stemSplitMode": "ROTATE_ANGLE", "stemSplitRotateAngle": 1.5700000524520874, "curvOffsetStrength": 0.0, "stemSplitHeightInLevelList": [0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.5, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.46694183349609375, 0.14462800323963165, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5, 0.15380950272083282, 0.5], "stemSplitHeightInLevelListIndex": 5, "splitHeightVariation": 0.11999999731779099, "splitLengthVariation": 0.030000001192092896, "stemSplitAngle": 0.29580000042915344, "stemSplitPointAngle": 0.27379998564720154, "branchClusters": 1, "showBranchClusterList": [true], "showParentClusterList": [true], "parentClusterBoolListList": [[true]], "nrBranchesList": [24], "treeShapeList": ["INVERSE_CONICAL"], "branchShapeList": ["CYLINDRICAL"], "branchTypeList": ["SINGLE"], "branchWhorlCountStartList": [3], "branchWhorlCountEndList": [3], "relBranchLengthList": [0.5838925838470459], "relBranchLengthVariationList": [0.0], "taperFactorList": [0.8120805621147156], "useTaperCurveList": [false], "ringResolutionList": [6], "branchesStartHeightGlobalList": [0.24161073565483093], "branchesEndHeightGlobalList": [0.9127516746520996], "branchesStartHeightClusterList": [0.0], "branchesEndHeightClusterList": [1.0], "branchesStartPointVariationList": [0.0], "showNoiseSettingsList": [true], "noiseAmplitudeHorizontalList": [0.0], "noiseAmplitudeVerticalList": [0.0], "noiseAmplitudeGradientList": [0.0], "noiseAmplitudeExponentList": [1.0], "noiseScaleList": [1.0], "showAngleSettingsList": [true], "verticalAngleCrownStartList": [1.417330026626587], "verticalAngleCrownEndList": [-0.09004999697208405], "verticalAngleBranchStartList": [0.0], "verticalAngleBranchEndList": [0.0], "branchAngleModeList": ["WINDING"], "useFibonacciAnglesList": [true], "fibonacciNr": [6], "rotateAngleRangeList": [3.1415927410125732], "rotateAngleOffsetList": [0.0], "rotateAngleCrownStartList": [0.0], "rotateAngleCrownEndList": [0.0], "rotateAngleBranchStartList": [0.0], "rotateAngleBranchEndList": [0.0], "rotateAngleRangeFactorList": [1.0], "reducedCurveStepCutoffList": [0.0], "reducedCurveStepFactorList": [0.0], "branchGlobalCurvatureStartList": [0.10000000149011612], "branchGlobalCurvatureEndList": [-0.10599999874830246], "branchCurvatureStartList": [0.0], "branchCurvatureEndList": [0.0], "branchCurvatureOffsetStrengthList": [0.0], "showSplitSettingsList": [true], "nrSplitsPerBranchList": [1.5], "branchSplitModeList": ["HORIZONTAL"], "branchSplitRotateAngleList": [0.0], "branchSplitAxisVariationList": [0.23999999463558197], "branchSplitAngleList": [0.26179999113082886], "branchSplitPointAngleList": [0.26179999113082886], "splitsPerBranchVariationList": [0.0], "branchVarianceList": [0.0], "outwardAttractionList": [0.0], "branchSplitHeightVariationList": [0.2569444477558136], "branchSplitLengthVariationList": [0.2013888955116272], "showBranchSplitHeights": [true], "branchSplitHeightInLevelListIndex": 0, "branchSplitHeightInLevelList_0": [0.4166666567325592, 0.2300613522529602], "branchSplitHeightInLevelListIndex_0": 0, "branchSplitHeightInLevelList_1": [], "branchSplitHeightInLevelListIndex_1": 0, "branchSplitHeightInLevelList_2": [], "branchSplitHeightInLevelListIndex_2": 0, "branchSplitHeightInLevelList_3": [], "branchSplitHeightInLevelListIndex_3": 0, "branchSplitHeightInLevelList_4": [], "branchSplitHeightInLevelListIndex_4": 0, "branchSplitHeightInLevelList_5": [], "branchSplitHeightInLevelListIndex_5": 2, "branchSplitHeightInLevelList_6": [], "branchSplitHeightInLevelListIndex_6": 0, "branchSplitHeightInLevelList_7": [], "branchSplitHeightInLevelListIndex_7": 0, "branchSplitHeightInLevelList_8": [], "branchSplitHeightInLevelListIndex_8": 0, "branchSplitHeightInLevelList_9": [], "branchSplitHeightInLevelListIndex_9": 0, "branchSplitHeightInLevelList_10": [], "branchSplitHeightInLevelListIndex_10": 0, "branchSplitHeightInLevelList_11": [], "branchSplitHeightInLevelListIndex_11": 0, "branchSplitHeightInLevelList_12": [], "branchSplitHeightInLevelListIndex_12": 0, "branchSplitHeightInLevelList_13": [], "branchSplitHeightInLevelListIndex_13": 0, "branchSplitHeightInLevelList_14": [], "branchSplitHeightInLevelListIndex_14": 0, "branchSplitHeightInLevelList_15": [], "branchSplitHeightInLevelListIndex_15": 0, "branchSplitHeightInLevelList_16": [], "branchSplitHeightInLevelListIndex_16": 0, "branchSplitHeightInLevelList_17": [], "branchSplitHeightInLevelListIndex_17": 0, "branchSplitHeightInLevelList_18": [], "branchSplitHeightInLevelListIndex_18": 0, "branchSplitHeightInLevelList_19": [], "branchSplitHeightInLevelListIndex_19": 0, "branchSplitHeightInLevelListList": [], "showLeafSettings": [], "leavesDensityList": [], "leafSizeList": [], "leafAspectRatioList": [], "leafStartHeightGlobalList": [], "leafEndHeightGlobalList": [], "leafStartHeightClusterList": [], "leafEndHeightClusterList": [], "leafTypeList": [], "leafWhorlCountList": [], "leafAngleModeList": [], "leafVerticalAngleBranchStartList": [], "leafVerticalAngleBranchEndList": [], "leafRotateAngleBranchStartList": [], "leafRotateAngleBranchEndList": [], "leafTiltAngleBranchStartList": [], "leafTiltAngleBranchEndList": [], "showLeafClusterList": [true], "leafParentClusterBoolListList": [[true, false]]}'
        data = json.loads(f)
        props = context.scene
        init_properties(data, props)
        

def init_properties(data, props):
        props.treeSettings.treeHeight = data.get("treeHeight", props.treeSettings.treeHeight)
        treeGrowDir = data.get("treeGrowDir", props.treeSettings.treeGrowDir)
        if isinstance(treeGrowDir, list) and len(treeGrowDir) == 3:
            props.treeSettings.treeGrowDir = treeGrowDir
        props.treeSettings.taper = data.get("taper", props.treeSettings.taper)
        
        controlPts = []
        controlPts = data.get("taperCurvePoints", controlPts)
        handleTypes = []
        handleTypes = data.get("taperCurveHandleTypes", handleTypes)
        #nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
                
        ensure_stem_curve_node()
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup') #taperNodeGroup')
        curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] #'Stem'
    
        
                
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
        curveElement.points[0].location = controlPts[0]
        curveElement.points[0].handle_type = handleTypes[0]
        curveElement.points[1].location = controlPts[1]
        curveElement.points[1].handle_type = handleTypes[1]
        
        if len(controlPts) > 2:
            for i in range(2, len(controlPts)):
                curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                curveElement.points[len(curveElement.points) - 1].location.x = controlPts[i][0]
                curveElement.points[len(curveElement.points) - 1].location.y = controlPts[i][1]
                
                curveElement.points[len(curveElement.points) - 1].handle_type = handleTypes[i]
                
        nodeGroups.nodes[curve_node_mapping['Stem']].mapping.update()
        
        props.treeSettings.branchTipRadius = data.get("branchTipRadius", props.treeSettings.branchTipRadius)
        props.treeSettings.ringSpacing = data.get("ringSpacing", props.treeSettings.ringSpacing)
        props.treeSettings.stemRingResolution = data.get("stemRingResolution", props.treeSettings.stemRingResolution)
        props.treeSettings.resampleDistance = data.get("resampleDistance", props.treeSettings.resampleDistance)
        
        props.treeSettings.noiseAmplitudeVertical = data.get("noiseAmplitudeVertical", props.treeSettings.noiseAmplitudeVertical)
        props.treeSettings.noiseAmplitudeHorizontal = data.get("noiseAmplitudeHorizontal", props.treeSettings.noiseAmplitudeHorizontal)
        props.treeSettings.noiseAmplitudeGradient = data.get("noiseAmplitudeGradient", props.treeSettings.noiseAmplitudeGradient)
        props.treeSettings.noiseAmplitudeExponent = data.get("noiseAmplitudeExponent", props.treeSettings.noiseAmplitudeExponent)
        props.treeSettings.noiseScale = data.get("noiseScale", props.treeSettings.noiseScale)
        props.treeSettings.seed = data.get("seed", props.treeSettings.seed)
        
        props.treeSettings.curvatureStart = data.get("curvatureStart", props.treeSettings.curvatureStart)
        props.treeSettings.curvatureEnd = data.get("curvatureEnd", props.treeSettings.curvatureEnd)
        
        props.treeSettings.nrSplits = data.get("nrSplits", props.treeSettings.nrSplits)
        props.treeSettings.variance = data.get("variance", props.treeSettings.variance)
        props.treeSettings.stemSplitMode = data.get("stemSplitMode", props.treeSettings.stemSplitMode)
        props.treeSettings.stemSplitRotateAngle = data.get("stemSplitRotateAngle", props.treeSettings.stemSplitRotateAngle)
        props.treeSettings.curvOffsetStrength = data.get("curvOffsetStrength", props.treeSettings.curvOffsetStrength)
        
        for value in data.get("stemSplitHeightInLevelList", []):
            item = props.treeSettings.stemSplitHeightInLevelList.add()
            item.value = value
        props.treeSettings.stemSplitHeightInLevelListIndex = data.get("stemSplitHeightInLevelListIndex", props.treeSettings.stemSplitHeightInLevelListIndex)
                
        props.treeSettings.splitHeightVariation = data.get("splitHeightVariation", props.treeSettings.splitHeightVariation)
        props.treeSettings.splitLengthVariation = data.get("splitLengthVariation", props.treeSettings.splitLengthVariation)
        props.treeSettings.stemSplitAngle = data.get("stemSplitAngle", props.treeSettings.stemSplitAngle)
        props.treeSettings.stemSplitPointAngle = data.get("stemSplitPointAngle", props.treeSettings.stemSplitPointAngle)
        
        for outerList in props.treeSettings.parentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.treeSettings.parentClusterBoolListList.clear()
        
        props.treeSettings.branchClusters = data.get("branchClusters", props.treeSettings.branchClusters)
        
        
        # nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        #
        # for clusterIndex in range(props.branchClusters):
        #   curve_name = ensure_branch_curve_node(clusterIndex)
        #   curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        #   clusterTaperControlPts.append([])
        #   clusterTaperCurveHandleTypes.append([])
        #   for i in range(0, len(curveElement.points)):
        #     clusterTaperControlPts[clusterIndex].append(curveElement.points[i].location)
        #     clusterTaperCurveHandleTypes[clusterIndex].append(curveElement.points[i].handle_type)
        
        nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        
        clusterControlPts = []
        clusterControlPts = data.get("clusterTaperControlPts", controlPts)
        clusterHandleTypes = []
        clusterHandleTypes = data.get("clusterTaperCurveHandleTypes", handleTypes)
        
        for clusterIndex in range(props.treeSettings.branchClusters):
            
            bpy.ops.scene.reset_branch_cluster_curve(idx = clusterIndex)
            
            
            curve_name = ensure_branch_curve_node(clusterIndex)
            curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
            
            
            
            if len(curveElement.points) > 2:
                for i in range(2, len(curveElement.points)):
                    curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                    
                curveElement.points[0].location = controlPts[0]
                curveElement.points[0].handle_type = handleTypes[0]
                curveElement.points[1].location = controlPts[1]
                curveElement.points[1].handle_type = handleTypes[1]
                
                if len(controlPts) > 2:
                    for i in range(2, len(controlPts)):
                        curveElement.points.new(curveElement.points[len(curveElement.points) - 1].location.x, curveElement.points[len(curveElement.points) - 1].location.y)
                        curveElement.points[len(curveElement.points) - 1].location.x = clusterControlPts[clusterIndex][i][0]
                        curveElement.points[len(curveElement.points) - 1].location.y = clusterControlPts[clusterIndex][i][1]
                
                        curveElement.points[len(curveElement.points) - 1].handle_type = clusterHandleTypes[clusterIndex][i]
            
            nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.update()
            
        
        nestedList = []
        nestedList = data.get("parentClusterBoolListList", nestedList)
        for n in range(0, props.treeSettings.branchClusters):
            innerList = nestedList[n]
            item = props.treeSettings.parentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            for b in innerList:
                i = item.value.add()
                i.value = b
                
        for outerList in props.treeSettings.leafParentClusterBoolListList:
            while len(outerList.value) > 0:
                outerList.value.clear()
        
        props.treeSettings.leafParentClusterBoolListList.clear()
        
        nestedLeafList = []
        nestedLeafList = data.get("leafParentClusterBoolListList", nestedLeafList)
        for n in range(0, len(nestedLeafList)):
            innerLeafList = nestedLeafList[n]
            item = props.treeSettings.leafParentClusterBoolListList.add()
            for n in item.value:
                item.remove(n)
            for b in innerLeafList:
                i = item.value.add()
                i.value = b
        
        props.branchClusterSettingsList.clear()
        
        for i in range(0, props.treeSettings.branchClusters):
            props.branchClusterSettingsList.add()
        
        for i, value in enumerate(data.get("nrBranchesList", [])):
            props.branchClusterSettingsList[i].nrBranches = value
        
        for i, value in enumerate(data.get("treeShapeList", [])):
            props.branchClusterSettingsList[i].treeShape.value = value
        
        for i, value in enumerate(data.get("branchShapeList", [])):
            props.branchClusterSettingsList[i].branchShape.value = value
            
        for i, value in enumerate(data.get("branchTypeList", [])):
            props.branchClusterSettingsList[i].branchType.value = value
            
        for i, value in enumerate(data.get("branchWhorlCountStartList", [])):
            props.branchClusterSettingsList[i].branchWhorlCountStart = value
            
        for i, value in enumerate(data.get("branchWhorlCountEndList", [])):
            props.branchClusterSettingsList[i].branchWhorlCountEndStart = value
            
        for i, value in enumerate(data.get("relBranchLengthList", [])):
            props.branchClusterSettingsList[i].relBranchLength = value
            
        for i, value in enumerate(data.get("relBranchLengthVariationList", [])):
            props.branchClusterSettingsList[i].relBranchLengthVariation = value
        
        props.taperFactorList.clear()
        while len(props.taperFactorList) < props.treeSettings.branchClusters:
            props.taperFactorList.add()
        for i, value in enumerate(data.get("taperFactorList", [])):
            props.taperFactorList[i].taperFactor = value
        
        for i, value in enumerate(data.get("useTaperCurveList", [])):
            props.branchClusterSettingsList[i].useTaperCurve = value
            
        for i, value in enumerate(data.get("ringResolutionList", [])):
            props.branchClusterSettingsList[i].ringResolution = value
        
        for i, value in enumerate(data.get("branchesStartHeightGlobalList", [])):
            props.branchClusterSettingsList[i].branchesStartHeightGlobal = value
            
        for i, value in enumerate(data.get("branchesEndHeightGlobalList", [])):
            props.branchClusterSettingsList[i].branchesEndHeightGlobal = value
        
        for i, value in enumerate(data.get("branchesStartHeightClusterList", [])):
            props.branchClusterSettingsList[i].branchesStartHeightCluster = value
        
        for i, value in enumerate(data.get("branchesEndHeightClusterList", [])):
            props.branchClusterSettingsList[i].branchesEndHeightCluster = value
            
        for i, value in enumerate(data.get("branchesStartPointVariationList", [])):
            props.branchClusterSettingsList[i].branchesStartPointVariation = value
        
        for i, value in enumerate(data.get("noiseAmplitudeHorizontalBranchList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeHorizontalBranch = value
        
        for i, value in enumerate(data.get("noiseAmplitudeVerticalBranchList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeVerticalBranch = value
        
        for i, value in enumerate(data.get("noiseAmplitudeBranchGradientList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudeBranchGradient = value
            
        for i, value in enumerate(data.get("noiseAmplitudeBranchExponentList", [])):
            props.branchClusterSettingsList[i].noiseAmplitudBranchExponent = value
            
        for i, value in enumerate(data.get("noiseScaleList", [])):
            props.branchClusterSettingsList[i].noiseScale = value
            
        
        for i, value in enumerate(data.get("verticalAngleCrownStartList", [])):
            props.branchClusterSettingsList[i].verticalAngleCrownStart = value
            
        for i, value in enumerate(data.get("verticalAngleCrownEndList", [])):
            props.branchClusterSettingsList[i].verticalAngleCrownEnd = value
            
        for i, value in enumerate(data.get("verticalAngleBranchStartList", [])):
            props.branchClusterSettingsList[i].verticalAngleBranchStart = value
            
        for i, value in enumerate(data.get("verticalAngleBranchEndList", [])):
            props.branchClusterSettingsList[i].verticalAngleBranchEnd = value
        
        
        for i, value in enumerate(data.get("branchAngleModeList", [])):
            props.branchClusterSettingsList[i].branchAngleMode.value = value
            
        for i, value in enumerate(data.get("useFibonacciAnglesList", [])):
            props.branchClusterSettingsList[i].useFibonacciAngles = value
            
        for i, value in enumerate(data.get("fibonacciNr", [])):
            props.branchClusterSettingsList[i].fibonacciNr.fibonacci_nr = value
        
        for i, value in enumerate(data.get("rotateAngleRangeList", [])):
            props.branchClusterSettingsList[i].rotateAngleRange = value
            
        for i, value in enumerate(data.get("rotateAngleOffsetList", [])):
            props.branchClusterSettingsList[i].rotateAngleOffset = value
        
        
        for i, value in enumerate(data.get("rotateAngleCrownStartList", [])):
            props.branchClusterSettingsList[i].rotateAngleCrownStart = value
            
        for i, value in enumerate(data.get("rotateAngleCrownEndList", [])):
            props.branchClusterSettingsList[i].rotateAngleCrownEnd = value
            
        for i, value in enumerate(data.get("rotateAngleBranchStartList", [])):
            props.branchClusterSettingsList[i].rotateAngleBranchStart = value
            
        for i, value in enumerate(data.get("rotateAngleBranchEndList", [])):
            props.branchClusterSettingsList[i].rotateAngleBranchEnd = value
        
        for i, value in enumerate(data.get("rotateAngleRangeFactorList", [])):
            props.branchClusterSettingsList[i].rotateAngleRangeFactor = value
            
            
        for i, value in enumerate(data.get("reducedCurveStepCutoffList", [])):
            props.branchClusterSettingsList[i].reducedCurveStepCutoff = value
            
        for i, value in enumerate(data.get("reducedCurveStepFactorList", [])):
            props.branchClusterSettingsList[i].reducedCurveStepFactor = value
        
        for i, value in enumerate(data.get("branchGlobalCurvatureStartList", [])):
            props.branchClusterSettingsList[i].branchGlobalCurvatureStart = value
            
        for i, value in enumerate(data.get("branchGlobalCurvatureEndList", [])):
            props.branchClusterSettingsList[i].branchGlobalCurvatureEnd = value
        
        for i, value in enumerate(data.get("branchCurvatureStartList", [])):
            props.branchClusterSettingsList[i].branchCurvatureStart = value
           
        for i, value in enumerate(data.get("branchCurvatureEndList", [])):
            props.branchClusterSettingsList[i].branchCurvatureEnd = value
        
        for i, value in enumerate(data.get("branchCurvatureOffsetStrengthList", [])):
            props.branchClusterSettingsList[i].branchCurvatureOffsetStrength = value
        
        
        for i, value in enumerate(data.get("nrSplitsPerBranchList", [])):
            props.branchClusterSettingsList[i].nrSplitsPerBranch = value
            
        for i, value in enumerate(data.get("branchSplitModeList", [])):
            props.branchClusterSettingsList[i].branchSplitMode.value = value
            
        for i, value in enumerate(data.get("branchSplitRotateAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitRotateAngle = value
            
        for i, value in enumerate(data.get("branchSplitAxisVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitAxisVariation = value
            
        
        for i, value in enumerate(data.get("branchSplitAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitAngle = value
            
        for i, value in enumerate(data.get("branchSplitPointAngleList", [])):
            props.branchClusterSettingsList[i].branchSplitPointAngle = value
            
        
        for i, value in enumerate(data.get("splitsPerBranchVariationList", [])):
            props.branchClusterSettingsList[i].splitsPerBranchVariation = value
            
        for i, value in enumerate(data.get("branchVarianceList", [])):
            props.branchClusterSettingsList[i].branchVariance = value
            
        for i, value in enumerate(data.get("outwardAttractionList", [])):
            props.branchClusterSettingsList[i].outwardAttraction = value
        
        for i, value in enumerate(data.get("branchSplitHeightVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitHeightVariation = value
        
        for i, value in enumerate(data.get("branchSplitLengthVariationList", [])):
            props.branchClusterSettingsList[i].branchSplitLengthVariation = value
        
        props.treeSettings.branchSplitHeightInLevelListList.clear()
        nestedBranchSplitHeightInLevelList = []
        nestedBranchSplitHeightInLevelList = data.get("branchSplitHeightInLevelListList", nestedBranchSplitHeightInLevelList)
        for n in range(0, len(nestedBranchSplitHeightInLevelList)):
            innerList = nestedBranchSplitHeightInLevelList[n]
            item = props.treeSettings.branchSplitHeightInLevelListList.add()
            for n in item.value:
                item.remove(n)
            for h in innerList:
                i = item.value.add()
                i.value = h
            
        props.branchSplitHeightInLevelListIndex = data.get("branchSplitHeightInLevelListIndex", props.branchSplitHeightInLevelListIndex)
            
        for value in data.get("branchSplitHeightInLevelList_0", []):
            item = props.treeSettings.branchSplitHeightInLevelList_0.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_0 = data.get("branchSplitHeightInLevelListIndex_0", props.treeSettings.branchSplitHeightInLevelListIndex_0)
        
        for value in data.get("branchSplitHeightInLevelList_1", []):
            item = props.treeSettings.branchSplitHeightInLevelList_1.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_1 = data.get("branchSplitHeightInLevelListIndex_1", props.treeSettings.branchSplitHeightInLevelListIndex_1)
        
        for value in data.get("branchSplitHeightInLevelList_2", []):
            item = props.treeSettings.branchSplitHeightInLevelList_2.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_2 = data.get("branchSplitHeightInLevelListIndex_2", props.treeSettings.branchSplitHeightInLevelListIndex_2)
        
        for value in data.get("branchSplitHeightInLevelList_3", []):
            item = props.treeSettings.branchSplitHeightInLevelList_3.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_3 = data.get("branchSplitHeightInLevelListIndex_3", props.treeSettings.branchSplitHeightInLevelListIndex_3)
        
        for value in data.get("branchSplitHeightInLevelList_4", []):
            item = props.treeSettings.branchSplitHeightInLevelList_4.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_4 = data.get("branchSplitHeightInLevelListIndex_4", props.treeSettings.branchSplitHeightInLevelListIndex_4)
        
        for value in data.get("branchSplitHeightInLevelList_5", []):
            item = props.treeSettings.branchSplitHeightInLevelList_5.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_5 = data.get("branchSplitHeightInLevelListIndex_5", props.treeSettings.branchSplitHeightInLevelListIndex_5)
        
        for value in data.get("branchSplitHeightInLevelList_6", []):
            item = props.treeSettings.branchSplitHeightInLevelList_6.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_6 = data.get("branchSplitHeightInLevelListIndex_6", props.treeSettings.branchSplitHeightInLevelListIndex_6)
        
        for value in data.get("branchSplitHeightInLevelList_7", []):
            item = props.treeSettings.branchSplitHeightInLevelList_7.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_7 = data.get("branchSplitHeightInLevelListIndex_7", props.treeSettings.branchSplitHeightInLevelListIndex_7)
        
        for value in data.get("branchSplitHeightInLevelList_8", []):
            item = props.treeSettings.branchSplitHeightInLevelList_8.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_8 = data.get("branchSplitHeightInLevelListIndex_8", props.treeSettings.branchSplitHeightInLevelListIndex_8)
        
        for value in data.get("branchSplitHeightInLevelList_9", []):
            item = props.treeSettings.branchSplitHeightInLevelList_9.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_9 = data.get("branchSplitHeightInLevelListIndex_9", props.treeSettings.branchSplitHeightInLevelListIndex_9)
        
        for value in data.get("branchSplitHeightInLevelList_10", []):
            item = props.treeSettings.branchSplitHeightInLevelList_10.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_10 = data.get("branchSplitHeightInLevelListIndex_10", props.treeSettings.branchSplitHeightInLevelListIndex_10)
        
        for value in data.get("branchSplitHeightInLevelList_11", []):
            item = props.treeSettings.branchSplitHeightInLevelList_11.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_11 = data.get("branchSplitHeightInLevelListIndex_11", props.treeSettings.branchSplitHeightInLevelListIndex_11)
        
        for value in data.get("branchSplitHeightInLevelList_12", []):
            item = props.treeSettings.branchSplitHeightInLevelList_12.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_12 = data.get("branchSplitHeightInLevelListIndex_12", props.treeSettings.branchSplitHeightInLevelListIndex_12)
        
        for value in data.get("branchSplitHeightInLevelList_13", []):
            item = props.treeSettings.branchSplitHeightInLevelList_13.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_13 = data.get("branchSplitHeightInLevelListIndex_13", props.treeSettings.branchSplitHeightInLevelListIndex_13)
        
        for value in data.get("branchSplitHeightInLevelList_14", []):
            item = props.treeSettings.branchSplitHeightInLevelList_14.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_14 = data.get("branchSplitHeightInLevelListIndex_14", props.treeSettings.branchSplitHeightInLevelListIndex_14)
        
        for value in data.get("branchSplitHeightInLevelList_15", []):
            item = props.treeSettings.branchSplitHeightInLevelList_15.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_15 = data.get("branchSplitHeightInLevelListIndex_15", props.treeSettings.branchSplitHeightInLevelListIndex_15)
        
        for value in data.get("branchSplitHeightInLevelList_16", []):
            item = props.treeSettings.branchSplitHeightInLevelList_16.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_16 = data.get("branchSplitHeightInLevelListIndex_16", props.treeSettings.branchSplitHeightInLevelListIndex_16)
        
        for value in data.get("branchSplitHeightInLevelList_17", []):
            item = props.treeSettings.branchSplitHeightInLevelList_17.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_17 = data.get("branchSplitHeightInLevelListIndex_17", props.treeSettings.branchSplitHeightInLevelListIndex_17)
        
        for value in data.get("branchSplitHeightInLevelList_18", []):
            item = props.treeSettings.branchSplitHeightInLevelList_18.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_18 = data.get("branchSplitHeightInLevelListIndex_18", props.treeSettings.branchSplitHeightInLevelListIndex_18)
        
        for value in data.get("branchSplitHeightInLevelList_19", []):
            item = props.treeSettings.branchSplitHeightInLevelList_19.add()
            item.value = value
            
        props.treeSettings.branchSplitHeightInLevelListIndex_19 = data.get("branchSplitHeightInLevelListIndex_19", props.treeSettings.branchSplitHeightInLevelListIndex_19)
        
        props.leafClusterSettingsList.clear()
        
        for value in data.get("leavesDensityList", []):
            item = props.leafClusterSettingsList.add()
            item.leavesDensity = value
        
        i = 0
        for value in data.get("leafSizeList", []):
            props.leafClusterSettingsList[i].leafSize = value
            i += 1
        i = 0
        for value in data.get("leafAspectRatioList", []):
            props.leafClusterSettingsList[i].leafAspectRatio = value
            i += 1
        i = 0
        for value in data.get("leafStartHeightGlobalList", []):
            props.leafClusterSettingsList[i].leafStartHeightGlobal = value
            i += 1
        i = 0
        for value in data.get("leafEndHeightGlobalList", []):
            props.leafClusterSettingsList[i].leafEndHeightGlobal = value
            i += 1
        i = 0
        for value in data.get("leafStartHeightClusterList", []):
            props.leafClusterSettingsList[i].leafStartHeightCluster = value
            i += 1
        i = 0
        for value in data.get("leafEndHeightClusterList", []):
            props.leafClusterSettingsList[i].leafEndHeightCluster = value
            i += 1
        i = 0
        for value in data.get("leafTypeList", []):
            props.leafClusterSettingsList[i].leafType.value = value
            i += 1
        i = 0
        for value in data.get("leafWhorlCountList", []):
            props.leafClusterSettingsList[i].leafWhorlCount = value
            i += 1
        i = 0
        for value in data.get("leafAngleModeList", []):
            props.leafClusterSettingsList[i].leafAngleMode.value = value
            i += 1
        i = 0
        for value in data.get("leafVerticalAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafVerticalAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafVerticalAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafVerticalAngleBranchEnd = value
            i += 1
        i = 0
        for value in data.get("leafRotateAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafRotateAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafRotateAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafRotateAngleBranchEnd = value
            i += 1
        i = 0
        for value in data.get("leafTiltAngleBranchStartList", []):
            props.leafClusterSettingsList[i].leafTiltAngleBranchStart = value
            i += 1
        i = 0
        for value in data.get("leafTiltAngleBranchEndList", []):
            props.leafClusterSettingsList[i].leafTiltAngleBranchEnd = value
            i += 1

def save_properties(filePath, treeGen):
    props = bpy.context.scene
    
    
    
    # stem ------
    #
    # nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
    # curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3] 
    
    controlPts = []
    handleTypes = []
    nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
    curveElement = nodeGroups.nodes[curve_node_mapping['Stem']].mapping.curves[3]
    for n in range(0, len(curveElement.points)):
        controlPts.append(list(curveElement.points[n].location))
        handleTypes.append(curveElement.points[n].handle_type)
    
    nestedBranchList = []
    for cluster in props.treeSettings.parentClusterBoolListList:
        innerList = []
        for boolProp in cluster.value:
            innerList.append(boolProp.value)
        nestedBranchList.append(innerList)
        
    nestedLeafList = []
    for cluster in props.treeSettings.leafParentClusterBoolListList:
        innerLeafList = []
        for boolProp in cluster.value:
            innerLeafList.append(boolProp.value)
        nestedLeafList.append(innerLeafList)
        
    nestedBranchSplitHeightInLevelList = []
    for item in props.branchSplitHeightInLevelListList:
        innerHeightList = []
        for height in item.value:
            innerHeightList.append(height.value)
        nestedBranchSplitHeightInLevelList.append(innerHeightList)
    
    storeSplitHeights_0 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 0:
        if bpy.context.scene.branchClusterSettingsList[0].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_0):
            storeSplitHeights_0 = [props.treeSettings.branchSplitHeightInLevelList_0[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[0].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 0:
                storeSplitHeights_0 = props.treeSettings.branchSplitHeightInLevelList_0
        
    storeSplitHeights_1 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 1:
        if bpy.context.scene.branchClusterSettingsList[1].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_1):
            storeSplitHeights_1 = [props.treeSettings.branchSplitHeightInLevelList_1[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[1].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 1:
                storeSplitHeights_1 = props.treeSettings.branchSplitHeightInLevelList_1
            
    storeSplitHeights_2 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 2:
        if bpy.context.scene.branchClusterSettingsList[2].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_2):
            storeSplitHeights_2 = [props.treeSettings.branchSplitHeightInLevelList_2[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[2].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 2:
                storeSplitHeights_2 = props.treeSettings.branchSplitHeightInLevelList_2
        
    storeSplitHeights_3 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 3:
        if bpy.context.scene.branchClusterSettingsList[3].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_3):
            storeSplitHeights_3 = [props.treeSettings.branchSplitHeightInLevelList_3[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[3].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 3:
                storeSplitHeights_3 = props.treeSettings.branchSplitHeightInLevelList_3
        
    storeSplitHeights_4 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 4:
        if bpy.context.scene.branchClusterSettingsList[4].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_4):
            storeSplitHeights_4 = [props.treeSettings.branchSplitHeightInLevelList_4[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[4].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 4:
                storeSplitHeights_4 = props.treeSettings.branchSplitHeightInLevelList_4
        
    storeSplitHeights_5 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 5:
        if bpy.context.scene.branchClusterSettingsList[5].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_5):
            storeSplitHeights_5 = [props.treeSettings.branchSplitHeightInLevelList_5[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[5].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 5:
                storeSplitHeights_5 = props.treeSettings.branchSplitHeightInLevelList_5
    
    storeSplitHeights_6 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 6:
        if bpy.context.scene.branchClusterSettingsList[6].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_6):
            storeSplitHeights_6 = [props.treeSettings.branchSplitHeightInLevelList_6[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[6].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 6:
                storeSplitHeights_6 = props.treeSettings.branchSplitHeightInLevelList_6
    
    storeSplitHeights_7 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 7:
        if bpy.context.scene.branchClusterSettingsList[7].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_7):
            storeSplitHeights_7 = [props.treeSettings.branchSplitHeightInLevelList_7[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[7].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 7:
                storeSplitHeights_7 = props.treeSettings.branchSplitHeightInLevelList_7
    
    storeSplitHeights_8 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 8:
        if bpy.context.scene.branchClusterSettingsList[8].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_8):
            storeSplitHeights_8 = [props.treeSettings.branchSplitHeightInLevelList_8[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[8].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 8:
                storeSplitHeights_5 = props.treeSettings.branchSplitHeightInLevelList_8
    
    storeSplitHeights_9 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 9:
        if bpy.context.scene.branchClusterSettingsList[9].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_9):
            storeSplitHeights_9 = [props.treeSettings.branchSplitHeightInLevelList_9[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[9].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 9:
                storeSplitHeights_9 = props.treeSettings.branchSplitHeightInLevelList_9
    
    storeSplitHeights_10 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 10:
        if bpy.context.scene.branchClusterSettingsList[10].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_10):
            storeSplitHeights_10 = [props.treeSettings.branchSplitHeightInLevelList_10[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[10].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 10:
                storeSplitHeights_10 = props.treeSettings.branchSplitHeightInLevelList_10
    
    storeSplitHeights_11 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 11:
        if bpy.context.scene.branchClusterSettingsList[11].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_11):
            storeSplitHeights_11 = [props.treeSettings.branchSplitHeightInLevelList_11[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[11].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 11:
                storeSplitHeights_11 = props.treeSettings.branchSplitHeightInLevelList_11
    
    storeSplitHeights_12 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 12:
        if bpy.context.scene.branchClusterSettingsList[12].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_12):
            storeSplitHeights_12 = [props.treeSettings.branchSplitHeightInLevelList_12[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[12].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 12:
                storeSplitHeights_12 = props.treeSettings.branchSplitHeightInLevelList_12
    
    storeSplitHeights_13 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 13:
        if bpy.context.scene.branchClusterSettingsList[13].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_13):
            storeSplitHeights_13 = [props.treeSettings.branchSplitHeightInLevelList_13[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[13].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 13:
                storeSplitHeights_13 = props.treeSettings.branchSplitHeightInLevelList_13
    
    storeSplitHeights_14 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 14:
        if bpy.context.scene.branchClusterSettingsList[14].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_14):
            storeSplitHeights_14 = [props.treeSettings.branchSplitHeightInLevelList_14[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[14].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 14:
                storeSplitHeights_14 = props.treeSettings.branchSplitHeightInLevelList_14
    
    storeSplitHeights_15 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 15:
        if bpy.context.scene.branchClusterSettingsList[15].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_15):
            storeSplitHeights_15 = [props.treeSettings.branchSplitHeightInLevelList_15[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[15].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 15:
                storeSplitHeights_15 = props.treeSettings.branchSplitHeightInLevelList_15
    
    storeSplitHeights_16 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 16:
        if bpy.context.scene.branchClusterSettingsList[16].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_16):
            storeSplitHeights_16 = [props.treeSettings.branchSplitHeightInLevelList_16[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[16].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 16:
                storeSplitHeights_16 = props.treeSettings.branchSplitHeightInLevelList_16
    
    storeSplitHeights_17 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 17:
        if bpy.context.scene.branchClusterSettingsList[17].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_17):
            storeSplitHeights_17 = [props.treeSettings.branchSplitHeightInLevelList_17[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[17].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 17:
                storeSplitHeights_17 = props.treeSettings.branchSplitHeightInLevelList_17
    
    storeSplitHeights_18 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 18:
        if bpy.context.scene.branchClusterSettingsList[18].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_18):
            storeSplitHeights_18 = [props.treeSettings.branchSplitHeightInLevelList_18[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[18].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 18:
                storeSplitHeights_18 = props.treeSettings.branchSplitHeightInLevelList_18
    
    storeSplitHeights_19 = []
    if len(bpy.context.scene.branchClusterSettingsList) > 19:
        if bpy.context.scene.branchClusterSettingsList[19].maxSplitHeightUsed <= len(props.treeSettings.branchSplitHeightInLevelList_19):
            storeSplitHeights_19 = [props.treeSettings.branchSplitHeightInLevelList_19[i].value for i in range(0, bpy.context.scene.branchClusterSettingsList[19].maxSplitHeightUsed + 1)]
        else:
            if len(props.branchClusterSettingsList) > 19:
                storeSplitHeights_19 = props.treeSettings.branchSplitHeightInLevelList_19
    
    clusterTaperControlPts = []
    clusterTaperCurveHandleTypes = []
    
    nodeGroups = bpy.data.node_groups.get('CurveNodeGroup')
        
    for clusterIndex in range(props.treeSettings.branchClusters):
        curve_name = ensure_branch_curve_node(clusterIndex)
        curveElement = nodeGroups.nodes[curve_node_mapping[curve_name]].mapping.curves[3]
        clusterTaperControlPts.append([])
        clusterTaperCurveHandleTypes.append([])
        for i in range(0, len(curveElement.points)):
            clusterTaperControlPts[clusterIndex].append(curveElement.points[i].location)
            clusterTaperCurveHandleTypes[clusterIndex].append(curveElement.points[i].handle_type)
    
    data = {
        "treeHeight": props.treeSettings.treeHeight,
        "treeGrowDir": list(props.treeSettings.treeGrowDir),
        "taper": props.treeSettings.taper,
        
        "taperCurvePoints": [list(pt.location) for pt in bpy.data.node_groups.get('CurveNodeGroup').nodes[curve_node_mapping['Stem']].mapping.curves[3].points],
        "taperCurveHandleTypes": [pt.handle_type for pt in bpy.data.node_groups.get('CurveNodeGroup').nodes[curve_node_mapping['Stem']].mapping.curves[3].points],
        
        "clusterTaperCurvePoints": [list(list(pt) for pt in clusterTaperPoints) for clusterTaperPoints in clusterTaperControlPts],
        "clusterTaperCurveHandleTypes": [list(clusterTaperHandles) for clusterTaperHandles in clusterTaperCurveHandleTypes],
    
        "branchTipRadius": props.treeSettings.branchTipRadius,
        "ringSpacing": props.treeSettings.ringSpacing,
        "stemRingResolution": props.treeSettings.stemRingResolution,
        "resampleDistance": props.treeSettings.resampleDistance,
    
        "noiseAmplitudeVertical": props.treeSettings.noiseAmplitudeVertical,
        "noiseAmplitudeHorizontal": props.treeSettings.noiseAmplitudeHorizontal,
        "noiseAmplitudeGradient": props.treeSettings.noiseAmplitudeGradient,
        "noiseAmplitudeExponent": props.treeSettings.noiseAmplitudeExponent,
        "noiseScale": props.treeSettings.noiseScale,
        "seed": props.treeSettings.seed,
        
        "curvatureStart": props.treeSettings.curvatureStart,
        "curvatureEnd": props.treeSettings.curvatureEnd,
        
        "nrSplits": props.treeSettings.nrSplits,
        "variance": props.treeSettings.variance,
        "stemSplitMode": props.treeSettings.stemSplitMode,
        "stemSplitRotateAngle": props.treeSettings.stemSplitRotateAngle,
        "curvOffsetStrength": props.treeSettings.curvOffsetStrength,
        
        "stemSplitHeightInLevelList": [item.value for item in props.treeSettings.stemSplitHeightInLevelList],
        "stemSplitHeightInLevelListIndex": props.treeSettings.stemSplitHeightInLevelListIndex,
            
        "splitHeightVariation": props.treeSettings.splitHeightVariation,
        "splitLengthVariation": props.treeSettings.splitLengthVariation,
        "stemSplitAngle": props.treeSettings.stemSplitAngle,
        "stemSplitPointAngle": props.treeSettings.stemSplitPointAngle,
    
        "branchClusters": props.treeSettings.branchClusters,
        "showBranchClusterList": [props.branchClusterBoolListList[i].show_branch_cluster for i in range(props.treeSettings.branchClusters)],
        "showParentClusterList": [props.treeSettings.parentClusterBoolListList[i].show_cluster for i in range(props.treeSettings.branchClusters)],
    
        "parentClusterBoolListList": nestedBranchList,
        
        "nrBranchesList": [props.branchClusterSettingsList[i].nrBranches for i in range(props.treeSettings.branchClusters)],
        "treeShapeList": [props.branchClusterSettingsList[i].treeShape.value for i in range(props.treeSettings.branchClusters)],
        "branchShapeList": [props.branchClusterSettingsList[i].branchShape.value for i in range(props.treeSettings.branchClusters)],
        "branchTypeList": [props.branchClusterSettingsList[i].branchType.value for i in range(props.treeSettings.branchClusters)],
        "branchWhorlCountStartList": [props.branchClusterSettingsList[i].branchWhorlCountStart for i in range(props.treeSettings.branchClusters)],
        "branchWhorlCountEndList": [props.branchClusterSettingsList[i].branchWhorlCountEnd for i in range(props.treeSettings.branchClusters)],
        "relBranchLengthList": [props.branchClusterSettingsList[i].relBranchLength for i in range(props.treeSettings.branchClusters)],
        "relBranchLengthVariationList": [props.branchClusterSettingsList[i].relBranchLengthVariation for i in range(props.treeSettings.branchClusters)],
        "taperFactorList": [props.taperFactorList[i].taperFactor for i in range(props.treeSettings.branchClusters)],
        "useTaperCurveList": [props.branchClusterSettingsList[i].useTaperCurve for i in range(props.treeSettings.branchClusters)],
        "ringResolutionList": [props.branchClusterSettingsList[i].ringResolution for i in range(props.treeSettings.branchClusters)],
        "branchesStartHeightGlobalList": [props.branchClusterSettingsList[i].branchesStartHeightGlobal for i in range(props.treeSettings.branchClusters)],
        "branchesEndHeightGlobalList": [props.branchClusterSettingsList[i].branchesEndHeightGlobal for i in range(props.treeSettings.branchClusters)],
        "branchesStartHeightClusterList": [props.branchClusterSettingsList[i].branchesStartHeightCluster for i in range(props.treeSettings.branchClusters)],
        "branchesEndHeightClusterList": [props.branchClusterSettingsList[i].branchesEndHeightCluster for i in range(props.treeSettings.branchClusters)],
        "branchesStartPointVariationList": [props.branchClusterSettingsList[i].branchesStartPointVariation for i in range(props.treeSettings.branchClusters)],
        
        "showNoiseSettingsList": [props.branchClusterSettingsList[i].showNoiseSettings for i in range(props.treeSettings.branchClusters)],
        
        "noiseAmplitudeHorizontalList": [props.branchClusterSettingsList[i].noiseAmplitudeHorizontalBranch for i in range(props.treeSettings.branchClusters)],
        "noiseAmplitudeVerticalList": [props.branchClusterSettingsList[i].noiseAmplitudeVerticalBranch for i in range(props.treeSettings.branchClusters)],
        "noiseAmplitudeGradientList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchGradient for i in range(props.treeSettings.branchClusters)],
        "noiseAmplitudeExponentList": [props.branchClusterSettingsList[i].noiseAmplitudeBranchExponent for i in range(props.treeSettings.branchClusters)],
        "noiseScaleList": [props.branchClusterSettingsList[i].noiseScale for i in range(props.treeSettings.branchClusters)],
        
        "showAngleSettingsList": [props.branchClusterSettingsList[i].showAngleSettings for i in range(props.treeSettings.branchClusters)],
        
        "verticalAngleCrownStartList": [props.branchClusterSettingsList[i].verticalAngleCrownStart for i in range(props.treeSettings.branchClusters)],
        "verticalAngleCrownEndList": [props.branchClusterSettingsList[i].verticalAngleCrownEnd for i in range(props.treeSettings.branchClusters)],
        "verticalAngleBranchStartList": [props.branchClusterSettingsList[i].verticalAngleBranchStart for i in range(props.treeSettings.branchClusters)],
        "verticalAngleBranchEndList": [props.branchClusterSettingsList[i].verticalAngleBranchEnd for i in range(props.treeSettings.branchClusters)],
        "branchAngleModeList": [props.branchClusterSettingsList[i].branchAngleMode.value for i in range(props.treeSettings.branchClusters)],
        "useFibonacciAnglesList": [props.branchClusterSettingsList[i].useFibonacciAngles for i in range(props.treeSettings.branchClusters)],
        "fibonacciNr": [props.branchClusterSettingsList[i].fibonacciNr.fibonacci_nr for i in range(props.treeSettings.branchClusters)],
        "rotateAngleRangeList": [props.branchClusterSettingsList[i].rotateAngleRange for i in range(props.treeSettings.branchClusters)],
        "rotateAngleOffsetList": [props.branchClusterSettingsList[i].rotateAngleOffset for i in range(props.treeSettings.branchClusters)],
        
        "rotateAngleCrownStartList": [props.branchClusterSettingsList[i].rotateAngleCrownStart for i in range(props.treeSettings.branchClusters)],
        "rotateAngleCrownEndList": [props.branchClusterSettingsList[i].rotateAngleCrownEnd for i in range(props.treeSettings.branchClusters)],
        "rotateAngleBranchStartList": [props.branchClusterSettingsList[i].rotateAngleBranchStart for i in range(props.treeSettings.branchClusters)],
        "rotateAngleBranchEndList": [props.branchClusterSettingsList[i].rotateAngleBranchEnd for i in range(props.treeSettings.branchClusters)],
        "rotateAngleRangeFactorList": [props.branchClusterSettingsList[i].rotateAngleRangeFactor for i in range(props.treeSettings.branchClusters)],
        
        "reducedCurveStepCutoffList": [props.branchClusterSettingsList[i].reducedCurveStepCutoff for i in range(props.treeSettings.branchClusters)],
        "reducedCurveStepFactorList": [props.branchClusterSettingsList[i].reducedCurveStepFactor for i in range(props.treeSettings.branchClusters)],
        
        "branchGlobalCurvatureStartList": [props.branchClusterSettingsList[i].branchGlobalCurvatureStart for i in range(props.treeSettings.branchClusters)],
        "branchGlobalCurvatureEndList": [props.branchClusterSettingsList[i].branchGlobalCurvatureEnd for i in range(props.treeSettings.branchClusters)],
        "branchCurvatureStartList": [props.branchClusterSettingsList[i].branchCurvatureStart for i in range(props.treeSettings.branchClusters)],
        "branchCurvatureEndList": [props.branchClusterSettingsList[i].branchCurvatureEnd for i in range(props.treeSettings.branchClusters)],
        "branchCurvatureOffsetStrengthList": [props.branchClusterSettingsList[i].branchCurvatureOffsetStrength for i in     range(props.treeSettings.branchClusters)],
        
        "showSplitSettingsList": [props.branchClusterSettingsList[i].showSplitSettings for i in range(props.treeSettings.branchClusters)],
        
        "nrSplitsPerBranchList": [props.branchClusterSettingsList[i].nrSplitsPerBranch for i in range(props.treeSettings.branchClusters)],
        "branchSplitModeList": [props.branchClusterSettingsList[i].branchSplitMode.value for i in range(props.treeSettings.branchClusters)],
        "branchSplitRotateAngleList": [props.branchClusterSettingsList[i].branchSplitRotateAngle for i in range(props.treeSettings.branchClusters)],
        "branchSplitAxisVariationList": [props.branchClusterSettingsList[i].branchSplitAxisVariation for i in range(props.treeSettings.branchClusters)],
        
        "branchSplitAngleList": [props.branchClusterSettingsList[i].branchSplitAngle for i in range(props.treeSettings.branchClusters)],
        "branchSplitPointAngleList": [props.branchClusterSettingsList[i].branchSplitPointAngle for i in range(props.treeSettings.branchClusters)],
        
        "splitsPerBranchVariationList": [props.branchClusterSettingsList[i].splitsPerBranchVariation for i in range(props.treeSettings.branchClusters)],
        "branchVarianceList": [props.branchClusterSettingsList[i].branchVariance for i in range(props.treeSettings.branchClusters)],
        "outwardAttractionList": [props.branchClusterSettingsList[i].outwardAttraction for i in range(props.treeSettings.branchClusters)],
        "branchSplitHeightVariationList": [props.branchClusterSettingsList[i].branchSplitHeightVariation for i in range(props.treeSettings.branchClusters)],
        "branchSplitLengthVariationList": [props.branchClusterSettingsList[i].branchSplitLengthVariation for i in range(props.treeSettings.branchClusters)],
        
        "showBranchSplitHeights": [props.branchClusterSettingsList[i].showBranchSplitHeights for i in range(props.treeSettings.branchClusters)],
        
        "branchSplitHeightInLevelListIndex": props.treeSettings.branchSplitHeightInLevelListIndex,
        #------
        "branchSplitHeightInLevelList_0": storeSplitHeights_0,
        "branchSplitHeightInLevelListIndex_0": props.treeSettings.branchSplitHeightInLevelListIndex_0,
        
        "branchSplitHeightInLevelList_1": storeSplitHeights_1,
        "branchSplitHeightInLevelListIndex_1": props.treeSettings.branchSplitHeightInLevelListIndex_1,
        
        "branchSplitHeightInLevelList_2": storeSplitHeights_2,
        "branchSplitHeightInLevelListIndex_2": props.treeSettings.branchSplitHeightInLevelListIndex_2,
        
        "branchSplitHeightInLevelList_3": storeSplitHeights_3,
        "branchSplitHeightInLevelListIndex_3": props.treeSettings.branchSplitHeightInLevelListIndex_3,
        
        "branchSplitHeightInLevelList_4": storeSplitHeights_4,
        "branchSplitHeightInLevelListIndex_4": props.treeSettings.branchSplitHeightInLevelListIndex_4,
        
        "branchSplitHeightInLevelList_5": storeSplitHeights_5,
        "branchSplitHeightInLevelListIndex_5": props.treeSettings.branchSplitHeightInLevelListIndex_5,
        
        "branchSplitHeightInLevelList_6": storeSplitHeights_6,
        "branchSplitHeightInLevelListIndex_6": props.treeSettings.branchSplitHeightInLevelListIndex_6,
        
        "branchSplitHeightInLevelList_7": storeSplitHeights_7,
        "branchSplitHeightInLevelListIndex_7": props.treeSettings.branchSplitHeightInLevelListIndex_7,
        
        "branchSplitHeightInLevelList_8": storeSplitHeights_8,
        "branchSplitHeightInLevelListIndex_8": props.treeSettings.branchSplitHeightInLevelListIndex_8,
        
        "branchSplitHeightInLevelList_9": storeSplitHeights_5,
        "branchSplitHeightInLevelListIndex_9": props.treeSettings.branchSplitHeightInLevelListIndex_9,
        
        "branchSplitHeightInLevelList_10": storeSplitHeights_10,
        "branchSplitHeightInLevelListIndex_10": props.treeSettings.branchSplitHeightInLevelListIndex_10,
        
        "branchSplitHeightInLevelList_11": storeSplitHeights_11,
        "branchSplitHeightInLevelListIndex_11": props.treeSettings.branchSplitHeightInLevelListIndex_11,
        
        "branchSplitHeightInLevelList_12": storeSplitHeights_12,
        "branchSplitHeightInLevelListIndex_12": props.treeSettings.branchSplitHeightInLevelListIndex_12,
        
        "branchSplitHeightInLevelList_13": storeSplitHeights_13,
        "branchSplitHeightInLevelListIndex_13": props.treeSettings.branchSplitHeightInLevelListIndex_13,
        
        "branchSplitHeightInLevelList_14": storeSplitHeights_14,
        "branchSplitHeightInLevelListIndex_14": props.treeSettings.branchSplitHeightInLevelListIndex_14,
        
        "branchSplitHeightInLevelList_15": storeSplitHeights_15,
        "branchSplitHeightInLevelListIndex_15": props.treeSettings.branchSplitHeightInLevelListIndex_15,
        
        "branchSplitHeightInLevelList_16": storeSplitHeights_16,
        "branchSplitHeightInLevelListIndex_16": props.treeSettings.branchSplitHeightInLevelListIndex_16,
        
        "branchSplitHeightInLevelList_17": storeSplitHeights_17,
        "branchSplitHeightInLevelListIndex_17": props.treeSettings.branchSplitHeightInLevelListIndex_17,
        
        "branchSplitHeightInLevelList_18": storeSplitHeights_18,
        "branchSplitHeightInLevelListIndex_18": props.treeSettings.branchSplitHeightInLevelListIndex_18,
        
        "branchSplitHeightInLevelList_19": storeSplitHeights_19,
        "branchSplitHeightInLevelListIndex_19": props.treeSettings.branchSplitHeightInLevelListIndex_19,
        
        "branchSplitHeightInLevelListList": nestedBranchSplitHeightInLevelList,
        
        "showLeafSettings": [props.leafClusterSettingsList[i].showLeafSettings for i in range(props.treeSettings.leafClusters)],
        #------------
        "leavesDensityList": [props.leafClusterSettingsList[i].leavesDensity for i in range(props.treeSettings.leafClusters)],
        "leafSizeList": [props.leafClusterSettingsList[i].leafSize for i in range(props.treeSettings.leafClusters)],
        "leafAspectRatioList": [props.leafClusterSettingsList[i].leafAspectRatio for i in range(props.treeSettings.leafClusters)],
        "leafStartHeightGlobalList": [props.leafClusterSettingsList[i].leafStartHeightGlobal for i in range(props.treeSettings.leafClusters)],
        "leafEndHeightGlobalList": [props.leafClusterSettingsList[i].leafEndHeightGlobal for i in range(props.treeSettings.leafClusters)],
        "leafStartHeightClusterList": [props.leafClusterSettingsList[i].leafStartHeightCluster for i in range(props.treeSettings.leafClusters)],
        "leafEndHeightClusterList": [props.leafClusterSettingsList[i].leafEndHeightCluster for i in range(props.treeSettings.leafClusters)],
        "leafTypeList": [props.leafClusterSettingsList[i].leafType.value for i in range(props.treeSettings.leafClusters)],
        "leafWhorlCountList": [props.leafClusterSettingsList[i].leafWhorlCount for i in range(props.treeSettings.leafClusters)],
        "leafAngleModeList": [props.leafClusterSettingsList[i].leafAngleMode.value for i in range(props.treeSettings.leafClusters)],
        
        "leafVerticalAngleBranchStartList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchStart for i in range(props.treeSettings.leafClusters)],
        "leafVerticalAngleBranchEndList": [props.leafClusterSettingsList[i].leafVerticalAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
        "leafRotateAngleBranchStartList": [props.leafClusterSettingsList[i].leafRotateAngleBranchStart for i in range(props.treeSettings.leafClusters)],
        "leafRotateAngleBranchEndList": [props.leafClusterSettingsList[i].leafRotateAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
        "leafTiltAngleBranchStartList": [props.leafClusterSettingsList[i].leafTiltAngleBranchStart for i in range(props.treeSettings.leafClusters)],
        "leafTiltAngleBranchEndList": [props.leafClusterSettingsList[i].leafTiltAngleBranchEnd for i in range(props.treeSettings.leafClusters)],
        
        "showLeafClusterList": [props.treeSettings.leafParentClusterBoolListList[i].show_leaf_cluster for  i in range(len(props.treeSettings.leafParentClusterBoolListList))],
        "leafParentClusterBoolListList": nestedLeafList
    }

    with open(filePath, 'w') as f:
        json.dump(data, f)


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


        
def register():
    #save and load
    bpy.utils.register_class(importProperties)
    bpy.utils.register_class(exportProperties)
    bpy.utils.register_class(loadPreset)
    
    #data types
    bpy.utils.register_class(treePresetEnumProp)
    
    bpy.utils.register_class(treeShapeEnumProp)
    bpy.utils.register_class(splitModeEnumProp)
    bpy.utils.register_class(angleModeEnumProp)
    bpy.utils.register_class(branchTypeEnumProp)
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
    
    bpy.utils.register_class(treeSettings)
    bpy.utils.register_class(branchClusterSettings)
    bpy.utils.register_class(leafClusterSettings)
    
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
    bpy.utils.register_class(addLeafItem)
    bpy.utils.register_class(removeLeafItem)
    bpy.utils.register_class(toggleUseTaperCurveOperator)
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(treeSettingsPanel)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(angleSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(leafSettings)
    
    bpy.utils.register_class(BranchSettings)
    
    #bpy.utils.register_class(CurvyPanel)
    
    #UILists
    bpy.utils.register_class(UL_stemSplitLevelList)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_0)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_1)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_2)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_3)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_4)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_5)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_6)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_7)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_8)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_9)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_10)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_11)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_12)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_13)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_14)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_15)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_16)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_17)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_18)
    bpy.utils.register_class(UL_branchSplitLevelListLevel_19)
    
    
    
    bpy.utils.register_class(evaluateButton)
    bpy.utils.register_class(initButton)
    bpy.utils.register_class(AddBranchClusterButton)
    bpy.utils.register_class(BranchClusterEvaluateButton)
    bpy.utils.register_class(BranchClusterResetButton)
    
    
    #collections    
    bpy.types.Scene.branchClusterSettingsList = bpy.props.CollectionProperty(type=branchClusterSettings)
    
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.showStemSplitHeights = bpy.props.BoolProperty(
        name = "Show/hide stem split heights",
        default = True
    )
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.treePreset = bpy.props.PointerProperty(type=treePresetEnumProp)
    
    bpy.types.Scene.folder_path = bpy.props.StringProperty(name="Folder", subtype='DIR_PATH', default="")
    bpy.types.Scene.file_name = bpy.props.StringProperty(name="File Name", default="")
        
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=boolProp)
    #bpy.types.Scene.parentClusterBoolListList = bpy.props.CollectionProperty(type=parentClusterBoolListProp)
    bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
    bpy.types.Scene.nrBranchesListIndex = bpy.props.IntProperty(default=0)
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)

    
    bpy.types.Scene.leafClusterSettingsList = bpy.props.CollectionProperty(type=leafClusterSettings)
    
    bpy.types.Scene.leavesDensityListIndex = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.bark_material = bpy.props.PointerProperty(type=bpy.types.Material)
    bpy.types.Scene.leaf_material = bpy.props.PointerProperty(type=bpy.types.Material)
    
    bpy.types.Scene.maxSplitHeightUsed = bpy.props.IntProperty(default = 0)
    
    #bpy.types.Scene.leafParentClusterBoolListList = bpy.props.CollectionProperty(type=leafParentClusterBoolListProp)
            
    bpy.types.Scene.treeSettings = bpy.props.PointerProperty(type=treeSettings)
    
#    bpy.types.Scene.evaluate = bpy.props.FloatProperty(
#        name = "evaluate at",
#        default = 0.0,
#        min = 0.0, 
#        max = 1.0
#    )
#    
#    bpy.types.Scene.nrBranchClusters = bpy.props.IntProperty(
#        name = "nr branch clusters",
#        default = 0,
#        min = 0
#    )
#    
#    bpy.types.Scene.my_curve_mapping : bpy.props.CurveMappingProperty(
#        name="My Curve Mapping", 
#        min=0.0, 
#        max=1.0,
#        subtype='VALUE' # or 'XYZ', 'HSV', 'CRGB'
#    )
#    
#    bpy.types.Scene.treeHeight = bpy.props.FloatProperty(
#        name = "tree height",
#        description = "the heihgt of the tree",
#        default = 10,
#        min = 0,
#        soft_max = 50
#    )
#    
#    bpy.types.Scene.taper = bpy.props.FloatProperty(
#        name = "taper",
#        description = "taper of the stem",
#        default = 0.1,
#        min = 0,
#        soft_max = 0.5
#    )
#    
#    bpy.types.Scene.branchTipRadius = bpy.props.FloatProperty(
#        name = "branch tip radius",
#        description = "branch radius at the tip",
#        default = 0, 
#        min = 0,
#        soft_max = 0.1
#    )
#    
#    bpy.types.Scene.ringSpacing = bpy.props.FloatProperty(
#        name = "Ring Spacing",
#        description = "Spacing between rings",
#        default = 0.1,
#        min = 0.001
#    )
#    bpy.types.Scene.noiseAmplitudeHorizontal = bpy.props.FloatProperty(
#        name = "Noise Amplitude Horizontal",
#        description = "Noise amplitude horizontal",
#        default = 0.0,
#        min = 0.0
#    )
#    bpy.types.Scene.noiseAmplitudeVertical = bpy.props.FloatProperty(
#        name = "Noise Amplitude Vertical",
#        description = "Noise amplitude vertical",
#        default = 0.0,
#        min = 0.0
#    )
#    bpy.types.Scene.noiseAmplitudeGradient = bpy.props.FloatProperty(
#        name = "Noise Amplitude Gradient",
#        description = "Gradient of noise Amplitude at the base of the tree",
#        default = 0.1,
#        min = 0.0
#    )
#    bpy.types.Scene.noiseAmplitudeExponent = bpy.props.FloatProperty(
#        name = "Noise Amplitude Exponent",
#        description = "Exponent for noise amplitude",
#        default = 1.0,
#        min = 0.0
#    )
#    bpy.types.Scene.noiseScale = bpy.props.FloatProperty(
#        name = "Noise Scale",
#        description = "Scale of the noise",
#        default = 1.0,
#        min = 0.0
#    )
#    bpy.types.Scene.seed = bpy.props.IntProperty(
#        name = "Seed",
#        description = "Noise generator seed"
#    )
#    bpy.types.Scene.curvatureStart = bpy.props.FloatProperty(
#        name = "Curvature Start",
#        description = "Curvature at start of branches",
#        default = 0.0
#    )
#    bpy.types.Scene.curvatureEnd = bpy.props.FloatProperty(
#        name = "Curvature End",
#        description = "Curvature at end of branches",
#        default = 0.0
#    )
#    bpy.types.Scene.stemSplitRotateAngle = bpy.props.FloatProperty(
#        name = "Stem Split Rotate Angle",
#        description = "Rotation angle for stem splits",
#        default = 0.0,
#        min = 0.0,
#        max = 360.0
#    )
#    bpy.types.Scene.variance = bpy.props.FloatProperty(
#        name = "Variance",
#        description = "Variance",
#        default = 0.0,
#        min = 0.0,
#        max = 1.0
#    )
#    bpy.types.Scene.curvOffsetStrength = bpy.props.FloatProperty(
#        name = "Curvature Offset Strength",
#        description = "Strength of the curvature offset",
#        default = 0.0,
#        min = 0.0
#    )
#    bpy.types.Scene.stemSplitAngle = bpy.props.FloatProperty(
#        name = "Stem Split Angle",
#        description = "Angle of stem splits",
#        default = 0.0,
#        min = 0.0,
#        max = 360.0
#    )
#    
#    bpy.types.Scene.stemSplitPointAngle = bpy.props.FloatProperty(
#        name = "Stem Split Point Angle",
#        description = "Point angle of stem splits",
#        default = 0.0,
#        min = 0.0,
#        max = 360.0
#    )
#    bpy.types.Scene.splitHeightVariation = bpy.props.FloatProperty(
#        name = "Split Height Variation",
#        description = "Variation in split height",
#        default = 0.0,
#        min = 0.0
#    )
#    bpy.types.Scene.splitLengthVariation = bpy.props.FloatProperty(
#        name = "Split Length Variation",
#        description = "Variation in split length",
#        default = 0.0,
#        min = 0.0
#    )
#    bpy.types.Scene.treeShape = bpy.props.EnumProperty(
#        name="Shape",
#        description="The shape of the tree.",
#        items=[
#            ('CONICAL', "Conical", "A cone-shaped tree."),
#            ('SPHERICAL', "Spherical", "A sphere-shaped tree."),
#            ('HEMISPHERICAL', "Hemispherical", "A half-sphere shaped tree."),
#            ('INVERSE_HEMISPHERICAL', "Inverse Hemispherical", "An upside-down half-sphere shaped tree."),
#            ('CYLINDRICAL', "Cylindrical", "A cylinder-shaped tree."),
#            ('TAPERED_CYLINDRICAL', "Tapered Cylindrical", "A cylinder that tapers towards the top."),
#            ('FLAME', "Flame", "A flame-shaped tree."),
#            ('INVERSE_CONICAL', "Inverse Conical", "An upside-down cone-shaped tree."),
#            ('TEND_FLAME', "Tend Flame", "A more slender flame-shaped tree.")
#        ],
#        default='CONICAL'
#    )
#    
#    bpy.types.Scene.stemRingResolution = bpy.props.IntProperty(
#        name = "Stem Ring Resolution",
#        description = "Resolution of the stem rings",
#        default = 16,
#        min = 3
#    )
#    bpy.types.Scene.resampleDistance = bpy.props.FloatProperty(
#        name = "Resample Distance", 
#        description = "Distance between nodes",
#        default = 10.0,
#        min = 0.0
#    )
#    bpy.types.Scene.shyBranchesIterations = bpy.props.IntProperty(
#        name = "Shy Branches Iterations",
#        description = "Iterations for shy branches",
#        default = 0,
#        min = 0
#    )
#    bpy.types.Scene.nrSplits = bpy.props.IntProperty(
#        name = "Number of Splits",
#        description = "Number of splits",
#        default = 0,
#        min = 0
#    )
#    bpy.types.Scene.stemSplitMode = bpy.props.EnumProperty(
#        name = "Stem Split Mode",
#        description = "Mode for stem splits",
#        items=[
#            ('ROTATE_ANGLE', "Rotate Angle", "Split by rotating the angle"),
#            ('HORIZONTAL', "Horizontal", "Split horizontally"),
#        ],
#        default='ROTATE_ANGLE',
#    )
#    bpy.types.Scene.branchClusters = bpy.props.IntProperty(
#        name = "Branch Clusters",
#        description = "Number of branch clusters",
#        default = 0,
#        min = 0
#    )

#    bpy.types.Scene.treeGrowDir = bpy.props.FloatVectorProperty(
#        name = "Tree Grow Direction",
#        description = "Direction the tree grows in",
#        default = (0.0, 0.0, 1.0),
#        subtype = 'XYZ'  # Important for direction vectors
#    )
#    
#    bpy.types.Scene.ringResolution = bpy.props.IntVectorProperty(
#        name="Ring Resolution",
#        description="Resolution per ring",
#        size = 1, # Start with a single element
#        default = [16],
#        min = 3
#    )
#    
#    bpy.types.Scene.leafClusters = bpy.props.IntProperty(
#        name = "Leaf Clusters",
#        description = "Number of leaf clusters",
#        default = 0,
#        min = 0
#    )
    
    bpy.app.timers.register(reset_taper_curve_deferred, first_interval=0.1)
    
    

def unregister():
    #save and load
    bpy.utils.unregister_class(importProperties)
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
    bpy.utils.unregister_class(addItem)
    bpy.utils.unregister_class(removeItem)
    bpy.utils.unregister_class(toggleBool)
    bpy.utils.unregister_class(toggleLeafBool)
    bpy.utils.unregister_class(addStemSplitLevel)
    bpy.utils.unregister_class(removeStemSplitLevel)
    bpy.utils.unregister_class(addBranchSplitLevel)
    bpy.utils.unregister_class(removeBranchSplitLevel)
    bpy.utils.unregister_class(generateTree)
    bpy.utils.unregister_class(resetCurvesButton)
    bpy.utils.unregister_class(resetCurvesClusterButton)
    bpy.utils.unregister_class(addLeafItem)
    bpy.utils.unregister_class(removeLeafItem)
    
    bpy.utils.unregister_class(evaluateButton)
    bpy.utils.unregister_class(updateButton)
    bpy.utils.unregister_class(AddBranchClusterButton)
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
    
    #bpy.utils.unregister_class(CurvyPanel)
    bpy.utils.unregister_class(BranchSettings)
    bpy.utils.unregister_class(bendBranchesPanel)
    
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
    del bpy.types.Scene.evaluate
    del bpy.types.Scene.my_curve_mapping
    del bpy.types.Scene.nrBranchClusters
    
    del bpy.types.Scene.branchClusterSettingsList
    del bpy.types.Scene.stemSplitHeightInLevelList
    del bpy.types.Scene.showStemSplitHeights
    del bpy.types.Scene.stemSplitHeightInLevelListIndex
    del bpy.types.Scene.file_name
    del bpy.types.Scene.folder_path
    del bpy.types.Scene.treePreset
    del bpy.types.Scene.parentClusterBoolList
    #del bpy.types.Scene.parentClusterBoolListList
    del bpy.types.Scene.branchClusterBoolListList
    del bpy.types.Scene.nrBranchesListIndex
    del bpy.types.Scene.taperFactorList
    del bpy.types.Scene.branchSplitHeightInLevelListList
    del bpy.types.Scene.leafClusterSettingsList
    del bpy.types.Scene.leavesDensityListIndex
    del bpy.types.Scene.bark_material
    del bpy.types.Scene.leaf_material
    del bpy.types.Scene.maxSplitHeightUsed
    #del bpy.types.Scene.leafParentClusterBoolListList
#    del bpy.types.Scene.treeHeight
#    del bpy.types.Scene.taper
#    del bpy.types.Scene.branchTipRadius
#    del bpy.types.Scene.ringSpacing
#    del bpy.types.Scene.noiseAmplitudeHorizontal
#    del bpy.types.Scene.noiseAmplitudeVertical
#    del bpy.types.Scene.noiseAmplitudeGradient
#    del bpy.types.Scene.noiseAmplitudeExponent
#    del bpy.types.Scene.noiseScale
#    del bpy.types.Scene.seed
#    del bpy.types.Scene.curvatureStart
#    del bpy.types.Scene.curvatureEnd
#    del bpy.types.Scene.stemSplitRotateAngle
#    del bpy.types.Scene.variance
#    del bpy.types.Scene.curvOffsetStrength
#    del bpy.types.Scene.stemSplitAngle
#    del bpy.types.Scene.stemSplitPointAngle
#    del bpy.types.Scene.splitHeightVariation
#    del bpy.types.Scene.splitLengthVariation
#    del bpy.types.Scene.treeShape
#    del bpy.types.Scene.stemRingResolution
#    del bpy.types.Scene.resampleDistance
#    del bpy.types.Scene.shyBranchesIterations
#    del bpy.types.Scene.nrSplits
#    del bpy.types.Scene.stemSplitMode
#    del bpy.types.Scene.branchClusters
#    del bpy.types.Scene.treeGrowDir
#    del bpy.types.Scene.ringResolution
#    del bpy.types.Scene.leafClusters
    
    # Unregister timers
    bpy.app.timers.unregister(reset_taper_curve_deferred)
    
    # Unregister the panels and the UI
    bpy.utils.unregister_class(treeGenPanel)
    bpy.utils.unregister_class(treeSettingsPanel)
    bpy.utils.unregister_class(noiseSettings)
    bpy.utils.unregister_class(angleSettings)
    bpy.utils.unregister_class(splitSettings)
    bpy.utils.unregister_class(leafSettings)
    
if __name__ == "__main__":
    register()