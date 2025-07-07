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
from mathutils import Vector, Quaternion
import random

class startNodeInfo():
    def __init__(self, StartNode, NextIndex, StartTval, EndTval):
        self.startNode = StartNode
        self.nextIndex = NextIndex
        self.startTval = StartTval
        self.endTval = EndTval
        
class startPointData():
    def __init__(self, StartPoint, OutwardDir, StartNode, StartNodeIndex, StartNodeNextIndex, T, Tangent):
        self.startPoint = StartPoint
        self.outwardDir = OutwardDir
        self.startNode = StartNode
        self.startNodeIndex = StartNodeIndex
        self.startNodeNextIndex = StartNodeNextIndex
        self.t = T
        self.tangent = Tangent

class node():
    def __init__(self, Point, Radius, Cotangent, RingResolution, Taper, TvalGlobal, TvalBranch):
        self.point = Point
        self.radius = Radius
        self.tangent = []
        self.cotangent = Cotangent
        self.ringResolution = RingResolution
        self.taper = Taper
        self.tValGlobal = TvalGlobal
        self.tValBranch = TvalBranch
        self.next = []
        
    def drawDebugPoint(pos, name="debugPoint"):
        bpy.ops.object.empty_add(type='SPHERE', location=pos)
        bpy.context.active_object.empty_display_size = 0.1
        bpy.context.active_object.name=name
    
        
    def getAllSegments(self, treeGen, segments, connectedToPrev):
        #if len(activeNode.next) > 2:
        #treeGen.report({'INFO'}, f"len(activeNode.next) = {len(activeNode.next)}")
        
        for n, nextNode in enumerate(self.next):
            if len(self.next) > 1:
                #treeGen.report({'INFO'}, f"in getAllSegments(): len(tangent): {len(self.tangent)}, n: {n}")
                
                segments.append(segment(self.point, nextNode.point, self.tangent[n + 1], nextNode.tangent[0], self.cotangent, nextNode.cotangent, self.radius, nextNode.radius, self.ringResolution, False))
            else:
                #treeGen.report({'INFO'}, f"in getAllSegments(): len(tangent): {len(self.tangent)}, n: {n}")
                segments.append(segment(self.point, nextNode.point, self.tangent[0], nextNode.tangent[0], self.cotangent, nextNode.cotangent, self.radius, nextNode.radius, self.ringResolution, connectedToPrev))
        
            nextNode.getAllSegments(treeGen, segments, True)
            # TODO: children...
            
    
        
    
    def getAllStartNodes(self, treeGen, startNodesNextIndexStartTvalEndTval, startHeightGlobal, endHeightGlobal, startHeightCluster, endHeightCluster, parentClusterBoolListList):
        
        #stem
        for n in range(len(self.next)):
            # test if overlap    |----*--v--*----*---v--*
            if self.next[n].tValGlobal > startHeightGlobal and self.tValGlobal < endHeightGlobal:
                segmentStartGlobal = max(self.tValGlobal, startHeightGlobal)
                segmentEndGlobal = min(self.next[n].tValGlobal, endHeightGlobal)
                
                startTvalSegment = (segmentStartGlobal - self.tValGlobal) / (self.next[n].tValGlobal - self.tValGlobal)
                endTvalSegment = (segmentEndGlobal - self.tValGlobal) / (self.next[n].tValGlobal - self.tValGlobal)
                
                startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, startTvalSegment, endTvalSegment))
        
        #if self.tValGlobal >= startHeightGlobal and self.tValGlobal <= endHeightGlobal:
        #    if len(self.next) > 0:
        #        for n in range(len(self.next)):
        #            startNodesNextIndexStartTvalEndTval.append(startNodeInfo(self, n, 0.0, 1.0))
        #            #drawDebugPoint(self.point)
                    
                    
        for n in self.next:
            n.getAllStartNodes(treeGen, startNodesNextIndexStartTvalEndTval, startHeightGlobal, endHeightGlobal, startHeightCluster, endHeightCluster, parentClusterBoolListList)
            
            
        #treeGen.report({'INFO'}, f"in getAllStartNodes(): len(startNodes): {len(startNodesNextIndexStartTvalEndTval)}")
        
        
        
class segment():
    def __init__(self, Start, End, StartTangent, EndTangent, StartCotangent, EndCotangent, StartRadius, EndRadius, RingResolution, ConnectedToPrevious):
        self.start = Start
        self.end = End
        self.startTangent = StartTangent
        self.endTangent = EndTangent
        self.startCotangent = StartCotangent
        self.endCotangent = EndCotangent
        self.startRadius = StartRadius
        self.endRadius = EndRadius
        self.ringResolution = RingResolution
        self.connectedToPrevious = ConnectedToPrevious

class splitMode:
    HORIZONTAL = 0
    ROTATE_ANGLE = 1
    ALTERNATING = 2
        
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
            
            nodes.append(node(Vector((0.0, 0.0, 0.0)), 0.1, Vector((1.0, 0.0, 0.0)), context.scene.stemRingResolution, context.scene.taper, 0.0, 0.0))
            
            nodes[0].tangent.append(Vector((0.0, 0.0, 1.0)))
            
            #nodes.append(node(dir * height * 0.7, 0.1, Vector((0.0, 0.5, 1.0)), Vector((1.0, 0.0, 0.0)), context.scene.stemRingResolution, context.scene.taper, 0.7, 0.0))
            nodes.append(node(dir * height, 0.1, Vector((1.0, 0.0, 0.0)), context.scene.stemRingResolution, context.scene.taper, 1.0, 0.0))
            nodes[1].tangent.append(Vector((0.0, 0.0, 1.0)))
            nodes[0].next.append(nodes[1])
            #nodes[1].next.append(nodes[2])
        
            #drawDebugPoint(nodes[0].point)
            #drawDebugPoint(nodes[1].point)
            #drawDebugPoint(nodes[2].point)
            
            #if context.scene.nrSplits > 0:
                #splitRecursive(nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, [0.5], context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0], context.scene.stemRingResolution)
                
             #split(startNode, nextIndex, splitHeight, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution):
             
            #split(nodes[0], 0, 0.4, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, 0, 0, context.scene.stemSplitRotateAngle, context.scene.stemRingResolution, context.scene.curvOffsetStrength, self) # funkt!
            
            #def splitRecursive(startNode, nrSplits, splitAngle, splitPointAngle, variance, splitHeightInLevel, stemSplitMode, stemSplitRotateAngle, root_node, stemRingResolution, curvOffsetStrength, self):
            if context.scene.nrSplits > 0:
                splitRecursive(nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, context.scene.stemSplitHeightInLevelList, context.scene.splitHeightVariation, context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0], context.scene.stemRingResolution, context.scene.curvOffsetStrength, self, nodes[0])
            
            addBranches(self, context, nodes[0], context.scene.nrBranchesList, context.scene.parentClusterBoolListList, context.scene.branchesStartHeightGlobalList, context.scene.branchesEndHeightGlobalList, context.scene.branchesStartHeightClusterList, context.scene.branchesEndHeightClusterList, context.scene.treeGrowDir, context.scene.treeHeight, context.scene.verticalAngleCrownStart, context.scene.verticalAngleCrownEnd, context.scene.branchAngleModeList, context.scene.branchSplitRotateAngleList, context.scene.rotateAngleRangeList, context.scene.stemRingResolution, context.scene.taper, context.scene.taperFactor, context.scene.relBranchLengthList)
            
            #def addBranches(self, context, rootNode, nrBranchesList, parentClusterBoolListList, branchesStartHeightGlobalList, branchesEndHeightGlobalList, branchesStartHeightClusterList, branchesEndHeightClusterList, treeGrowDir, treeHeight, verticalAngleCrownStart, verticalAngleCrownEnd, branchAngleModeList, windingAngleList, rotateAngleRangeList, ringResolution, taper, taperFactor, relBranchLengthList):
            
            #drawDebugPoint(nodes[0].point)
            #drawDebugPoint(nodes[1].point)
            #drawDebugPoint(nodes[0].next[0].point)
            #drawDebugPoint(nodes[0].next[0].next[0].point)
            #drawDebugPoint(nodes[0].next[0].next[1].point)
            #drawDebugPoint(nodes[2].point)
            #drawDebugPoint(nodes[3].point)
            
            calculateRadius(self, nodes[0], 100.0, context.scene.branchTipRadius)
            segments = []
            nodes[0].getAllSegments(self, segments, False)
            generateVerticesAndTriangles(self, segments, dir, context.scene.taper, radius, context.scene.ringSpacing, context.scene.stemRingResolution)
            
            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
    
def drawDebugPoint(pos, name="debugPoint"):
    bpy.ops.object.empty_add(type='SPHERE', location=pos)
    bpy.context.active_object.empty_display_size = 0.1
    bpy.context.active_object.name=name
    
def calculateRadius(self, activeNode, maxRadius, branchTipRadius):
    if len(activeNode.next) > 0:
        sum = 0.0
        max = 0.0
        for n in activeNode.next:
            s = calculateRadius(self, n, maxRadius, branchTipRadius)
            s += (n.point - activeNode.point).length * activeNode.taper * activeNode.taper
            if s > max:
                max = s
            #self.report({'INFO'}, f"s: {s}, max: {max}")
        sum = max
        
        
        #sum = calculateRadius(activeNode.next[0], maxRadius, branchTipRadius)
        #sum += (activeNode.next[0].point - activeNode.point).length * activeNode.taper * activeNode.taper
        
        #if len(branches) > 0: ....
        if sum < maxRadius:
            #if sum == 0.0:
                #activeNode.radius = 0.01
            #else:
                activeNode.radius = sum
        else:
            activeNode.radius = maxRadius
        return sum
    else:
        activeNode.radius = branchTipRadius
        return branchTipRadius
    

#nodes[0], context.scene.nrSplits, context.scene.stemSplitAngle, context.scene.stemSplitPointAngle, context.scene.variance, 0.5, context.scene.stemSplitMode, context.scene.stemSplitRotateAngle, nodes[0]

def splitRecursive(startNode, nrSplits, splitAngle, splitPointAngle, variance, splitHeightInLevel, splitHeightVariation, stemSplitMode, stemSplitRotateAngle, root_node, stemRingResolution, curvOffsetStrength, self, rootNode):
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
    if addAmount > 0 and expectedSplitsInLevel[addToLevel] + addAmount <= maxPossibleSplits:
        expectedSplitsInLevel[addToLevel] += addAmount

    splitProbabilityInLevel[addToLevel] = float(expectedSplitsInLevel[addToLevel]) / float(maxPossibleSplits)

    nodesInLevelNextIndex = [[] for _ in range(nrSplits + 1)]
    for n in range(len(startNode.next)):
        nodesInLevelNextIndex[0].append((startNode, n))

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
                    splitNode = split(
                        nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][0],
                        nodesInLevelNextIndex[level][nodeIndices[indexToSplit]][1],
                        splitHeight, splitAngle, splitPointAngle, level, stemSplitMode, stemSplitRotateAngle, stemRingResolution, curvOffsetStrength, self, rootNode)
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
            
def split(startNode, nextIndex, splitHeight, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, rootNode):
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
                    calculateSplitData(splitNode, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
                else:
                    # TODO -> split at new node!!!
                    return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, rootNode)
                    #return startNode
                #    self.report({'INFO'}, f"splitNode == startNode")
                #    if splitNode == rootNode:
                #        calculateSplitData(splitNode, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
               # self.report({'INFO'}, f"split at existing node")
                #return splitNode
            else:
                return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, rootNode)
                
    #self.report({'INFO'}, f"split failed! nrNodesToTip: {nrNodesToTip}, len(startNode.next): {len(startNode.next)}, nextIndex: {nextIndex}")
    return startNode

def splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self, rootNode):
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

                newNode = node(newPoint, newRadius, newCotangent, ring_res, taper, newTvalGlobal, newTvalBranch)
                #self.report({'INFO'}, f"split: newNode.taper: {newNode.taper}")
                newNode.tangent.append(newTangent)
                # Insert new node in the chain
                newNode.next.append(splitAfterNode.next[nextIndex])
                splitAfterNode.next[nextIndex] = newNode
                
                # TODO: splitNode = newNode ???
                
                # ERROR: when splitHeightVariation is large !!!
                
                

                calculateSplitData(newNode, splitAngle, splitPointAngle, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, self)
                #self.report({'INFO'}, f"did split!")
                return newNode

def calculateSplitData(splitNode, splitAngle, splitPointAngle, level, sMode, rotationAngle, stemRingResolution, curvOffsetStrength, self):
    
    n = splitNode
    nodesAfterSplitNode = 0
    
    while n.next:
        nodesAfterSplitNode += 1
        n = n.next[0]

    # Initialize splitAxis
    splitAxis = Vector((0, 0, 0))

    if sMode == "HORIZONTAL":
        splitAxis = splitNode.cotangent
        right = splitNode.tangent[0].cross(Vector((0.0, 1.0, 0.0)))
        splitAxis = right.cross(splitNode.tangent[0]).normalized()

    elif sMode == "ROTATE_ANGLE":
        splitAxis = splitNode.cotangent.normalized()
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
        offset_b = (Quaternion(splitAxis, -math.radians(splitAngle)) @ rel_pos)

        # Assuming the class node has a constructor that matches the parameters
        tValBranch = 0.0  # TODO: define this as needed
        ring_res_index = -1 # TODO: = splitNode.cluster_index
        ring_resolution = stemRingResolution # TODO: if ring_res_index == -1 else cluster_ring_resolution[ring_res_index]

        nodeA = node(splitNode.point + offset_a + curv_offset, 1.0, cotangent_a, ring_resolution, s.taper, s.tValGlobal, tValBranch)
        nodeA.tangent.append(tangent_a)
        nodeB = node(splitNode.point + offset_b + curv_offset, 1.0, cotangent_b, ring_resolution, s.taper, s.tValGlobal, tValBranch)
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


def addBranches(self, context, rootNode, nrBranchesList, parentClusterBoolListList, branchesStartHeightGlobalList, branchesEndHeightGlobalList, branchesStartHeightClusterList, branchesEndHeightClusterList, treeGrowDir, treeHeight, verticalAngleCrownStart, verticalAngleCrownEnd, branchAngleModeList, windingAngleList, rotateAngleRangeList, ringResolution, taper, taperFactor, relBranchLengthList):
    
    nrBranches = nrBranchesList[0].value
    branchesStartHeightGlobal = branchesStartHeightGlobalList[0].value
    branchesEndHeightGlobal = branchesEndHeightGlobalList[0].value
    branchesStartHeightCluster = branchesStartHeightClusterList[0].value
    branchesEndHeightCluster = branchesEndHeightClusterList[0].value
    
    self.report({'INFO'}, f"in addBranches(): nr: {nrBranches}")
    
    startNodesNextIndexStartTvalEndTval = []
    rootNode.getAllStartNodes(self, startNodesNextIndexStartTvalEndTval, branchesStartHeightGlobal, branchesEndHeightGlobal, branchesStartHeightCluster, branchesEndHeightCluster, parentClusterBoolListList)
    
    #for s in startNodesNextIndexStartTvalEndTval:
    #    drawDebugPoint(s.startNode.point)
    
    if len(startNodesNextIndexStartTvalEndTval) > 0:
        segmentLengths = []
        
        totalLength = calculateSegmentLengthsAndTotalLength(startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal)
        self.report({'INFO'}, f"total length: {totalLength}")
        
        for branchIndex in range(0, nrBranches):
            branchPos = branchIndex * totalLength / nrBranches
            
            data = generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, False)
            
            startNodeNextIndex = data.startNodeNextIndex
            startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                     data.startNode.next[startNodeNextIndex].point, 
                                                     data.tangent, 
                                                     data.startNode.next[startNodeNextIndex].tangent[0], 
                                                     data.t)
            
            globalVerticalAngle = lerp(verticalAngleCrownStart[0], verticalAngleCrownEnd[0], data.startNode.tValGlobal)
            branchVerticalAngle = 0.0 #... TODO
            verticalAngle = globalVerticalAngle + branchVerticalAngle
            
            centerDir = Quaternion(startPointTangent.cross(data.outwardDir), math.radians(-verticalAngle)) @ data.outwardDir
            
            self.report({'INFO'}, f"in addBranches: angleMode: {branchAngleModeList[0].value}")
            
            if branchAngleModeList[0].value == "WINDING":
                angle = windingAngleList[0].value % (2.0 * rotateAngleRangeList[0].value)
                self.report({'INFO'}, "in addBranches(): angleMode.winding")
                branchDir = Quaternion(startPointTangent, math.radians(-rotateAngleRangeList[0].value + angle)) @ centerDir
                
            if branchAngleModeList[0].value == "SYMMETRIC":
                if branchIndex % 2 == 0:
                    branchDir = Quaternion(startPointTangent, math.radians(-rotateAngleRangeList[0].value)) @ centerDir
                    branchDir = Quaternion(startPointTangent.cross(branchDir), math.radians(verticalAngle - 90.0)) @ branchDir
                else:
                    branchDir = Quaternion(startPointTangent, math.radians(rotateAngleRangeList[0].value)) @ centerDir
                    branchDir = Quaternion(startPointTangent.cross(-branchDir), math.radians(-verticalAngle + 90.0)) @ branchDir 
                
            #rotv = Quaternion(axis, math.radians(angle)) @ v
            
            branchCotangent = Vector((0.0, 0.0, 0.0))            
            #There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem
            
            if branchDir.x != 0.0:
                branchCotangent = Vector((-branchDir.y, branchDir.x, 0.0))
            else:
                if branchDir.y != 0.0:
                    branchCotangent = Vector((0.0, -branchDir.z, branchDir.y))
                else:
                    branchCotangent = Vector((branchDir.z, 0.0, -branchDir.y))
            
            #class node():
            #   def __init__(self, Point, Radius, Cotangent, RingResolution, Taper, TvalGlobal, TvalBranch):
            branch = node(data.startPoint, 1.0, branchCotangent, ringResolution, taper, data.startNode.tValGlobal, 0.0)
            
            branchLength = 0.0
            # if clusterIndex == 0:
            nextIndex = startNodesNextIndexStartTvalEndTval[data.startNodeIndex].nextIndex
            startTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[startNodeNextIndex].tValGlobal, data.t)
            branchLength = treeHeight * relBranchLengthList[0].value * shapeRatio(context, startTvalGlobal)
            
            # TODO
            #lengthToTip = data.startNode.lengthToTip()
            #lengthToTop -= data.t * (data.startNode.next[data.startNodeNextIndex].point - data.startNode.point).length
            #if branchLength > lengthToTip:
            #    branchLength = lengthToTip 
            
            #branch = node(data.startPoint, 1.0, branchCotangent, ringResolution, taper, data.startNode.tValGlobal, 0.0)
            branch.next.append(node(data.startPoint + branchDir * branchLength, 1.0, branchCotangent, ringResolution, taper, data.startNode.tValGlobal, 0.0))
            drawDebugPoint(data.startPoint + branchDir * branchLength)
            
            
def shapeRatio(context, tValGlobal):
    if context.scene.treeShape == "CONICAL":
        return 0.2 + 0.8 * tValGlobal
            

def calculateSegmentLengthsAndTotalLength(startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal):
    #useTvalBranch == False
    totalLength = 0.0
    for i in range(0, len(startNodesNextIndexStartTvalEndTval)):
        segmentLength = 0.0
        if startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex] != None:
            segmentLength = (startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex].point - startNodesNextIndexStartTvalEndTval[i].startNode.point).length
            
        tA_global = startNodesNextIndexStartTvalEndTval[i].startNode.tValGlobal
        tB_global = startNodesNextIndexStartTvalEndTval[i].startNode.next[startNodesNextIndexStartTvalEndTval[i].nextIndex].tValGlobal
        
        segmentLengthAbove = 0.0
        if tA_global > tB_global:
            temp = tA_global
            tA_global = tB_global
            tB_global = temp
            
        if tB_global <= branchesStartHeightGlobal:
            continue
        
        tStart = max(tA_global, branchesStartHeightGlobal)
        tEnd = tB_global
        frac = 0.0
        if tB_global - tA_global != 0.0:
            frac = (tEnd - tStart) / (tB_global - tA_global)
        segmentLengthAbove = segmentLength * frac
        
        segmentLengths.append(segmentLengthAbove)
        totalLength += segmentLengthAbove
            
    return totalLength

def generateStartPointData(self, startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, calledFromAddLeaves):
    accumLength = 0.0
    startNodeIndex = 0
    
    for i in range(len(segmentLengths)):
        if accumLength + segmentLengths[i] >= branchPos:
            startNodeIndex = i
            segStart = accumLength
            segLen = segmentLengths[i]
            t = 0.0
            if segLen > 0.0:
                t = (branchPos - segStart) / segLen
            
            startTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].startTval
            endTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].endTval
            #self.report({'INFO'}, f"startTval: {startTval}, endTval:{endTval}, segmentLength: {segmentLengths[i]}") # startTval: 0.0, endTval:0.2, segmentLength: 6.18

            
            if startTval >= 0.0 and t < startTval:
                t = startTval
            if startTval >= 0.0 and t > endTval:
                t = endTval
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
        t)
    
    nextTangent = (treeGrowDir.normalized() * treeHeight - (rootNode.point + rootNode.tangent[0] * (treeGrowDir.normalized() * treeHeight - rootNode.point).length * (1.5 / 3.0))).normalized()
    
    centerPoint = sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0, 1.0, 0.0)), nextTangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);
    
    outwardDir = outward_dir = lerp(
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, t) - centerPoint
    
    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = lerp(
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent,
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, t)
        
    outwardDir.y = 0.0

    if outwardDir == Vector((0.0, 0.0, 0.0)):
        outwardDir = lerp(
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent,
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent,
            t)
        # print("outward_dir is zero, using cotangent: ", outward_dir)
    outwardDir = outwardDir.normalized()
    
    #self.report({'INFO'}, f"startPoint: {startPoint}")
    drawDebugPoint(startPoint)
    
    
    return startPointData(startPoint, outwardDir, nStart, startNodeIndex, startNodeNextIndex, t, tangent)
    


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
    
    
    
def generateVerticesAndTriangles(self, segments, dir, taper, radius, ringSpacing, stemRingRes):
    vertices = []
    faces = []
    
    offset = 0
    counter = 0
        
    for s in range(0, len(segments)):
        startSection = 0
        
        segmentLength = (segments[s].end - segments[s].start).length
        if segmentLength > 0:
            sections = round(segmentLength / ringSpacing)
            if sections <= 0:
                sections = 1
            branchRingSpacing = segmentLength / sections
            
            if segments[s].connectedToPrevious == True:
                startSection = 1
                #offset -= stemRingRes + 1
            else:
                offset = len(vertices) # ERROR HERE: double splits... !!!
                #self.report({'INFO'}, f"in generateVerticesAndTriangles: connectedToPrevious == False, offset: {offset}")
                
            # double split
            #  ist: 0    8   20   32
            # soll: 0    8   20   32
            
            #  ist: 0   16   24   40   56
            # soll: 0   16   24   40   56
            #       *    *         *         <--- double split not sequentially!
                
            controlPt1 = segments[s].start + segments[s].startTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
            controlPt2 = segments[s].end - segments[s].endTangent.normalized() * (segments[s].end - segments[s].start).length / 3.0
        
            for section in range(startSection, sections + 1):
                pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections)
                tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / sections).normalized()
                dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / sections)
                dirB = (tangent.cross(dirA)).normalized()
                dirA = (dirB.cross(tangent)).normalized()
                
                for i in range(0, segments[s].ringResolution):
                    angle = (2 * math.pi * i) / segments[s].ringResolution
                    x = math.cos(angle)
                    y = math.sin(angle)
                    v = pos + dirA * lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing)) * math.cos(angle) + dirB * lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing)) * math.sin(angle)
                    #self.report({'INFO'}, f"in generateVerticesAndTriangles: vertex.append:  {v}")
                    if v.x < -10.0:
                        self.report({'ERROR'}, f"ERROR: vertex: {v}")
                    vertices.append(v)
                    counter += 1
    
            for c in range(0, sections): 
                for j in range(0, segments[s].ringResolution):
                    faces.append((offset + c * (segments[s].ringResolution) + j,
                        offset + c * (segments[s].ringResolution) + (j + 1) % (segments[s].ringResolution), 
                        offset + c * (segments[s].ringResolution) + segments[s].ringResolution  + (j + 1) % (segments[s].ringResolution), 
                        offset + c * (segments[s].ringResolution) + segments[s].ringResolution  + j))
        
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
    
class floatListProp01(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "floatListProperty01", type=floatProp01)
        
class boolProp(bpy.types.PropertyGroup):
    value: bpy.props.BoolProperty(name = "boolValue", default=False)
    
class parentClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "parentClusterBoolListProperty", type=boolProp)
    show_cluster: bpy.props.BoolProperty(
        name="Show Cluster",
        description="Show/hide parent clusters",
        default=True
    )
    
class branchClusterBoolListProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "branchClusterBoolListProperty", type=boolProp)
    show_branch_cluster: bpy.props.BoolProperty(
        name="Show Branch Cluster",
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
    
class UL_stemSplitLevelList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Level {index}")
        row = layout.row()
        layout.prop(item, "value", text="", slider=True)
    
class addStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_stem_split_level"
    bl_label = "Add split level"
    
    def execute(self, context):
        newSplitHeight = context.scene.stemSplitHeightInLevelList.add()
        newSplitHeight.value = 0.5
        context.scene.stemSplitHeightInLevelListIndex = len(context.scene.stemSplitHeightInLevelList) - 1
        return {'FINISHED'}

class addBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.add_branch_split_level"
    bl_label = "Add split level"
    level: bpy.props.IntProperty()
    
    def execute(self, context):
        newSplitHeight = context.scene.branchSplitHeightInLevelListList[self.level].value.add()
        newSplitHeight = 0.5
        return {'FINISHED'}
    
class removeStemSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_stem_split_level"
    bl_label = "Remove split level"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        if len(context.scene.stemSplitHeightInLevelList) > self.index:
            context.scene.stemSplitHeightInLevelList.remove(self.index)
        return {'FINISHED'}

class removeBranchSplitLevel(bpy.types.Operator):
    bl_idname = "scene.remove_branch_split_level"
    bl_label = "Remove split level"
    level: bpy.props.IntProperty()
        
    def execute(self, context):
        branchSplitHeightInLevelList = context.scene.branchSplitHeightInLevelListList
        if self.level < len(branchSplitHeightInLevelList):
            branchSplitHeightInLevelList[self.level].value.remove(len(branchSplitHeightInLevelList[self.level].value) - 1)
                        
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
        
        branchClusterBoolListList = context.scene.branchClusterBoolListList.add()
                
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
        scene = context.scene
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
        
        box = layout.box()
        row = box.row()
        row.operator("scene.add_stem_split_level", text="Add split level")
        row.operator("scene.remove_stem_split_level", text="Remove").index = scene.stemSplitHeightInLevelListIndex
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
            
            #box.label(text=f"Branch cluster {i}")
            
            
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
                    mode = scene.branchSplitModeList[i].value
                    #self.report({'INFO'}, f"mode: {mode}")
                    if mode == "ROTATE_ANGLE":
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
                
                box.operator("scene.add_branch_split_level", text="Add split level").level = i
                box.operator("scene.remove_branch_split_level", text="Remove split level").level = i
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
    bpy.utils.register_class(floatListProp01)
    bpy.utils.register_class(boolProp)
    bpy.utils.register_class(parentClusterBoolListProp)
    bpy.utils.register_class(branchClusterBoolListProp)
    
    #operators
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(toggleBool)
    bpy.utils.register_class(addStemSplitLevel)
    bpy.utils.register_class(removeStemSplitLevel)
    bpy.utils.register_class(addBranchSplitLevel)
    bpy.utils.register_class(removeBranchSplitLevel)
    bpy.utils.register_class(generateTree)
    
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    bpy.utils.register_class(treeSettings)
    bpy.utils.register_class(noiseSettings)
    bpy.utils.register_class(splitSettings)
    bpy.utils.register_class(branchSettings)
    #bpy.utils.register_class(parentClusterPanel)
    
    #UILists
    bpy.utils.register_class(UL_stemSplitLevelList)
    bpy.types.Scene.UL_stemSplitLevelListIndex = bpy.props.IntProperty(default = 0)
          
    #collections
    bpy.types.Scene.stemSplitHeightInLevelList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.stemSplitHeightInLevelListIndex = bpy.props.IntProperty(default = 0)
    
    bpy.types.Scene.parentClusterBoolList = bpy.props.CollectionProperty(type=boolProp)
    bpy.types.Scene.parentClusterBoolListList = bpy.props.CollectionProperty(type=parentClusterBoolListProp)
    bpy.types.Scene.branchClusterBoolListList = bpy.props.CollectionProperty(type=branchClusterBoolListProp)
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
    bpy.types.Scene.branchesStartHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesEndHeightGlobalList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesStartHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchesEndHeightClusterList = bpy.props.CollectionProperty(type=floatProp01)
    bpy.types.Scene.branchCurvatureList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.nrSplitsPerBranchList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.splitsPerBranchVariationList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitHeightVariationList = bpy.props.CollectionProperty(type=floatProp)
    bpy.types.Scene.branchSplitHeightInLevelListList = bpy.props.CollectionProperty(type=floatListProp01)
        
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