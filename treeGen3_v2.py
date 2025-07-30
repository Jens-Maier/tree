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
        #    #drawArrow(self.point, self.point + t)
        #if self.clusterIndex == -1: 
        #    #drawDebugPoint(self.point, 0.1)
        
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
        if self.clusterIndex == -1:
            drawDebugPoint(self.point, 0.8)
        if self.clusterIndex == 0:
            drawDebugPoint(self.point, 0.3)
        if self.clusterIndex == 1:
            drawDebugPoint(self.point, 0.1)
        
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
            treeGen.report({'INFO'}, f"resampleNr: {resampleNr}, startNode.ringResolution: {startNode.ringResolution}")
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
                    drawDebugPoint(samplePoint, 0.4)
                    
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
        dir = context.scene.treeGrowDir
        height = context.scene.treeHeight
        taper = context.scene.taper
        radius = context.scene.branchTipRadius
        stemRingRes = context.scene.stemRingResolution
        
        #normals: mesh overlays (only in edit mode) -> Normals
        
        # test sampleCurve:
        n = 50
        for x in range(0, n - 1):
            point = sampleCurve(self, x / n)
            #drawDebugPoint((x, 0.0, 100.0 * point), 0.1)
        
        #delete all existing empties
        if context.active_object is not None and context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY':
                    obj.select_set(True)
            bpy.ops.object.delete()
            
            nodes = []
            nodeTangents = []
            nodeTangents.append(Vector((0.0, 0.0, 1.0)))
            nodes.append(node(Vector((0.0, 0.0, 0.0)), 0.1, Vector((1.0, 0.0, 0.0)), -1, context.scene.stemRingResolution, context.scene.taper, 0.0, 0.0, height))
            nodes[0].tangent.append(Vector((0.0, 0.0, 1.0)))
            nodes.append(node(dir * height, 0.1, Vector((1.0, 0.0, 0.0)), -1, context.scene.stemRingResolution, context.scene.taper, 1.0, 0.0, height))
            nodes[1].tangent.append(Vector((0.0, 0.0, 1.0)))
            nodes[0].next.append(nodes[1])
            
            if context.scene.nrSplits > 0:
                splitRecursive(nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, context.scene.stemSplitHeightInLevelList, context.scene.splitHeightVariation, context.scene.splitLengthVariation, context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0], context.scene.stemRingResolution, context.scene.curvOffsetStrength, self, nodes[0])
            
            
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
         
      
            
            if context.scene.treeGrowDir == Vector((0.0,0.0,1.0)):
                #self.report({'ERROR'}, "ERROR: when treeGrowDir == (0,0,1)")
                self.report({'INFO'}, "treeGrowDir == (0,0,1)")
                
            # splitRecursive -> resampleSpline -> applyCurvature
            nodes[0].drawTangentArrows(self)
            
            if context.scene.branchClusters > 0:
                addBranches(
                self, 
                self, 
                context.scene.resampleDistance,
                
                context,
                nodes[0], 
                context.scene.branchClusters,
                
                context.scene.nrBranchesList, 
                context.scene.parentClusterBoolListList, 
                context.scene.branchesStartHeightGlobalList, 
                
                context.scene.branchesEndHeightGlobalList, 
                context.scene.branchesStartHeightClusterList, 
                context.scene.branchesEndHeightClusterList, 
                
                context.scene.treeGrowDir, 
                context.scene.treeHeight, 
                context.scene.verticalAngleCrownStartList,
                 
                context.scene.verticalAngleCrownEndList, 
                context.scene.verticalAngleBranchStartList,
                context.scene.verticalAngleBranchEndList,
                context.scene.branchAngleModeList,  
                
                context.scene.rotateAngleCrownStartList,
                context.scene.rotateAngleCrownEndList,
                context.scene.rotateAngleBranchStartList,
                context.scene.rotateAngleBranchEndList,
                
                context.scene.rotateAngleList,
                context.scene.rotateAngleRangeList, # -> use fibonacci rotateAngleRange!
                context.scene.useFibonacciAnglesList,
                context.scene.fibonacciNrList,
                
                context.scene.taper, 
                context.scene.taperFactorList, 
                context.scene.ringResolutionList,
                context.scene.relBranchLengthList, 
                
                context.scene.branchShapeList, 
                context.scene.nrSplitsPerBranchList, 
                context.scene.splitsPerBranchVariationList,
                
                context.scene.branchSplitAngleList, 
                context.scene.branchSplitPointAngleList, 
                context.scene.branchSplitHeightInLevelList_0, 
                context.scene.branchSplitHeightInLevelList_1, 
                context.scene.branchSplitHeightInLevelList_2, 
                context.scene.branchSplitHeightInLevelList_3, 
                context.scene.branchSplitHeightInLevelList_4, 
                context.scene.branchSplitHeightInLevelList_5, 
                
                
                context.scene.branchSplitHeightVariationList,
                context.scene.branchSplitLengthVariationList,
                context.scene.branchSplitModeList,
                context.scene.branchSplitRotateAngleList,
                context.scene.branchSplitAxisVariationList,
                
                context.scene.branchCurvatureOffsetStrengthList[0],
                context.scene.branchVarianceList, 
                
                context.scene.hangingBranchesList, 
                context.scene.branchGlobalCurvatureStartList, 
                context.scene.branchGlobalCurvatureEndList)
              
            calculateRadius(self, nodes[0], 100.0, context.scene.branchTipRadius)
            segments = []
            nodes[0].getAllSegments(self, nodes[0], segments, False)
            
            generateVerticesAndTriangles(self, self, context, segments, dir, context.scene.taper, radius, context.scene.ringSpacing, context.scene.stemRingResolution, context.scene.taperFactorList, context.scene.branchTipRadius)
            
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

    if sMode == "HORIZONTAL":
        #splitAxis = splitNode.cotangent
        right = splitNode.tangent[0].cross(Vector((0.0, 0.0, 1.0)))
        #drawDebugPoint(splitNode.point + right / 2.0, 0.1)
        splitAxis = right.cross(splitNode.tangent[0]).normalized()
        
        splitAxis = Quaternion(splitNode.tangent[0], random.uniform(-branchSplitAxisVariation, branchSplitAxisVariation)) @ splitAxis
        #drawDebugPoint(splitNode.point + splitAxis / 2.0, 0.1)

    elif sMode == "ROTATE_ANGLE":
        splitAxis = splitNode.cotangent.normalized()
        #self.report({'INFO'}, f"splitNode.tangent[0] {splitNode.tangent[0]}")
        ##self.report({'INFO'}, f"rotationAngle {rotationAngle}")
       # self.report({'INFO'}, f"level {level}")
       # self.report({'INFO'}, f"splitAxis {splitAxis}")
        #
        splitAxis = (Quaternion(splitNode.tangent[0], math.radians(rotationAngle) * level) @ splitAxis).normalized()

    else:
        self.report({'INFO'}, f"ERROR: invalid splitMode: {sMode}")
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



def addBranches(
self, 
treeGen, 
resampleDistance,

context, #ERROR: when treeGrowDir == (0,0,1) !!
rootNode, 
branchClusters,

nrBranchesList, 
parentClusterBoolListList, 
branchesStartHeightGlobalList, 

branchesEndHeightGlobalList, 
branchesStartHeightClusterList, 
branchesEndHeightClusterList, 

treeGrowDir, 
treeHeight, 
verticalAngleCrownStart, 

verticalAngleCrownEnd, 
verticalAngleBranchStart,
verticalAngleBranchEnd,

branchAngleModeList, 

rotateAngleCrownStartList,
rotateAngleCrownEndList,
rotateAngleBranchStartList,
rotateAngleBranchEndList,
                
rotateAngleList,

rotateAngleRangeList, 
useFibonacciAnglesList,
fibonacciNrList,
taper, 

taperFactorList, 
ringResolutionList, # ...TODO... -> use ringResolution! (init with resolution of stem /previous cluster!!!)
relBranchLengthList,
branchShapeList, 

nrSplitsPerBranch, 
splitsPerBranchVariation,
branchSplitAngle, 

branchSplitPointAngle, 
branchSplitHeightInLevel, #==branchSplitHeightInLevelList_0
branchSplitHeightInLevelList_1,
branchSplitHeightInLevelList_2,
branchSplitHeightInLevelList_3,
branchSplitHeightInLevelList_4,
branchSplitHeightInLevelList_5, 
                
branchSplitHeightVariation,
branchSplitLengthVariation,

branchSplitMode,
branchSplitRotateAngle,
branchSplitAxisVariationList,
branchCurvOffsetStrength,
branchVariance, 

hangingBranchesList, 
curvatureStartGlobalList, 
curvatureEndGlobalList):
    
    #treeGen.report({'INFO'}, f"in add Branches(): len(nrBranchesList): {len(nrBranchesList)}, ")
    #if len(nrBranchesList) > 0 and len(branchesStartHeightGlobalList) > 0:
    for clusterIndex in range(0, branchClusters):
        nrBranches = nrBranchesList[clusterIndex].value        
        branchesStartHeightGlobal = branchesStartHeightGlobalList[clusterIndex].value
        branchesEndHeightGlobal = branchesEndHeightGlobalList[clusterIndex].value
        branchesStartHeightCluster = branchesStartHeightClusterList[clusterIndex].value
        branchesEndHeightCluster = branchesEndHeightClusterList[clusterIndex].value
        
        #treeGen.report({'INFO'}, f"in add Branches() clusterIndex: {clusterIndex}")
        
        startNodesNextIndexStartTvalEndTval = []
        branchNodesNextIndexStartTvalEndTval = []
        branchNodes = []
        c = 0
        if clusterIndex - 1 >= 0:
            c = clusterIndex - 1
        else:
            c = clusterIndex
            
        for i in range(0, nrBranchesList[c].value):
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
            
        if clusterIndex == 1:
            for startNode in startNodesNextIndexStartTvalEndTval:
                drawDebugPoint(startNode.startNode.point, 0.1)
            
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
            for branchIndex in range(0, nrBranchesList[clusterIndex].value):
                branchPos = branchIndex * totalLength / nrBranchesList[clusterIndex].value
                #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex}, branchPos: {branchPos}") 
                
                data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False)
                
                startPoint = data.startPoint
                #treeGen.report({'INFO'}, f"clusterIndex: {clusterIndex}, startPoint: {startPoint}")
                
                startNodeNextIndex = data.startNodeNextIndex
                startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                         data.startNode.next[startNodeNextIndex].point, 
                                                         data.tangent, 
                                                         data.startNode.next[startNodeNextIndex].tangent[0], 
                                                         data.t)
                                                         
                branchStartTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
                
                globalVerticalAngle = lerp(verticalAngleCrownStart[clusterIndex].value, verticalAngleCrownEnd[clusterIndex].value, data.startNode.tValGlobal)
                
                branchVerticalAngle = lerp(verticalAngleBranchStart[clusterIndex].value, verticalAngleBranchEnd[clusterIndex].value, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t))
                
                verticalAngle = globalVerticalAngle + branchVerticalAngle
                #treeGen.report({'INFO'}, f"in add Branches: branchStartTvalGlobal: {branchStartTvalGlobal}, globalVerticalAngle: {globalVerticalAngle}, verticalAngle: {verticalAngle}")
                
                globalRotateAngle = lerp(rotateAngleCrownStartList[clusterIndex].value, rotateAngleCrownEndList[clusterIndex].value, branchStartTvalGlobal)
                
                
                branchRotateAngle = lerp(rotateAngleBranchStartList[clusterIndex].value, rotateAngleBranchEndList[clusterIndex].value, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t)) # tValBranch == 0 !!!
                
                #treeGen.report({'INFO'}, f"in add Branches: rotateAngleBranchStartList: {rotateAngleBranchStartList[clusterIndex].value:.3f}, rotateAngleBranchEndList: {rotateAngleBranchEndList[clusterIndex].value:.3f}")
                #treeGen.report({'INFO'}, f"in add Branches: branchRotateAngle: {branchRotateAngle}, data.t: {data.t:.3f}, data.startNode.tValBranch: {data.startNode.tValBranch:.3f}, data.startNode.next[data.startNodeNextIndex].tValBranch: {data.startNode.next[data.startNodeNextIndex].tValBranch:.3f}")
                
                #treeGen.report({'INFO'}, f"in add Branches: clusterIndex: {clusterIndex}, rotateAngleBranchStart: {rotateAngleBranchStartList[clusterIndex].value}, rotateAngleBranchEnd: {rotateAngleBranchEndList[clusterIndex].value}, tValBranch: {data.startNode.tValBranch}, branchRotateAngle: {branchRotateAngle}, globalRotateAngle: {globalRotateAngle}")
                
                #treeGen.report({'INFO'}, f"in add Branches: rotateAngleRange: {rotateAngleRangeList[clusterIndex].value}")
                if rotateAngleRangeList[clusterIndex].value == 0.0:
                    rotateAngleRangeList[clusterIndex].value = 180.0
                
                
                
                #treeGen.report({'INFO'}, f"in add Branches: outwardDir: {data.outwardDir}")
                #treeGen.report({'INFO'}, f"in add Branches: centerDir: {centerDir}")
                #treeGen.report({'INFO'}, f"in add Branches: angleMode: {branchAngleModeList[0].value}")
                
                #treeGen.report({'INFO'}, f"in add Branches: clusterIndex: {clusterIndex}, branchClusters: {branchClusters}")
                if branchAngleModeList[clusterIndex].value == "WINDING":
                    
                    centerDir = data.outwardDir # for symmetric!
                    #drawArrow(startPoint, startPoint + data.outwardDir)
                
                
                    #drawArrow(startPoint, startPoint + centerDir * 2.5) #???
                
                    if useFibonacciAnglesList[clusterIndex].value == True:
                
                        
                        if rotateAngleRangeList[clusterIndex].value > 0:
                            angle = (windingAngle + 360.0) % 360.0
                            # fibonacciNrList,
                        else:
                            angle = 0.0
                    else:
                        #treeGen.report({'INFO'}, f"in add Branches: fibonacciNrList[clusterIndex].rotate_angle_range: {fibonacciNrList[clusterIndex].rotate_angle_range}")
                        #treeGen.report({'INFO'}, f"in add Branches: windingAngle: {windingAngle}")
                        if fibonacciNrList[clusterIndex].rotate_angle_range <= 0.0:
                            fibonacciNrList[clusterIndex].rotate_angle_range = 180.0
                        angle = windingAngle % fibonacciNrList[clusterIndex].rotate_angle_range + fibonacciNrList[clusterIndex].rotate_angle_offset - fibonacciNrList[clusterIndex].rotate_angle_range / 2.0
                        #treeGen.report({'INFO'}, f"in add Branches: angle: {angle}")
                        
                    right = startPointTangent.cross(Vector((0.0,0.0,1.0))).normalized()
                    axis = right.cross(startPointTangent).normalized()
                    #axis = startPointTangent.cross(data.outwardDir)
                    branchDir = Quaternion(axis, math.radians(-verticalAngle)) @ startPointTangent
                    #treeGen.report({'INFO'}, f"WINDING: verticalAngle: {verticalAngle}, axis: {axis}, branchDir: {branchDir}")
                    branchDir = Quaternion(startPointTangent, math.radians(angle)) @ branchDir
                    
                # if context.scene.useFibonacciAnglesList[clusterIndex].value == True:
                #     windingAngle += context.scene.fibonacciNrList[clusterIndex].fibonacci_angle
                # else:
                #     windingAngle += rotateAngle
                   
                if branchAngleModeList[clusterIndex].value == "SYMMETRIC":
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
                shapeRatioValue = shapeRatio(self, context, startTvalGlobal, branchShapeList[clusterIndex].value)
                branchLength = treeHeight * relBranchLengthList[clusterIndex].value * shapeRatioValue
                
                #class node():
                #   def __init__(self, Point, Radius, Cotangent, RingResolution, Taper, TvalGlobal, TvalBranch):
                
                #treeGen.report({'INFO'}, f"in addBranches(): branch node.tValGlobal: {data.startNode.tValGlobal}")
                # ERROR HERE !!  ->  should be start Height!  -> WRONG! do not use data.startNode.tValGlobal!
                
                
                
                branch = node(data.startPoint, 
                              1.0, 
                              branchCotangent, 
                              clusterIndex, 
                              ringResolutionList[clusterIndex].value, 
                              taper * taperFactorList[clusterIndex].value, 
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
                                  ringResolutionList[clusterIndex].value, taper * taperFactorList[clusterIndex].value, 
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
                
                if context.scene.useFibonacciAnglesList[clusterIndex].value == True:
                    windingAngle += context.scene.fibonacciNrList[clusterIndex].fibonacci_angle
                else:
                    rotateAngle = (globalRotateAngle + branchRotateAngle) % fibonacciNrList[clusterIndex].rotate_angle_range #rotateAngleRangeList[clusterIndex].value
                    windingAngle += rotateAngle
                
        
        if hangingBranchesList[clusterIndex].value == False:
            if nrSplitsPerBranch != None:
                if len(nrSplitsPerBranch) > 0: # > clusterIndex:
                    if nrSplitsPerBranch[clusterIndex].value > 0.0: # [clusterIndex]
                        
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
                        
                        nrSplits = int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value)
                        length = len(splitHeightInLevelList)
                        if length < int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value):
                            for i in range(length, nrSplits):
                                newHeight = splitHeightInLevelList.add()
                                newHeight = 0.5
                        
                        splitBranches(treeGen,
                                      rootNode, 
                                      clusterIndex, 
                                      nrSplits, 
                                      
                                      branchSplitAngle[clusterIndex].value, 
                                      branchSplitPointAngle[clusterIndex].value, 
                                      nrSplitsPerBranch[clusterIndex].value, 
                                      
                                      splitsPerBranchVariation[clusterIndex].value, 
                                      splitHeightInLevelList,
                                      branchSplitHeightVariation[clusterIndex].value, 
                                      branchSplitLengthVariation[clusterIndex].value,
                                      
                                      branchSplitMode[clusterIndex].value, 
                                      branchSplitRotateAngle[clusterIndex].value,
                                      
                                      ringResolutionList[clusterIndex].value, 
                                      0.0,#branchCurvOffsetStrength[0], #TODO: variable for each branch cluster... 
                                      branchVariance[clusterIndex].value, 
                                      
                                      branchSplitAxisVariationList[clusterIndex].value, 
                                      False, 
                                      
                                      curvatureStartGlobalList[clusterIndex].value, 
                                      curvatureEndGlobalList[clusterIndex].value)
                                      
                                      
                
            for branchNode in branchNodes:
                
                branchNode.resampleSpline(rootNode, treeGen, resampleDistance)
                
                branchNode.applyCurvature(treeGen, 
                                          rootNode, 
                                          treeGrowDir, 
                                          treeHeight, 
                                          context.scene.branchGlobalCurvatureStartList[clusterIndex].value, 
                                          context.scene.branchCurvatureStartList[clusterIndex].value, 
                                          context.scene.branchGlobalCurvatureEndList[clusterIndex].value, 
                                          context.scene.branchCurvatureEndList[clusterIndex].value, 
                                          clusterIndex, 
                                          branchNode.point, 
                                          0, 
                                          context.scene.maxCurveSteps)
                                          
        else: #hangingBranchesList[clusterIndex].value == True:
            for branchNode in branchNodes:
                
                #branchNode.resampleSpline(rootNode, treeGen, resampleDistance)
                
                branchNode.hangingBranches(treeGen, 
                                           context.scene.branchGlobalCurvatureStartList[clusterIndex].value, 
                                           context.scene.branchGlobalCurvatureEndList[clusterIndex].value)
            
                # TODO -> split() -> splitNode.hangingBranches() after each split!
                if nrSplitsPerBranch != None:
                    if len(nrSplitsPerBranch) > 0: # > clusterIndex:
                        if nrSplitsPerBranch[clusterIndex].value > 0.0: # [clusterIndex]
                            
                            splitBranches(treeGen,
                                          rootNode, 
                                          clusterIndex, 
                                          int(nrSplitsPerBranch[clusterIndex].value * nrBranchesList[clusterIndex].value), 
                                          
                                          branchSplitAngle[clusterIndex].value, 
                                          branchSplitPointAngle[clusterIndex].value, 
                                          nrSplitsPerBranch[clusterIndex].value, 
                                          
                                          splitsPerBranchVariation[clusterIndex].value, 
                                          branchSplitHeightInLevel, # == branchSplitHeightInLevelList_0
                                          branchSplitHeightVariation[clusterIndex].value, 
                                          branchSplitLengthVariation[clusterIndex].value,
                                          
                                          branchSplitMode[clusterIndex].value, 
                                          branchSplitRotateAngle[clusterIndex].value,
                                          
                                          ringResolutionList[clusterIndex].value, 
                                          0.0,#branchCurvOffsetStrength[0], #TODO: variable for each branch cluster... 
                                          branchVariance[clusterIndex].value, 
                                          
                                          branchSplitAxisVariationList[clusterIndex].value, 
                                          True, 
                                          
                                          context.scene.branchGlobalCurvatureStartList[clusterIndex].value, 
                                          context.scene.branchGlobalCurvatureEndList[clusterIndex].value)
                                          
                #def splitBranches(self, 
                  # rootNode, 
                  # branchCluster, 
                  # nrBranchSplits, 
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
                  
                  # stemRingResolution, 
                  # curvOffsetStrength, 
                  # variance, 
                  # 
                  # branchSplitAxisVariation, 
                  # hangingBranches, 
                  # treeGen, 
                  # 
                  # curvatureStartGlobal, 
                  # curvatureEndGlobal):
                      
                      
            
def splitBranches(treeGen, 
                  rootNode, 
                  branchCluster, 
                  nrBranchSplits, 
                  
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
    
    rootNode.getAllBranchStartNodes(treeGen, allBranchNodes, branchCluster) #0)# ERROR HERE ???
    treeGen.report({'INFO'}, f"in split Branches(): branchCluster: {branchCluster}, nrSplits: {nrBranchSplits}, len(allBranchNodes): {len(allBranchNodes)}, hangingBranches: {hangingBranches}")  
    
    splitProbabilityInLevel = [0.0 for i in range(nrBranchSplits)]
    expectedSplitsInLevel = [0 for i in range(nrBranchSplits)]
    
    meanLevelBranch = 0
    if nrBranchSplits > 0:
        meanLevelBranch = max(0, math.floor(math.log2(nrBranchSplits / len(allBranchNodes))))
    
    #treeGen.report({'INFO'}, f"in split Branches(): meanLevelBranch: {meanLevelBranch}, nrBranchSplits: {nrBranchSplits}, len(allBranchNodes): {len(allBranchNodes)}")
    
    if meanLevelBranch >= 0 and nrBranchSplits > 0:
        if nrBranchSplits < len(allBranchNodes):
            expectedSplitsInLevel[0] = nrBranchSplits
            splitProbabilityInLevel[0] = 1.0
            for i in range(1, nrBranchSplits):
                expectedSplitsInLevel[i] = 0
        else:
            if nrBranchSplits > 0:
                splitProbabilityInLevel[0] = 1.0
                expectedSplitsInLevel[0] = len(allBranchNodes)
            else:
                splitProbabilityInLevel[0] = 0.0
                expectedSplitsInLevel[0] = 0
            
            for i in range(1, math.floor(meanLevelBranch - variance * meanLevelBranch)):
                splitProbabilityInLevel[i] = 1.0
                expectedSplitsInLevel[i] = len(allBranchNodes) * math.floor(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
                if expectedSplitsInLevel[i] > 1024:
                    expectedSplitsInLevel[i] = 1024
            
            for i in range(math.floor(meanLevelBranch - variance * meanLevelBranch), math.floor(meanLevelBranch + variance * meanLevelBranch)):
                splitProbabilityInLevel[i] = 1.0 - (7.0/8.0) * (i - math.floor(meanLevelBranch - variance * meanLevelBranch)) / math.floor(meanLevelBranch + variance * meanLevelBranch - math.floor(meanLevelBranch - variance * meanLevelBranch))
                
                expectedSplitsInLevel[i] = len(allBranchNodes) * math.floor(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
                if expectedSplitsInLevel[i] > 1024:
                    expectedSplitsInLevel[i] = 1024
            
            for i in range(math.floor(meanLevelBranch + variance * meanLevelBranch), nrBranchSplits):
                if i > 0:
                    splitProbabilityInLevel[i] = 1.0 / 8.0
                    expectedSplitsInLevel[i] = len(allBranchNodes) * math.floor(splitProbabilityInLevel[i] * 2.0 * expectedSplitsInLevel[i - 1])
                    if expectedSplitsInLevel[i] > 1024:
                        expectedSplitsInLevel[i] = 1024
                        
        nodesInLevelNextIndexSplitsPerBranch = []
        for i in range(0, nrBranchSplits + 1):
            nodesInLevelNextIndexSplitsPerBranch.append([])
            
        for branch in allBranchNodes:
            for n in range(0, len(branch.next)):
                nodesInLevelNextIndexSplitsPerBranch[0].append(nodeInfo(branch, n, 0))
        
        totalSplitCounter = 0
        #treeGen.report({'INFO'}, f"in split Branches(): nrBranchSplits: {nrBranchSplits}")
        for level in range(0, nrBranchSplits):
            maxSplitsPerBranch = math.floor(nrSplitsPerBranch + splitsPerBranchVariation)
            
            branchLengths = []
            branchWeights = []
            totalWeight = 0.0
            
            #class nodeInfo():
            #    def __init__(self, NodeInLevel, NextIndex, SplitsPerBranch):
            #        self.nodeInLevel = NodeInLevel
            #        self.nextIndex = NextIndex
            #        self.splitsPerBranch = SplitsPerBranch
            length = len(nodesInLevelNextIndexSplitsPerBranch[level])
            
            #if length > 0:
                #treeGen.report({'INFO'}, f"in split Branches(): level: {level}: len(nodesInLevelNextIndexSplitsPerBranch): {length}")
            
            
            for n in range(0, len(nodesInLevelNextIndexSplitsPerBranch[level])):
                N = nodesInLevelNextIndexSplitsPerBranch[level][n]
                #treeGen.report({'INFO'}, f"type: {type(N).__name__}") #FUNKT!
                nde = N.nodeInLevel
                #treeGen.report({'INFO'}, f"type: {type(nde).__name__}") #FUNKT!
                branchLength = nde.lengthToTip()
                #if n == 0:
                    #treeGen.report({'INFO'}, f"level: {level}: branchLength: {branchLength}")
            
            for n in nodesInLevelNextIndexSplitsPerBranch[level]:
                N = n.nodeInLevel
                branchLength = N.lengthToTip()
                branchLengths.append(branchLength)
                treeGen.report({'INFO'}, f"adding branchLength: {branchLength}")
                
                weight = pow(branchLength, 8.0)
                branchWeights.append(weight)
                totalWeight += weight
                treeGen.report({'INFO'}, f"adding branchWeight: {weight}")
                
            #if len(nodesInLevelNextIndexSplitsPerBranch[level]) > 0:
                #treeGen.report({'INFO'}, f"totalWeight: {totalWeight}")
                #for i in range(len(branchWeights)):
                    #treeGen.report({'INFO'}, f"branchWeights[{i}]: {branchWeights[i]}")
            
            splitsInLevel = 0
            safetyCounter = 0
            
            nodeIndices = []
            for i in range(len(nodesInLevelNextIndexSplitsPerBranch)):
                nodeIndices.append(i)
            #treeGen.report({'INFO'}, f"len(nodeIndices): {len(nodeIndices)}")
            
            if len(nodeIndices) == 0:
                continue
            
            safetyCounter = 0
            while splitsInLevel < expectedSplitsInLevel[level]:
                if safetyCounter > 11474:
                    treeGen.report({'INFO'}, f"ERROR: safetyCounter: {safetyCounter}")
                    break
                safetyCounter += 1
                if len(nodeIndices) == 0:
                    break
                if totalSplitCounter == nrBranchSplits:
                    break
                r = random.uniform(0.0, 1.0 - 1e-10)
                h = random.uniform(0.0, 1.0 - 1e-10) - 0.5
                if r < splitProbabilityInLevel[level]:
                    #split
                    #treeGen.report({'INFO'}, "in split Branches(): split!")
                    randomValue = random.uniform(0.0, 1.0 - 1e-10) * totalWeight
                    cumulativeWeight = 0.0
                    indexToSplit = -1
                    
                    for i in range(len(branchWeights)):
                        cumulativeWeight += branchWeights[i]
                        if randomValue <= cumulativeWeight:
                            indexToSplit = i
                            break
                    
                    if indexToSplit != -1 and len(nodeIndices) > 0  and indexToSplit >= 0 and indexToSplit < len(nodeIndices) and nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch < maxSplitsPerBranch:
                        # == branchSplitHeightInLevelList_0
                        branchSplitHeight = max(0.05, min(branchSplitHeightInLevel[level].value + h * branchSplitHeightVariation * min(branchSplitHeightInLevel[level].value, 1.0 - branchSplitHeightInLevel[level].value), 0.95))
                        
                        #treeGen.report({'INFO'}, "in split Branches(): branchSplitHeightInLevel[{level}]: {branchSplitHeightInLevel[level].value}")
                        
                        #treeGen.report({'INFO'}, f"split Branches(): branchSplitRotateAngle {branchSplitRotateAngle}")
                        
                        splitNode = split(
                            nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nodeInLevel,
                            nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nextIndex, 
                            branchSplitHeight, 
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
                            
                        treeGen.report({'INFO'}, f"in split Branches(): splitNode.tValBranch: {splitNode.tValBranch}") # ERROR HERE !!!
                            
                        if splitNode == nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nodeInLevel:
                            #did not split
                            totalWeight -= branchWeights[indexToSplit]
                            treeGen.report({'INFO'}, f"did not split: indexToSplit: {indexToSplit}")
                            for weight in branchWeights:
                                treeGen.report({'INFO'}, f"did not split: branchWeight: {weight}")
                            for index in nodeIndices:
                                treeGen.report({'INFO'}, f"did not split: nodeIndex: {index}")
                            
                            del branchWeights[indexToSplit]
                            del nodeIndices[indexToSplit]
                            
                            #treeGen.report({'INFO'}, "did not split!")
                        else:
                            #treeGen.report({'INFO'}, f"index to remove: {indexToSplit}, len(nodeIndices): {len(nodeIndices)}")
                            #for index in nodeIndices:
                            #    treeGen.report({'INFO'}, f"in nodeIndices: {index}")
                            totalWeight -= branchWeights[indexToSplit]
                            lengthA = splitNode.next[0].lengthToTip()
                            lengthB = splitNode.next[1].lengthToTip()
                            
                            del branchWeights[indexToSplit]
                            totalWeight += lengthA + lengthB
                            
                            nodesInLevelNextIndexSplitsPerBranch[level + 1].append(nodeInfo(splitNode, 0, nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch + 1))
                            nodesInLevelNextIndexSplitsPerBranch[level + 1].append(nodeInfo(splitNode, 1, nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch + 1))
                            
                            del nodeIndices[indexToSplit]
                            
                            splitsInLevel += 1
                            totalSplitCounter += 1
                            
                        if hangingBranches == True:
                            splitNode.hangingBranches(treeGen, curvatureStartGlobal, curvatureEndGlobal)
                
                safetyCounter += 1
                if safetyCounter > 2147483647:
                    treeGen.report({'INFO'}, f"ERROR: safetyCounter: {safetyCounter}")
                    break
                                        
            
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
    
    
    
def generateVerticesAndTriangles(self, treeGen, context, segments, dir, taper, radius, ringSpacing, stemRingRes, taperFactor, branchTipRadius):
    vertices = []
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
                    offset -= stemRingRes
                    #self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == True, offset: {offset}") 
                
                if segments[s].connectedToPrevious == False:
                    startSection = 0
                    offset = len(vertices)
                    #self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == False, offset: {offset}")
                
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
    else:
        treeObject = bpy.data.objects.new("tree", meshData)
        bpy.context.collection.objects.link(treeObject)
        treeObject.select_set(True)
        



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
        
    rotate_angle_range: bpy.props.FloatProperty(name="", default=0.0, min=0.0)
    rotate_angle_offset: bpy.props.FloatProperty(name="", default=0.0)
        

    
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
    
class posFloatPropSoftMax1(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue", default=1, min=0, soft_max=1.0)

class floatProp01(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name = "floatValue01", default=0, min=0, max=1)
    
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
    bl_description = "At least one item has to he true"
    
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
    bl_description = "At least one item has to he true"
    
    list_index: bpy.props.IntProperty()
    bool_index: bpy.props.IntProperty()
    
    def execute(self, context):
        boolList = context.scene.leafParentClusterBoolListList[self.list_index].value
        boolItem = boolList[self.bool_index]
        boolItem.value = not boolItem.value
        
        if not any(b.value for b in boolList):
            boolList[0].value = True
            
        return {'FINISHED'} #bpy.ops.scene.toggle_bool(list_index=0, bool_index=0)

    
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
        taperFactor = context.scene.taperFactorList.add()
        taperFactor.value = 1.0
        ringResolution = context.scene.ringResolutionList.add()
        
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
        rotateAngle = context.scene.rotateAngleList.add()
        rotateAngle.value = 0.0
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
        context.scene.taperFactorList.remove(len(context.scene.taperFactorList) - 1)
        context.scene.ringResolutionList.remove(len(context.scene.ringResolutionList) - 1)
        #context.scene.verticalRangeList.remove(len(context.scene.verticalRangeList) - 1)
        context.scene.showAngleSettings.remove(len(context.scene.showAngleSettings) - 1)
        context.scene.showSplitSettings.remove(len(context.scene.showSplitSettings) - 1)
        context.scene.verticalAngleCrownStartList.remove(len(context.scene.verticalAngleCrownStartList) - 1)
        context.scene.verticalAngleCrownEndList.remove(len(context.scene.verticalAngleCrownEndList) - 1)
        context.scene.verticalAngleBranchStartList.remove(len(context.scene.verticalAngleBranchStartList) - 1)
        context.scene.verticalAngleBranchEndList.remove(len(context.scene.verticalAngleBranchEndList) - 1)
        context.scene.branchAngleModeList.remove(len(context.scene.branchAngleModeList) - 1)
        context.scene.useFibonacciAnglesList.remove(len(context.scene.useFibonacciAnglesList) - 1)
        context.scene.fibonacciNrList.remove(len(context.scene.fibonacciNrList) - 1)
        context.scene.rotateAngleList.remove(len(context.scene.rotateAngleList) - 1)
        
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
        layout.prop(context.scene, "noiseAmplitudeLower")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeUpper")
        row = layout.row()
        layout.prop(context.scene, "noiseAmplitudeLowerUpperExponent")
        row = layout.row()
        layout.prop(context.scene, "noiseScale")

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
        row = layout.row()
        layout.prop(context.scene, "testRecursionStop")
        
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
        curveElement.points[0].location = (0.0, 1.0)
        curveElement.points[1].location = (1.0, 0.0)
        curveElement.points[0].handle_type = "VECTOR"
        curveElement.points[1].handle_type = "VECTOR"
        if len(curveElement.points) > 2:
            for i in range(2, len(curveElement.points)):
                curveElement.points.remove(curveElement.points[len(curveElement.points) - 1])
                #self.report({'INFO'}, "removing point")
        nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.update()
        return {'FINISHED'}

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
    
def draw_leaf_cluster_bools(layout, scene, cluster_index):
    boolListItem = scene.leafParentClusterBoolListList[cluster_index].value
    split = layout.split(factor=0.6)
    split.label(text="Parent clusters")
    
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
                row = box.row()
                
                row.prop(outer, "show_cluster", icon="TRIA_DOWN" if outer.show_cluster else "TRIA_RIGHT", emboss=False, text=f"Parent clusters", toggle=True)
                
                if outer.show_cluster:
                    if i < len(context.scene.nrBranchesList):
                        
                        box1 = box.box()
                        draw_parent_cluster_bools(box1, scene, i) #FUNKT!
                        
                        parentClusterBoolListList = context.scene.parentClusterBoolListList
                    
            
            
                if i < len(scene.nrBranchesList):
                    split = box.split(factor=0.6)
                    split.label(text="Number of branches")
                    split.prop(scene.nrBranchesList[i], "value", text="")#, slider=True)
                    
                if i < len(scene.branchVarianceList):
                    split = box.split(factor=0.6)
                    split.label(text="Branch variance")
                    split.prop(scene.branchVarianceList[i], "value", text="", slider=True)
                
                if i < len(scene.branchShapeList):
                    split = box.split(factor=0.6)
                    split.label(text="Branch shape")
                    split.prop(scene.branchShapeList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Relative branch length")
                if i < len(scene.relBranchLengthList):
                    split.prop(scene.relBranchLengthList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Taper factor")
                if i < len(scene.taperFactorList):
                    split.prop(scene.taperFactorList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Ring resolution")
                if i < len(scene.ringResolutionList):
                    split.prop(scene.ringResolutionList[i], "value", text="")
                
                split = box.split(factor=0.6)
                split.label(text="Branches start height global")
                if i < len(scene.branchesStartHeightGlobalList):
                    split.prop(scene.branchesStartHeightGlobalList[i], "value", text="", slider=True)
            
                split = box.split(factor=0.6)
                split.label(text="Branches end height global")
                if i < len(scene.branchesEndHeightGlobalList):
                    split.prop(scene.branchesEndHeightGlobalList[i], "value", text="", slider=True)
                
                split = box.split(factor=0.6)
                split.label(text="Branches start height cluster")
                if i < len(scene.branchesStartHeightClusterList):
                    split.prop(scene.branchesStartHeightClusterList[i], "value", text="", slider=True)
            
                split = box.split(factor=0.6)
                split.label(text="Branches end height cluster")
                if i < len(scene.branchesEndHeightClusterList):
                    split.prop(scene.branchesEndHeightClusterList[i], "value", text="", slider=True)
                
                
                
            split = box.split(factor=0.6)
            if len(scene.showAngleSettings) <= i:
                split.label(text=f"ERROR: len(showAngleSettings): {len(scene.showAngleSettings)}")
            else:
                split.prop(scene.showAngleSettings[i], "value", icon="TRIA_DOWN" if scene.showAngleSettings[i].value else "TRIA_RIGHT", emboss=False, text="Angle settings", toggle=True)
           
                
            
                if scene.showAngleSettings[i].value:
                    box1 = box.box()
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle crown start")
                    if i < len(scene.verticalAngleCrownStartList):
                        split.prop(scene.verticalAngleCrownStartList[i], "value", text="")
                        
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle crown end")
                    if i < len(scene.verticalAngleCrownEndList):
                        split.prop(scene.verticalAngleCrownEndList[i], "value", text="")
                
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle branch start")
                    if i < len(scene.verticalAngleBranchStartList):
                        split.prop(scene.verticalAngleBranchStartList[i], "value", text="")
                    
                    split = box1.split(factor=0.6)
                    split.label(text="Vertical angle branch end")
                    if i < len(scene.verticalAngleBranchEndList):
                        split.prop(scene.verticalAngleBranchEndList[i], "value", text="")
                
                    split = box1.split(factor=0.6)
                    split.label(text="Branch angle mode")
                    if i < len(scene.branchAngleModeList):
                        split.prop(scene.branchAngleModeList[i], "value", text="")
                    
                    box2 = box1.box()
                    split = box2.split(factor=0.6)
                    
                    if i < len(scene.branchAngleModeList):
                        if scene.branchAngleModeList[i].value == 'WINDING':
                            split.label(text="Use Fibonacci angles")
                            if i < len(scene.useFibonacciAnglesList):
                                split.prop(scene.useFibonacciAnglesList[i], "value", text="")
                            if scene.useFibonacciAnglesList[i].value == True:
                            
                                split = box2.split(factor=0.6)
                                split.label(text="Fibonacci number")
                                split.prop(scene.fibonacciNrList[i], "fibonacci_nr", text="")
                                
                                split1 = box2.split(factor=0.6)
                                split1.label(text="Angle:")
                                split1.label(text=f"{scene.fibonacciNrList[i].fibonacci_angle:.2f}°")
                            
                        if scene.useFibonacciAnglesList[i].value == False or scene.branchAngleModeList[i].value == 'SYMMETRIC':
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle range")
                            split.prop(scene.fibonacciNrList[i], "rotate_angle_range", text="")
                            
                        if scene.useFibonacciAnglesList[i].value == False and scene.branchAngleModeList[i].value == 'WINDING':
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle offset")
                            split.prop(scene.fibonacciNrList[i], "rotate_angle_offset", text="")
                        
                        if scene.useFibonacciAnglesList[i].value == False or scene.branchAngleModeList[i].value == 'SYMMETRIC':
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle crown start")
                            if i < len(scene.rotateAngleCrownStartList):
                                split.prop(scene.rotateAngleCrownStartList[i], "value", text="")
                                
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle crown end")
                            if i < len(scene.rotateAngleCrownEndList):
                                split.prop(scene.rotateAngleCrownEndList[i], "value", text="")
                                
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle branch start")
                            if i < len(scene.rotateAngleBranchStartList):
                                split.prop(scene.rotateAngleBranchStartList[i], "value", text="")
                                
                            split = box2.split(factor=0.6)
                            split.label(text="Rotate angle branch end")
                            if i < len(scene.rotateAngleBranchEndList):
                                split.prop(scene.rotateAngleBranchEndList[i], "value", text="")
                        
                        box3 = box1.box()
                        #split = box3.split(factor=0.6)
                        #split.label(text="Hanging branches")
                        #if i < len(scene.hangingBranchesList):
                        #    split.prop(scene.hangingBranchesList[i], "value", text="")
                        
                        if scene.hangingBranchesList[i].value == True:
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature start")
                            if i < len(scene.branchGlobalCurvatureStartList):
                                split.prop(scene.branchGlobalCurvatureStartList[i], "value", text="")
                            
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature end")
                            if i < len(scene.branchGlobalCurvatureEndList):
                                split.prop(scene.branchGlobalCurvatureEndList[i], "value", text="")
                        else:
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature start")
                            if i < len(scene.branchGlobalCurvatureStartList):
                                split.prop(scene.branchGlobalCurvatureStartList[i], "value", text="")
                            
                            split = box3.split(factor=0.6)
                            split.label(text="Branch global curvature end")
                            if i < len(scene.branchGlobalCurvatureEndList):
                                split.prop(scene.branchGlobalCurvatureEndList[i], "value", text="")
                            
                            split = box3.split(factor=0.6)
                            split.label(text="Branch curvature start")
                            if i < len(scene.branchCurvatureStartList):
                                split.prop(scene.branchCurvatureStartList[i], "value", text="")
                                
                            split = box3.split(factor=0.6)
                            split.label(text="Branch curvature end")
                            if i < len(scene.branchCurvatureEndList):
                                split.prop(scene.branchCurvatureEndList[i], "value", text="")
                        
                            split = box3.split(factor=0.6)
                            split.label(text="Branch curvature offset")
                            if i < len(scene.branchCurvatureOffsetStrengthList):
                                split.prop(scene.branchCurvatureOffsetStrengthList[i], "value", text="")
                        
                
                split = box.split(factor=0.6)
                split.prop(scene.showSplitSettings[i], "value", icon="TRIA_DOWN" if scene.showSplitSettings[i].value else "TRIA_RIGHT", emboss=False, text="Split settings", toggle=True)
                
                if scene.showSplitSettings[i].value:
                    box2 = box.box()
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Nr splits per branch")
                    if i < len(scene.nrSplitsPerBranchList):
                        split.prop(scene.nrSplitsPerBranchList[i], "value", text="")
                
                    box3 = box2.box()
                    split = box3.split(factor=0.6)
                    if i < len(scene.branchSplitModeList):
                        split.label(text="Branch split mode")
                        split.prop(scene.branchSplitModeList[i], "value", text="")
                        mode = scene.branchSplitModeList[i].value
                        if mode == "ROTATE_ANGLE":
                            split = box3.split(factor=0.6)
                            split.label(text="Branch split rotate angle")
                            if i < len(scene.branchSplitRotateAngleList):
                                split.prop(scene.branchSplitRotateAngleList[i], "value", text="")
                                
                        if mode == "HORIZONTAL":
                            split = box3.split(factor=0.6)
                            split.label(text="Branch split axis variation")
                            if i < len(scene.branchSplitAxisVariationList):
                                split.prop(scene.branchSplitAxisVariationList[i], "value", text="")
                    
                    if i < len(scene.branchSplitAngleList):
                        split = box2.split(factor=0.6)
                        split.label(text="Branch split angle")
                        split.prop(scene.branchSplitAngleList[i], "value", text="")
                    
                    if i < len(scene.branchSplitPointAngleList):
                        split = box2.split(factor=0.6)
                        split.label(text="Branch split point angle")
                        split.prop(scene.branchSplitPointAngleList[i], "value", text="")
                        
                    split = box2.split(factor=0.6)
                    split.label(text="Splits per branch variation")
                    if i < len(scene.splitsPerBranchVariationList):
                        split.prop(scene.splitsPerBranchVariationList[i], "value", text="")
                
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split height variation")
                    if i < len(scene.branchSplitHeightVariationList):
                        split.prop(scene.branchSplitHeightVariationList[i], "value", text="", slider=True)
                    
                    split = box2.split(factor=0.6)
                    split.label(text="Branch split length variation")
                    if i < len(scene.branchSplitLengthVariationList):
                        split.prop(scene.branchSplitLengthVariationList[i], "value", text="", slider=True)
                    
                    row = box2.row()
                    
                    row.prop(scene.showBranchSplitHeights[i], "value", icon="TRIA_DOWN" if scene.showBranchSplitHeights[i].value else "TRIA_RIGHT", text="", toggle=True)
            
                    row.operator("scene.add_branch_split_level", text="Add split level").level = i
                    row.operator("scene.remove_branch_split_level", text="Remove").level = i
                  
                    if context.scene.showBranchSplitHeights[i].value == True:
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
                            for splitLevel in context.scene.branchSplitHeightInLevelListList[i].value:
                                box2.prop(splitLevel, "value", text=f"Split height level {j}", slider=True)
                                j += 1

class addLeafItem(bpy.types.Operator):
    bl_idname = "scene.add_leaf_item"
    bl_label = "Add Item"
    def execute(self, context):
        context.scene.leafClusters += 1
        
        nrLeaves = context.scene.nrLeavesList.add()
        
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
        
        if len(context.scene.nrLeavesList) > 0:
            context.scene.nrLeavesList.remove(len(context.scene.nrLeavesList) - 1)
        
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
        row.operator("scene.remove_leaf_item", text="Remove").index = context.scene.nrLeavesListIndex
        row = layout.row()
        
        for i, outer in enumerate(scene.nrLeavesList):
            box = layout.box()
            
            split = box.split(factor=0.6)
            split.label(text="Number of leaves")
            split.prop(scene.nrLeavesList[i], "value", text="")
            
            #box1 = box.box()
            #draw_parent_cluster_bools(box1, scene, i)
            
            box1 = box.box()
            draw_leaf_cluster_bools(box1, scene, i)
                        
            
            
            
def register():
    #save and load
    bpy.utils.register_class(importProperties)
    bpy.utils.register_class(exportProperties)
    
    
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
    bpy.utils.register_class(floatProp01)
    bpy.utils.register_class(posFloatPropSoftMax1)
    bpy.utils.register_class(floatListProp)
    bpy.utils.register_class(floatListProp01)
    bpy.utils.register_class(boolProp)
    bpy.utils.register_class(parentClusterBoolListProp)
    bpy.utils.register_class(branchClusterBoolListProp)
    bpy.utils.register_class(leafParentClusterBoolListProp)
    
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
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.showStemSplitHeights = bpy.props.BoolProperty(
        name = "Show/hide stem split heights",
        default = True
    )
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.file_name = bpy.props.StringProperty(name="File Name", default="my_tree_properties")
    
    bpy.types.Scene.showAngleSettings = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.showSplitSettings = bpy.props.CollectionProperty(type=boolProp)
    
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
    bpy.types.Scene.taperFactorList = bpy.props.CollectionProperty(type=posFloatPropSoftMax1)
    bpy.types.Scene.ringResolutionList = bpy.props.CollectionProperty(type=posIntProp3)
    bpy.types.Scene.verticalAngleCrownStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleCrownEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchStartList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.verticalAngleBranchEndList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchAngleModeList = bpy.props.CollectionProperty(type=angleModeEnumProp)
    bpy.types.Scene.useFibonacciAnglesList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.fibonacciNrList = bpy.props.CollectionProperty(type=fibonacciProps)
    bpy.types.Scene.rotateAngleList = bpy.props.CollectionProperty(type=floatProp)
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
    bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitLengthVariationList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_0 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_0 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_1 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_1 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_2 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_2 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_3 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_3 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_4 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_4 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.branchSplitHeightInLevelList_5 = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchSplitHeightInLevelListIndex_5 = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.showBranchSplitHeights = bpy.props.CollectionProperty(type=boolProp)
    
    bpy.types.Scene.nrLeavesList = bpy.props.CollectionProperty(type=intPropL)
    bpy.types.Scene.nrLeavesListIndex = bpy.props.IntProperty(default=0)
    
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
    

def save_properties(filePath):
    props = bpy.context.scene
    
    controlPts = []
    handleTypes = []
    nodeGroups = bpy.data.node_groups.get('taperNodeGroup')
    curveElement = nodeGroups.nodes[taper_node_mapping['taperMapping']].mapping.curves[3]
    for n in range(0, len(curveElement.points)):
        controlPts.append(list(curveElement.points[n].location))
        handleTypes.append(curveElement.points[n].handle_type)
    
    data = {
        "treeHeight": props.treeHeight,
        "treeGrowDir": list(props.treeGrowDir),  
        "taper": props.taper,
        "taperCurvePoints": controlPts,
        "taperCurveHandleTypes": handleTypes,
        "branchTipRadius": props.branchTipRadius,
        "ringSpacing": props.ringSpacing,
        "stemRingResolution": props.stemRingResolution,
        "resampleDistance": props.resampleDistance,
        
        "noiseAmplitudeLower": props.noiseAmplitudeLower,
        "noiseAmplitudeUpper": props.noiseAmplitudeUpper,
        "noiseAmplitudeLowerUpperExponent": props.noiseAmplitudeLowerUpperExponent,
        "noiseScale": props.noiseScale,
        
        "nrSplits": props.nrSplits, 
        "curvatureStart": props.curvatureStart,
        "curvatureEnd": props.curvatureEnd,
        "testRecursionStop": props.testRecursionStop,
        "variance": props.variance,
        "stemSplitMode": props.stemSplitMode,
        "stemSplitRotateAngle": props.stemSplitRotateAngle,
        "curvOffsetStrength": props.curvOffsetStrength,
        
        "branchSplitHeightInLevelListIndex": props.branchSplitHeightInLevelListIndex,
        # Add additional split height collections  
        **{f"branchSplitHeightInLevelList_{i}": [item.value for item in getattr(props, f"branchSplitHeightInLevelList_{i}")]
           for i in range(6)},
        **{f"branchSplitHeightInLevelListIndex_{i}": getattr(props, f"branchSplitHeightInLevelListIndex_{i}")
           for i in range(6)},
           
        "splitHeightVariation": props.splitHeightVariation,
        "splitLengthVariation": props.splitLengthVariation,
        "stemSplitAngle": props.stemSplitAngle,
        "stemSplitPointAngle": props.stemSplitPointAngle,
        
        "branchClusters": props.branchClusters,
        
        "nrBranchesList": [props.nrBranchesList[i].value for i in range(0, props.branchClusters)],
        #"nrBranchesList": [item.value for item in props.nrBranchesList],
        
        #"parentClusterBoolList": [item.value for item in props.parentClusterBoolList],#TODO
        #"parentClusterBoolListList": [item.value for item in props.parentClusterBoolListList],
        #"branchClusterBoolListList": [item.value for item in props.branchClusterBoolListList],
        #"nrBranchesListIndex": props.nrBranchesListIndex,
        "branchSplitModeList": [item.value for item in props.branchSplitModeList],
        "branchVarianceList": [item.value for item in props.branchVarianceList],
        "branchSplitRotateAngleList": [item.value for item in props.branchSplitRotateAngleList],
        "branchSplitAxisVariationList": [item.value for item in props.branchSplitAxisVariationList],
        "rotateAngleCrownStartList": [item.value for item in props.rotateAngleCrownStartList],
        "rotateAngleCrownEndList": [item.value for item in props.rotateAngleCrownEndList],
        "rotateAngleBranchStartList": [item.value for item in props.rotateAngleBranchStartList],
        "rotateAngleBranchEndList": [item.value for item in props.rotateAngleBranchEndList],
        "branchSplitAngleList": [item.value for item in props.branchSplitAngleList],
        "branchSplitPointAngleList": [item.value for item in props.branchSplitPointAngleList],
        "branchShapeList": [item.value for item in props.branchShapeList],
        "relBranchLengthList": [item.value for item in props.relBranchLengthList],
        "taperFactorList": [item.value for item in props.taperFactorList],
        "ringResolutionList": [item.value for item in props.ringResolutionList],
        "verticalAngleCrownStartList": [item.value for item in props.verticalAngleCrownStartList],
        "verticalAngleCrownEndList": [item.value for item in props.verticalAngleCrownEndList],
        "verticalAngleBranchStartList": [item.value for item in props.verticalAngleBranchStartList],
        "verticalAngleBranchEndList": [item.value for item in props.verticalAngleBranchEndList],
        "branchAngleModeList": [item.value for item in props.branchAngleModeList],
        "useFibonacciAnglesList": [item.value for item in props.useFibonacciAnglesList],
        "rotateAngleList": [item.value for item in props.rotateAngleList],
        "rotateAngleRangeList": [item.value for item in props.rotateAngleRangeList],
        "branchesStartHeightGlobalList": [item.value for item in props.branchesStartHeightGlobalList],
        "branchesEndHeightGlobalList": [item.value for item in props.branchesEndHeightGlobalList],
        "branchesStartHeightClusterList": [item.value for item in props.branchesStartHeightClusterList],
        "branchesEndHeightClusterList": [item.value for item in props.branchesEndHeightClusterList],
        "hangingBranchesList": [item.value for item in props.hangingBranchesList],
        "branchGlobalCurvatureStartList": [item.value for item in props.branchGlobalCurvatureStartList],
        "branchGlobalCurvatureEndList": [item.value for item in props.branchGlobalCurvatureEndList],
        "branchCurvatureStartList": [item.value for item in props.branchCurvatureStartList],
        "branchCurvatureEndList": [item.value for item in props.branchCurvatureEndList],
        "branchCurvatureOffsetStrengthList": [item.value for item in props.branchCurvatureOffsetStrengthList],
        "nrSplitsPerBranchList": [item.value for item in props.nrSplitsPerBranchList],
        "splitsPerBranchVariationList": [item.value for item in props.splitsPerBranchVariationList],
        "branchSplitHeightVariationList": [item.value for item in props.branchSplitHeightVariationList],
        
        #"branchSplitHeightInLevelListList": [item.value for item in props.branchSplitHeightInLevelListList],
        
        # "branchSplitHeightInLevelListList": [
        #    [item.value for item in getattr(props, f"branchSplitHeightInLevelList_{i}_0")]
        #    for i in range(6)
        #],
        
        
    
        
        #"branchSplitHeightInLevelListIndex": props.branchSplitHeightInLevelListIndex,
        
        #"branchSplitHeightInLevelList_0": [item.value for item in props.branchSplitHeightInLevelList_0],
        #"branchSplitHeightInLevelListIndex_0": props.branchSplitHeightInLevelListIndex_0,
        #"branchSplitHeightInLevelList_1": [item.value for item in props.branchSplitHeightInLevelList_1],
        #"branchSplitHeightInLevelListIndex_1": props.branchSplitHeightInLevelListIndex_1,
        #"branchSplitHeightInLevelList_2": [item.value for item in props.branchSplitHeightInLevelList_2],
        #"branchSplitHeightInLevelListIndex_2": props.branchSplitHeightInLevelListIndex_2,
        #"branchSplitHeightInLevelList_3": [item.value for item in props.branchSplitHeightInLevelList_3],
        #"branchSplitHeightInLevelListIndex_3": props.branchSplitHeightInLevelListIndex_3,
        #"branchSplitHeightInLevelList_4": [item.value for item in props.branchSplitHeightInLevelList_4],
        #"branchSplitHeightInLevelListIndex_4": props.branchSplitHeightInLevelListIndex_4,
        #"branchSplitHeightInLevelList_5": [item.value for item in props.branchSplitHeightInLevelList_5],
        #"branchSplitHeightInLevelListIndex_5": props.branchSplitHeightInLevelListIndex_5
        
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
        
        props.noiseAmplitudeLower = data.get("noiseAmplitudeLower", props.noiseAmplitudeLower)
        props.noiseAmplitudeUpper = data.get("noiseAmplitudeUpper", props.noiseAmplitudeUpper)
        props.noiseAmplitudeLowerUpperExponent = data.get("noiseAmplitudeLowerUpperExponent", props.noiseAmplitudeLowerUpperExponent)
        props.noiseScale = data.get("noiseScale", props.noiseScale)
        
        props.nrSplits = data.get("nrSplits", props.nrSplits)
        props.curvatureStart = data.get("curvatureStart", props.curvatureStart)
        props.curvatureEnd = data.get("curvatureEnd", props.curvatureEnd)
        props.testRecursionStop = data.get("testRecursionStop", props.testRecursionStop)
        props.variance = data.get("variance", props.variance)
        props.stemSplitMode = data.get("stemSplitMode", props.stemSplitMode)
        props.stemSplitRotateAngle = data.get("stemSplitRotateAngle", props.stemSplitRotateAngle)
        props.curvOffsetStrength = data.get("curvOffsetStrength", props.curvOffsetStrength)
        props.splitHeightVariation = data.get("splitHeightVariation", props.splitHeightVariation)
        props.splitLengthVariation = data.get("splitLengthVariation", props.splitLengthVariation)
        props.stemSplitAngle = data.get("stemSplitAngle", props.stemSplitAngle)
        props.stemSplitPointAngle = data.get("stemSplitPointAngle", props.stemSplitPointAngle)
        
        props.branchClusters = data.get("branchClusters", props.branchClusters)
        
        for value in data.get("nrBranchesList", []):
            item = props.nrBranchesList.add()
            item.value = value
            
        for value in data.get("branchVarianceList", []):
            item = props.branchVarianceList.add()
            item.value = value
            
        for value in data.get("branchSplitRotateAngleList", []):
            item = props.branchSplitRotateAngleList.add()
            item.value = value
            
        for value in data.get("branchSplitAxisVariationList", []):
            item = props.branchSplitAxisVariationList.add()
            item.value = value
        
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
            
            
        
            
        for value in data.get("branchSplitPointAngleList", []):
            item = props.branchSplitPointAngleList.add()
            item.value = value
            
        for value in data.get("branchShapeList", []):
            item = props.branchShapeList.add()
            item.value = value
            
        for value in data.get("taperFactorList", []):
            item = props.taperFactorList.add()
            item.value = value
        
        for value in data.get("ringResolutionList", []):
            item = props.ringResolutionList.add()
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
            
        for value in data.get("rotateAngleList", []):
            item = props.rotateAngleList.add()
            item.value = value
            
        for value in data.get("rotateAngleRangeList", []):
            item = props.rotateAngleRangeList.add()
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
            
        for value in data.get("hangingBranchesList", []):
            item = props.hangingBranchesList.add()
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
            
        for value in data.get("splitsPerBranchVariationList", []):
            item = props.splitsPerBranchVariationList.add()
            item.value = value
            
        for value in data.get("branchSplitHeightVariationList", []):
            item = props.branchSplitHeightVariationList.add()
            item.value = value
        
        for value in data.get("branchSplitLengthVariationList", []):
            item = props.branchSplitLengthVariationList.add()
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
    bpy.utils.unregister_class(treeShapeEnumProp)
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