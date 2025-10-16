# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math
import mathutils
from mathutils import Vector, Quaternion, Matrix
import random
import json
import os
import bmesh

class testClass():
    def __init__(self):
        self.x = 10

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
                                        self.tangent[0],# -> firstTangent = self.tangent[0] 
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
    
         
    def lengthToTip(self):
        if len(self.next) > 0:
            return self.next[0].lengthToTip() + (self.next[0].point - self.point).length
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
        prevNode = None
    ):
                
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
                
        for step in rotationSteps:
            self.point = step.rotationPoint + Quaternion(step.curveAxis, step.curvature) @ (self.point - step.rotationPoint)
            if step.isLast == False:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature) @ self.tangent[tangentIndex]
                self.cotangent = Quaternion(step.curveAxis, step.curvature) @ self.cotangent
            else:
                for tangentIndex in range(0, len(self.tangent)):
                    self.tangent[tangentIndex] = Quaternion(step.curveAxis, step.curvature) @ self.tangent[tangentIndex]
                    self.cotangent = Quaternion(step.curveAxis, step.curvature) @ self.cotangent
            
        if len(rotationSteps) > 0:
            rotationSteps[len(rotationSteps) - 1].isLast = False
        
        if len(self.next) > 0:
            isLast = False
            if len(self.next[0].next) == 0:
                isLast = True
                
            if Vector((self.tangent[0].x, self.tangent[0].y, 0.0)).dot(Vector((self.next[0].tangent[0].x, self.next[0].tangent[0].y, 0.0))) < reducedCurveStepCutoff:
                rotationSteps.append(rotationStep(self.point, curvature * reducedCurveStepFactor, curveAxis, isLast))
            else:
                rotationSteps.append(rotationStep(self.point, curvature, curveAxis, isLast))
        
        
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
                self)
        
        tanCount = len(self.tangent)
        if prevPoint != None:
            if tanCount == 1 and len(self.next) == 1:
                self.tangent[0] = (self.next[0].point - prevPoint).normalized()
            if tanCount == 3 and len(self.next) == 2:
                self.tangent[0] = ((self.next[0].point + self.next[1].point) / 2.0 - prevPoint).normalized()
                self.tangent[1] = (self.next[0].point - self.point).normalized()
                self.tangent[2] = (self.next[1].point - self.point).normalized()
    
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
    self.report({'INFO'}, f"in calculateRadius() point: {activeNode.point}")
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
    
    seamIndices = []
    seamOffset = 0
    
    UVs = []
    faceUVs = []
    cumulative_u_start = 0.0
    cumulative_u_end = 0.0
    max_v = 0.0
    
    offset = 0
    counter = 0
    
    startSection = 0
    
    startOffset = 0.0
    
    uvRows = 2
    
    treeGen.report({'INFO'}, f"segments: {len(segments)}") # 1
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
                    offset -= segments[s].ringResolution + 1 # TEST
                    
                if segments[s].connectedToPrevious == False:
                    startSection = 0
                    offset = len(vertices)
                    
            # in segment: -> firstTangent = self.tangent[0] 
            
                    
            controlPt1 = segments[s].start + segments[s].startTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
            controlPt2 = segments[s].end - segments[s].endTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
        
            sectionStartPos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, startSection / sections)
                        
            for section in range(startSection, sections + 1):
                pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections)
                tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections).normalized()
                
                if section == 0:
                   tangent = segments[s].firstTangent
                
                
                dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / sections)
                dirB = (tangent.cross(dirA)).normalized()
                dirA = (dirB.cross(tangent)).normalized()
                
                tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / sections)
                nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((section + 1) / sections)
                
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
                
                treeGen.report({'INFO'}, f"mesh: segments[{s}].startRadius: {segments[s].startRadius}")
                treeGen.report({'INFO'}, f"mesh: segments[{s}].endRadius: {segments[s].endRadius}")
                treeGen.report({'INFO'}, f"mesh: segments[{s}], section[{section}]: radius: {radius}")
                
                for i in range(0, segments[s].ringResolution + 1):
                    angle = (2 * math.pi * i) / segments[s].ringResolution
                    x = math.cos(angle)
                    y = math.sin(angle)
                    vertexPos = pos + dirA * radius * math.cos(angle) + dirB * radius * math.sin(angle) 
                    vertices.append(vertexPos)
                    normals.append(dirA * radius * math.cos(angle) + dirB * radius * math.sin(angle))
                    # TODO: double seam vertex -> custom normals -> for UVs !!!
                    
                    vertexTvalGlobal.append(tVal)
                    ringAngle.append(angle)
                    counter += 1
                     
            seamOffset += (sections + 1) * (segments[s].ringResolution + 1) # TEST +1 !!!
                    
            treeGen.report({'INFO'}, f"sections: {sections}")
            startRadius = 0.0
            for c in range(0, sections): 
                treeGen.report({'INFO'}, f"section: {c}")
                treeGen.report({'INFO'}, f"offset: {offset}")
                treeGen.report({'INFO'}, f"cumulative u start: {cumulative_u_start}") # 0.0
                treeGen.report({'INFO'}, f"cumulative u end: {cumulative_u_end}") # 0.0
                treeGen.report({'INFO'}, f"segments[{s}].startRadius: {segments[s].startRadius}") # 2.58
                treeGen.report({'INFO'}, f"segments[{s}].endRadius: {segments[s].endRadius}") # 0.05
                
                tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / sections)
                
                nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / sections)
                treeGen.report({'INFO'}, f"segments[{s}].sections[{c}].tVal: {tVal}")
                treeGen.report({'INFO'}, f"segments[{s}].sections[{c}].nextTval: {nextTval}")
                
                
                
                pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / sections)
                nextPos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, (c + 1) / sections)
                
                
                linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing))
                normalizedCurve = (1.0 - branchTipRadius) * tVal + sampleCurveStem(treeGen, tVal)
                
                radius = linearRadius * normalizedCurve
                
                if c == 0:
                    startRadius = radius
                
                nextLinearRadius = lerp(segments[s].startRadius, segments[s].endRadius, (c + 1) / (segmentLength / branchRingSpacing))
                nextNormalizedCurve = (1.0 - branchTipRadius) * nextTval + sampleCurveStem(treeGen, nextTval)
                nextRadius = nextLinearRadius * nextNormalizedCurve
                
                treeGen.report({'INFO'}, f"segments[{s}].sections[{c}].radius: {radius}")
                treeGen.report({'INFO'}, f"segments[{s}].sections[{c}].nextRadius: {nextRadius}")
                
                
                for j in range(0, segments[s].ringResolution): # offset += ringRes + 1
                    fa = offset + (c * (segments[s].ringResolution)) % segments[s].ringResolution + j
                    fb = offset + (c * (segments[s].ringResolution)) % segments[s].ringResolution + (j + 1)
                    fc = offset + (c * (segments[s].ringResolution)) % segments[s].ringResolution + segments[s].ringResolution + 1 + (j + 1)
                    fd = offset + (c * (segments[s].ringResolution)) % segments[s].ringResolution + segments[s].ringResolution + 1 + j
                    
                    faces.append((fa, fb, fc, fd))
                    
                    #if c == 1:
                    treeGen.report({'INFO'}, f"offset: {offset}-------fa: {fa}, fb: {fb}, fc: {fc}, fd: {fd}")
                        
                        # TODO: double seam vertex -> custom normals -> for UVs !!!
                        
                    faceUVData = []
                    
                    
                    faceUVData.append((startOffset + ( j      * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength , (0 + c) / sections)) # 0
                    
                    faceUVData.append((startOffset + ((j + 1) * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength, (0 + c) / sections)) # 1
                    
                    faceUVData.append((startOffset + ((j + 1) * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 7
                    
                    faceUVData.append((startOffset + ( j      * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 6
                    
                    
                    faceUVs.append(faceUVData)
            
            
            startOffset += segments[s].startRadius * segments[s].ringResolution / segmentLength
            
            treeGen.report({'INFO'}, f"adding {counter - 1} to offset")
            offset += counter
            counter = 0
    
    #maxU = 0.0
    #for faceUVData in faceUVs:
    #    for n in range(0, len(faceUVData)):
    #        faceUVData[n] = (faceUVData[n][0] / uvRows, faceUVData[n][1] / uvRows)
        #if faceUVData[1][0] > maxU:
        #    maxU = faceUVData[1][0]
    
    #if (maxU / uvRows) # TODO...
    
    treeGen.report({'INFO'}, f"len(faces: {len(faces)}")
    
    
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
    #############################################################
    
    # can not set normals in meshData, only in bmesh
    bmesh_obj = bmesh.new()
    bmesh_obj.from_mesh(meshData)
    
    for i, vertex in enumerate(bmesh_obj.verts):
        vertex.normal = normals[i]
        #treeGen.report({'INFO'}, f"normals[{i}]: {normals[i]}")
        

    # Update the mesh with the new normals
    bmesh_obj.to_mesh(meshData)
    bmesh_obj.free()
    
    # Update mesh data
    meshData.update()


    
        
    if len(meshData.uv_layers) == 0:
        meshData.uv_layers.new()
    
    uvLayer = meshData.uv_layers.active
    
    for i, face in enumerate(faces):
        uvLayer.data[meshData.polygons[i].loop_indices[0]].uv = (faceUVs[i][0][0], faceUVs[i][0][1])
        uvLayer.data[meshData.polygons[i].loop_indices[1]].uv = (faceUVs[i][1][0], faceUVs[i][1][1])
        uvLayer.data[meshData.polygons[i].loop_indices[2]].uv = (faceUVs[i][2][0], faceUVs[i][2][1])
        uvLayer.data[meshData.polygons[i].loop_indices[3]].uv = (faceUVs[i][3][0], faceUVs[i][3][1])
    
    
    
    meshData.update()
    
    
    
        
    #for i, face in enumerate(leafFaces):
    #    uvLayer.data[leafMeshData.polygons[i].loop_indices[0]].uv = leafUVs[face[0]]
    #    uvLayer.data[leafMeshData.polygons[i].loop_indices[1]].uv = leafUVs[face[1]]
    #    uvLayer.data[leafMeshData.polygons[i].loop_indices[2]].uv = leafUVs[face[2]]
    #    uvLayer.data[leafMeshData.polygons[i].loop_indices[3]].uv = leafUVs[face[3]]
      
    
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
    
    bpy.ops.object.shade_auto_smooth(angle=0.5)
    
    #bpy.ops.object.mode_set(mode='EDIT')
    #bpy.ops.uv.select_all(action='SELECT')
    #bpy.ops.uv.pack_islands(udim_source='ACTIVE_UDIM', rotate=False, margin=0.02, shape_method='CONVEX')
    
    #bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = treeObject.data
    
    #if "tVal" not in mesh.vertex_attributes:
    #    mesh.vertex_attributes.add(name="tVal", type='FLOAT')
    
    if "tVal" not in mesh.attributes:
        #bpy.ops.geometry.attribute_add(name="tVal", domain='POINT', data_type='FLOAT2')
        bpy.ops.geometry.attribute_add(name="tVal", domain='POINT', data_type='FLOAT')
        
    if "ringAngle" not in mesh.attributes:
        bpy.ops.geometry.attribute_add(name="ringAngle", domain='POINT', data_type='FLOAT')
    
    tValAttribute = mesh.attributes["tVal"]
    ringAngleAttribute = mesh.attributes["ringAngle"]
        
    for i, vertex in enumerate(mesh.vertices):
        #tValAttribute.data[i].vector = Vector((0.5,0.5))
        tValAttribute.data[i].value = vertexTvalGlobal[i]
        ringAngleAttribute.data[i].value = ringAngle[i] / (2.0 * math.pi)
        
    treeObject.data.materials.clear()
    treeObject.data.materials.append(barkMaterial)
