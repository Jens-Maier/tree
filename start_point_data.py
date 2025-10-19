from mathutils import Vector, Quaternion
import math

from . import treegen_utils_


class StartPointData():
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
        
    @staticmethod
    def generateStartPointData(self, 
                           startNodesNextIndexStartTvalEndTval, 
                           segmentLengths, 
                           branchPos, 
                           treeGrowDir, 
                           rootNode, 
                           treeHeight, 
                           calledFromAddLeaves):
        #self.report({'INFO'}, "---------------------------------------------")
        #self.report({'INFO'}, "in generateStartPointData()")
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
        
        startPoint = treegen_utils_.treegen_utils.sampleSplineT(
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point,
            tangent,
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].tangent[0], 
            tVal)
        
        nextTangent = (treeGrowDir.normalized() * treeHeight - (rootNode.point + rootNode.tangent[0] *  (treeGrowDir.normalized() * treeHeight - rootNode.point).length * (1.5 / 3.0))).normalized()
        
        centerPoint = treegen_utils_.treegen_utils.sampleSplineT(rootNode.point, treeGrowDir.normalized() * treeHeight, Vector((0.0, 0.0, 1.0)), nextTangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);
        
        startPointCotangent = treegen_utils_.treegen_utils.lerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent,            
            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, tVal)
        
        outwardDir = treegen_utils_.treegen_utils.lerp(
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
        startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal) - centerPoint
        
        if outwardDir == Vector((0.0, 0.0, 0.0)):
            outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent
            
        outwardDir.z = 0.0
    
        if outwardDir == Vector((0.0, 0.0, 0.0)):
            outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent
            
        outwardDir = outwardDir.normalized()
        
        #self.report({'INFO'}, f"in generateStartPointData(): outwardDir: {outwardDir}")
        return StartPointData(startPoint, startPointTvalGlobal, outwardDir, nStart, startNodeIndex, startNodeNextIndex, tVal, tangent, startPointCotangent)
    
    @staticmethod
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
    
    def register():
        print("in startPointData: register")

    def unregister():
        print("in startPointData: unregister")

    
    
class DummyStartPointData():
    def __init__(self):
        self.dummyStartPoints = [] # for all other stems at same height as startPoint
        
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
            dummyStartPointData.append(StartPointData(p, startPointDatum.startPointTvalGlobal, Vector((0.0,0.0,0.0)), None, 0, 0, 0, Vector((0.0,0.0,0.0)), Vector((0.0,0.0,0.0))))
        
        return (dummyStartPointData, centerPoint)


        
    def register():
        print("in DummyStartPointData: register")
    
    def unregister():
        print("in DummyStartPointData: unregister")
        
        
def register():
    print("register StartPointData")
    StartPointData.register()
    DummyStartPointData.register()
    
def unregister():
    StartPointData.unregister()
    DummyStartPointData.unregister()
    print("unregister StartPointData")