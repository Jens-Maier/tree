
using System.Collections.Generic;
using System.Numerics;
using System;
using System.Security.AccessControl;
using System.Security.Cryptography.X509Certificates;
using UnityEngine;
using System.Drawing;
using System.Diagnostics;

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
                    UnityEngine.Debug.Log("adding segment");
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[n + 1], 
                                            nextNode.tangent[0], 
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
                    UnityEngine.Debug.Log("adding segment: point: " + point);
                    UnityEngine.Debug.Log("segments count before: " + segments.Count);
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[0], 
                                            nextNode.tangent[0], 
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

                    nextNode.getAllSegments(rootNode, segments, true);
                }
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


        // nodes.append(node(Vector((0.0,0.0,0.0)), 0.1, Vector((1.0,0.0,0.0)), -1, stemRingRes, taper, 0.0, 0.0, height))
        // nodes[0].tangent.append(Vector((0.0,0.0,1.0)))
        // nodes[0].cotangent = Vector((1.0,0.0,0.0))
        // nodes.append(node(dir * height, 0.1, Vector((1.0,0.0,0.0)), -1, stemRingRes, taper, 1.0, 0.0, height))
        // nodes[1].tangent.append(Vector((0.0,0.0,1.0)))
        // nodes[1].cotangent = Vector((1.0,0.0,0.0))
        // nodes[0].next.append(nodes[1])
        // nodes[0].outwardDir.append(nodes[0].cotangent)
        // nodes[0].rotateAngleRange.append(math.pi)
        // nodes[1].outwardDir.append(nodes[0].cotangent)
        // nodes[1].rotateAngleRange.append(math.pi)


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
            }

            // if context.scene.treeSettings.nrSplits > 0:
            //     maxSplitHeightUsed = treeGenerator.splitRecursive(nodes[0], 
            //                                         context.scene.treeSettings.nrSplits, 
            //                                         context.scene.treeSettings.stemSplitAngle, 
            //                                         context.scene.treeSettings.stemSplitPointAngle, 
            //                                         context.scene.treeSettings.variance, 
            //                                         context.scene.treeSettings.stemSplitHeightInLevelList, 
            //                                         context.scene.treeSettings.splitHeightVariation, 
            //                                         context.scene.treeSettings.splitLengthVariation, 
            //                                         context.scene.treeSettings.stemSplitMode, 
            //                                         context.scene.treeSettings.stemSplitRotateAngle, 
            //                                         context.scene.treeSettings.stemRingResolution, 
            //                                         context.scene.treeSettings.curvOffsetStrength, self, nodes[0])

            calculateRadius(nodes[0], 100.0f, settings.branchTipRadius);

            segments = new List<segment>();
            nodes[0].getAllSegments(nodes[0], segments, false);

            foreach (segment s in segments)
            {
                UnityEngine.Debug.Log("segment: start: " + s.start);
                UnityEngine.Debug.Log("segment: end: " + s.end);
            }

            generateVerticesAndTriangles(segments, settings.ringSpacing, settings.branchTipRadius);

            // TODO: mesh
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

            //nodesInLevelNextIndex = [[] for _ in range(nrSplits + 1)]
            List<List<(node, int)>> nodesInLevelNextIndex = new List<List<(node, int)>>();
            for (int i = 0; i < nrSplits + 1; i++)
            {
                nodesInLevelNextIndex.Add(new List<(node, int)>());
            }
            //for n in range(len(startNode.next)):
            //    nodesInLevelNextIndex[0].append((startNode, n))
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
                int nrNodesToTip = nodesToTip(startNode.next[nextIndex], 0);
                if (splitHeight > 0.999f)
                {
                    splitHeight = 0.999f;
                }
                int splitAfterNodeNr = (int)(nrNodesToTip * splitHeight);
                {
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
            }
            return startNode;
        }

        int nodesToTip(node n, int i)
        {
            if (n.next.Count > 0)
            {
                if (i > 500)
                {
                    UnityEngine.Debug.Log("ERROR: in nodesToTip(): max iteration reached!");
                    return i;
                }
                return 1 + nodesToTip(n.next[0], i + 1);
            }
            else
            {
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

            int tangentIndex = 0;
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
                        if (segments[s].connectedToPrevious == true && segments[s - 1].connectedToPrevious == false) // only on first segment
                        {
                            startSection = 1;
                            offset -= segments[s].ringResolution + 1;
                        }

                        if (segments[s].connectedToPrevious == false)
                        {
                            startSection = 0;
                            offset = vertices.Count;
                        }
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
                }
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


        void OnDrawGizmos()
        {
            if (nodes != null)
            {
                //foreach (node n in nodes)
                //{
                //    Gizmos.color = Color.red;
                //    Gizmos.DrawSphere(n.point, 0.2f);
                //}
                foreach (segment s in segments)
                {
                    Gizmos.color = UnityEngine.Color.red;
                    Gizmos.DrawSphere(s.start, 0.2f);
                    Gizmos.DrawSphere(s.end, 0.1f);
                }

                foreach (UnityEngine.Vector3 v in vertices)
                {
                    Gizmos.color = UnityEngine.Color.blue;
                    Gizmos.DrawSphere(v, 0.05f);
                }
            }
        }

    }

    

}