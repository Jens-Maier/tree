
using System.Collections.Generic;
using System.Numerics;
using System;
using System.Security.AccessControl;
using System.Security.Cryptography.X509Certificates;
using UnityEngine;
using System.Drawing;
using System.Diagnostics;
using System.Text;

namespace treeGenNamespace
{

    public class segment
    {
        public int clusterIndex;
        public UnityEngine.Vector3 start;
        public UnityEngine.Vector3 end;
        public UnityEngine.Vector3 firstTangent;
        public UnityEngine.Vector3 startTangent;
        public UnityEngine.Vector3 endTangent;
        public UnityEngine.Vector3 startCotangent;
        public UnityEngine.Vector3 endCotangent;
        public float startRadius;
        public float endRadius;
        public float startTvalGlobal;
        public float endTvalGlobal;
        public float startTvalBranch;
        public float endTvalBranch;
        public int ringResolution;
        public bool connectedToPrevious;
        public float branchLength;
        public float longestBranchLengthInCluster;
        public float startTaper;
        public float endTaper;

        public segment(int ClusterIndex, UnityEngine.Vector3 Start, UnityEngine.Vector3 End, UnityEngine.Vector3 FirstTangent, UnityEngine.Vector3 StartTangent, UnityEngine.Vector3 EndTangent, UnityEngine.Vector3 StartCotangent, UnityEngine.Vector3 EndCotangent, float StartRadius, float EndRadius, float StartTvalGlobal, float EndTvalGlobal, float StartTvalBranch, float EndTvalBranch, int RingResolution, bool ConnectedToPrevious, float BranchLength, float LongestBranchLengthInCluster, float StartTaper, float EndTaper)
        {
            clusterIndex = ClusterIndex;
            start = Start;
            end = End;
            firstTangent = FirstTangent;
            startTangent = StartTangent;
            endTangent = EndTangent;
            startCotangent = StartCotangent;
            endCotangent = EndCotangent;
            startRadius = StartRadius;
            endRadius = EndRadius;
            startTvalGlobal = StartTvalGlobal;
            endTvalGlobal = EndTvalGlobal;
            startTvalBranch = StartTvalBranch;
            endTvalBranch = EndTvalBranch;
            ringResolution = RingResolution;
            connectedToPrevious = ConnectedToPrevious;
            branchLength = BranchLength;
            longestBranchLengthInCluster = LongestBranchLengthInCluster;
            startTaper = StartTaper;
            endTaper = EndTaper;
        }
    }

    public class startNodeInfo
    {
        public node startNode;
        public int nextIndex;
        public float startTval;
        public float endTval;
        public float startTvalGlobal;
        public float endTvalGlobal;

        public startNodeInfo(node StartNode, int NextIndex, float StartTval, float EndTval, float StartTvalGlobal, float EndTvalGlobal)
        {
            startNode = StartNode;
            nextIndex = NextIndex;
            startTval = StartTval;
            endTval = EndTval;
            startTvalGlobal = StartTvalGlobal;
            endTvalGlobal = EndTvalGlobal;
        }
    }

    public class StartPointData
    {
        public UnityEngine.Vector3 startPoint;
        public float startPointTvalGlobal;
        public UnityEngine.Vector3 outwardDir;
        public node startNode;
        public int startNodeIndex;
        public int startNodeNextIndex;
        public float t;
        public UnityEngine.Vector3 tangent;
        public UnityEngine.Vector3 cotangent;
        public float rotateAngleRange;

        public StartPointData(UnityEngine.Vector3 StartPoint, float StartPointTvalGlobal, UnityEngine.Vector3 OutwardDir, node StartNode, int StartNodeIndex, int StartNodeNextIndex, float T, UnityEngine.Vector3 Tangent, UnityEngine.Vector3 Cotangent)
        {
            startPoint = StartPoint;
            startPointTvalGlobal = StartPointTvalGlobal;
            outwardDir = OutwardDir;
            startNode = StartNode;
            startNodeIndex = StartNodeIndex;
            startNodeNextIndex = StartNodeNextIndex;
            t = T;
            tangent = Tangent;
            cotangent = Cotangent;
            rotateAngleRange = 0f;
        }
        
        static UnityEngine.Vector3 sampleSplineT(UnityEngine.Vector3 start, UnityEngine.Vector3 end, UnityEngine.Vector3 startTangent, UnityEngine.Vector3 endTangent, float t)
        {
            UnityEngine.Vector3 controlPt1 = start + norm(startTangent) * (end - start).magnitude / 3.0f;
            UnityEngine.Vector3 controlPt2 = end - norm(endTangent) * (end - start).magnitude / 3.0f;
            return (1.0f - t)*(1.0f - t)*(1.0f - t) * start + 3.0f * (1.0f - t)*(1.0f - t) * t * controlPt1 + 3.0f * (1.0f - t) * t*t * controlPt2 + t*t*t * end;
        }

        static UnityEngine.Vector3 norm(UnityEngine.Vector3 v)
        {
            if (v ==  new UnityEngine.Vector3(0f, 0f, 0f))
            {
                return v;
            }
            else
            {
                return v / v.magnitude;
            }
        }

        static float length(UnityEngine.Vector3 v)
        {
            return v.magnitude;
        }

        static UnityEngine.Vector3 lerp(UnityEngine.Vector3 a, UnityEngine.Vector3 b, float t)
        {
            return a + t * (b - a);
        }

        public static StartPointData generateStartPointData(List<startNodeInfo> startNodesNextIndexStartTvalEndTval, List<float> segmentLengths, float branchPos, UnityEngine.Vector3 treeGrowDir, node rootNode, float treeHeight, bool calledFromAddLeaves)
        {
            float accumLength = 0f;
            int startNodeIndex = 0;
            float tVal = 0f;
            float startPointTvalGlobal = 0f;

            for (int i = 0; i < segmentLengths.Count; i++)
            {
                if (accumLength + segmentLengths[i] >= branchPos)
                {
                    startNodeIndex = i;
                    float segStart = accumLength;
                    float segLen = segmentLengths[i];
                    if (segLen > 0f)
                    {
                        tVal = (branchPos - segStart) / segLen;
                    }
                    float startTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].startTval;
                    float endTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].endTval;
                    node startNode = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode;
                    node nextNode = startNode.next[startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex];

                    tVal = startTval + tVal * (endTval - startTval);
                    startPointTvalGlobal = startNode.tValGlobal + tVal * (nextNode.tValGlobal - startNode.tValGlobal);
                    break;
                }
                accumLength += segmentLengths[i];
            }
            int startNodeNextIndex = startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex;
            node nStart = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode;
            UnityEngine.Vector3 tangent = new UnityEngine.Vector3(0f, 0f, 0f);

            if (startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next.Count > 1)
            {
                tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[startNodeNextIndex + 1];
            }
            else
            {
                tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[0];
            }

            UnityEngine.Vector3 startPoint = sampleSplineT(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point, 
                                                    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, 
                                                    tangent,
                                                    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].tangent[0], 
                                                    tVal);

            UnityEngine.Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * length(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));

            UnityEngine.Vector3 centerPoint = sampleSplineT(rootNode.point, norm(treeGrowDir) * treeHeight, new UnityEngine.Vector3(0f, 1f, 0f), nextTangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);

            UnityEngine.Vector3 startPointCotangent = lerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, tVal);

            UnityEngine.Vector3 outwardDir = lerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal) - centerPoint;

            if (outwardDir == new UnityEngine.Vector3(0f, 0f, 0f))
            {
                outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent;
            }

            outwardDir = new UnityEngine.Vector3(outwardDir.x, 0f, outwardDir.z);

            if (outwardDir == new UnityEngine.Vector3(0f, 0f, 0f))
            {
                outwardDir = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent;
            }

            outwardDir = norm(outwardDir);

            return new StartPointData(startPoint, startPointTvalGlobal, outwardDir, nStart, startNodeIndex, startNodeNextIndex, tVal, tangent, startPointCotangent);
        }

        static float getAngle(UnityEngine.Vector3 v)
        {
            float angle = MathF.Atan2(v.z, v.x);
            return (angle + 2f * MathF.PI) % (2f * MathF.PI);
        }

        public static (UnityEngine.Vector3, UnityEngine.Vector3, UnityEngine.Vector3, UnityEngine.Vector3, float, float) findClosestVectors(List<UnityEngine.Vector3> vectors, UnityEngine.Vector3 targetVector)
        {
            float targetAngle = getAngle(targetVector);

            float minClockwiseDiff = 2f * MathF.PI;
            UnityEngine.Vector3 closestClockwiseVector = new UnityEngine.Vector3(0f, 0f, 0f);

            float minAnticlockwiseDiff = 2f * MathF.PI;
            UnityEngine.Vector3 closestAnticlockwiseVector = new UnityEngine.Vector3(0f, 0f, 0f);

            foreach (UnityEngine.Vector3 v in vectors)
            {
                float vectorAngle = getAngle(v);

                // Calculate clockwise difference
                // This handles the wrap-around from 0 to 360
                float clockwiseDiff = (targetAngle - vectorAngle + 2f * MathF.PI) % (2f * MathF.PI);
                if (clockwiseDiff < minClockwiseDiff && clockwiseDiff != 0f)
                {
                    minClockwiseDiff = clockwiseDiff;
                    closestClockwiseVector = v;
                }

                // Calculate anticlockwise difference
                // This also handles the wrap-around
                float anticlockwiseDiff = (vectorAngle - targetAngle + 2f * MathF.PI) % (2f * MathF.PI);
                if (anticlockwiseDiff < minAnticlockwiseDiff && anticlockwiseDiff != 0f)
                {
                    minAnticlockwiseDiff = anticlockwiseDiff;
                    closestAnticlockwiseVector = v;
                }
            }

            // Handle the case where the target vector is not found in the list, but one of the vectors is the same.
            if (closestClockwiseVector == new UnityEngine.Vector3(0f, 0f, 0f))
            {
                closestClockwiseVector = closestAnticlockwiseVector;
            }
            if (closestAnticlockwiseVector == new UnityEngine.Vector3(0f, 0f, 0f))
            {
                closestAnticlockwiseVector = closestClockwiseVector;
            }

            float clockwiseAngleRange = minClockwiseDiff / 2f;
            float anticlockwiseAngleRange = minAnticlockwiseDiff / 2f;

            UnityEngine.Vector3 halfClosestClockwiseVector = UnityEngine.Quaternion.AngleAxis(-clockwiseAngleRange, new UnityEngine.Vector3(0f, 1f, 0f)) * targetVector;
            UnityEngine.Vector3 halfClosestAnticlockwiseVector = UnityEngine.Quaternion.AngleAxis(anticlockwiseAngleRange, new UnityEngine.Vector3(0f, 1f, 0f)) * targetVector;

            return (closestClockwiseVector, closestAnticlockwiseVector, halfClosestClockwiseVector, halfClosestAnticlockwiseVector, clockwiseAngleRange, anticlockwiseAngleRange);
        }
    }

    public class DummyStartPointData
    {
        List<StartPointData> dummyStartPoints = new List<StartPointData>(); 
        // for all other stems at same height as startPoint

        public static (List<StartPointData>, UnityEngine.Vector3) generateDummyStartPointData(node rootNode, StartPointData startPointDatum)
        {
            UnityEngine.Debug.Log("in generateDummyStartPointData()");
            List<UnityEngine.Vector3> parallelPoints = new List<UnityEngine.Vector3>();
            rootNode.getAllParallelStartPoints(startPointDatum.startPointTvalGlobal, startPointDatum.startNode, parallelPoints);

            List<StartPointData> dummyStartPointData = new List<StartPointData>();
            UnityEngine.Vector3 centerPoint = startPointDatum.startPoint;
            int n = 1;
            foreach (UnityEngine.Vector3 p in parallelPoints)
            {
                centerPoint += p;
                n += 1;
            }
            centerPoint = centerPoint / (float)n;

            foreach (UnityEngine.Vector3 p in parallelPoints)
            {
                dummyStartPointData.Add(new StartPointData(p, startPointDatum.startPointTvalGlobal, new UnityEngine.Vector3(0f, 0f, 0f), null, 0, 0, 0f, new UnityEngine.Vector3(0f, 0f, 0f), new UnityEngine.Vector3(0f, 0f, 0f)));
            }
            return (dummyStartPointData, centerPoint);
        }

        
    }

    

    //     # Handle the case where the target vector is not found in the list, but one of the vectors is the same.
    //     if closest_clockwise_vector is None:
    //         closest_clockwise_vector = closest_anticlockwise_vector
    //     if closest_anticlockwise_vector is None:
    //         closest_anticlockwise_vector = closest_clockwise_vector
    //         
    //     clockwise_angle_range = min_clockwise_diff / 2.0
    //     anticlockwise_angle_range = min_anticlockwise_diff / 2.0
    //     #treeGen.report({'INFO'}, f"clockwise_angle_range: {clockwise_angle_range}")
    //     #treeGen.report({'INFO'}, f"anticlockwise_angle_range: {anticlockwise_angle_range}")
    //     
    //     half_closest_clockwise_vector = Quaternion(Vector((0.0,0.0,1.0)), -clockwise_angle_range) @ target_vector
    //     half_closest_anticlockwise_vector = Quaternion(Vector((0.0,0.0,1.0)), anticlockwise_angle_range) @ target_vector
    //     
    //     return closest_clockwise_vector, closest_anticlockwise_vector, half_closest_clockwise_vector, half_closest_anticlockwise_vector, // clockwise_angle_range, anticlockwise_angle_range
    // 
    // def register():
    //     print("in startPointData: register")
// 
    // def unregister():
    //     print("in startPointData: unregister")

    
    
// class DummyStartPointData():
//     def __init__(self):
//         self.dummyStartPoints = [] # for all other stems at same height as startPoint
//         
//     def generateDummyStartPointData(treeGen, rootNode, startPointDatum):
//         
//         #treeGen.report({'INFO'}, "in generateDummyStartPointData()")
//         parallelPoints = []
//         rootNode.getAllParallelStartPoints(treeGen, startPointDatum.startPointTvalGlobal, startPointDatum.startNode, parallelPoints)
//         
//         dummyStartPointData = []
//         centerPoint = Vector(startPointDatum.startPoint)
//         n = 1
//         for p in parallelPoints:
//             centerPoint += p
//             n += 1
//         centerPoint = centerPoint / n
//         
//         for p in parallelPoints:
//             dummyStartPointData.append(StartPointData(p, startPointDatum.startPointTvalGlobal, Vector((0.0,0.0,0.0)), None, 0, 0, 0, Vector((0.0,0.0,0.// 0)), Vector((0.0,0.0,0.0))))
//         
//         return (dummyStartPointData, centerPoint)
// 
// 
//         
//     def register():
//         print("in DummyStartPointData: register")
//     
//     def unregister():
//         print("in DummyStartPointData: unregister")
//         
//         
// def register():
//     print("register StartPointData")
//     StartPointData.register()
//     DummyStartPointData.register()
//     
// def unregister():
//     StartPointData.unregister()
//     DummyStartPointData.unregister()
//     print("unregister StartPointData")

    public class node
    {
        public UnityEngine.Vector3 point;
        public float radius;
        public List<UnityEngine.Vector3> tangent;
        public UnityEngine.Vector3 cotangent;
        public int clusterIndex;
        public int ringResolution;
        public float taper;
        public float tValGlobal;
        public float tValBranch;
        public List<node> next;
        public List<List<node>> branches;
        public float branchLength;
        public bool isLastRotated = false;
        public List<UnityEngine.Vector3> outwardDir;
        public List<float> rotateAngleRange;


        public node(UnityEngine.Vector3 Point, float Radius, UnityEngine.Vector3 Cotangent, int ClusterIndex, int RingResolution, float Taper, float TvalGlobal, float TvalBranch,  float BranchLength)
        {
            point = Point;
            radius = Radius;
            tangent = new List<UnityEngine.Vector3>();
            cotangent = Cotangent;
            clusterIndex = ClusterIndex;
            ringResolution = RingResolution;
            taper = Taper;
            tValGlobal = TvalGlobal;
            tValBranch = TvalBranch;
            next = new List<node>();
            branches = new List<List<node>>();
            branchLength = BranchLength;
            isLastRotated = false;
            outwardDir = new List<UnityEngine.Vector3>();
            rotateAngleRange = new List<float>();
        }

        public void getAllSegments(node rootNode, List<segment> segments, bool connectedToPrev)
        {
            UnityEngine.Debug.Log("in getAllSegments: point: " + point + ", next.Count: " + next.Count);
            //for n, nextNode in enumerate(self.next):
            //    longestBranchLengthInCluster = 1.0
            int n = 0;
            foreach (node nextNode in next)
            {
                if (next.Count > 1)
                {
                    UnityEngine.Debug.Log("next.Count > 1");
                    UnityEngine.Debug.Log("segments count before: " + segments.Count);
                    UnityEngine.Debug.Log("adding segment: point" + point + " (next.Count: " + next.Count + ")");
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[n + 1], // startTangent
                                            nextNode.tangent[0], // endTangent
                                            cotangent, 
                                            nextNode.cotangent, 
                                            radius, 
                                            nextNode.radius, 
                                            tValGlobal, 
                                            nextNode.tValGlobal, 
                                            tValBranch, 
                                            nextNode.tValBranch, 
                                            ringResolution, 
                                            false, 
                                            branchLength, 
                                            1f, // longestBranchLengthInCluster, 
                                            taper, 
                                            nextNode.taper));
                }
                else
                {
                    UnityEngine.Debug.Log("segments count before: " + segments.Count);
                    UnityEngine.Debug.Log("adding segment: point: " + point);
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[0], // startTangent
                                            nextNode.tangent[0], // endTangent
                                            cotangent, 
                                            nextNode.cotangent, 
                                            radius, 
                                            nextNode.radius, 
                                            tValGlobal, 
                                            nextNode.tValGlobal, 
                                            tValBranch, 
                                            nextNode.tValBranch, 
                                            ringResolution, 
                                            connectedToPrev, 
                                            branchLength, 
                                            1f, // longestBranchLengthInCluster, 
                                            taper, 
                                            nextNode.taper));
                }
                UnityEngine.Debug.Log("calling nextNode.getAllSegments(), n = " + n);
                nextNode.getAllSegments(rootNode, segments, true);
                n += 1;
            }
        
            foreach (List<node> branchList in branches)
            {
                foreach (node b in branchList)
                {
                    b.getAllSegments(rootNode, segments, false);
                }
            }
        }

        public void getAllStartNodes(List<startNodeInfo> startNodesNextIndexStartTvalEndTval, 
                                     List<List<startNodeInfo>> branchNodesNextIndexStartTvalEndTval,
                                     int activeBranchIndex, 
                                     float startHeightGlobal, 
                                     float endHeightGlobal, 
                                     float startHeightCluster, 
                                     float endHeightCluster, 
                                     List<List<bool>> parentClusterBoolListList, 
                                     int newClusterIndex)
        {
            
        }

        public void getAllParallelStartPoints(float startPointTvalGlobal, node startNode, List<UnityEngine.Vector3> parallelPoints)
        {
            
        }

        public void resampleSpline(node rootNode, float resampleDistance)
        {
            UnityEngine.Debug.Log("in resampleSpline: point: " + point);
            UnityEngine.Debug.Log("in resampleSpline: next[0].point: " + next[0].point);
            UnityEngine.Debug.Log("in resampleSpline: resampleDistance: " + resampleDistance);
            UnityEngine.Debug.Log("in resampleSpline: next.Count: " + next.Count);

            for (int i = 0; i < next.Count; i++)
            {
                node activeNode = this;
                node startNode = this;
                node nextNode = next[i];

                int resampleNr = (int)MathF.Round((nextNode.point - startNode.point).magnitude / resampleDistance);
                UnityEngine.Debug.Log("activeNode.point: " + activeNode.point);
                UnityEngine.Debug.Log("nextNode.point: " + nextNode.point);
                UnityEngine.Debug.Log("next_i: " + i + ", resampleNr: " + resampleNr + ", startNode.ringResolution: " + startNode.ringResolution);
                if (resampleNr > 1)
                {
                    for (int n = 1; n < resampleNr; n++)
                    {
                        UnityEngine.Vector3 samplePoint;
                        UnityEngine.Vector3 sampleTangent;

                        if (next.Count > 1)
                        {
                            float t = (float)n / resampleNr;
                            UnityEngine.Debug.Log("i = " + i + ", n = " + n + ", spline sample: startNode.point: " + startNode.point + ", nextNode.point: " + nextNode.point + ", startNode.tangent[i + 1]: " + startNode.tangent[i + 1] + ", nextNode.tangent[0]: " + nextNode.tangent[0] + ", n/resampleNr: " + t);
                            samplePoint = sampleSplineT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], (float)n / resampleNr);
                            sampleTangent = sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[i + 1], nextNode.tangent[0], (float)n / resampleNr);
                        }
                        else
                        {
                            samplePoint = sampleSplineT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], (float)n / resampleNr);
                            sampleTangent = sampleSplineTangentT(startNode.point, nextNode.point, startNode.tangent[0], nextNode.tangent[0], (float)n / resampleNr);
                        }

                        UnityEngine.Vector3 sampleCotangent = lerp(startNode.cotangent, nextNode.cotangent, (float)n / resampleNr);
                        float sampleRadius = lerp(startNode.radius, nextNode.radius, (float)n / resampleNr);
                        float sampleTvalGlobal = lerp(startNode.tValGlobal, nextNode.tValGlobal, (float)n / resampleNr);
                        float sampleTvalBranch = lerp(startNode.tValBranch, nextNode.tValBranch, (float)n / resampleNr);
                        //drawDebugPoint(samplePoint, 0.4)

                        UnityEngine.Debug.Log("n = " + n + ", sample point: " + samplePoint);

                        node newNode = new node(samplePoint, sampleRadius, sampleCotangent, startNode.clusterIndex, startNode.ringResolution, taper, sampleTvalGlobal, sampleTvalBranch, startNode.branchLength);
                        newNode.tangent.Add(sampleTangent);
                        //newNode.connectedToPrevious = true;
                        if (n == 1)
                        {
                            activeNode.next[i] = newNode;
                        }
                        else
                        {
                            activeNode.next.Add(newNode);
                        }
                        activeNode = newNode;
                    }

                    activeNode.next.Add(nextNode);
                    //drawDebugPoint(nextNode.point, 0.1) #OK
                    //treeGen.report({'INFO'}, f"in resampleSpline: len(Next.next): {len(Next.next)}")
                }

                if (nextNode.next.Count > 0)
                {
                    nextNode.resampleSpline(rootNode, resampleDistance);
                }
            }

        }

        static UnityEngine.Vector3 sampleSplineT(UnityEngine.Vector3 start, UnityEngine.Vector3 end, UnityEngine.Vector3 startTangent, UnityEngine.Vector3 endTangent, float t)
        {
            UnityEngine.Vector3 controlPt1 = start + norm(startTangent) * (end - start).magnitude / 3.0f;
            UnityEngine.Vector3 controlPt2 = end - norm(endTangent) * (end - start).magnitude / 3.0f;
            return (1.0f - t)*(1.0f - t)*(1.0f - t) * start + 3.0f * (1.0f - t)*(1.0f - t) * t * controlPt1 + 3.0f * (1.0f - t) * t*t * controlPt2 + t*t*t * end;
        }

        static UnityEngine.Vector3 sampleSplineTangentT(UnityEngine.Vector3 start, UnityEngine.Vector3 end, UnityEngine.Vector3 startTangent, UnityEngine.Vector3 endTangent, float t)
        {
            UnityEngine.Vector3 controlPt1 = start + norm(startTangent) * length(end - start) / 3.0f;
            UnityEngine.Vector3 controlPt2 = end - norm(endTangent) * length(end - start) / 3.0f;
            return norm(-3.0f * (1.0f - t) * (1.0f - t) * start + 3.0f * (3.0f * t*t - 4.0f * t + 1.0f) * controlPt1 + 3.0f * (-3.0f * t*t + 2.0f * t) * controlPt2 + 3.0f * t*t * end);
        }

        static float length(UnityEngine.Vector3 v)
        {
            return v.magnitude;
        }

        static UnityEngine.Vector3 norm(UnityEngine.Vector3 v)
        {
            if (v ==  new UnityEngine.Vector3(0f, 0f, 0f))
            {
                return v;
            }
            else
            {
                return v / v.magnitude;
            }
        }

        static UnityEngine.Vector3 lerp(UnityEngine.Vector3 a, UnityEngine.Vector3 b, float t)
        {
            return a + t * (b - a);
        }

        static float lerp(float a, float b, float t)
        {
            return a + t * (b - a);
        }

        

        public void attractOutward(float outwardAttraction, UnityEngine.Vector3 outwardDir)
        {
            
        }

        public void applyCurvature(node rootNode, 
                                   UnityEngine.Vector3 treeGrowDir, 
                                   float treeHeight, 
                                   float branchGlobalCurvatureStart, 
                                   float branchCurvatureStart,
                                   float branchGlobalCurvatureEnd, 
                                   float branchCurvatureEnd,
                                   int clusterIndex,
                                   UnityEngine.Vector3 point,
                                   float reducedCurveStepCutoff,
                                   float reducedCurveStepFactor)
        {
            
        }
    }

    public class treeGenerator : MonoBehaviour
    {
        public treeSettings settings;
        public List<node> nodes;

        public List<segment> segments;

        public List<UnityEngine.Vector3> vertices = new List<UnityEngine.Vector3>();
        public List<UnityEngine.Vector3> normals = new List<UnityEngine.Vector3>();
        public List<float> vertexTvalGlobal = new List<float>();
        public List<float> vertexTvalBranch = new List<float>();
        public List<float> ringAngle = new List<float>();
        public List<int> triangles = new List<int>();

        public Mesh mesh;


        public void generateTree()
        {
            UnityEngine.Debug.Log("generateTree() in treeGenerator.cs");
            //settings = new treeSettings();
            nodes = new List<node>();
            nodes.Add(new node(new UnityEngine.Vector3(0f, 0f, 0f), 
                               0.1f, 
                               new UnityEngine.Vector3(1f, 0f, 0f), 
                               -1, 
                               settings.stemRingResolution, 
                               settings.taper, 
                               0f, 
                               0f, 
                               settings.treeHeight));
    
            nodes[0].tangent.Add(new UnityEngine.Vector3(0f, 1f, 0f));
            nodes[0].cotangent = new UnityEngine.Vector3(1f, 0f, 0f);
    
            nodes.Add(new node(settings.treeGrowDir * settings.treeHeight, 
                               0.1f, 
                               new UnityEngine.Vector3(1f, 0f, 0f), 
                               -1, 
                               settings.stemRingResolution, 
                               settings.taper, 
                               1.0f, 
                               0.0f, 
                               settings.treeHeight));
            
            nodes[1].tangent.Add(new UnityEngine.Vector3(0f, 1f, 0f));
            nodes[1].cotangent = new UnityEngine.Vector3(1f, 0f, 0f);

            nodes[0].next.Add(nodes[1]);

            UnityEngine.Debug.Log("settings.treeGrowDir: " + settings.treeGrowDir);
            UnityEngine.Debug.Log("settings.treeHeight: " + settings.treeHeight);

            foreach (node n in nodes)
            {
                UnityEngine.Debug.Log("node: point: " + n.point);
            }

            if (settings.nrSplits > 0)
            {
                int maxSplitHeightUsed = splitRecursive(nodes[0], 
                                                        settings.nrSplits,
                                                        settings.stemSplitAngle, 
                                                        settings.stemSplitPointAngle, 
                                                        settings.variance,
                                                        settings.stemSplitHeightInLevel,
                                                        settings.splitHeightVariation,
                                                        settings.splitLengthVariation,
                                                        settings.stemSplitMode, 
                                                        settings.stemSplitRotateAngle,
                                                        settings.stemRingResolution, 
                                                        settings.curvOffsetStrength, 
                                                        nodes[0]);

                if (settings.maxSplitHeightUsed < maxSplitHeightUsed)
                {
                    settings.maxSplitHeightUsed = maxSplitHeightUsed;
                }
            }

            nodes[0].resampleSpline(nodes[0], settings.resampleDistance);

            calculateRadius(nodes[0], 100.0f, settings.branchTipRadius);

            segments = new List<segment>();
            nodes[0].getAllSegments(nodes[0], segments, false);

            foreach (segment s in segments)
            {
                UnityEngine.Debug.Log("segment: start: " + s.start + ", connected: " + s.connectedToPrevious);
                UnityEngine.Debug.Log("segment: end: " + s.end);
            }

            generateVerticesAndTriangles(segments, settings.ringSpacing, settings.branchTipRadius);

            mesh = new Mesh();
            mesh.vertices = vertices.ToArray();
            mesh.triangles = triangles.ToArray();
            mesh.normals = normals.ToArray();
            UnityEngine.Debug.Log("vertices count: " + vertices.Count);
            UnityEngine.Debug.Log("triangles count: " + triangles.Count);

            GetComponent<MeshFilter>().mesh = mesh;
        }

        float calculateRadius(node activeNode, float maxRadius, float branchTipRadius)
        {
            if (activeNode.next.Count > 0 || activeNode.branches.Count > 0)
            {
                float sum = 0f;
                if (activeNode.next.Count > 0)
                {
                    float max = 0f;
                    foreach (node n in activeNode.next)
                    {
                        float s = calculateRadius(n, maxRadius, branchTipRadius);
                        s += (n.point - activeNode.point).magnitude * activeNode.taper * activeNode.taper;
                        if (s > max)
                        {
                            max = s;
                        }
                    }
                    sum = max;
                }
                if (activeNode.branches.Count > 0)
                {
                    foreach (List<node> c in activeNode.branches)
                    {
                        foreach (node n in c)
                        {
                            calculateRadius(n, sum, branchTipRadius);
                        }
                    }
                }
                    
                if (sum < maxRadius)
                {
                    activeNode.radius = sum;
                }
                else
                {
                    activeNode.radius = maxRadius;
                }
                return sum;
            }
            else
            {
                activeNode.radius = branchTipRadius;
                return branchTipRadius;
            }
        }

        int splitRecursive(node startNode, 
                            int nrSplits,
                            float stemSplitAngle, 
                            float stemSplitPointAngle, 
                            float variance,
                            List<float> splitHeightInLevel,
                            float splitHeightVariation,
                            float splitLengthVariation,
                            int stemSplitMode, 
                            float stemSplitRotateAngle,
                            int stemRingResolution, 
                            float curvOffsetStrength,
                            node rootNode)
        {
            while (splitHeightInLevel.Count < nrSplits)
            {
                splitHeightInLevel.Add(0.5f);
            }
            
            float[] splitProbabilityInLevel = new float[nrSplits];
            for (int i = 0; i < nrSplits; i++)
            {
                splitProbabilityInLevel[i] = 0f;
            }
            int[] expectedSplitsInLevel = new int[nrSplits];
            for (int i = 0; i < nrSplits; i++)
            {
                expectedSplitsInLevel[i] = 0;
            }

            int meanLevel = (int)Mathf.Log(nrSplits, 2f);
            if (meanLevel == 0)
            {
                meanLevel = 1;
            }

            if (nrSplits > 0)
            {
                splitProbabilityInLevel[0] = 1.0f;
                expectedSplitsInLevel[0] = 1;
            }
            else
            {
                splitProbabilityInLevel[0] = 0.0f;
                expectedSplitsInLevel[0] = 1;
            }

            for (int i = 1; i < (int)MathF.Round(meanLevel - variance * meanLevel); i++)
            {
                splitProbabilityInLevel[i] = 1.0f;
                expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2.0f * expectedSplitsInLevel[i - 1]);
            }

            if ((int)MathF.Round(meanLevel - variance * meanLevel) > 0)
            {
                for (int i = (int)MathF.Round(meanLevel - variance * meanLevel); i < (int)MathF.Round(meanLevel + variance * meanLevel); i++)
                {
                    splitProbabilityInLevel[i] = 1.0f - (7.0f / 8.0f) * (i - (int)MathF.Round(meanLevel - variance * meanLevel)) / (
                        MathF.Round(meanLevel + variance * meanLevel) - MathF.Round(meanLevel - variance * meanLevel));
                    expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2.0f * expectedSplitsInLevel[i - 1]);
                }
                for (int i = (int)MathF.Round(meanLevel + variance * meanLevel); i < nrSplits; i++)
                {
                    splitProbabilityInLevel[i] = 1.0f / 8.0f;
                    expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2.0f * expectedSplitsInLevel[i - 1]);
                }
            }
            if (nrSplits == 2)
            {
                expectedSplitsInLevel[0] = 1;
                expectedSplitsInLevel[1] = 1;
            }

            int addToLevel = 0;
            int maxPossibleSplits = 1;
            int totalExpectedSplits = 0;
            for (int i = 0; i < nrSplits; i++)
            {
                totalExpectedSplits += expectedSplitsInLevel[i];
                if (expectedSplitsInLevel[i] < maxPossibleSplits)
                {
                    addToLevel = i;
                    break;
                }
                maxPossibleSplits *= 2;
            }
            int addAmount = nrSplits - totalExpectedSplits;

            if (addAmount > 0)
            { 
                expectedSplitsInLevel[addToLevel] += addAmount < maxPossibleSplits - expectedSplitsInLevel[addToLevel] ? addAmount : maxPossibleSplits - expectedSplitsInLevel[addToLevel];
            }

            splitProbabilityInLevel[addToLevel] = (float)expectedSplitsInLevel[addToLevel] / (float)maxPossibleSplits;

            List<List<(node, int)>> nodesInLevelNextIndex = new List<List<(node, int)>>();
            for (int i = 0; i < nrSplits + 1; i++)
            {
                nodesInLevelNextIndex.Add(new List<(node, int)>());
            }
            for (int n = 0; n < startNode.next.Count; n++)
            {
                nodesInLevelNextIndex[0].Add((startNode, n));
            }

            int maxSplitHeightUsed = 0;

            int totalSplitCounter = 0;
            for (int level = 0; level < nrSplits; level++)
            {
                int splitsInLevel = 0;
                int safetyCounter = 0;

                List<int> nodeIndices = new List<int>();
                for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
                {
                    nodeIndices.Add(i);
                }

                while (splitsInLevel < expectedSplitsInLevel[level])
                {
                    if (nodeIndices.Count == 0)
                    {
                        break;
                    }
                    if (totalSplitCounter == nrSplits)
                    {
                        break;
                    }
                    float r = UnityEngine.Random.Range(0f, 1f);
                    float h = UnityEngine.Random.Range(0f, 1f) - 0.5f;
                    if (r <= splitProbabilityInLevel[level])
                    {
                        int indexToSplit = UnityEngine.Random.Range(0, nodeIndices.Count);
                        if (nodeIndices.Count > indexToSplit)
                        {
                            float splitHeight = splitHeightInLevel[level];
                            if (h * splitHeight < 0)
                            {
                                splitHeight = MathF.Max(splitHeight + h * splitHeightVariation, 0.05f);
                            }
                            else
                            {
                                splitHeight = MathF.Min(splitHeight + h * splitHeightVariation, 0.95f);
                            }
                            if (level > maxSplitHeightUsed)
                            {
                                maxSplitHeightUsed = level;
                            }
                            node splitNode = split(
                                nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1,
                                nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item2,
                                splitHeight, 
                                splitLengthVariation, 
                                stemSplitAngle, 
                                stemSplitPointAngle, 
                                level, 
                                stemSplitMode, 
                                stemSplitRotateAngle,
                                0.0f, 
                                stemRingResolution, 
                                curvOffsetStrength, 
                                rootNode);

                            nodeIndices.RemoveAt(indexToSplit);
                            nodesInLevelNextIndex[level + 1].Add((splitNode, 0));
                            nodesInLevelNextIndex[level + 1].Add((splitNode, 1));
                            splitsInLevel += 1;
                            totalSplitCounter += 1;
                        }
                    }
                    safetyCounter += 1;
                    if (safetyCounter > 500)
                    {
                        UnityEngine.Debug.Log("iteration 500 reached -> break!");
                        break;
                    }
                }
            }
            return maxSplitHeightUsed;
        }

        node split(node startNode, 
                   int nextIndex, 
                   float splitHeight, 
                   float splitLengthVariation,
                   float splitAngle, 
                   float splitPointAngle, 
                   int level, 
                   int mode, 
                   float rotationAngle, 
                   float branchSplitAxisVariation, 
                   int stemRingResolution, 
                   float curvOffsetStrength, 
                   node rootNode)
        {
            if (startNode.next.Count > 0 && nextIndex < startNode.next.Count)
            {
                UnityEngine.Debug.Log("before calling nodesToTip()");
                int nrNodesToTip = nodesToTip(startNode.next[nextIndex], 0); // .next???
                UnityEngine.Debug.Log("result int nrNodesToTip: " + nrNodesToTip);
                if (splitHeight > 0.999f)
                {
                    splitHeight = 0.999f;
                }
                int splitAfterNodeNr = (int)(nrNodesToTip * splitHeight);
                UnityEngine.Debug.Log("in split(): nrNodesToTip: " + nrNodesToTip);
                
                if (nrNodesToTip > 0)
                {
                    // Split at existing node if close enough
                    if (nrNodesToTip * splitHeight - splitAfterNodeNr < 0.1f)
                    {
                        node splitNode = startNode;
                        for (int i = 0; i < splitAfterNodeNr; i++)
                        {
                            if (i == 0)
                            {
                                splitNode = splitNode.next[nextIndex];
                                nextIndex = 0;
                            }
                            else
                            {
                                splitNode = splitNode.next[0];
                            }
                        }
                        if (splitNode != startNode)
                        {
                            calculateSplitData(splitNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, splitNode.outwardDir);
                        }
                        else
                        {
                            // -> split at new node!!!
                            return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength);
                        }
                    }
                    else
                    {
                        return splitAtNewNode(nrNodesToTip, splitAfterNodeNr, startNode, nextIndex, splitHeight, splitLengthVariation, splitAngle, splitPointAngle, level, mode, rotationAngle, branchSplitAxisVariation, stemRingResolution, curvOffsetStrength);
                    }
                }
                
            }
            return startNode;
        }

        int nodesToTip(node n, int i)
        {
            if (n.next.Count > 0)
            {
                UnityEngine.Debug.Log("in nodesToTip(): i: " + i);
                if (i > 500)
                {
                    UnityEngine.Debug.Log("ERROR: in nodesToTip(): max iteration reached!");
                    return i;
                }
                return 1 + nodesToTip(n.next[0], i + 1);
            }
            else
            {
                UnityEngine.Debug.Log("in nodesToTip(): return 1");
                return 1;
            }
        }

        node splitAtNewNode(int nrNodesToTip, 
                   int splitAfterNodeNr, 
                   node startNode, 
                   int nextIndex, 
                   float splitHeight, 
                   float splitLengthVariation, 
                   float splitAngle, 
                   float splitPointAngle, 
                   int level, 
                   int mode, 
                   float rotationAngle, 
                   float branchSplitAxisVariation, 
                   int stemRingResolution, 
                   float curvOffsetStrength)
        {
            // Split at new node between two nodes    
            node splitAfterNode = startNode;
            bool splitAtStartNode = true;
            for (int i = 0; i < splitAfterNodeNr; i++)
            {
                if (i == 0)
                {
                    splitAfterNode = splitAfterNode.next[nextIndex];
                    splitAtStartNode = false;
                    nextIndex = 0;
                }
                else
                {
                    splitAfterNode = splitAfterNode.next[0];
                    splitAtStartNode = false;
                }
            }

            int tangentIndex;
            if (splitAtStartNode == true && startNode.next.Count > 1)
            {
                tangentIndex = nextIndex + 1;
            }
            else
            {
                tangentIndex = nextIndex;
            }

            // Interpolate position and attributes for the new node
            float t = (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr;
            UnityEngine.Vector3 p0 = splitAfterNode.point;
            UnityEngine.Vector3 p1 = splitAfterNode.next[nextIndex].point;
            UnityEngine.Vector3 t0 = splitAfterNode.tangent[tangentIndex];
            UnityEngine.Vector3 t1 = splitAfterNode.next[nextIndex].tangent[0];
            UnityEngine.Vector3 c0 = splitAfterNode.cotangent;
            UnityEngine.Vector3 c1 = splitAfterNode.next[nextIndex].cotangent;
            float r0 = splitAfterNode.radius;
            float r1 = splitAfterNode.next[nextIndex].radius;
            int ring_res = splitAfterNode.ringResolution;
            float taper = splitAfterNode.taper;

            UnityEngine.Vector3 newPoint = sampleSplineT(p0, p1, t0, t1, t);
            UnityEngine.Vector3 newTangent = sampleSplineTangentT(p0, p1, t0, t1, t);
            UnityEngine.Vector3 newCotangent = lerp(c0, c1, t);
            float newRadius = lerp(r0, r1, t);
            float newTvalGlobal = lerp(splitAfterNode.tValGlobal, splitAfterNode.next[nextIndex].tValGlobal, nrNodesToTip * splitHeight -       splitAfterNodeNr);

            float newTvalBranch = lerp(splitAfterNode.tValBranch, splitAfterNode.next[nextIndex].tValBranch, splitHeight);

            node newNode = new node(newPoint, newRadius, newCotangent, splitAfterNode.clusterIndex, ring_res, taper, newTvalGlobal, newTvalBranch, splitAfterNode.branchLength);
            newNode.tangent.Add(newTangent);

            // Insert new node in the chain
            newNode.next.Add(splitAfterNode.next[nextIndex]);
            splitAfterNode.next[nextIndex] = newNode;

            newNode.outwardDir = splitAfterNode.outwardDir;

            calculateSplitData(newNode, splitAngle, splitPointAngle, splitLengthVariation, branchSplitAxisVariation, level, mode, rotationAngle, stemRingResolution, curvOffsetStrength, newNode.outwardDir);

            return newNode;
        }

        void calculateSplitData(node splitNode, 
                       float splitAngle, 
                       float splitPointAngle, 
                       float splitLengthVariation, 
                       float branchSplitAxisVariation, 
                       int level, 
                       int sMode, 
                       float rotationAngle, 
                       int stemRingResolution, 
                       float curvOffsetStrength, 
                       List<UnityEngine.Vector3> outwardDir)
        {
            UnityEngine.Debug.Log("in calculateSplitData() splitNode.point: " + splitNode.point);
            node n = splitNode;
            int nodesAfterSplitNode = 0;

            while (n.next.Count > 0)
            {
                nodesAfterSplitNode += 1;
                n = n.next[0];
            }

            // Initialize splitAxis
            UnityEngine.Vector3 splitAxis = new UnityEngine.Vector3(0f, 0f, 0f);

            // public enum splitMode
            // {
            //     rotateAngle,
            //     horizontal
            // }

            if (sMode == 1) // "HORIZONTAL":
            {
                UnityEngine.Vector3 right = UnityEngine.Vector3.Cross(splitNode.tangent[0],new UnityEngine.Vector3(0.0f, 0.0f, 1.0f));
                splitAxis = UnityEngine.Vector3.Cross(right,norm(splitNode.tangent[0]));
                splitAxis = UnityEngine.Quaternion.AngleAxis(UnityEngine.Random.Range(-branchSplitAxisVariation, branchSplitAxisVariation), splitNode.tangent[0]) * splitAxis;

                //splitAxis = Quaternion(splitNode.tangent[0], random.uniform(-branchSplitAxisVariation, branchSplitAxisVariation)) @ splitAxis
            }
            else
            {
                if (sMode == 0) //"ROTATE_ANGLE":
                {
                    splitAxis = norm(splitNode.cotangent);
                    splitAxis = norm(UnityEngine.Quaternion.AngleAxis(rotationAngle * level, splitNode.tangent[0]) * splitAxis);
                }
                else
                {
                    UnityEngine.Debug.LogError("ERROR: invalid splitMode: " + sMode);
                    splitAxis = norm(splitNode.cotangent);
                    if (level % 2 == 1)
                    {
                        splitAxis = norm(UnityEngine.Quaternion.AngleAxis(MathF.PI / 2.0f, splitNode.tangent[0]) * splitAxis);
                    }
                }
            }

            UnityEngine.Vector3 splitDirA = norm(UnityEngine.Quaternion.AngleAxis(splitPointAngle, splitAxis) * splitNode.tangent[0]);
            UnityEngine.Vector3 splitDirB = norm(UnityEngine.Quaternion.AngleAxis(-splitPointAngle, splitAxis) * splitNode.tangent[0]);

            splitNode.tangent.Add(splitDirA);
            splitNode.tangent.Add(splitDirB);

            node s = splitNode;
            node previousNodeA = splitNode;
            node previousNodeB = splitNode;
            UnityEngine.Vector3 curv_offset = norm(splitNode.tangent[0]) * length(s.next[0].point - s.point) * (splitAngle / 360.0f) * curvOffsetStrength;
            s.outwardDir = outwardDir;

            for (int i = 0; i < nodesAfterSplitNode; i++)
            {
                s = s.next[0];
                UnityEngine.Vector3 rel_pos = s.point - splitNode.point;
                s.outwardDir = outwardDir;

                UnityEngine.Vector3 tangent_a = norm(UnityEngine.Quaternion.AngleAxis(splitAngle, splitAxis) * s.tangent[0]);
                UnityEngine.Vector3 tangent_b = norm(UnityEngine.Quaternion.AngleAxis(-splitAngle, splitAxis) * s.tangent[0]);
                UnityEngine.Vector3 cotangent_a = norm(UnityEngine.Quaternion.AngleAxis(splitAngle, splitAxis) * s.cotangent);
                UnityEngine.Vector3 cotangent_b = norm(UnityEngine.Quaternion.AngleAxis(-splitAngle, splitAxis) * s.cotangent);

                UnityEngine.Vector3 offset_a = UnityEngine.Quaternion.AngleAxis(splitAngle, splitAxis) * rel_pos;
                offset_a = offset_a * (1.0f + UnityEngine.Random.Range(-1.0f, 1.0f) * splitLengthVariation);
                UnityEngine.Vector3 offset_b = UnityEngine.Quaternion.AngleAxis(-splitAngle, splitAxis) * rel_pos;
                offset_b = offset_b * (1.0f + UnityEngine.Random.Range(-1.0f, 1.0f) * splitLengthVariation);

                int ring_resolution = stemRingResolution;

                node nodeA = new node(splitNode.point + offset_a + curv_offset, 1.0f, cotangent_a, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength);
                nodeA.tangent.Add(tangent_a);
                node nodeB = new node(splitNode.point + offset_b + curv_offset, 1.0f, cotangent_b, s.clusterIndex, ring_resolution, s.taper, s.tValGlobal, s.tValBranch, s.branchLength);
                nodeB.tangent.Add(tangent_b);

                if (i == 0)
                {
                    splitNode.next[0] = nodeA;
                    splitNode.next.Add(nodeB);
                    previousNodeA = nodeA;
                    previousNodeB = nodeB;
                }
                else
                {
                    previousNodeA.next.Add(nodeA);
                    previousNodeB.next.Add(nodeB);
                    previousNodeA = nodeA;
                    previousNodeB = nodeB;
                }
            }
        }

        void addBranches(
            float resampleDistance,
            node rootNode, 
            int branchClusters,

            List<branchClusterSettings> branchClusterSettingsList,

            List<List<bool>> parentClusterBoolListList, 

            UnityEngine.Vector3 treeGrowDir, 
            float treeHeight, 
            float taper, 
            List<float> taperFactorList, 

            List<List<float>> branchSplitHeightInLevelListList) //,
            //noiseGenerator):
            {
            //treeGen.report({'INFO'}, f"in addBranches(): branchClusters: {branchClusters}")
            
            for (int clusterIndex = 0; clusterIndex < branchClusters; clusterIndex++)
            {
                int nrBranches = branchClusterSettingsList[clusterIndex].nrBranches;
                float branchesStartHeightGlobal = branchClusterSettingsList[clusterIndex].branchesStartHeightGlobal;
                float branchesEndHeightGlobal = branchClusterSettingsList[clusterIndex].branchesEndHeightGlobal;
                float branchesStartHeightCluster = branchClusterSettingsList[clusterIndex].branchesStartHeightCluster;
                float branchesEndHeightCluster = branchClusterSettingsList[clusterIndex].branchesEndHeightCluster;
                float branchesStartPointVariation = branchClusterSettingsList[clusterIndex].branchesStartPointVariation;
                
                List<startNodeInfo> startNodesNextIndexStartTvalEndTval = new List<startNodeInfo>();
                List<List<startNodeInfo>> branchNodesNextIndexStartTvalEndTval = new List<List<startNodeInfo>>();
                List<node> branchNodes = new List<node>();
                List<UnityEngine.Vector3> centerDirs = new List<UnityEngine.Vector3>();

                for (int i = 0; i < branchClusterSettingsList[clusterIndex].nrBranches; i++)
                {
                    branchNodesNextIndexStartTvalEndTval.Add(new List<startNodeInfo>());
                }
                
                if (parentClusterBoolListList.Count > 0)
                {
                    rootNode.getAllStartNodes(
                        startNodesNextIndexStartTvalEndTval, 
                        branchNodesNextIndexStartTvalEndTval,
                        -1, 
                        branchesStartHeightGlobal, 
                        branchesEndHeightGlobal, 
                        branchesStartHeightCluster, 
                        branchesEndHeightCluster, 
                        parentClusterBoolListList, 
                        clusterIndex);
                }
                
                //treeGen.report({'INFO'}, f"in addBranches(): len(startNodes): {len(startNodesNextIndexStartTvalEndTval)}")   
                if (startNodesNextIndexStartTvalEndTval.Count > 0)
                {
                    List<float> segmentLengths = new List<float>();
                    
                    float totalLength = calculateSegmentLengthsAndTotalLength(startNodesNextIndexStartTvalEndTval, segmentLengths, branchesStartHeightGlobal, branchesEndHeightGlobal, branchesStartHeightCluster, branchesEndHeightCluster);
                    
                    UnityEngine.Debug.Log("in addBranches(): totalLength: " + totalLength);
            
                    List<StartPointData> startPointData = new List<StartPointData>();
                    List<float> branchPositions = new List<float>();
                    
                    for (int branchIndex = 0; branchIndex < nrBranches; branchIndex++)
                    {
                        float branchPos = branchIndex * totalLength / nrBranches + UnityEngine.Random.Range(-branchesStartPointVariation, branchesStartPointVariation);
                        if (branchPos < 0f)
                        {
                            branchPos = 0f;
                        }
                        if (branchPos > totalLength)
                        {
                            branchPos = totalLength;
                        }
                        branchPositions.Add(branchPos);
                        startPointData.Add(StartPointData.generateStartPointData(startNodesNextIndexStartTvalEndTval, segmentLengths, branchPos, treeGrowDir, rootNode, treeHeight, false));
                    }

                    //treeGen.report({'INFO'}, "before sorting:")
                    //for data in startPointData:
                    //    treeGen.report({'INFO'}, f"outwardDir: {data.outwardDir}")
                    
                    //startPointData.sort(key=lambda x: x.startPointTvalGlobal)
                    startPointData.Sort((a, b) => a.startPointTvalGlobal.CompareTo(b.startPointTvalGlobal));

            
                    //#treeGen.report({'INFO'}, "after sorting:")
                    //#for n, data in enumerate(startPointData):
                    //#    treeGen.report({'INFO'}, f"startPointData[{n}].outwardDir: {data.outwardDir}")
                    
                    List<List<StartPointData>> dummyStartPointData = new List<List<StartPointData>>();
                    List<UnityEngine.Vector3> centerPoints = new List<UnityEngine.Vector3>();
                    List<float> rightRotationRange = new List<float>();
                    List<float> leftRotationRange = new List<float>();
                    foreach (StartPointData data in startPointData)
                    {
                        (List<StartPointData> dummyData, UnityEngine.Vector3 centerPoint) = DummyStartPointData.generateDummyStartPointData(rootNode, data);
                        dummyStartPointData.Add(dummyData);
                        centerPoints.Add(centerPoint);
                        // generates all parallel start points for one startPoint
                    }
                    // -> calculate outwardDir per startPoint startPointData.outwardDir
                    
                    // calculate right and left dummy neighbor
                    for (int n = 0; n < dummyStartPointData.Count; n++) // n: branchIndex
                    {
                        // -> calculate rotate angle range per startPoint
                        float startPointAngle = MathF.Atan2(startPointData[n].outwardDir.x, startPointData[n].outwardDir.z);

                        List<UnityEngine.Vector3> directions = new List<UnityEngine.Vector3>();
                        foreach (StartPointData data in dummyStartPointData[n])
                        {
                            directions.Add(new UnityEngine.Vector3((data.startPoint - centerPoints[n]).x, (data.startPoint - centerPoints[n]).z, 0f));
                        }

                        (UnityEngine.Vector3 cwVector, UnityEngine.Vector3 acwVector, UnityEngine.Vector3 halfCwVector, UnityEngine.Vector3 halfAcwVector, float halfAngleCW, float halfAngleACW) = StartPointData.findClosestVectors(directions, startPointData[n].outwardDir); // -> adaptive rotate angle range !!!

                        rightRotationRange.Add(halfAngleCW);
                        leftRotationRange.Add(halfAngleACW);
                    }

                    for (int n = 0; n < startPointData.Count; n++)
                    {
                        UnityEngine.Debug.Log("startPointData[n].startPoint: " + startPointData[n].startPoint);
                        UnityEngine.Debug.Log("centerPoints[" + n + "]: " + centerPoints[n]);
                        if (length(startPointData[n].startPoint - centerPoints[n]) > 0.0001f)
                        {
                            startPointData[n].outwardDir = startPointData[n].startPoint - centerPoints[n];
                            UnityEngine.Debug.Log("re-asigning startPointData[" + n + "].outwardDir: " + startPointData[n].outwardDir);
                        }
                        else
                        {
                            UnityEngine.Debug.Log("setting startPointData[" + n + "].outwardDir = startPointData[" + n + "].startNode.cotangent");
                            startPointData[n].outwardDir = startPointData[n].startNode.cotangent;
                        }
                    }
                       
                    float maxAngle = 0f;
                    float minAngle = 0f;
                    float windingAngle = 0f;
                        
                    for (int branchIndex = 0; branchIndex < nrBranches; branchIndex++)
                    {
                        StartPointData data = StartPointData.generateStartPointData(startNodesNextIndexStartTvalEndTval, segmentLengths, branchPositions[branchIndex], treeGrowDir, rootNode, treeHeight, false);

                        UnityEngine.Vector3 startPointTangent = sampleSplineTangentT(data.startNode.point, 
                                                                                     data.startNode.next[data.startNodeNextIndex].point, 
                                                                                     data.tangent,
                                                                                     data.startNode.next[data.startNodeNextIndex].tangent[0],
                                                                                     data.t);
                        
                        float branchStartTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[data.startNodeNextIndex].tValGlobal, data.t);

                        float globalVerticalAngle = lerp(branchClusterSettingsList[clusterIndex].verticalAngleCrownStart, branchClusterSettingsList[clusterIndex].verticalAngleCrownEnd, data.startNode.tValGlobal);

                        float branchVerticalAngle = lerp(branchClusterSettingsList[clusterIndex].verticalAngleBranchStart, branchClusterSettingsList[clusterIndex].verticalAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t));

                        float verticalAngle = globalVerticalAngle + branchVerticalAngle;

                        float globalRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleCrownStart, branchClusterSettingsList[clusterIndex].rotateAngleCrownEnd, branchStartTvalGlobal);

                        float branchRotateAngle = lerp(branchClusterSettingsList[clusterIndex].rotateAngleBranchStart, branchClusterSettingsList[clusterIndex].rotateAngleBranchEnd, lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t));

                        float rotateAngle = 0f;

                        //public enum angleMode
                        //{
                        //    symmetric,
                        //    winding, 
                        //    adaptiveWinding
                        //}

                        UnityEngine.Vector3 branchDir = new UnityEngine.Vector3(0f, 0f, 0f);
                            
                        if (branchClusterSettingsList[clusterIndex].rotateAngleRange == 0f)
                        {
                            branchClusterSettingsList[clusterIndex].rotateAngleRange = MathF.PI;
                        }
                        if (branchClusterSettingsList[clusterIndex].branchAngleMode == 2) // adaptiveWinding
                        {
                            UnityEngine.Vector3 centerDir = data.outwardDir;
                            centerDirs.Add(centerDir);

                            float angle;
                            if (rightRotationRange[branchIndex] + leftRotationRange[branchIndex] < 2f * MathF.PI)
                            {
                                angle = windingAngle % ((rightRotationRange[branchIndex] + leftRotationRange[branchIndex]) * branchClusterSettingsList[clusterIndex].rotateAngleRangeFactor) - leftRotationRange[branchIndex] * branchClusterSettingsList[clusterIndex].rotateAngleRangeFactor;
                            }
                            else
                            {
                                angle = windingAngle % (rightRotationRange[branchIndex] + leftRotationRange[branchIndex]) - leftRotationRange[branchIndex];
                            }

                            if (angle > maxAngle)
                            {
                                maxAngle = angle;
                            }
                            if (angle < minAngle)
                            {
                                minAngle = angle;
                            }

                            UnityEngine.Vector3 right = UnityEngine.Vector3.Cross(startPointData[branchIndex].outwardDir, startPointTangent);
                            UnityEngine.Vector3 axis = -UnityEngine.Vector3.Cross(-centerDir, startPointTangent);

                            branchDir = UnityEngine.Quaternion.AngleAxis(verticalAngle, axis) * startPointTangent;
                            branchDir = UnityEngine.Quaternion.AngleAxis(angle, startPointTangent) * branchDir;
                        }
                        if (branchClusterSettingsList[clusterIndex].branchAngleMode == 1) // winding
                        {
                            UnityEngine.Vector3 centerDir = data.outwardDir;
                            centerDirs.Add(centerDir);
                            float angle;
                            UnityEngine.Vector3 right;
                            if (branchClusterSettingsList[clusterIndex].useFibonacciAngles == true)
                            {
                                angle = (windingAngle + 2f * MathF.PI) % (2f * MathF.PI);
                                right = norm(UnityEngine.Vector3.Cross(startPointTangent, new UnityEngine.Vector3(1f, 0f, 0f))); // -> most likely vertical
                            }
                            else
                            {
                                if (branchClusterSettingsList[clusterIndex].rotateAngleRange <= 0f)
                                {
                                    branchClusterSettingsList[clusterIndex].rotateAngleRange = MathF.PI;
                                }
                                angle = windingAngle % branchClusterSettingsList[clusterIndex].rotateAngleRange + branchClusterSettingsList[clusterIndex].rotateAngleOffset - branchClusterSettingsList[clusterIndex].rotateAngleRange / 2f;
                                right = UnityEngine.Vector3.Cross(data.outwardDir, startPointTangent);

                                if (length(right) < 0.001f)
                                {
                                    UnityEngine.Vector3 d = data.startNode.next[data.startNodeNextIndex].point - data.startNode.point;
                                    UnityEngine.Vector3 h = new UnityEngine.Vector3(d.x, 0f, d.z);
                                    if (length(h) > 0.00001f)
                                    {
                                        right = UnityEngine.Vector3.Cross(h, data.startNode.tangent[0]);
                                    }
                                    else
                                    {
                                        right = new UnityEngine.Vector3(1f, 0f, 0f);
                                    }
                                }
                                else
                                {
                                    right = norm(right);
                                }
                            }
                            UnityEngine.Vector3 axis = norm(UnityEngine.Vector3.Cross(right, startPointTangent));
                            branchDir = UnityEngine.Quaternion.AngleAxis(-verticalAngle, axis) * startPointTangent;
                            branchDir = UnityEngine.Quaternion.AngleAxis(angle, startPointTangent) * branchDir;
                        }

                        if (branchClusterSettingsList[clusterIndex].branchAngleMode == 0) // symmetric
                        {
                            UnityEngine.Vector3 centerDir = UnityEngine.Quaternion.AngleAxis(-verticalAngle, UnityEngine.Vector3.Cross(startPointTangent, data.outwardDir)) * data.outwardDir;
                            centerDirs.Add(centerDir);
                            UnityEngine.Vector3 axis = norm(UnityEngine.Vector3.Cross(startPointTangent, centerDir));

                            rotateAngle = globalRotateAngle + branchRotateAngle;
                            UnityEngine.Vector3 right;
                            if (branchIndex % 2 == 0)
                            {
                                right = norm(UnityEngine.Vector3.Cross(startPointTangent, new UnityEngine.Vector3(0f, 1f, 0f)));
                                axis = norm(UnityEngine.Vector3.Cross(right, startPointTangent));
                                branchDir = UnityEngine.Quaternion.AngleAxis(-verticalAngle, axis) * startPointTangent;
                                branchDir = UnityEngine.Quaternion.AngleAxis(-rotateAngle, startPointTangent) * branchDir;
                            }
                            else
                            {
                                right = norm(UnityEngine.Vector3.Cross(startPointTangent, new UnityEngine.Vector3(0f, 1f, 0f)));
                                axis = norm(UnityEngine.Vector3.Cross(right, startPointTangent));
                                branchDir = UnityEngine.Quaternion.AngleAxis(verticalAngle, axis) * startPointTangent;
                                branchDir = UnityEngine.Quaternion.AngleAxis(rotateAngle, startPointTangent) * branchDir;
                            }
                        }

                        UnityEngine.Vector3 branchCotangent = new UnityEngine.Vector3(0f, 0f, 0f);
                        //There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem

                        if (branchDir.x != 0f)
                        {
                            branchCotangent = new UnityEngine.Vector3(-branchDir.z, 0f, branchDir.x);
                        }
                        else
                        {
                            if (branchDir.z != 0f)
                            {
                                branchCotangent = new UnityEngine.Vector3(0f, branchDir.z, -branchDir.y);
                            }
                            else
                            {
                                branchCotangent = new UnityEngine.Vector3(-branchDir.y, branchDir.x, 0f);
                            }
                        }

                        float startTvalGlobal = lerp(data.startNode.tValGlobal, data.startNode.next[data.startNodeNextIndex].tValGlobal, data.t);
                        float startTvalBranch = lerp(data.startNode.tValBranch, data.startNode.next[data.startNodeNextIndex].tValBranch, data.t);

                        float treeShapeRatioValue = shapeRatio(startTvalGlobal, branchClusterSettingsList[clusterIndex].treeShape);
                        float branchShapeRatioValue = shapeRatio(startTvalBranch, branchClusterSettingsList[clusterIndex].branchShape);

                        float branchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * UnityEngine.Random.Range(-1f, 1f)) * treeShapeRatioValue * branchShapeRatioValue;

                        node branch = new node(data.startPoint, 
                                               1f, 
                                               branchCotangent, 
                                               clusterIndex, 
                                               branchClusterSettingsList[clusterIndex].ringResolution, 
                                               taper * taperFactorList[clusterIndex], 
                                               startTvalGlobal, 
                                               0f, 
                                               branchLength);
                        
                        branch.tangent.Add(branchDir);
                        branch.tValBranch = 0f;

                        node branchNext = new node(data.startPoint + branchDir * branchLength, 
                                                      1f, 
                                                      branchCotangent, 
                                                      clusterIndex, 
                                                      branchClusterSettingsList[clusterIndex].ringResolution, 
                                                      taper * taperFactorList[clusterIndex], 
                                                      startTvalGlobal, 
                                                      0f, 
                                                      branchLength);
                        
                        branchNext.tangent.Add(branchDir);
                        branchNext.tValBranch = 1f;
                        branch.next.Add(branchNext);

                        if (data.startNode.branches.Count < data.startNodeNextIndex + 1)
                        {
                            for (int m = 0; m < data.startNode.next.Count; m++)
                            {
                                data.startNode.branches.Add(new List<node>());
                            }
                        }
                        data.startNode.branches[data.startNodeNextIndex].Add(branch);
                        branchNodes.Add(branch);

                        //public enum angleMode
                        //{
                        //    symmetric,
                        //    winding, 
                        //    adaptiveWinding
                        //}

                        if (branchClusterSettingsList[clusterIndex].useFibonacciAngles == true)
                        {
                            float fn0 = 1.0f;
                            float fn1 = 1.0f;
                            branchClusterSettingsList[clusterIndex].rotateAngleRange = 2.0f * MathF.PI;
                            if (branchClusterSettingsList[clusterIndex].fibonacciNr > 2)
                            {
                                for(int n = 2; n < branchClusterSettingsList[clusterIndex].fibonacciNr + 1; n++)
                                {
                                    float temp = fn0 + fn1;
                                    fn0 = fn1;
                                    fn1 = temp;
                                }
                            }
                            float fibonacciAngle = 2.0f * MathF.PI * (1.0f - fn0 / fn1);
                            windingAngle += fibonacciAngle;
                        }
                        else
                        {
                            if (branchClusterSettingsList[clusterIndex].branchAngleMode == 1) //"WINDING":
                            {
                                rotateAngle = (globalRotateAngle + branchRotateAngle) % branchClusterSettingsList[clusterIndex].rotateAngleRange;
                                windingAngle += rotateAngle;
                            }
                            
                            if (branchClusterSettingsList[clusterIndex].branchAngleMode == 2) //"ADAPTIVE":
                            {
                                rotateAngle = globalRotateAngle + branchRotateAngle;
                                windingAngle += rotateAngle;
                            }
                        } 

                        // public enum branchTypes
                        // {
                        //     single,
                        //     opposite,
                        //     whorled
                        // }  

                        //public enum angleMode
                        //{
                        //    symmetric,
                        //    winding, 
                        //    adaptiveWinding
                        //}            
                        
                        if (branchClusterSettingsList[clusterIndex].branchType == 1) //"OPPOSITE":    // UnityEngine.Quaternion(verticalAngle, axis) * startPointTangent;
                        {
                            centerDirs.Add(centerDirs[centerDirs.Count - 1]);
                            UnityEngine.Vector3 oppositeBranchDir = UnityEngine.Quaternion.AngleAxis(MathF.PI, startPointTangent) * branchDir;
                            UnityEngine.Vector3 oppositeBranchCotangent = UnityEngine.Quaternion.AngleAxis(MathF.PI, startPointTangent) * branchCotangent;
                            
                            if (branchClusterSettingsList[clusterIndex].branchAngleMode == 0) // "SYMMETRIC":
                            {
                                if (branchIndex % 2 == 0)
                                {
                                    oppositeBranchDir = UnityEngine.Quaternion.AngleAxis( 2.0f * rotateAngle, startPointTangent) * oppositeBranchDir;
                                }
                                else
                                {
                                    oppositeBranchDir = UnityEngine.Quaternion.AngleAxis(-2.0f * rotateAngle, startPointTangent) * oppositeBranchDir;
                                }
                            }
                            
                            float oppositeBranchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * UnityEngine.Random.Range(-1.0f, 1.0f)) * treeShapeRatioValue * branchShapeRatioValue;
                            
                            node oppositeBranch = new node(data.startPoint, 
                                                           1.0f, 
                                                           oppositeBranchCotangent, 
                                                           clusterIndex, 
                                                           branchClusterSettingsList[clusterIndex].ringResolution,
                                                           taper * taperFactorList[clusterIndex], 
                                                           startTvalGlobal,
                                                           0.0f, 
                                                           oppositeBranchLength);
                                          
                            oppositeBranch.tangent.Add(oppositeBranchDir);
                            oppositeBranch.tValBranch = 0f;
                            
                            node oppositeBranchNext = new node(data.startPoint + oppositeBranchDir * oppositeBranchLength, 
                                                               1.0f,
                                                               oppositeBranchCotangent,
                                                               clusterIndex,
                                                               branchClusterSettingsList[clusterIndex].ringResolution,
                                                               taper * taperFactorList[clusterIndex],
                                                               data.startNode.tValGlobal,
                                                               0.0f,
                                                               oppositeBranchLength);
                            oppositeBranchNext.tangent.Add(oppositeBranchDir);
                            oppositeBranchNext.tValBranch = 1.0f;
                            oppositeBranch.next.Add(oppositeBranchNext);
                            
                            if (data.startNode.branches.Count < data.startNodeNextIndex + 1)
                            {
                                for (int m = 0; m < data.startNode.next.Count; m++)
                                {
                                    data.startNode.branches.Add(new List<node>());
                                }
                            }
                            
                            data.startNode.branches[data.startNodeNextIndex].Add(oppositeBranch);
                            branchNodes.Add(oppositeBranch);
                        }

                        // public enum branchTypes
                        // {
                        //     single,
                        //     opposite,
                        //     whorled
                        // }  

                        //public enum angleMode
                        //{
                        //    symmetric,
                        //    winding, 
                        //    adaptiveWinding
                        //}  

                        if (branchClusterSettingsList[clusterIndex].branchType == 2) // "WHORLED":
                        {
                            int whorlCount = (int)MathF.Round(lerp(branchClusterSettingsList[clusterIndex].whorlCountStart, branchClusterSettingsList[clusterIndex].whorlCountEnd, startTvalGlobal));
                            
                            for (int n = 1; n < whorlCount; n++)
                            {
                                centerDirs.Add(centerDirs[centerDirs.Count - 1]);
                                UnityEngine.Vector3 whorlDir = UnityEngine.Quaternion.AngleAxis(n * 2f * MathF.PI / whorlCount, startPointTangent) * branchDir;
                                UnityEngine.Vector3 whorlCotangent = UnityEngine.Quaternion.AngleAxis(n * 2f * MathF.PI / whorlCount, branchCotangent) * branchCotangent;
                                
                                float whorlBranchLength = treeHeight * (branchClusterSettingsList[clusterIndex].relBranchLength + branchClusterSettingsList[clusterIndex].relBranchLengthVariation * UnityEngine.Random.Range(-1.0f, 1.0f)) * treeShapeRatioValue * branchShapeRatioValue;
                                
                                node whorlBranch = new node(data.startPoint, 
                                                            1.0f, 
                                                            whorlCotangent, 
                                                            clusterIndex, 
                                                            branchClusterSettingsList[clusterIndex].ringResolution, 
                                                            taper * taperFactorList[clusterIndex], 
                                                            startTvalGlobal, 
                                                            0.0f, 
                                                            whorlBranchLength);
                                           
                                whorlBranch.tangent.Add(whorlDir);
                                whorlBranch.tValBranch = 0.0f;
                                
                                node whorlBranchNext = new node(data.startPoint + whorlDir * whorlBranchLength, 
                                                           1.0f,
                                                           whorlCotangent,
                                                           clusterIndex,
                                                           branchClusterSettingsList[clusterIndex].ringResolution,
                                                           taper * taperFactorList[clusterIndex],
                                                           data.startNode.tValGlobal,
                                                           0.0f,
                                                           branchLength);
                                whorlBranchNext.tangent.Add(whorlDir);
                                whorlBranchNext.tValBranch = 1.0f;
                                whorlBranch.next.Add(whorlBranchNext);
                                
                                if (data.startNode.branches.Count < data.startNodeNextIndex + 1)
                                {
                                    for (int m = 0; m < data.startNode.next.Count; m++)
                                    {
                                        data.startNode.branches.Add(new List<node>());
                                    }
                                }
                                
                                data.startNode.branches[data.startNodeNextIndex].Add(whorlBranch);
                                branchNodes.Add(whorlBranch);
                            }
                        }
                    }
                }

                // for each branch cluster
                if (branchClusterSettingsList[clusterIndex].nrSplitsPerBranch > 0f)
                {
                    List<float> splitHeightInLevelList = branchSplitHeightInLevelListList[clusterIndex]; 

                    int nrSplits = (int)(branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches);
                    
                    int length = splitHeightInLevelList.Count;
                    if (length < (int)branchClusterSettingsList[clusterIndex].nrSplitsPerBranch * branchClusterSettingsList[clusterIndex].nrBranches)
                    {
                        for (int i = length; i < nrSplits; i++)
                        {
                            splitHeightInLevelList.Add(0.5f);
                        }
                    }

                    branchClusterSettingsList[clusterIndex].maxSplitHeightUsed = splitBranches(rootNode, 
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
                                                                                               branchClusterSettingsList[clusterIndex].branchCurvatureOffset,

                                                                                               branchClusterSettingsList[clusterIndex].branchVariance,
                                                                                               branchClusterSettingsList[clusterIndex].branchSplitAxisVariation);
                }

                for (int i = 0; i < branchNodes.Count; i++)
                {
                    branchNodes[i].resampleSpline(rootNode, resampleDistance);
                    branchNodes[i].applyCurvature(rootNode, 
                                                  treeGrowDir, 
                                                  treeHeight, 
                                                  branchClusterSettingsList[clusterIndex].branchGlobalCurvatureStart, 
                                                  branchClusterSettingsList[clusterIndex].branchCurvatureStart,
                                                  branchClusterSettingsList[clusterIndex].branchGlobalCurvatureEnd, 
                                                  branchClusterSettingsList[clusterIndex].branchCurvatureEnd,
                                                  clusterIndex,
                                                  branchNodes[i].point,
                                                  branchClusterSettingsList[clusterIndex].reducedCurveStepCutoff,
                                                  branchClusterSettingsList[clusterIndex].reducedCurveStepFactor);

                    if (clusterIndex == 0)
                    {
                        branchNodes[i].attractOutward(branchClusterSettingsList[clusterIndex].outwardAttraction, branchNodes[i].tangent[0]);
                    }
                    else
                    {
                        branchNodes[i].attractOutward(branchClusterSettingsList[clusterIndex].outwardAttraction, centerDirs[i]);
                    }

                    if (branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch > 0f || branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch > 0f)
                    {
                        // TODO
                        //
                        // branchNodes[i].applyNoise(noiseGenerator, 
                        //                       branchClusterSettingsList[clusterIndex].noiseAmplitudeHorizontalBranch, 
                        //                       branchClusterSettingsList[clusterIndex].noiseAmplitudeVerticalBranch,
                        //                       branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchGradient,
                        //                       branchClusterSettingsList[clusterIndex].noiseAmplitudeBranchExponent, 
                        //                       branchClusterSettingsList[clusterIndex].noiseScale, 
                        //                       branchNodes[i].point - (branchNodes[i].next[0].point - branchNodes[i].point), 
                        //                       branchLength);
                    }
                }

            }
        }

        float calculateSegmentLengthsAndTotalLength(List<startNodeInfo> startNodesNextIndexStartTvalEndTval, 
                                                    List<float> segmentLengths, 
                                                    float branchesStartHeightGlobal, 
                                                    float branchesEndHeightGlobal, 
                                                    float branchesStartHeightCluster, 
                                                    float branchesEndHeightCluster)
        {
            UnityEngine.Debug.LogError("TODO");
            return -1f; 
        }

        public int splitBranches(node rootNode, 
                                  int clusterIndex,
                                  int nrSplits, 
                                  
                                  float branchSplitAngle, 
                                  float branchSplitPointAngle,
                                  float nrSplitsPerBranch,
                                  
                                  float splitsPerBranchVariation,
                                  List<float> splitHeightInLevelList,
                                  float branchSplitHeightVariation,
                                  float branchSplitLengthVariation,
                                  int branchSplitMode, 
                                  
                                  float branchSplitRotateAngle, 
                                  int ringResolution,
                                  float branchCurvatureOffsetStrength,
              
                                  float branchVariance,
                                  float branchSplitAxisVariation)
        {
            return 0;
        }

        static float shapeRatio(float tValGlobal, int treeShape)
        {
            if (treeShape == 0)//"CONICAL":
            {
                return 0.2f + 0.8f * tValGlobal;
            }
            if (treeShape == 1)//"SPHERICAL":
            {
                return 0.2f + 0.8f * MathF.Sin(MathF.PI * tValGlobal);
            }
            if (treeShape == 2)//"HEMISPHERICAL":
            {
                return 0.2f + 0.8f * MathF.Sin(0.5f * MathF.PI * tValGlobal);
            }
            if (treeShape == 3)//"INVERSE_HEMISPHERICAL":
            {
                return 0.2f + 0.8f * MathF.Sin(0.5f * MathF.PI * (1.0f - tValGlobal));
            }
            if (treeShape == 4)//"CYLINDRICAL":
            {
                return 1.0f;
            }
            if (treeShape == 5)//"TAPERED_CYLINDRICAL":
            {
                return 0.5f + 0.5f * tValGlobal;
            }
            if (treeShape == 6)//"FLAME":
            {
                if (tValGlobal <= 0.7f)
                {
                    return tValGlobal / 0.7f;
                }
                else
                {
                    return (1f - tValGlobal) / 0.3f;
                }
            }
            if (treeShape == 7)//"INVERSE_CONICAL":
            {
                return 1.0f - 0.8f * tValGlobal;
            }
            if (treeShape == 8)//"TEND_FLAME":
            {
                if (tValGlobal <= 0.7f)
                {
                    return 0.5f + 0.5f * tValGlobal / 0.7f;
                }
                else
                {
                    return 0.5f + 0.5f * (1.0f - tValGlobal) / 0.3f;
                }
            }
            else
            {
                UnityEngine.Debug.LogError("ERROR: invalid tree shape!");
                return 0f;
            }
        }

        void generateVerticesAndTriangles(List<segment> segments, float ringSpacing, float branchTipRadius)
        {
            UnityEngine.Debug.Log("in generateVerticesAndTriangles()");
            vertices = new List<UnityEngine.Vector3>();
            normals = new List<UnityEngine.Vector3>();
            vertexTvalGlobal = new List<float>();
            vertexTvalBranch = new List<float>();
            ringAngle = new List<float>();
            triangles = new List<int>();

            int offset = 0;
            int counter = 0;

            int startSection = 0;
            UnityEngine.Debug.Log("segments.Count: " + segments.Count);

            for (int s = 0; s < segments.Count; s++)
            {
                float segmentLength = length(segments[s].end - segments[s].start);
                UnityEngine.Debug.Log("segment length: " + segmentLength);
                if (segmentLength > 0f)
                {
                    int sections = (int)MathF.Round(segmentLength / ringSpacing);
                    if (sections <= 0)
                    {
                        sections = 1;
                    }
                    float branchRingSpacing = segmentLength / sections;

                    if (s > 0)
                    {
                        UnityEngine.Debug.Log("segment " + s + ".connectedToPrevious: " + segments[s].connectedToPrevious);
                        if (segments[s].connectedToPrevious == true && segments[s - 1].connectedToPrevious == false) // only on first segment
                        {
                            startSection = 1;
                            offset -= segments[s].ringResolution + 1;
                            UnityEngine.Debug.Log("startSection = 1, offset = " + offset);
                        }

                        if (segments[s].connectedToPrevious == false)
                        {
                            startSection = 0;
                            offset = vertices.Count;
                            UnityEngine.Debug.Log("startSection = 0, offset = " + offset);
                        }
                    }
                    else
                    {
                        UnityEngine.Debug.Log("segment " + s);
                        UnityEngine.Debug.Log("startSection = " + startSection + ", offset = " + offset);
                    }

                    UnityEngine.Vector3 controlPt1 = segments[s].start + norm(segments[s].startTangent) * (segments[s].end - segments[s].start).magnitude / 3f;
                    UnityEngine.Vector3 controlPt2 = segments[s].end - norm(segments[s].endTangent) * (segments[s].end - segments[s].start).magnitude / 3f;

                    for (int section = startSection; section < sections + 1; section++)
                    {
                        UnityEngine.Vector3 pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / (float)sections);
                        UnityEngine.Vector3 tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / (float)sections);

                        if (section == 0)
                        {
                            tangent = segments[s].firstTangent;
                        }

                        UnityEngine.Vector3 dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / (float)sections);
                        UnityEngine.Vector3 dirB = norm(UnityEngine.Vector3.Cross(tangent, dirA));
                        dirA = norm(UnityEngine.Vector3.Cross(dirB, tangent));

                        float tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / (float)sections);
                        float tValBranch = segments[s].startTvalBranch + (segments[s].endTvalBranch - segments[s].startTvalBranch) * (section / (float)sections);
                        float radius = 0f;
                        if (segments[s].clusterIndex == -1)
                        {
                            float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing));
                            // TODO: taper curve...
                            float normalizedCurve = (1f - branchTipRadius) * tVal + 1.0f - tVal;
                            radius = linearRadius * normalizedCurve;
                        }
                        else
                        {
                            float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing));
                            // TODO: taper curve...
                            float normalizedCurve = (1f - branchTipRadius) * tVal + 1.0f - tValBranch;
                            radius = linearRadius * normalizedCurve;
                        }

                        for (int i = 0; i < segments[s].ringResolution + 1; i++)
                        {
                            float angle = 2f * MathF.PI * i / segments[s].ringResolution;
                            UnityEngine.Vector3 normalVector = dirA * radius * MathF.Cos(angle) + dirB * radius * MathF.Sin(angle);
                            UnityEngine.Vector3 v = pos + normalVector;

                            vertices.Add(v);
                            normals.Add(normalVector);
                            vertexTvalGlobal.Add(tVal);
                            if (segments[s].clusterIndex == -1)
                            {
                                vertexTvalBranch.Add(tVal);
                            }
                            else
                            {
                                vertexTvalBranch.Add(tValBranch);
                            }
                            ringAngle.Add(angle);

                            counter += 1;
                        }
                    }

                    for (int c = 0; c < sections; c++)
                    {
                        float tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / (float)sections);
                        float nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / (float)sections);

                        UnityEngine.Vector3 pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / (float)sections);

                        float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing));
                        // TODO: taper curve...
                        float normalizedCurve = (1f - branchTipRadius) * tVal + 1f - tVal;
                        float radius = linearRadius * normalizedCurve;

                        UnityEngine.Debug.Log("adding triangles: section: " + c + ", offset: " + offset);

                        for (int j = 0; j < segments[s].ringResolution; j++)
                        {
                            if (c % 2 == 0)
                            {
                                if (j % 2 == 0)
                                {
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));

                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);
                                }
                                else
                                {
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);

                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);
                                }
                            }
                            else
                            {
                                if (j % 2 == 0)
                                {
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);
    
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);
                                }
                                else
                                {
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
    
                                    triangles.Add(offset +  c      * (segments[s].ringResolution + 1) +  j);
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                                    triangles.Add(offset + (c + 1) * (segments[s].ringResolution + 1) +  j);
                                }
                            }
                        }
                    }
                    offset += counter;
                    counter = 0;
                }
            }

            int vCount = vertices.Count;
            for (int i = 0; i < triangles.Count; i++)
            {
                if (triangles[i] >= vCount || triangles[i] < 0)
                {
                    UnityEngine.Debug.LogError("triangles[" + i + "]: " + triangles[i] + " out of bounds!");
                }
                //else
                //{
                //    UnityEngine.Debug.Log("triangles[" + i + "]: " + triangles[i]);
                //}
            }
            /*  
                for c in range(0, sections): 
                    tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / sections)
                    nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / sections)
                    
                    pos = treegen_utils.sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / sections)
                    
                    linearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing))

                    if context.scene.treeSettings.useStemTaperCurve == True:
                        normalizedCurve = (1.0 - branchTipRadius) * tVal + treegen_utils.sampleCurveStem(treeGen, tVal)
                    else:
                        normalizedCurve = (1.0 - branchTipRadius) * tVal + 1.0 - tVal
                    
                    radius = linearRadius * normalizedCurve
                    
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
                custom_normals[loop_index] = normals[vertex_index]  # Your custom normal !!
    
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
        
        #uvLayer = meshData.uv_layers.active
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
            #self.report({'INFO'}, "Found object 'tree'!")
        else:
            treeObject = bpy.data.objects.new("tree", meshData)
            bpy.context.collection.objects.link(treeObject)
            treeObject.select_set(True)
            #self.report({'INFO'}, "Created new object!")
        
        bpy.context.view_layer.objects.active = treeObject
        
        bpy.ops.object.shade_auto_smooth(angle=0.01)
        
        mesh = treeObject.data
        
        if "tValGlobal" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="tValGlobal", domain='POINT', data_type='FLOAT')

        if "tValBranch" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="tValBranch", domain='POINT', data_type='FLOAT')
        
        if "ringAngle" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="ringAngle", domain='POINT', data_type='FLOAT')
        
        tValGlobalAttribute = mesh.attributes["tValGlobal"]
        tValBranchAttribute = mesh.attributes["tValBranch"]
        ringAngleAttribute = mesh.attributes["ringAngle"]
        
        for i, vertex in enumerate(mesh.vertices):
            tValGlobalAttribute.data[i].value = vertexTvalGlobal[i]
            tValBranchAttribute.data[i].value = vertexTvalBranch[i]
            ringAngleAttribute.data[i].value = ringAngle[i] / (2.0 * math.pi)
        
        treeObject.data.materials.clear()
        treeObject.data.materials.append(barkMaterial)
            */
        }

        static UnityEngine.Vector3 norm(UnityEngine.Vector3 v)
        {
            if (v ==  new UnityEngine.Vector3(0f, 0f, 0f))
            {
                return v;
            }
            else
            {
                return v / v.magnitude;
            }
        }

        static float length(UnityEngine.Vector3 v)
        {
            return v.magnitude;
        }

        static UnityEngine.Vector3 sampleSplineC(UnityEngine.Vector3 controlPt0, UnityEngine.Vector3 controlPt1, UnityEngine.Vector3 controlPt2, UnityEngine.Vector3 controlPt3, float t)
        {
            return (1.0f - t) * (1.0f - t) * (1.0f - t) * controlPt0 + 3.0f * (1.0f - t) * (1.0f - t) * t * controlPt1 + 3.0f * (1.0f- t) * t * t * controlPt2 + t * t * t * controlPt3;
        }
        // def sampleSplineC(controlPt0, controlPt1, controlPt2, controlPt3, t):
        // return (1.0 - t)**3.0 * controlPt0 + 3.0 * (1.0 - t)**2.0 * t * controlPt1 + 3.0 * (1.0 - t) * t**2.0 * controlPt2 + t**3.0 * controlPt3
        
        static UnityEngine.Vector3 sampleSplineT(UnityEngine.Vector3 start, UnityEngine.Vector3 end, UnityEngine.Vector3 startTangent, UnityEngine.Vector3 endTangent, float t)
        {
            UnityEngine.Vector3 controlPt1 = start + norm(startTangent) * (end - start).magnitude / 3.0f;
            UnityEngine.Vector3 controlPt2 = end - norm(endTangent) * (end - start).magnitude / 3.0f;
            return (1.0f - t)*(1.0f - t)*(1.0f - t) * start + 3.0f * (1.0f - t)*(1.0f - t) * t * controlPt1 + 3.0f * (1.0f - t) * t*t * controlPt2 + t*t*t * end;
        }
        // def sampleSplineT(start, end, startTangent, endTangent, t):
        // controlPt1 = start + startTangent.normalized() * (end - start).length / 3.0
        // controlPt2 = end - endTangent.normalized() * (end - start).length / 3.0
        // return (1.0 - t)**3.0 * start + 3.0 * (1.0 - t)**2.0 * t * controlPt1 + 3.0 * (1.0 - t) * t**2.0 * controlPt2 + t**3.0 * end
    // 

        static UnityEngine.Vector3 sampleSplineTangentC(UnityEngine.Vector3 controlPt0, UnityEngine.Vector3 controlPt1, UnityEngine.Vector3 controlPt2, UnityEngine.Vector3 controlPt3, float t)
        {
            return norm(-3.0f * (1.0f - t) * (1.0f - t) * controlPt0 + 3.0f * (3.0f * t * t - 4.0f * t + 1.0f) * controlPt1 + 3.0f * (-3.0f * t * t + 2.0f * t) * controlPt2 + 3.0f * t * t * controlPt3);
        }
        // def sampleSplineTangentC(controlPt0, controlPt1, controlPt2, controlPt3, t):
        // return (-3.0 * (1.0 - t)**2.0 * controlPt0 + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * controlPt3).normalized()
    

        static UnityEngine.Vector3 sampleSplineTangentT(UnityEngine.Vector3 start, UnityEngine.Vector3 end, UnityEngine.Vector3 startTangent, UnityEngine.Vector3 endTangent, float t)
        {
            UnityEngine.Vector3 controlPt1 = start + norm(startTangent) * length(end - start) / 3.0f;
            UnityEngine.Vector3 controlPt2 = end - norm(endTangent) * length(end - start) / 3.0f;
            return norm(-3.0f * (1.0f - t) * (1.0f - t) * start + 3.0f * (3.0f * t*t - 4.0f * t + 1.0f) * controlPt1 + 3.0f * (-3.0f * t*t + 2.0f * t) * controlPt2 + 3.0f * t*t * end);
        }

        //def sampleSplineTangentT(start, end, startTangent, endTangent, t):
        // controlPt1 = start + startTangent.normalized() * (end - start).length / 3.0
        // controlPt2 = end - endTangent.normalized() * (end - start).length / 3.0
        // return (-3.0 * (1.0 - t)**2.0 * start + 3.0 * (3.0 * t**2.0 - 4.0 * t + 1.0) * controlPt1 + 3.0 * (-3.0 * t**2.0 + 2.0 * t) * controlPt2 + 3.0 * t**2.0 * end).normalized()

        static UnityEngine.Vector3 lerp(UnityEngine.Vector3 a, UnityEngine.Vector3 b, float t)
        {
            return a + t * (b - a);
        }

        static float lerp(float a, float b, float t)
        {
            return a + t * (b - a);
        }

        public void getAllNodes(List<node> allNodes, node activeNode)
        {
            allNodes.Add(activeNode);
            foreach (node n in activeNode.next)
            {
                getAllNodes(allNodes, n);
            }
        }


        void OnDrawGizmos()
        {
            if (nodes != null)
            {
                List<node> allNodes = new List<node>();
                getAllNodes(allNodes, nodes[0]);
                foreach (node n in allNodes)
                {
                    Gizmos.color = UnityEngine.Color.red;
                    Gizmos.DrawSphere(n.point, 0.2f);
                }
                //foreach (segment s in segments)
                //{
                //    Gizmos.color = new UnityEngine.Color(0.8f, 0f, 0f, 0.5f);
                //    Gizmos.DrawSphere(s.start, 0.2f);
                //    Gizmos.color = UnityEngine.Color.green;
                //    Gizmos.DrawSphere(s.end, 0.1f);
                //}

                foreach (UnityEngine.Vector3 v in vertices)
                {
                    Gizmos.color = UnityEngine.Color.blue;
                    Gizmos.DrawSphere(v, 0.05f);
                }
            }
        }

    }

    

}