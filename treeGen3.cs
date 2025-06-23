#pragma warning disable IDE1006 // Naming Styles
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Random = System.Random;


public struct line
{
    public Vector3 start;
    public Vector3 end;

    public line(Vector3 s, Vector3 e)
    {
        start = s;
        end = e;
    }
}

public enum Shape
{
    conical,
    spherical,
    hemispherical,
    cylindrical,
    taperedCylindrical,
    flame,
    inverseConical,
    tendFlame
}

public enum angleMode
{
    symmetric,
    winding
}

public enum splitMode
{
    rotateAngle, 
    horizontal
}

public struct nodeInfo
{
    public node nodeInLevel;
    public int nextIndex;
    public int splitsPerBranch;
    public nodeInfo(node NodeInLevel, int NextIndex, int SplitsPerBranch)
    {
        nodeInLevel = NodeInLevel;
        nextIndex = NextIndex;
        splitsPerBranch = SplitsPerBranch;
    }
}

public struct StartNodeInfo
{
    public node startNode;
    public int nextIndex;
    public float startTval;
    public float endTval;
    public StartNodeInfo(node StartNode, int NextIndex, float StartTval, float EndTval)
    {
        startNode = StartNode;
        nextIndex = NextIndex;
        startTval = StartTval;
        endTval = EndTval;
    }
}

public class node
{
    public Vector3 point;
    public List<Vector3> tangent; //list<tangent> for splits! [tangentIn, tangentOutA, tangentOutB] ((only[tangent] without split!)
    public Vector3 cotangent;
    public List<node> next;
    public node parent;
    public int clusterIndex;
    public float radius;
    public float tValGlobal; // point height along tree [0..1]
    public float tValBranch; // point height along branch [0..1]
    public float taper;
    public int ringResolution;
    public treeGen3 gen;
    public List<List<node>> branches; // one list for each node in next 

    public node(Vector3 Point, Vector3 newTangent, Vector3 newCotangent, float t_global, float t_branch, float newTaper, treeGen3 g, node par, int clustIndex, int ringRes)
    {
        if (point.y > g.treeHeight)
        {
            Debug.Log("ERROR: point.y > treeHeight! " + point.y + " > " + g.treeHeight);
        }

        point = Point;
        tangent = new List<Vector3>();
        tangent.Add(newTangent);
        cotangent = newCotangent;
        tValGlobal = t_global;
        tValBranch = t_branch;
        radius = 0f;
        next = new List<node>();
        taper = newTaper;
        //if (clusterIndex == -1)
        //{
        //    ringResolution = g.stemRingResolution;
        //}
        //else
        //{
        ringResolution = ringRes;
        //}
        gen = g;
        parent = par;
        clusterIndex = clustIndex;
        branches = new List<List<node>>();
    }

    public void getAllLeafNodes(List<node> allLeafNodes)
    {
        if (next.Count > 0)
        {
            foreach (node n in next)
            {
                n.getAllLeafNodes(allLeafNodes);
            }
        }
        else
        {
            allLeafNodes.Add(this);
        }
    }

    public void getAllStartNodes(List<StartNodeInfo> startNodesNextIndexStartTvalEndTval, List<List<StartNodeInfo>> branchNodesNextIndexStartTvalEndTval, int activeBranchIndex, List<int> nrSplitsPassedAtStartNode, int nrSplitsPassed, float startHeightGlobal, float startHeightCluster, float endHeightGlobal, float endHeightCluster, int level, List<bool> parentClusterBools, int parentLevelCounter)
    {
        // branchNodesNextIndex: one list<(node, int)> for each branch

        //Debug.Log("parentClusterBools.Count: " + parentClusterBools.Count + ", clusterIndex: " + clusterIndex);
        if (clusterIndex == -1)
        {
            // stem
            //Debug.Log("start nodes in stem!");
            if (tValGlobal >= startHeightGlobal && tValGlobal <= endHeightGlobal)// && tValBranch >= startHeightCluster) // no startHeightCluster in stem!
            {
                if (next.Count > 0)
                {
                    for (int n = 0; n < next.Count; n++)
                    {
                        startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, 0f, 1f)); // TODO: startTval [0..1] from startNode to startNode.next!!!
                    }
                    nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
                }
            }
            else
            {
                // TODO! (s. else...)
                //
                // if (next.Count > 0)
                // {
                //     for (int n = 0; n < next.Count; n++)
                //     {
                //         if (tValGlobal <= endHeightGlobal)// && next[n].tValBranch >= startHeightCluster) // no startHeightCluster in stem!
                //         {
                //             // float tVal = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                // 
                //             //   |------*-------*---------*
                //             //          ^   ^   ^-next[n].tValBranch
                //             //          |   -startHeightCluster 
                //             //          -tValBranch
                // 
                //             startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, 0f, 1f)); //tVal));
                //         }
                //         else
                //         {
                //             if (next[n].tValBranch < startHeightCluster)
                //             {
                //                 if (tValGlobal > endHeightGlobal)
                //                 {
                //                     Debug.Log("startNode not added because next[n].tValBranch < startHeightCluster AND tValGlobal > endHeight");
                //                 }
                //                 else
                //                 {
                //                     Debug.Log("startNode not added because next[n].tValBranch < startHeightCluster");
                //                 }
                //             }
                //             else
                //             {
                //                 if (tValGlobal > endHeightGlobal)
                //                 {
                //                     Debug.Log("startNode not added because tValGlobal > endHeight");
                //                 }
                //             }
                //         }
                //     }
                //     nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
                // }

            }
            if (next.Count > 1)
            {
                nrSplitsPassed += 1;
            }
            foreach (node n in next)
            {
                n.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, activeBranchIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeightGlobal, startHeightCluster, endHeightGlobal, endHeightCluster, level + 1, parentClusterBools, parentLevelCounter);
            }
        }
        else
        {
            //Debug.Log("start nodes in cluster: " + clusterIndex + ", parentLevelCounter: " + parentLevelCounter + ", level: " + level);

            if (parentClusterBools.Count > clusterIndex + 1) // test new! (for leaves...)
            {
                if (parentClusterBools[clusterIndex + 1] == true) // TEST +1 TEST !!! // ??? ERROR HERE !!! needed for branch cluster but ERROR at addLeaves! 
                {
                    Debug.Log("cluster: " + clusterIndex + ", tValBranch: " + tValBranch + ", startHeightCluster: " + startHeightCluster);
                    if (next.Count > 0)
                    {
                        // if (next.Count > 1) // TEST!
                        // {
                        //     // TODO...
                        //     
                        // 
                        // 
                        // 
                        // 
                        // 
                        // }
                        // else
                        // {
                        for (int n = 0; n < next.Count; n++)
                        {
                            if (next.Count > 1)
                            {
                                Debug.Log("2 next nodes: in getAllStartNodes: tValBranch: " + tValBranch + ", next[0].tValBranch: " + next[0].tValBranch + ", next[1].tValBranch: " + next[1].tValBranch);
                                // ERROR HERE !!!
                            }
                            else
                            {
                                Debug.Log("1 next node: in getAllStartNodes: tValBranch: " + tValBranch + ", next[0].tValBranch: " + next[0].tValBranch);
                            }

                            if (tValGlobal >= startHeightGlobal && tValGlobal <= endHeightGlobal)
                            {

                                // TEST (AI)
                                float tA = tValBranch;
                                float tB = next[n].tValBranch;
                                if (tA > tB)
                                {
                                    float tmp = tA;
                                    tA = tB;
                                    tB = tmp;
                                }

                                // Only process if there is overlap
                                if (tB > startHeightCluster && tA < endHeightCluster)
                                {
                                    float segStart = Mathf.Max(tA, startHeightCluster);
                                    float segEnd = Mathf.Min(tB, endHeightCluster);

                                    float startTval = (segStart - tA) / (tB - tA);
                                    float endTval = (segEnd - tA) / (tB - tA);

                                    startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, startTval, endTval));
                                    if (activeBranchIndex != -1)
                                    {
                                        branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, startTval, endTval));
                                    }
                                }




                                //  |-----v---*------*---v------*
                                //        |   |          endHeightGlobal
                                //        |   tValGlobal
                                //        startHeightGlobal

                                // if (tValBranch < startHeightCluster && next[n].tValBranch >= endHeightCluster)
                                // {
                                //     //   |------*---v----v---*---------*
                                //     //          ^   ^    ^   ^-next[n].tValBranch
                                //     //          |   |    -endHeightCluster
                                //     //          |   -startHeightCluster 
                                //     //          -tValBranch
                                // 
                                //     float startTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch); // 0 - 1 from node to node.next
                                //     float endTval = (endHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                // 
                                //     startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, startTval, endTval));
                                //     if (activeBranchIndex != -1)
                                //     {
                                //         branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, startTval, endTval));
                                //     }
                                // }
                                // 
                                // if (tValBranch < startHeightCluster && next[n].tValBranch < endHeightCluster && next[n].tValBranch >= startHeightCluster)
                                // {
                                //     //   |------*---v----*---v-----*
                                //     //          ^   ^    ^   ^-endHeightCluster
                                //     //          |   |    -next[n].tValBranch
                                //     //          |   -startHeightCluster 
                                //     //          -tValBranch
                                // 
                                //     float startTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                // 
                                //     startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, startTval, 1f));
                                //     if (activeBranchIndex != -1)
                                //     {
                                //         branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, startTval, 1f));
                                //     }
                                // }
                                // 
                                // if (tValBranch >= startHeightCluster && next[n].tValBranch >= endHeightCluster && tValBranch < endHeightCluster)
                                // {
                                //     //   |------v---*----v---*-----*
                                //     //          ^   ^    ^   ^-next[n].tValBranch
                                //     //          |   |    -endHeightCluster
                                //     //          |   -tValBranch 
                                //     //          -startHeightCluster
                                // 
                                //     float endTval = (endHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                // 
                                //     startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, 0f, endTval));
                                //     if (activeBranchIndex != -1)
                                //     {
                                //         branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, 0f, endTval));
                                //     }
                                // }
                                // 
                                // if (tValBranch >= startHeightCluster && next[n].tValBranch < endHeightCluster)
                                // {
                                //     //   |------v---*----*---v---------*
                                //     //          ^   ^    ^   ^-endHeightCluster
                                //     //          |   |    -next[n].tValBranch
                                //     //          |   -tValBranch
                                //     //          -startHeightCluster
                                // 
                                //     startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, 0f, 1f));
                                //     if (activeBranchIndex != -1)
                                //     {
                                //         branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, 0f, 1f));
                                //     }
                                // }


                                // if (tValBranch >= startHeightCluster && next[0].tValBranch <= endHeightCluster)
                                // {
                                //     if (next[n].tValBranch >= startHeightCluster && tValGlobal <= endHeightGlobal) // TODO: same for branch tVals........................
                                //     {
                                //         float startTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                // 
                                //         float endTval = (endHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                // 1
                                //         //   |------*-------*---------*
                                //         //          ^   ^   ^-next[n].tValBranch
                                //         //          |   -startHeightCluster 
                                //         //          -tValBranch
                                // 
                                //         startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, startTval, endTval)); // TODO
                                //                                                                                 // branchNodesNextIndexStartTval[activeBranchIndex].Add(new StartNodeInfo(this, n, (startHeightCluster - tValBranch) / (next[0].tValBranch - tValBranch))); // startTval: tval between startNode and startNode.next
                                //                                                                                 // Debug.Log("in getAllStartNodes: branchNodesNextIndexStartTval[" + activeBranchIndex + "][" + n + "]: " + branchNodesNextIndexStartTval[activeBranchIndex][branchNodesNextIndexStartTval[activeBranchIndex].Count - 1]);
                                //         if (activeBranchIndex != -1)
                                //         {
                                //             float branchStartTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                                //             branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, branchStartTval, 1f));
                                //         }
                                //     }
                                // 
                                // }
                                //     0     0.3      0.6      1
                            }
                        }
                        nrSplitsPassedAtStartNode.Add(nrSplitsPassed);             //     |------*----v---*-------*
                                                                                   // }
                    }
                    // else // ??? why is this ever true???
                    // {
                    //     if (tValGlobal >= startHeightGlobal && tValGlobal <= endHeightGlobal) // it next.Count == 0 then tValBranch is 1 > startHeightCluster
                    //     {
                    //         if (next.Count > 0)
                    //         {
                    //             for (int n = 0; n < next.Count; n++)
                    //             {
                    //                 if (next[n].tValBranch >= startHeightCluster && tValGlobal <= endHeightGlobal)
                    //                 {
                    //                     float startTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                    // 
                    //                     float endTval = (endHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                    // 
                    //                     //   |------*-------*---------*
                    //                     //          ^   ^   ^-next[n].tValBranch
                    //                     //          |   -startHeightCluster 
                    //                     //          -tValBranch
                    // 
                    //                     startNodesNextIndexStartTvalEndTval.Add(new StartNodeInfo(this, n, startTval, endTval)); // TODO
                    //                     // branchNodesNextIndexStartTval[activeBranchIndex].Add(new StartNodeInfo(this, n, 0)); // 0 (?)
                    //                     if (activeBranchIndex != -1)
                    //                     {
                    //                         float branchStartTval = (startHeightCluster - tValBranch) / (next[n].tValBranch - tValBranch);
                    //                         branchNodesNextIndexStartTvalEndTval[activeBranchIndex].Add(new StartNodeInfo(this, n, branchStartTval, 1f));
                    //                     }
                    //                 }
                    //             }
                    //             nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
                    //         }
                    //     }
                    //     else
                    //     {
                    //         if (tValGlobal > endHeightGlobal)
                    //         {
                    //             if (tValGlobal < startHeightGlobal)
                    //             {
                    //                 Debug.Log("clusterIndex: " + clusterIndex + ", branch startNode not added because (tValGlobal = " + tValGlobal + ") < (startHeightGlobal = " + startHeightGlobal + ") AND (tValGlobal = " + tValGlobal + ") > (endHeight = " + endHeightGlobal + ")");
                    //             }
                    //             else
                    //             {
                    //                 Debug.Log("clusterIndex: " + clusterIndex + ", branch startNode not added because (tValGlobal = " + tValGlobal + ") > endHeight = " + endHeightGlobal + ")");
                    //             }
                    //         }
                    //         else
                    //         {
                    //             if (tValGlobal < startHeightGlobal)
                    //             {
                    //                 Debug.Log("clusterIndex: " + clusterIndex + ", branch startNode not added because (tValGlobal = " + tValGlobal + ") < (startHeightGlobal = " + startHeightGlobal + ") | tValBranch: " + tValBranch + ", startHeightCluster: " + startHeightCluster);
                    //             }
                    //         }
                    //     }
                    // }
                    if (next.Count > 1)
                    {
                        nrSplitsPassed += 1;
                    }
                    foreach (node n in next)
                    {
                        n.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, activeBranchIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeightGlobal, startHeightCluster, endHeightGlobal, endHeightCluster, level + 1, parentClusterBools, parentLevelCounter);
                    }
                }
                else
                {
                    foreach (node n in next)
                    {
                        n.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, activeBranchIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeightGlobal, startHeightCluster, endHeightGlobal, endHeightCluster, level, parentClusterBools, parentLevelCounter);
                    }
                    //int branchIndex = 0; // test!
                    foreach (List<node> c in branches) // branchNodesNextIndex: one list<(node, int)> for each branch
                    {
                        branchNodesNextIndexStartTvalEndTval.Add(new List<StartNodeInfo>());
                        foreach (node n in c)
                        {
                            for (int i = 0; i < n.next.Count; i++)
                            {
                                branchNodesNextIndexStartTvalEndTval[branchNodesNextIndexStartTvalEndTval.Count - 1].Add(new StartNodeInfo(n, i, 0f, 1f)); // 0 (?)
                            }
                            n.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, activeBranchIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeightGlobal, startHeightCluster, endHeightGlobal, endHeightCluster, level, parentClusterBools, parentLevelCounter + 1);
                        }
                        //branchIndex += 1; // test!
                    }
                }
            }
        }
    }

    // safety copy
    // public void getAllStartNodes(List<(node, int)> startNodesNextIndex, List<(node, int)> branchNodesNextIndex, List<int> nrSplitsPassedAtStartNode, int nrSplitsPassed, float startHeight, float endHeight, int level, List<bool> parentClusterBools, int parentLevelCounter)
    // {
    //     //Debug.Log("parentClusterBools.Count: " + parentClusterBools.Count + ", clusterIndex: " + clusterIndex);
    //     if (clusterIndex == -1)
    //     {
    //         // stem
    //         //Debug.Log("start nodes in stem!");
    //         if (tValGlobal >= startHeight && tValGlobal <= endHeight)
    //         {
    //             if (next.Count > 0)
    //             {
    //                 for (int n = 0; n < next.Count; n++)
    //                 {
    //                     startNodesNextIndex.Add((this, n));
    //                 }
    //                 nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
    //             }
    //         }
    //         if (next.Count > 1)
    //         {
    //             nrSplitsPassed += 1;
    //         }
    //         foreach (node n in next)
    //         {
    //             n.getAllStartNodes(startNodesNextIndex, branchNodesNextIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeight, endHeight, level + 1, parentClusterBools, parentLevelCounter);
    //         }
    //     }
    //     else
    //     {
    //         //Debug.Log("start nodes in cluster: " + clusterIndex + ", parentLevelCounter: " + parentLevelCounter + ", level: " + level);
    // 
    //         if (parentClusterBools[clusterIndex + 1] == true) // TEST +1 TEST !!!
    //         {
    //             if (tValGlobal >= startHeight && tValGlobal <= endHeight)
    //             {
    //                 if (next.Count > 0)
    //                 {
    //                     for (int n = 0; n < next.Count; n++)
    //                     {
    //                         startNodesNextIndex.Add((this, n));
    //                     }
    //                     nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
    //                 }
    //             }
    //             if (next.Count > 1)
    //             {
    //                 nrSplitsPassed += 1;
    //             }
    //             foreach (node n in next)
    //             {
    //                 n.getAllStartNodes(startNodesNextIndex, branchNodesNextIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeight, endHeight, level + 1, parentClusterBools, parentLevelCounter);
    //             }
    //         }
    //         else
    //         {
    //             foreach (node n in next)
    //             {
    //                 n.getAllStartNodes(startNodesNextIndex, branchNodesNextIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeight, endHeight, level, parentClusterBools, parentLevelCounter);
    //             }
    //             foreach (List<node> c in branches)
    //             {
    //                 foreach (node n in c)
    //                 {
    //                     for (int i = 0; i < n.next.Count; i++)
    //                     {
    //                         branchNodesNextIndex.Add((n, i));
    //                     }
    //                     n.getAllStartNodes(startNodesNextIndex, branchNodesNextIndex, nrSplitsPassedAtStartNode, nrSplitsPassed, startHeight, endHeight, level, parentClusterBools, parentLevelCounter + 1);
    //                 }
    //             }
    //         }
    //     }
    // }

    public void getAllNodes(List<node> allNodes)
    {
        allNodes.Add(this);
        foreach (node n in next)
        {
            n.getAllNodes(allNodes);
        }
        foreach (List<node> c in branches)
        {
            foreach (node n in c)
            {
                n.getAllNodes(allNodes);
            }
        }
    }

    public void getAllBranchNodes(List<node> allBranchNodes, int branchCluster) // rootNode.getAllBranchNodes(startNodes, l, 1); // starts with l = 1
    {
        if (clusterIndex == branchCluster)
        {
            allBranchNodes.Add(this);
            return;
        }

        foreach (List<node> c in branches)
        {
            foreach (node n in c)
            {
                n.getAllBranchNodes(allBranchNodes, branchCluster);
            }
        }

        foreach (node n in next)
        {
            n.getAllBranchNodes(allBranchNodes, branchCluster);
        }
    }

    public void getAllSegments(List<segment> allSegments, bool connectedToPrev)
    {
        //foreach (node n in next)
        for (int nextIndex = 0; nextIndex < next.Count; nextIndex++)
        {
            if (float.IsNaN(point.x))
            {
                Debug.Log("ERROR point is NaN!");
            }
            //if (next.Count > 1)
            //{
            //    Debug.Log("next: count: " + next.Count);
            //    Debug.Log("next: start point same? " + point);
            //}
            if (tangent.Count > 1) // list<tangent> for splits! [tangentIn, tangentOutA, tangentOutB]
            {
                int index = nextIndex + 1;
                //Debug.Log("tangent count: " + tangent.Count + ", using tangent index " + index + ", next count: " + next.Count);
                //Debug.Log("next[0].point: " + next[0].point + ", next[1].point: " + next[1].point);

                allSegments.Add(new segment(point, next[nextIndex].point, tangent[nextIndex + 1], next[nextIndex].tangent[0], cotangent, next[nextIndex].cotangent, radius, next[nextIndex].radius, ringResolution, false, gen));
                // Vector3 a = norm(next[nextIndex].point - point);
                // Vector3 b = norm(tangent[nextIndex + 1]);
                // if (a != b)
                // {
                //     Debug.Log("ERROR: next[nextIndex].point - point: " + a + ", tangent[i + 1]: " + b  +"radius: " + radius);
                //     gen.debugErrorPoints.Add(point);
                //     gen.debugErrorPoints.Add(next[nextIndex].point);
                // }
                //gen.debugLinesRed.Add(new line(point, point + tangent[nextIndex + 1]));
                //gen.debugLinesRed.Add(new line(next[nextIndex].point, next[nextIndex].point + next[nextIndex].tangent[0] * 1.4f));

               
            }
            else
            {
                //Debug.Log("tangent count: " + tangent.Count); // 1
                //Debug.Log("next count: " + next.Count); // 1

                allSegments.Add(new segment(point, next[nextIndex].point, tangent[0], next[nextIndex].tangent[0], cotangent, next[nextIndex].cotangent, radius, next[nextIndex].radius, ringResolution, connectedToPrev, gen));

                //gen.debugLinesRed.Add(new line(point, point + tangent[0]));
                //gen.debugLinesRed.Add(new line(next[nextIndex].point, next[nextIndex].point + next[nextIndex].tangent[0] * 1.4f));
            }
            next[nextIndex].getAllSegments(allSegments, true);
        }

        if (clusterIndex == 0)
        {
            gen.debugPointsRed.Add(point);
        }

        foreach (List<node> l in branches)
        {
            foreach (node c in l)
            {
                //Debug.Log("branch start point: " + c.point);
                //Debug.Log("branch next count: " + c.next.Count);
                c.getAllSegments(allSegments, false);
            }
        }
    }

    public node subdivideSegment(int nextIndex, float splitHeight)
    {
        Vector3 splitPoint = sampleSpline(point, next[nextIndex].point, tangent[nextIndex], next[nextIndex].tangent[0], splitHeight);
        Vector3 splitTangent = sampleSplineTangentT(point, next[nextIndex].point, tangent[nextIndex], next[nextIndex].tangent[0], splitHeight);
        Vector3 splitCotangent = vLerp(cotangent, next[nextIndex].cotangent, splitHeight);
        float t_global = fLerp(tValGlobal, next[nextIndex].tValGlobal, splitHeight); // TODO: only if node is in stem!
        float t_branch = 0f;
        Debug.Log("new node: clusterIndex: " + clusterIndex);
        node newNode = new node(splitPoint, splitTangent, splitCotangent, t_global, t_branch, taper, gen, this, clusterIndex, ringResolution);
        newNode.next = next;
        foreach (node n in next)
        {
            n.parent = newNode;
        }
        next.Clear();
        next.Add(newNode);
        newNode.parent = this;
        return newNode;
    }

    public void resampleSpline(int n, float noiseAmplitudeLower, float noiseAmplitudeUpper, float noiseScale)
    {
        if (n > 1)
        {
            node nodeNext = next[0];
            node currentNode = this;
            Vector3 prevPoint = point;
            Vector3 prevDirA = cotangent; // TODO: cancel screw!

            for (int i = 1; i < n; i++)
            {
                Vector3 dirA = vLerp(cotangent, nodeNext.cotangent, (float)i / (float)n);
                Vector3 dirB = norm(Vector3.Cross(sampleSplineTangentT(point, nodeNext.point, tangent[0], nodeNext.tangent[0], (float)i / (float)n), dirA));

                Vector3 samplePoint = sampleSpline(point, nodeNext.point, tangent[0], nodeNext.tangent[0], (float)i / (float)n);
                samplePoint += fLerp(noiseAmplitudeLower, noiseAmplitudeUpper, Mathf.Pow((float)i / (float)n, gen.noiseAmplitudeLowerUpperExponent)) * (dirA * Mathf.Sin((float)(5 * i) / noiseScale) + dirB * Mathf.Cos(((float)(5 * i) + 1.3f) / noiseScale));
                // TODO: simplex noise...

                Vector3 nextPoint = sampleSpline(point, nodeNext.point, tangent[0], nodeNext.tangent[0], (float)(i + 1) / (float)n);
                nextPoint += fLerp(noiseAmplitudeLower, noiseAmplitudeUpper, Mathf.Pow((float)i / (float)n, gen.noiseAmplitudeLowerUpperExponent)) * (dirA * Mathf.Sin(((float)(5 * i + 1)) / noiseScale) + dirB * Mathf.Cos(((float)(5 * i + 1) + 1.3f) / noiseScale));
                // TODO: simplex noise...

                // gen.debugSamplePoints.Add(samplePoint); // OK

                //Vector3 sampleTangent = sampleSplineTangentT(point, nodeNext.point, tangent[0], nodeNext.tangent[0], (float)i / (float)n); // does not work with noise added!
                Vector3 sampleTangent = norm(nextPoint - prevPoint);
                prevPoint = samplePoint;

                if (i == 2)
                {
                    gen.debugNext = nextPoint;
                    gen.debugPrev = prevPoint;
                }

                gen.debugSampleTangents.Add(sampleTangent);

                Vector3 sampleCotangent = vLerp(cotangent, nodeNext.cotangent, (float)i / (float)n);

                dirB = norm(Vector3.Cross(sampleTangent, sampleCotangent)); // TODO (find better strategy)

                float sampleTvalGlobal = fLerp(tValGlobal, nodeNext.tValGlobal, (float)i / (float)n);
                float sampleTvalBranch = fLerp(tValBranch, nodeNext.tValBranch, (float)i / (float)n);
                // improve sampleCotangent!
                sampleCotangent = norm(Vector3.Cross(dirB, sampleTangent));
                node newNode;
                if (i == 1)
                {
                    //Debug.Log("new node: clusterIndex: " + clusterIndex);
                    newNode = new node(samplePoint, sampleTangent, sampleCotangent, sampleTvalGlobal, sampleTvalBranch, taper, gen, this, clusterIndex, ringResolution);
                }
                else
                {
                    //Debug.Log("new node: clusterIndex: " + clusterIndex);
                    newNode = new node(samplePoint, sampleTangent, sampleCotangent, sampleTvalGlobal, sampleTvalBranch, taper, gen, currentNode, clusterIndex, ringResolution);
                }

                if (currentNode.next.Count == 0)
                {
                    currentNode.next.Add(newNode);
                }
                else
                {
                    currentNode.next[0] = newNode;
                }
                currentNode = newNode;
            }

            nodeNext.point += noiseAmplitudeUpper * new Vector3(Mathf.Sin((float)n / noiseScale), 0f, Mathf.Cos(((float)5 * n + 0.3f) / noiseScale));

            currentNode.next.Add(nodeNext);
        }
    }

    public void curveBranches(float curvature, Vector3 axis)
    {
        curveStep(-curvature, norm(axis), point, true);

        foreach (node n in next)
        {
            n.curveBranches(curvature, axis);
        }
    }


    public void applyCurvature(float curvature, Vector3 axis)
    {
        // centerLine
        //rootNode = new node(new Vector3(0f, 0f, 0f), new Vector3(0f, 1f, 0f), Vector3.Cross(treeGrowDir, new Vector3(treeGrowDir.x, 0f, treeGrowDir.z)), this, null);
        //
        //rootNode.cotangent = norm(Vector3.Cross(dirB, rootNode.tangent[0]));
        //
        //rootNode.next.Add(new node(norm(treeGrowDir) * treeHeight, nextTangent, new Vector3(1f, 1f, 1f), this, rootNode));

        //
        //rootNode.next.Add(new node(norm(treeGrowDir) * treeHeight, nextTangent, new Vector3(1f, 1f, 1f), this, rootNode));
        //rootNode.next[0].cotangent = norm(Vector3.Cross(rootNode.next[0].tangent[0], Vector3.Cross(rootNode.cotangent, rootNode.next[0].tangent[0])));

        //Debug.Log("applyCurvature: point: " + point);

        Vector3 nextTangent = norm(norm(gen.treeGrowDir) * gen.treeHeight - (gen.rootNode.point + gen.rootNode.tangent[0] * vLength(norm(gen.treeGrowDir) * gen.treeHeight - gen.rootNode.point) * (1.5f / 3f)));
        Vector3 centerPoint = sampleSpline(gen.rootNode.point, norm(gen.treeGrowDir) * gen.treeHeight, new Vector3(0f, 1f, 0f), nextTangent, tValGlobal);

        Vector3 outwardDir = point - centerPoint;

        Vector3 curveAxis = Vector3.Cross(outwardDir, tangent[0]);

        //gen.debugLinesBlue.Add(new line(point, centerPoint));

        //gen.debugLinesBlue.Add(new line(point, point + curveAxis));

        if (vLength(curveAxis) > 0f)
        {
            curveAxis = norm(curveAxis);

            curveStep(curvature, curveAxis, point, true);
        }

        foreach (node n in next)
        {
            n.applyCurvature(curvature, axis);
        }
    }

    public void curveStep(float curvature, Vector3 curveAxis, Vector3 rotationPoint, bool firstNode)
    {
        point = rotationPoint + Quaternion.AngleAxis(curvature, curveAxis) * (point - rotationPoint);
        if (firstNode == true)
        {
            for (int tangentIndex = 0; tangentIndex < tangent.Count; tangentIndex++)
            {
                tangent[tangentIndex] = Quaternion.AngleAxis(curvature / 2f, curveAxis) * tangent[tangentIndex];
            }
        }
        else
        {
            for (int tangentIndex = 0; tangentIndex < tangent.Count; tangentIndex++)
            {
                tangent[tangentIndex] = Quaternion.AngleAxis(curvature, curveAxis) * tangent[tangentIndex];
            }
        }

        foreach (node n in next)
        {
            n.curveStep(curvature, curveAxis, rotationPoint, false);
        }
    }

    public void grow()
    {

    }

    public float lengthToTip()
    {
        if (next.Count > 0)
        {
            return next[0].lengthToTip() + vLength(next[0].point - point);
        }
        else
        {
            return 0f;
        }
    }

    public int nodesToTip(int i)
    {
        if (next.Count > 0)
        {
            if (i > 500)
            {
                Debug.Log("ERROR: in nodesToTip(): max iteration reached!");
                return i;
            }
            return (1 + next[0].nodesToTip(i + 1));
        }
        else
        {
            return 1;
        }
    }

    public float calculateRadius(float maxRadius)
    {
        if (next.Count > 0 || branches.Count > 0)
        {
            float sum = 0f;
            if (next.Count > 0)
            {
                float max = 0f;
                foreach (node n in next)
                {
                    float s = n.calculateRadius(maxRadius);
                    s += vLength(n.point - point) * n.taper * n.taper;
                    if (s > max)
                    {
                        max = s;
                    }
                }
                sum = max;
            }
            if (branches.Count > 0)
            {
                foreach (List<node> c in branches)
                {
                    foreach (node n in c)
                    {
                        n.calculateRadius(sum);
                    }
                }
            }
            if (sum < maxRadius) // clamp radius to radius of parent branch
            {
                radius = sum;
            }
            else
            {
                radius = maxRadius;
            }
            //Debug.Log("crossSection: " + sum);
            return sum;
        }
        else
        {
            radius = gen.branchTipRadius;
            return radius;
        }
    }

    static float fLerp(float a, float b, float t)
    {
        return (a + (b - a) * t);
    }

    static Vector3 vLerp(Vector3 a, Vector3 b, float t)
    {
        return (a + (b - a) * t);
    }

    static float vLength(Vector3 v)
    {
        return Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    }

    static Vector3 norm(Vector3 v)
    {
        return v / Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    }

    //static Vector3 sampleSplineC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    //{
    //    return ((1f - t) * (1f - t) * (1f - t) * controlA + 3f * (1f - t) * (1f - t) * t * controlB + 3f * (1f - t) * t * t * controlC + t * t * t * controlD);
    //}

    public static Vector3 sampleSpline(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;

        return (1f - t) * (1f - t) * (1f - t) * start + 3f * (1f - t) * (1f - t) * t * controlPt1 + 3f * (1f - t) * t * t * controlPt2 + t * t * t * end;
    }

    //Vector3 controlPt1 = allSegments[s].start + allSegments[s].startTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
    //        Vector3 controlPt2 = allSegments[s].end - allSegments[s].endTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f;


    //static Vector3 sampleSplineTangentC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    //{
    //    //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
    //    return norm((-3f * (1f - t) * (1f - t) * controlA + 3f * (3f * t * t - 4f * t + 1f) * controlB + 3f * (-3f * t * t + 2f * t) * controlC + 3f * t * t * controlD));
    //}

    static Vector3 sampleSplineTangentT(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;
        //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
        return norm(-3f * (1f - t) * (1f - t) * start + 3f * (3f * t * t - 4f * t + 1f) * controlPt1 + 3f * (-3f * t * t + 2f * t) * controlPt2 + 3f * t * t * end);
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return 6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD;
    }


}

public class segment
{
    public Vector3 start;
    public Vector3 end;
    public Vector3 startTangent;
    public Vector3 endTangent;
    public Vector3 startCotangent;
    public Vector3 endCotangent;
    public int sections;
    public float startRadius;
    public float endRadius;
    public float taper;
    public int ringResolution;
    public bool connectedToPrevious;
    public treeGen3 treeGen;

    public List<Vector3> vertices;
    public List<Vector2> UVs;
    public List<int> triangles;

    public segment(Vector3 Start, Vector3 End, Vector3 startTan, Vector3 endTan, Vector3 startCotan, Vector3 endCotan, float StartRadius, float EndRadius, int ringRes, bool connected, treeGen3 gen)
    {
        start = Start;
        end = End;
        startTangent = startTan;
        startCotangent = startCotan;
        endTangent = endTan;
        endCotangent = endCotan;
        startRadius = StartRadius;
        endRadius = EndRadius;
        ringResolution = ringRes;
        connectedToPrevious = connected;
        taper = 1f;
        vertices = new List<Vector3>();
        UVs = new List<Vector2>();
        triangles = new List<int>();
        treeGen = gen;
    }
}

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class treeGen3 : MonoBehaviour
{
    [Range(0f, 0.1f)]
    public float gizmoRadius;
    [Range(0f, 0.2f)]
    public float normalGizmoSize;
    public List<Vector3> vertices;
    public List<int> triangles;
    public List<Vector3> normals;
    public List<Vector2> UVs;
    public Mesh mesh;
    public MeshFilter meshFilter;

    public Random random;

    public node rootNode;
    public List<segment> allSegments;

    public float treeHeight;
    public Shape treeShape;
    public List<Shape> branchShape;
    public Vector3 treeGrowDir;

    [Range(0f, 0.5f)]
    public float taper; // TODO: taper for stem and branches
    public List<float> taperFactor; // for each branch cluster
    [Range(0f, 0.01f)]
    public float branchTipRadius;
    [Range(0.001f, 1f)]
    public float ringSpacing;
    public int stemRingResolution;
    public List<int> clusterRingResolution; // for each branch cluster
    [Range(1, 25)]
    public int resampleNr;
    [Range(0f, 1f)]
    public float noiseAmplitudeLower;
    [Range(0f, 1f)]
    public float noiseAmplitudeUpper;
    [Range(1f, 5f)]
    public float noiseAmplitudeLowerUpperExponent;
    [Range(0.1f, 10f)]
    public float noiseScale;
    [Range(-20f, 20f)]
    public float splitCurvature;
    [Range(0, 200)]
    public int testRecursionStop;

    [Range(0, 20)]
    public int shyBranchesIterations;
    public float shyBranchesMaxDistance;
    [Range(0, 50)]
    public int nrSplits;

    public splitMode stemSplitMode;
    [Range(0f, 0.75f)]
    public float variance;

    [Range(0f, 10f)]
    public float curvOffsetStrength;
    
    public List<float> splitHeightInLevel;
    public List<List<float>> branchSplitHeightInLevel;
    public List<float> branchSplitHeightVariation;
    [Range(0f, 1f)]
    public float splitHeightVariation;
    [Range(0f, 90f)]
    public float testSplitAngle;
    public float stemSplitRotateAngle;
    [Range(0f, 90f)]
    public float testSplitPointAngle;

    public float[] splitProbabilityInLevel;
    public int[] expectedSplitsInLevel;

    public int nrBranchClusters;

    //public List<int> parentClusterIndex;
    public List<List<bool>> parentClusterBools;
    public List<int> nrBranches;
    [Range(0f, 1f)]
    public List<float> relBranchLength;
    [Range(0f, 45f)]
    public List<float> verticalRange;
    [Range(-90f, 90f)]
    public List<float> verticalAngleCrownStart;
    [Range(-90f, 90f)]
    public List<float> verticalAngleCrownEnd;
    public List<float> verticalAngleBranchStart;
    public List<float> verticalAngleBranchEnd;
    public List<float> rotateAngle;
    public List<float> rotateAngleRange;
    //public bool symmetric; // TODO
    public List<float> branchesStartHeightGlobal;
    public List<float> branchesStartHeightCluster;
    public List<float> branchesEndHeightGlobal;
    public List<float> branchesEndHeightCluster;
    [Range(-90f, 90f)]
    public List<float> branchCurvature;
    public List<float> nrSplitsPerBranch;
    public List<float> splitsPerBranchVariation;

    public List<angleMode> branchAngleMode;
    public List<splitMode> branchSplitMode;
    public List<float> branchSplitRotateAngle;
    public int nrLeaves;
    public float leafSize;
    public int seed;

    public List<int> nodeIndices;
    public int meanLevel;

    public List<line> debugDisplacementLines;
    public List<line> debugRepulsionForces;

    public List<line> tangentDebugLines;
    public List<line> dirAdebugLines;
    public List<line> dirBdebugLines;
    public List<line> debugLinesRed;
    public List<line> debugLinesGreen;

    public List<line> debugLinesBlue;

    public List<Vector3> debugList;
    public List<Vector3> debugListRadius;
    public List<Vector3> debugListGreen;
    public List<Vector3> debugListRed;
    public List<Vector3> debugListBlue;

    public List<Vector3> debugSamplePoints;
    public List<Vector3> debugSampleTangents;

    public List<Vector3> debugErrorPoints;
    public List<Vector3> debugErrorPointsCompare;
    public List<Vector3> debugPointsRed;

    public Vector3 debugPrev;
    public Vector3 debugNext;
    public Vector3 debugSplitDirA;
    public Vector3 debugSplitDirB;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }
    public void initTree()
    {
        random = new Random(seed);

        debugDisplacementLines = new List<line>();
        debugRepulsionForces = new List<line>();
        tangentDebugLines = new List<line>();
        dirAdebugLines = new List<line>();
        dirBdebugLines = new List<line>();
        debugLinesBlue = new List<line>();
        debugLinesGreen = new List<line>();
        debugLinesRed = new List<line>();
        debugList = new List<Vector3>();
        debugListRadius = new List<Vector3>();
        debugListGreen = new List<Vector3>();
        debugListRed = new List<Vector3>();
        debugListBlue = new List<Vector3>();
        debugSamplePoints = new List<Vector3>();
        debugSampleTangents = new List<Vector3>();
        debugErrorPoints = new List<Vector3>();
        debugErrorPointsCompare = new List<Vector3>();
        debugPointsRed = new List<Vector3>();

        vertices = new List<Vector3>();
        triangles = new List<int>();
        normals = new List<Vector3>();
        UVs = new List<Vector2>();

        allSegments = new List<segment>();

        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();
    }

    List<segment> getAllSegments()
    {
        List<segment> allSegments = new List<segment>();
        if (rootNode != null)
        {
            rootNode.getAllSegments(allSegments, false);
        }
        //Debug.Log("allSegmants count " + allSegments.Count);
        return allSegments;
    }

    public void addBranches()
    {
        //Debug.Log("in addBranches: nrBranchLevels: " + nrBranchClusters);
        if (nrBranches == null)
        {
            nrBranches = new List<int>();
        }
        //Debug.Log("in addBranches: nrbranches.Count: " + nrBranches.Count);
        //for (int branchIndex = 0; branchIndex < nrBranches.Count; branchIndex++)
        //{
        //    Debug.Log("in addBranches: nrBranches[" + branchIndex + "]: " + nrBranches[branchIndex]);
        //}

        float minAngle = 999f;
        float maxAngle = -999f;

        for (int i = 0; i < parentClusterBools.Count; i++)
        {
            Debug.Log("in addBranches: parentClusterBools: "); 
            for (int j = 0; j < parentClusterBools[i].Count; j++)
            {
                if (parentClusterBools[i][j] == true)
                    Debug.Log("in addBranches: parentClusterBools[" + i + "][" + j + "]: true");
                else
                    Debug.Log("in addBranches: parentClusterBools[" + i + "][" + j + "]: false"); // OK
            }
        }

        for (int clusterIndex = 0; clusterIndex < nrBranchClusters; clusterIndex++)
        {
            Debug.Log("in addBranches: add branches cluster " + clusterIndex + ": nr: " + nrBranches[clusterIndex]);
            List<StartNodeInfo> startNodesNextIndexStartTvalEndTval = new List<StartNodeInfo>(); // (startNode, nextIndex, startTval, endTval) // startTval: 0..1 from startNode to startNode.next
            List<List<StartNodeInfo>> branchNodesNextIndexStartTvalEndTval = new List<List<StartNodeInfo>>(); // one list for each branch, startTvalNode
            for (int i = 0; i < nrBranches[clusterIndex - 1 >= 0 ? clusterIndex - 1 : clusterIndex]; i++) // TEST!
            {
                branchNodesNextIndexStartTvalEndTval.Add(new List<StartNodeInfo>());
            }
            List<int> nrSplitsPassedAtStartNode = new List<int>();

            // if (clusterIndex == 0)
            // {
            //     Debug.Log("branchesStartHeight.Count: " + branchesStartHeight.Count + ", branchesEndHeight.Count: " + branchesEndHeight.Count);
            //     rootNode.getAllStartNodes(startNodesNextIndex, nrSplitsPassedAtStartNode, 0, branchesStartHeight[0], branchesEndHeight[0], 0, parentClusterBools[0], 0); // TODO...
            //     Debug.Log("in addBranches: branchLevel: l = 0, getAllStartNodes: startNodes.Count: " + startNodesNextIndex.Count);
            // 
            //     Debug.Log("startNodes.Count: " + startNodesNextIndex.Count); // 30
            // }
            // else
            // {
            //     Debug.Log("in addBranches: branchCluster: " + clusterIndex);
            //     //Debug.Log("parentClusterIndex.count: " + parentClusterIndex.Count);
            //     //Debug.Log("parentClusterIndex[c]: " + parentClusterIndex[c]);
            //     Debug.Log("startNodes.Count: " + startNodesNextIndex.Count);
            //     rootNode.getAllStartNodes(startNodesNextIndex, nrSplitsPassedAtStartNode, 0, branchesStartHeight[clusterIndex], branchesEndHeight[clusterIndex], clusterIndex, parentClusterBools[clusterIndex], 0);

            // old code:
            // for (int j = 0; j < parentClusterBools[clusterIndex].Count; j++)
            // {
            //     if (parentClusterBools[clusterIndex][j] == true)
            //     {
            //         rootNode.getAllStartNodes(startNodesNextIndex, nrSplitsPassedAtStartNode, 0,
            //                     branchesStartHeight[clusterIndex], branchesEndHeight[clusterIndex], j, parentClusterBools[clusterIndex], 0);
            //     }
            // }

            bool useTvalBranch = true; // TODO...
            if (parentClusterBools.Count > clusterIndex)
            {
                if (parentClusterBools[clusterIndex].Count > 0)
                {
                    if (parentClusterBools[clusterIndex][0] == true) // TODO...
                    {
                        useTvalBranch = false;
                    }
                }
            }
            
            if (useTvalBranch == true)
            {

            }

            // new code (AI)
            for (int j = 0; j < parentClusterBools[clusterIndex].Count; j++)
            {
                if (parentClusterBools[clusterIndex][j] == true)
                {
                    if (j == 0)
                    {
                        Debug.Log("branchesStartHeightGlobal.Count: " + branchesStartHeightGlobal.Count + ", branchesStartHeightCluster.Count: " + branchesStartHeightCluster.Count + "startNodesNextIndexStartTval.Count: " + startNodesNextIndexStartTvalEndTval.Count + ", clusterIndex: " + clusterIndex);
                        // Start from the stem
                        Debug.Log("in addBranches: parentClsuterBool[clusterIndex=" + clusterIndex + "][" + j + "], startNodesNextIndexStartTval.Count: " + startNodesNextIndexStartTvalEndTval.Count);

                        rootNode.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, -1, nrSplitsPassedAtStartNode, 0,
                                                    branchesStartHeightGlobal[clusterIndex], branchesStartHeightCluster[clusterIndex], branchesEndHeightGlobal[clusterIndex],
                                                    branchesEndHeightCluster[clusterIndex], j, parentClusterBools[clusterIndex], 0);

                        Debug.Log("startNodesNextIndexStartTval.Count: " + startNodesNextIndexStartTvalEndTval.Count);

                        for (int b = 0; b < branchNodesNextIndexStartTvalEndTval.Count; b++)
                        {
                            Debug.Log("clusterIndex=" + clusterIndex + ", j: " + j + ", branchNodesNextIndex[" + b + "].Count: " + branchNodesNextIndexStartTvalEndTval[b].Count);
                        }
                    }
                    else
                    {
                        // Start from all nodes in cluster j
                        List<node> parentNodes = new List<node>();
                        rootNode.getAllBranchNodes(parentNodes, j - 1); // !!!
                        Debug.Log("in addBranches: clusterIndex: " + clusterIndex + ", parentNodes.Count: " + parentNodes.Count); // OK
                        int activeBranchIndex = -1;
                        foreach (node n in parentNodes)
                        {
                            n.getAllStartNodes(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, activeBranchIndex, nrSplitsPassedAtStartNode, 0,
                                                branchesStartHeightGlobal[clusterIndex], branchesStartHeightCluster[clusterIndex], branchesEndHeightGlobal[clusterIndex],
                                                branchesEndHeightCluster[clusterIndex], j, parentClusterBools[clusterIndex], 0); // startNodesNextIndex.Count = 49 OK !!!
                            activeBranchIndex += 1; // TEST!
                        }
                        Debug.Log("in addBranches: parentClusterBool[clusterIndex=" + clusterIndex + "][" + j + "], startNodesNextIndex.Count: " + startNodesNextIndexStartTvalEndTval.Count + ", parentNodes.Count: " + parentNodes.Count);
                        // ERROR HERE: startNodesNextIndex.Count = 0 for clusterIndex=1 and branchesStartHeightCluster > 0 !!!
                        for (int b = 0; b < branchNodesNextIndexStartTvalEndTval.Count; b++)
                        {
                            Debug.Log("clusterIndex=" + clusterIndex + ", j: " + j + ", branchNodesNextIndex[" + b + "].Count: " + branchNodesNextIndexStartTvalEndTval[b].Count);
                        }
                    }
                }  // branchNodesNextIndex: one list<(node, int)> for each branch
            }




            if (clusterIndex > 0)
            {
                for (int i = 0; i < startNodesNextIndexStartTvalEndTval.Count; i++)
                {
                    nrSplitsPassedAtStartNode.Add(0); // TODO
                }
            }

            float windingAngle = 0f;
            //Debug.Log("branchCluster: " + clusterIndex + ", startNodes: " + startNodesNextIndex.Count);
            
            if (startNodesNextIndexStartTvalEndTval.Count > 0)
            {
                // NEW: startNodeIndex calculation (AI) ----------------------------
                // 1. Calculate segment lengths and total length


                //----------------
                List<float> segmentLengths = new List<float>();
                
                if (parentClusterBools[clusterIndex][0] == true) // TODO...
                {
                    useTvalBranch = false;
                }
                Debug.Log("useTvalBranch: " + useTvalBranch);
                float totalLength = calculateSegmentLengthsAndTotalLength(startNodesNextIndexStartTvalEndTval, branchNodesNextIndexStartTvalEndTval, segmentLengths, clusterIndex, useTvalBranch);
                //List<float> segmentTStart = new List<float>();
                //List<float> segmentTEnd = new List<float>();
                
                Debug.Log("clusterIndex: " + clusterIndex + ", startNodesNextIndex.Count: " + startNodesNextIndexStartTvalEndTval.Count + ", totalLength: " + totalLength);
                // ERROR HERE: clusterIndex: 1, startNodesNextIndex.Count: 124, totalLength: 0

                Debug.Log("clusterIndex: " + clusterIndex + ", startNodesNextIndex.Count: " + startNodesNextIndexStartTvalEndTval.Count + ", branchNodesNextIndexStartTval.Count: " + branchNodesNextIndexStartTvalEndTval.Count);

                for (int i = 0; i < branchNodesNextIndexStartTvalEndTval.Count; i++)
                {
                    //Debug.Log("branch: " + i);
                    for (int j = 0; j < branchNodesNextIndexStartTvalEndTval[i].Count; j++)
                    {
                        Debug.Log("branchNodesNextIndexStartTval[" + i + "][" + j + "]: startTval:" + branchNodesNextIndexStartTvalEndTval[i][j].startTval); // OK ([0...1] for entire branch!)
                    }
                }

                // in getAllStartNodes: 
                //
                // for (int n = 0; n < next.Count; n++)
                // {
                //     startNodesNextIndex.Add((this, n));
                //     branchNodesNextIndexStartTval[activeBranchIndex].Add(new StartNodeInfo(this, n, (startHeightCluster - tValBranch) / (next[0].tValBranch - tValBranch))); // startTval: tval between startNode and startNode.next
                // }
                // nrSplitsPassedAtStartNode.Add(nrSplitsPassed); //     |------*----v---*-------*
                // //                                                    0     0.3      0.6      1


                //Debug.Log("startNodesNextIndex.Count: " + startNodesNextIndex.Count + ", totalLength: " + totalLength); // 30, 0
                //Debug.Log("segmentTStart.Count: " + segmentTStart.Count + ", segmentTEnd.Count: " + segmentTEnd.Count + ", segmentLengths.Count: " + segmentLengths.Count);
                //                                         0                                                 0                                              0
                //-----------------------------------------------------------------

                //Debug.Log("nrBranches[" + clusterIndex + "]: " + nrBranches[clusterIndex]);
                for (int branchIndex = 0; branchIndex < nrBranches[clusterIndex]; branchIndex++) // nrBranches[0] // TODO: get the branch of the startNode!
                {
                    // NEW: startNodeIndex calculation (AI) ---------------------------
                    float branchPos = branchIndex * totalLength / nrBranches[clusterIndex]; // (branchIndex + 0.5) for center of segment <- TEST OFF!

                    // add random offset to branchPos (AI)
                    float avgSegmentLength = totalLength / nrBranches[clusterIndex];

                    // float branchPosOffset = ((float)random.NextDouble() - 0.5f) * 0.2f * avgSegmentLength; // TEST OFF
                    // branchPos += branchPosOffset;

                    // Find which segment this branch falls into
                    float accumLength = 0f;
                    int startNodeIndex = 0;
                    float t = 0f;
                    for (int i = 0; i < segmentLengths.Count; i++)
                    {
                        if (accumLength + segmentLengths[i] >= branchPos)
                        {
                            startNodeIndex = i;
                            float segStart = accumLength;
                            float segLen = segmentLengths[i];
                            t = segLen > 0f ? (branchPos - segStart) / segLen : 0f; // TODO: startTval...

                            // Ensure t is above startTval if startTval > 0
                            float startTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].startTval; // todo
                            float endTval = startNodesNextIndexStartTvalEndTval[startNodeIndex].endTval;
                            if (startTval > 0f && t < startTval)
                            {
                                t = startTval;
                            }
                            if (startTval > 0f && t > endTval)
                            {
                                t = endTval;
                            }
                            break;
                        }
                        accumLength += segmentLengths[i];
                    }

                    int startNodeNextIndex = startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex;
                    //-----------------------------------------------------------------

                    node nStart = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode;  // TODO: get the branch of the startNode!
                    //nStart.

                    // TODO: winding -> equal distances -> add random offsets

                    Vector3 tangent;
                    if (startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next.Count > 1)
                    {
                        tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[startNodeNextIndex + 1];
                    }
                    else
                    {
                        tangent = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[0];
                    }
                    // Map t from [0,1] to [tA, tB]
                    //Debug.Log("startNodeIndex: " + startNodeIndex + ", startNodesNextIndex.Count: " + startNodesNextIndex.Count + ", segmentTStart.Count: " + segmentTStart.Count + ", segmentTEnd.Count: " + segmentTEnd.Count);
                    //float tVal = segmentTStart[startNodeIndex] + t * (segmentTEnd[startNodeIndex] - segmentTStart[startNodeIndex]);

                    Vector3 startPoint = sampleSplineT(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
                                                       startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point,
                                                       tangent,
                                                       startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].tangent[0],
                                                       t);
                    Vector3 startPointTangent = sampleSplineTangentT(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
                                                                     startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point,
                                                                     tangent,
                                                                     startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].tangent[0],
                                                                     t);

                    Vector3 branchDir = new Vector3(0f, 0f, 0f);

                    Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));

                    Vector3 centerPoint = sampleSplineT(rootNode.point, norm(treeGrowDir) * treeHeight, new Vector3(0f, 1f, 0f), nextTangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);
                    //debugPointsRed.Add(centerPoint);
                    Vector3 outwardDir = vLerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point, t) - centerPoint;

                    if (outwardDir == Vector3.zero)
                    {
                        outwardDir = vLerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, t);
                        Debug.Log("outwardDir is zero, using cotangent: " + outwardDir);
                    }
                    //Debug.Log("outwardDir: " + outwardDir);


                    outwardDir.y = 0f;

                    if (outwardDir == Vector3.zero)
                    {
                        outwardDir = vLerp(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.cotangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].cotangent, t);
                        Debug.Log("outwardDir is zero, using cotangent: " + outwardDir);
                    }
                    outwardDir = norm(outwardDir);
                    //debugLinesGreen.Add(new line(startPoint, startPoint + outwardDir));

                    // float dirRange = 360f / ((float)nrSplitsPassedAtStartNode[startNodeIndex] + 1f);
                    // if (dirRange < 15f)
                    // {
                    //     dirRange = 15f;
                    // } // -> new: rotateAngleRange

                    //float tValBranchesStartLevel = startNodesNextIndex[0].Item1.tVal;
                    //(1f - tValBranchesStartLevel) * startNodes[startNodeIndex].tVal + tValBranchesStartLevel

                    float globalVerticalAngle = fLerp(verticalAngleCrownStart[clusterIndex], verticalAngleCrownEnd[clusterIndex], startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal);
                    float branchVerticalAngle = 0f;
                    if (verticalAngleBranchEnd.Count > clusterIndex)
                    {
                        branchVerticalAngle = fLerp(verticalAngleBranchStart[clusterIndex], verticalAngleBranchEnd[clusterIndex], startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValBranch);
                    }
                    else
                    {
                        Debug.Log("ERROR: verticalAngleBranchEnd...");
                    }

                    float verticalAngle = globalVerticalAngle + branchVerticalAngle;



                    // 90 -> 0
                    // 0 -> -90


                    //Debug.Log("verticalAngleCrownStart[0]: " + verticalAngleCrownStart[clusterIndex] + ", verticalAngleCrownEnd[0]: " + verticalAngleCrownEnd[clusterIndex] + ", verticalAngle: " + verticalAngle);

                    // float newVerticalAngle = fLerp(verticalAngleCrownStart[0], verticalAngleCrownEnd[0], (1f - tValBranchesStartLevel) * startNodes[startNodeIndex].tVal + tValBranchesStartLevel);

                    //float calculatedTVal = (1f - tValBranchesStartLevel) * startNodesNextIndex[startNodeIndex].Item1.tVal + tValBranchesStartLevel;
                    // Debug.Log("newVerticalAngle: " + newVerticalAngle + ", tValBranchesStartLevel: " + tValBranchesStartLevel + 
                    //             ", tVal: " + startNodes[startNodeIndex].tVal + ", calculatedTVal: " + calculatedTVal);  


                    if (minAngle > verticalAngle)
                    {
                        minAngle = verticalAngle;
                    }
                    if (maxAngle < verticalAngle)
                    {
                        maxAngle = verticalAngle;
                    }

                    // Vector3 dirStart = norm(Quaternion.AngleAxis(-rotateAngleRange[l], startPointTangent) * outwardDir);
                    // Vector3 dirEnd = norm(Quaternion.AngleAxis(rotateAngleRange[l], startPointTangent) * outwardDir);
                    // Vector3 verticalStart = norm(Quaternion.AngleAxis(-verticalAngle + verticalRange[0], norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);
                    // Vector3 verticalEnd = norm(Quaternion.AngleAxis(-verticalAngle - verticalRange[0], norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);

                    // TODO: dir for angleMode winding...!

                    // outwartDir.y = 0 !!!

                    Vector3 centerDir; // ERROR HERE!
                    if (clusterIndex == 0)
                    {
                        centerDir = norm(Quaternion.AngleAxis(-verticalAngle, norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);
                    }
                    else
                    {
                        centerDir = Vector3.Cross(startPointTangent, new Vector3(0f, 1f, 0f));
                        if (vLength(centerDir) > 0f)
                        {
                            centerDir = Vector3.Cross(centerDir, startPointTangent);
                            if (vLength(centerDir) > 0f)
                            {
                                centerDir = norm(centerDir);
                            }
                            else
                            {
                                centerDir = outwardDir;
                                Debug.Log("SHOULD NEVER HAPPEN! centerDir = outwardDir");
                            }
                        }
                        else
                        {
                            centerDir = -norm(outwardDir);
                        }
                    }

                    // TEST: (???)
                    // Vector3 centerDir = norm(Quaternion.AngleAxis(-verticalAngle, norm(Vector3.Cross(startPointTangent, outwardDir))) * startPointTangent);
                    //
                    // TEST (AI) (???)
                    //Vector3 projectedUp = norm(Vector3.up - Vector3.Dot(Vector3.up, norm(startPointTangent)) * norm(startPointTangent));
                    //Vector3 centerDir = Quaternion.AngleAxis(verticalAngle, norm(startPointTangent)) * projectedUp;

                    


                    //debugLinesGreen.Add(new line(startPoint, startPoint + centerDir));

                    //Debug.Log("centerDir: " + centerDir); // (0, 0, -1)
                    //Debug.Log("startPointTangent: " + startPointTangent); // (0, 1, 0)
                    //Debug.Log("branchAngleMode count: " + branchAngleMode.Count + ", l: " + clusterIndex);

                    if (branchAngleMode[clusterIndex] == angleMode.winding)
                    {
                        float angle = windingAngle % (2f * rotateAngleRange[clusterIndex]);
                        //Debug.Log("angle: " + angle); // 
                        branchDir = Quaternion.AngleAxis(-rotateAngleRange[clusterIndex] + angle, startPointTangent) * centerDir;
                    }
                    if (branchAngleMode[clusterIndex] == angleMode.symmetric)
                    {
                        // (TODO...)
                        if (branchIndex % 2 == 0)
                        {
                            branchDir = Quaternion.AngleAxis(-rotateAngle[clusterIndex], startPointTangent) * centerDir;
                            if (clusterIndex == 1)
                            {
                                //debugLinesRed.Add(new line(startPoint, startPoint + Vector3.Cross(startPointTangent, branchDir))); // axis for rotate verticalAngle 
                            }
                            branchDir = Quaternion.AngleAxis(verticalAngle - 90f, Vector3.Cross(startPointTangent, branchDir)) * branchDir;
                        }
                        else
                        {
                            branchDir = Quaternion.AngleAxis(rotateAngle[clusterIndex], startPointTangent) * centerDir;
                            if (clusterIndex == 1)
                            {
                                //debugLinesRed.Add(new line(startPoint, startPoint + Vector3.Cross(startPointTangent, -branchDir))); // axis for rotate verticalAngle 
                            }
                            branchDir = Quaternion.AngleAxis(-verticalAngle + 90f, Vector3.Cross(startPointTangent, -branchDir)) * branchDir;
                        }

                    }
                    //Debug.Log("dir: " + branchDir);

                    // There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem
                    Vector3 branchCotangent;
                    if (branchDir.x != 0f)
                    {
                        branchCotangent = new Vector3(-branchDir.y, branchDir.x, 0f);
                    }
                    else
                    {
                        if (branchDir.y != 0f)
                        {
                            branchCotangent = new Vector3(0f, -branchDir.z, branchDir.y);
                        }
                        else
                        {
                            branchCotangent = new Vector3(branchDir.z, 0f, -branchDir.x);
                        }
                    }

                    //debugLinesGreen.Add(new line(startPoint, startPoint + outwardDir)); 
                    //debugLinesGreen.Add(new line(startPoint, startPoint + branchCotangent));
                    //debugLinesBlue.Add(new line(startPoint, startPoint + norm(Vector3.Cross(startPointTangent, outwardDir))));

                    //Debug.Log("branch cotangent: " + branchCotangent);
                    //Debug.Log("new node: clusterIndex: " + clusterIndex);
                    float tValBranchStart = 0f;
                    node branch = new node(startPoint, branchDir, branchCotangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal, tValBranchStart, taper * taperFactor[clusterIndex], this, null, clusterIndex, clusterRingResolution[clusterIndex]); // taper[] for each level


                    //Vector3 startPoint = sampleSplineT(startNodesNextIndexStartTval[startNodeIndex].Item1.point,
                    //                                   startNodesNextIndexStartTval[startNodeIndex].Item1.next[startNodeNextIndex].point,
                    //                                   tangent,
                    //                                   startNodesNextIndexStartTval[startNodeIndex].Item1.next[startNodeNextIndex].tangent[0],
                    //                                   t);
                    float branchLength = 0f;
                    if (clusterIndex == 0)
                    {
                        node startNode = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode;
                        int nextIndex = startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex;
                        float startTvalGlobal = fLerp(startNode.tValGlobal, startNode.next[nextIndex].tValGlobal, t);
                        branchLength = treeHeight * relBranchLength[clusterIndex] * shapeRatio(startTvalGlobal);
                    }
                    else
                    {
                        Debug.Log("clusterIndex: " + clusterIndex);
                        node startNode = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode;
                        int nextIndex = startNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex;
                        float startTval = fLerp(startNode.tValBranch, startNode.next[nextIndex].tValBranch, t);
                        branchLength = treeHeight * relBranchLength[clusterIndex] * shapeRatioBranch(clusterIndex, startTval); // ..lerp!
                    }
                    float lengthToTip = startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.lengthToTip();
                    lengthToTip -= t * vLength(startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[startNodeNextIndex].point - startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point);
                    if (branchLength > lengthToTip)
                    {
                        branchLength = lengthToTip;
                    }
                    //Debug.Log("new node: clusterIndex: " + clusterIndex);
                    float tValBranchEnd = 1f;
                    branch.next.Add(new node(startPoint + branchDir * branchLength, branchDir, branchCotangent, startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tValGlobal, tValBranchEnd, taper * taperFactor[clusterIndex], this, branch, clusterIndex, clusterRingResolution[clusterIndex]));
                    //Debug.Log("branches count: " + startNodesNextIndex[startNodeIndex].Item1.branches.Count + ", n: " + startNodeNextIndex);
                    if (startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.branches.Count < startNodeNextIndex + 1)
                    {
                        for (int m = 0; m < startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next.Count; m++)
                        {
                            startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.branches.Add(new List<node>());
                        }
                    }

                    startNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.branches[startNodeNextIndex].Add(branch);
                    //Debug.Log("added branch!");

                    // debugPointsRed.Add(startPoint);
                    //debugLinesGreen.Add(new line(startPoint, startPoint + branchDir * branchLength));

                    //debugLinesRed.Add(new line(startPoint, startPoint + dirStart * branchLength));
                    //debugLinesRed.Add(new line(startPoint, startPoint + dirEnd * branchLength));
                    //
                    //debugLinesRed.Add(new line(startPoint, startPoint + verticalStart * branchLength));
                    //debugLinesRed.Add(new line(startPoint, startPoint + verticalEnd * branchLength));

                    windingAngle += rotateAngle[clusterIndex]; // TODO: fibonacci numbers: 1/2, 1/3, 2/5, 3/8 -> 180, 120, 144, 135, -> f(n)/f(n+2)

                    //Debug.Log("branches[" + startNodeNextIndex + "] count: " + startNodesNextIndex[startNodeIndex].Item1.branches[startNodeNextIndex].Count);
                    // startNodes[startNodeIndex].branches[n][0].resampleSpline(3, 0f, 0f, 1f);

                    // curvature
                    branch.curveBranches(branchCurvature[clusterIndex], Vector3.Cross(startPointTangent, branchDir));
                    //debugLinesGreen.Add(new line(startPoint, startPoint + norm(Vector3.Cross(startPointTangent, branchDir))));


                    // resample
                    branch.resampleSpline(3, 0f, 0f, 1f); // TODO: make parameter!
                }
                // add one branch at tip of spline -> do not clamp length by length to tip! -> smaller taper!
                // TODO: add to branch list!
                List<node> leafNodes = new List<node>();
                rootNode.getAllLeafNodes(leafNodes);
                //Debug.Log("leafNodes count: " + leafNodes.Count);
                foreach (node n in leafNodes)
                {
                    float branchLength = treeHeight * relBranchLength[clusterIndex] * shapeRatio(1f);
                    Vector3 branchDir = n.tangent[0];
                    Vector3 branchCotangent;
                    if (n.tangent[0].x != 0f)
                    {
                        branchCotangent = new Vector3(-branchDir.y, branchDir.x, 0f);
                    }
                    else
                    {
                        if (branchDir.y != 0f)
                        {
                            branchCotangent = new Vector3(0f, -branchDir.z, branchDir.y);
                        }
                        else
                        {
                            branchCotangent = new Vector3(branchDir.z, 0f, -branchDir.x);
                        }
                    }

                    Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));
                    Vector3 centerPoint = sampleSplineT(rootNode.point, norm(treeGrowDir) * treeHeight, new Vector3(0f, 1f, 0f), nextTangent, 1f);
                    Vector3 outwardDir = n.point - centerPoint;

                    if (outwardDir == Vector3.zero)
                    {
                        outwardDir = n.cotangent;
                    }
                    //Debug.Log("new node: clusterIndex: " + clusterIndex);
                    float tValBranch = 0f;
                    node branch = new node(n.point + n.tangent[0] * branchLength, branchDir, branchCotangent, n.tValGlobal, tValBranch, taper * taperFactor[clusterIndex], this, n, clusterIndex, clusterRingResolution[clusterIndex]);

                    // before
                    //n.next.Add(branch); // TODO: store node level in node! (-> TODO: update getAllBranchNodes())
                    //n.applyCurvature(splitCurvature, outwardDir);

                    // -> add as branch! (TEST!) // does not work! ()
                    // if (n.branches.Count == 0)
                    // {
                    //     n.branches.Add(new List<node>());
                    // }
                    // n.branches[n.branches.Count - 1].Add(new node(n.point, n.tangent[0], n.cotangent, n.tVal, n.taper, n.gen, n));
                    // n.branches[n.branches.Count - 1][n.branches[n.branches.Count - 1].Count - 1].next.Add(branch);
                    // //Debug.Log("add branch at leafNode "); // TODO...
                    // n.applyCurvature(splitCurvature, outwardDir);
                }

            }

            
            // split branches
            if (nrSplitsPerBranch != null)
            {
                if (nrSplitsPerBranch.Count > clusterIndex)
                {
                    if (nrSplitsPerBranch[clusterIndex] > 0f) // nrSplitsPerBranch[branchLevel] * (float)nrBranches[branchLevel]
                    {
                        //Debug.Log("in addBranches: splitBranches: branchLevel:" + clusterIndex); // 0
                        splitBranches(clusterIndex, (int)(nrSplitsPerBranch[clusterIndex] * (float)nrBranches[clusterIndex]), testSplitAngle, testSplitPointAngle); // TODO: split before adding next branch level!
                                                                                                                                                                    // splitBranches() treats stem as branch level 0
                                                                                                                                                                    // addBranches() counts branchLevels from 0 (not including stem)
                    }
                }
            }
        }
        //Debug.Log("minAngle: " + minAngle);
        //Debug.Log("maxAngle: " + maxAngle);
    
    }

    public float calculateSegmentLengthsAndTotalLength(List<StartNodeInfo> startNodesNextIndexStartTvalEndTval, List<List<StartNodeInfo>> branchNodesNextIndexStartTvalEndTval, List<float> segmentLengths, int clusterIndex, bool useTvalBranch)
    {
        // branchNodesNextIndexStartTval: all startNodes that are the start of a branch (not inbetween nodes), one list<(node, int)> for each branch
        // TODO: startTval...

        float totalLength = 0f;
        if (clusterIndex == 1)
        {
            Debug.Log("calculateSegmentLengthsAndTotalLength: clusterIndex: " + clusterIndex + ", startNodesNextIndex.Count: " + startNodesNextIndexStartTvalEndTval.Count);
        }
        // for (int i = 0; i < startNodesNextIndex.Count; i++)
        // {
        //     //Debug.Log("in loop: i = " + i + ", startNodesNextIndex.Count: " + startNodesNextIndex.Count);
        //     //(var) (node startNode, int nextIndex) = startNodesNextIndex[i];
        //     (node, int) startNodeNextIndex = startNodesNextIndex[i];
        //     float segLen = startNodeNextIndex.Item1.next[startNodeNextIndex.Item2] != null ? vLength(startNodeNextIndex.Item1.next[startNodeNextIndex.Item2].point - startNodeNextIndex.Item1.point) : 0f;
        //     
        //     float tA_global = startNodeNextIndex.Item1.tValGlobal;
        //     float tB_global = startNodeNextIndex.Item1.next[startNodeNextIndex.Item2].tValGlobal;
        //     
        //     float tA_branch = startNodeNextIndex.Item1.tValBranch; 
        //     float tB_branch = startNodeNextIndex.Item1.next[startNodeNextIndex.Item2].tValBranch;
        //     
        //     Debug.Log("tA_global: " + tA_global + ", tB_global: " + tB_global + ", tA_branch: " + tA_branch + ", tB_branch: " + tB_branch);
        //     
        //     new code (AI)
        //    
        //     
        //     if (tA_branch > tB_branch)
        //     {
        //         // Swap to ensure tA < tB
        //         float temp = tA_branch;
        //         tA_branch = tB_branch;
        //         tB_branch = temp;
        //     }
        //    
        //     if (tA_global > tB_global)
        //     {
        //         // Swap to ensure tA < tB
        //         float temp = tA_global;
        //         tA_global = tB_global;
        //         tB_global = temp;
        //     }
        //     
        //     // ---  AI
        //     // Only include segment if both conditions are satisfied
        //     if (tB_branch <= branchesStartHeightCluster[clusterIndex] ||
        //         tB_global <= branchesStartHeightGlobal[clusterIndex])
        //     {
        //         continue; // Skip segments that are below the start height in either system
        //     }
        //     
        //     // Clamp tStart to the higher of the two thresholds
        //     float tStart_branch = Mathf.Max(tA_branch, branchesStartHeightCluster[clusterIndex]);
        //     float tStart_global = Mathf.Max(tA_global, branchesStartHeightGlobal[clusterIndex]);
        //     float tStart = Mathf.Max(tStart_branch, tStart_global);
        //     
        //     float tEnd_branch = tB_branch;
        //     float tEnd_global = tB_global;
        //     float tEnd = Mathf.Min(tEnd_branch, tEnd_global);
        //     
        //     // Compute fractions for both systems
        //     float frac_branch = (tB_branch - tStart_branch) / (tB_branch - tA_branch == 0f ? 1f : tB_branch - tA_branch);
        //     float frac_global = (tB_global - tStart_global) / (tB_global - tA_global == 0f ? 1f : tB_global - tA_global);
        //    
        //     // branch: frac = (tEnd - tStart) / (tB_branch - tA_branch);
        //     // global: frac = (tEnd - tStart) / (tB_global - tA_global);
        //     
        //     // Use the minimum fraction to ensure both conditions are satisfied
        //     float frac = Mathf.Min(frac_branch, frac_global);
        //    
        //     if (clusterIndex == 0)
        //     {
        //         frac = frac_global;
        //     }
        //     
        //     float segLenAbove = segLen * frac;
        //     // ---
        //
        //     old code
        //    
        //
        //     if (clusterIndex == 1)
        //     {
        //         useTvalBranch = true; // TODO: TEMP! REMOVE THIS LINE
        //     }
            


        if (useTvalBranch == true) // ERROR HERE -> do not use startNodes -> use branches! (branches have startNodes inbetween!!!)
        {
            for (int branchNode = 0; branchNode < branchNodesNextIndexStartTvalEndTval.Count; branchNode++)
            {
                for (int i = 0; i < branchNodesNextIndexStartTvalEndTval[branchNode].Count; i++)
                {
                    StartNodeInfo startNodeNextIndexStartTvalEndTval = branchNodesNextIndexStartTvalEndTval[branchNode][i];
                    float segLen = startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex] != null ? vLength(startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex].point - startNodeNextIndexStartTvalEndTval.startNode.point) : 0f;

                    float tA_branch = startNodeNextIndexStartTvalEndTval.startNode.tValBranch;
                    float tB_branch = startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex].tValBranch;
                    float startTval = startNodeNextIndexStartTvalEndTval.startTval;
                    float endTval = startNodeNextIndexStartTvalEndTval.endTval;

                    Debug.Log("tA_branch: " + tA_branch + ", tB_branch: " + tB_branch);


                    float segLenAbove;
                    //                     // List<List<(node, int)>> branchNodesNextIndex: every list starts with startNode at the start of a branch, one list<(node, int)> for each branch

                    Debug.Log("useTvalBranch == true, clusterIndex: " + clusterIndex);
                    Debug.Log("clusterIndex: " + clusterIndex + ", tA_branch: " + tA_branch + ", tB_branch: " + tB_branch +
                                ", branchesStartHeightCluster[clusterIndex]: " + branchesStartHeightCluster[clusterIndex] +
                                ", branchNodesNextIndex[" + branchNode + "].Count: " + branchNodesNextIndexStartTvalEndTval[branchNode].Count);
                    if (tA_branch > tB_branch)
                    {
                        // Swap to ensure tA < tB
                        float temp = tA_branch;
                        tA_branch = tB_branch;
                        tB_branch = temp;
                    }

                    if (tB_branch <= branchesStartHeightCluster[clusterIndex] || tA_branch >= branchesEndHeightCluster[clusterIndex])
                    {
                        Debug.Log("continue: tB <= branchesStartHeight[clusterIndex]: " + tB_branch + " <= " + branchesStartHeightCluster[clusterIndex] +
                                          " OR tA >= branchesEndHeight[clusterIndex]: " + tA_branch + " >= " + branchesEndHeightCluster[clusterIndex]);
                        continue; // Skip segments that are below the start height
                    }

                    Debug.Log("test: tA_branch: " + tA_branch + ", branchesStartHeightCluster: " + branchesStartHeightCluster[clusterIndex] + ", tB_branch: " + tB_branch + ", branchesEndHeightCluster: " + branchesEndHeightCluster[clusterIndex]);


                    float tStart = Mathf.Max(tA_branch, branchesStartHeightCluster[clusterIndex]);
                    float tEnd = Mathf.Min(tB_branch, branchesEndHeightCluster[clusterIndex]); 
                    //float tStart = tA_branch; // TEST
                    //float tEnd = tB_branch; // TEST

                    float frac;
                    if (tB_branch - tA_branch == 0f)
                    {
                        Debug.Log("ERROR: tB_branch - tA_branch == 0f, tA: " + tA_branch + ", tB: " + tB_branch + ", startNode.tValGlobal: " + startNodeNextIndexStartTvalEndTval.startNode.tValGlobal + ", nextIdx: " + startNodeNextIndexStartTvalEndTval.nextIndex);
                        frac = 0f;
                    }
                    else
                    {
                        // Fraction of segment above minT
                        frac = (tEnd - tStart) / (tB_branch - tA_branch);
                        //Debug.Log("frac: " + frac);
                    }
                    segLenAbove = segLen * frac;

                    // segmentTStart.Add(tStart); // tVal of the segment start
                    // segmentTEnd.Add(tEnd);
                    // int debugStartIndex = segmentTStart.Count - 1;
                    // int debugEndIndex = segmentTEnd.Count - 1;
                    // Debug.Log("segmentTStart[" + debugStartIndex + "] added: " + segmentTStart[segmentTStart.Count - 1] +
                    //           ", segmentTEnd[" + debugEndIndex + "] added: " + segmentTEnd[segmentTEnd.Count - 1]);
                    segmentLengths.Add(segLenAbove);
                    totalLength += segLenAbove;
                }
            }
        }
        else // OK
        {
            for (int i = 0; i < startNodesNextIndexStartTvalEndTval.Count; i++)
            {
                StartNodeInfo startNodeNextIndexStartTvalEndTval = startNodesNextIndexStartTvalEndTval[i];
                float segLen = startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex] != null ? vLength(startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex].point - startNodeNextIndexStartTvalEndTval.startNode.point) : 0f;

                float tA_global = startNodeNextIndexStartTvalEndTval.startNode.tValGlobal;
                float tB_global = startNodeNextIndexStartTvalEndTval.startNode.next[startNodeNextIndexStartTvalEndTval.nextIndex].tValGlobal;

                Debug.Log("tA_global: " + tA_global + ", tB_global: " + tB_global);


                float segLenAbove;

                Debug.Log("useTvalBranch == false, clusterIndex: " + clusterIndex);
                if (tA_global > tB_global)
                {
                    // Swap to ensure tA < tB
                    float temp = tA_global;
                    tA_global = tB_global;
                    tB_global = temp;
                }
                if (tB_global <= branchesStartHeightGlobal[clusterIndex])
                {
                    //Debug.Log("continue: tB <= branchesStartHeight[clusterIndex]: " + tB + " <= " + branchesStartHeight[clusterIndex]); 
                    continue; // Skip segments that are below the start height
                }
                float tStart = Mathf.Max(tA_global, branchesStartHeightGlobal[clusterIndex]);
                float tEnd = tB_global;
                float frac;
                if (tB_global - tA_global == 0f)
                {
                    Debug.Log("ERROR: tB - tA == 0f, tA: " + tA_global + ", tB: " + tB_global + ", startNode.tValGlobal: " + startNodeNextIndexStartTvalEndTval.startNode.tValGlobal + ", nextIdx: " + startNodeNextIndexStartTvalEndTval.nextIndex);
                    frac = 0f;
                }
                else
                {
                    // Fraction of segment above minT
                    frac = (tEnd - tStart) / (tB_global - tA_global);
                    //Debug.Log("frac: " + frac);
                }
                segLenAbove = segLen * frac;
                // segmentTStart.Add(tStart); // tVal of the segment start
                // segmentTEnd.Add(tEnd);
                // int debugStartIndex = segmentTStart.Count - 1;
                // int debugEndIndex = segmentTEnd.Count - 1;
                // Debug.Log("segmentTStart[" + debugStartIndex + "] added: " + segmentTStart[segmentTStart.Count - 1] +
                //           ", segmentTEnd[" + debugEndIndex + "] added: " + segmentTEnd[segmentTEnd.Count - 1]);
                segmentLengths.Add(segLenAbove);
                totalLength += segLenAbove;
            }
        }
        


        if (clusterIndex == 1)
        {
            Debug.Log("calculateSegmentLengthsAndTotalLength: clusterIndex: " + clusterIndex + ", totalLength: " + totalLength + ", segmentLengths.Count: " + segmentLengths.Count);
            // ERROR: tVal for branches is the same for start of branch and end of branch
        }
        return totalLength;
    }


    public void splitBranches(int branchCluster, int nrBranchSplits, float splitAngle, float splitPointAngle) // TODO: split branch at tip of spline -> TODO: get all nodes... 
    {
        //Debug.Log("splitBranches() branchClsuter: " + branchCluster + ", nrBranchSplits: " + nrBranchSplits);
        List<node> allBranchNodes = new List<node>();
        rootNode.getAllBranchNodes(allBranchNodes, branchCluster);
        //Debug.Log("nrBranches: " + allBranchNodes.Count);

        splitProbabilityInLevel = new float[nrBranchSplits];
        expectedSplitsInLevel = new int[nrBranchSplits];

        int meanLevelBranch = (int)Mathf.Log((float)nrBranchSplits / (float)allBranchNodes.Count, 2f);
        //Debug.Log("splitBranches: nrBranchSplits: " + nrBranchSplits + ", meanLevelBranch: " + meanLevelBranch + ", nrBranches: " + allBranchNodes.Count);
        //                               1,                                    -4,                                   31
        if (meanLevelBranch >= 0)
        {
            if (nrBranchSplits < allBranchNodes.Count)
            {
                expectedSplitsInLevel[0] = nrBranchSplits;
                splitProbabilityInLevel[0] = 1f;
                for (int i = 1; i < nrBranchSplits; i++)
                {
                    expectedSplitsInLevel[i] = 0;
                }
            }
            else
            {
                if (nrBranchSplits > 0)
                {
                    splitProbabilityInLevel[0] = 1f;
                    expectedSplitsInLevel[0] = allBranchNodes.Count;
                }
                else
                {
                    splitProbabilityInLevel[0] = 0f;
                    expectedSplitsInLevel[0] = 0;
                }

                for (int i = 1; i < (int)Mathf.RoundToInt((float)meanLevelBranch - variance * (float)meanLevelBranch); i++)
                {
                    splitProbabilityInLevel[i] = 1f;
                    expectedSplitsInLevel[i] = allBranchNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
                    if (expectedSplitsInLevel[i] > 1024)
                    {
                        expectedSplitsInLevel[i] = 1024;
                    }
                }
                for (int i = (int)Mathf.RoundToInt((float)meanLevelBranch - variance * (float)meanLevelBranch); i < (int)Mathf.RoundToInt((float)meanLevelBranch + variance * (float)meanLevelBranch); i++)
                {
                    splitProbabilityInLevel[i] = 1f - (7f / 8f) * (float)(i - (int)Mathf.RoundToInt((float)meanLevelBranch - variance * (float)meanLevelBranch)) /
                                                    (Mathf.RoundToInt((float)meanLevelBranch + variance * (float)meanLevelBranch) - Mathf.RoundToInt((float)meanLevelBranch - variance * (float)meanLevelBranch));
                    expectedSplitsInLevel[i] = allBranchNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
                    if (expectedSplitsInLevel[i] > 1024)
                    {
                        expectedSplitsInLevel[i] = 1024;
                    }
                }
                for (int i = (int)Mathf.RoundToInt((float)meanLevelBranch + variance * (float)meanLevelBranch); i < nrBranchSplits; i++)
                {

                    //Debug.Log("i: " + i + ", nrBranchSplits: " + nrBranchSplits + ", expectedSplitsInLevel length: " + expectedSplitsInLevel.Length + ", splitProbability length: " + splitProbabilityInLevel.Length);
                    if (i > 0)
                    {
                        splitProbabilityInLevel[i] = 1f / 8f;
                        expectedSplitsInLevel[i] = allBranchNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
                    }
                    if (expectedSplitsInLevel[i] > 1024)
                    {
                        expectedSplitsInLevel[i] = 1024;
                    }

                    //i: 0, nrBranchSplits: 23, expectedSplitsInLevel length: 23, splitProbability length: 23
                }
            }

            //for (int i = 0; i < nrBranchSplits; i++)
            //{
            //    //Debug.Log("splitBranches: splitProbabilityInLevel[" + i + "]: " + splitProbabilityInLevel[i]);
            //}

            List<List<nodeInfo>> nodesInLevelNextIndexSplitsPerBranch = new List<List<nodeInfo>>();
            for (int i = 0; i <= nrBranchSplits; i++)
            {
                nodesInLevelNextIndexSplitsPerBranch.Add(new List<nodeInfo>());
            }

            foreach (node branch in allBranchNodes)
            {
                for (int n = 0; n < branch.next.Count; n++)
                {
                    nodesInLevelNextIndexSplitsPerBranch[0].Add(new nodeInfo(branch, n, 0));
                }
            }

            //Debug.Log("nodesInLevelNextIndex");
            //for (int i = 0; i < nodesInLevelNextIndexSplitsPerBranch.Count; i++)
            //{
            //    //Debug.Log("nodesInLevelNextIndex[" + i + "].Count: " + nodesInLevelNextIndexSplitsPerBranch[i].Count);
            //}


            // 
            // //TODO...
            // 
            int totalSplitCounter = 0;
            for (int level = 0; level < nrBranchSplits; level++)
            {
                //int maxSplitsPerBranch = 2; // TODO: make this a parameter
                int maxSplitsPerBranch = (int)(nrSplitsPerBranch[branchCluster] + splitsPerBranchVariation[branchCluster]);
                //Debug.Log("maxSplitsPerBranch: " + maxSplitsPerBranch);

                List<float> branchLengths = new List<float>();
                List<float> branchWeights = new List<float>();
                float totalWeight = 0f;

                foreach (nodeInfo n in nodesInLevelNextIndexSplitsPerBranch[level])
                {
                    float branchLength = n.nodeInLevel.lengthToTip();
                    branchLengths.Add(branchLength);

                    float weight = Mathf.Pow(branchLength, 8f); // TODO: scale parameter
                    branchWeights.Add(weight);
                    totalWeight += weight;
                }



                int splitsInLevel = 0;
                int safetyCounter = 0;

                nodeIndices = new List<int>();
                for (int i = 0; i < nodesInLevelNextIndexSplitsPerBranch[level].Count; i++)
                {
                    nodeIndices.Add(i);
                }
                //Debug.Log("splitBranches: begin of level " + level + ": nodeIndices.Count: " + nodeIndices.Count + ", expectedSplitsInLevel: " + expectedSplitsInLevel[level]);
                // for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
                // {
                //     Debug.Log("nodeIndices[" + i + "]: " + nodeIndices[i]);
                // }

                if (nodeIndices.Count <= 0)
                {
                    continue;
                }

                while (splitsInLevel < expectedSplitsInLevel[level])
                {
                    //Debug.Log("begin of iteration: nodeIndices.Count: " + nodeIndices.Count);
                    if (nodeIndices.Count == 0)
                    {
                        break;
                    }

                    if (totalSplitCounter == nrBranchSplits)
                    {
                        break;
                    }
                    float r = (float)random.NextDouble();
                    float h = (float)random.NextDouble() - 0.5f;
                    if (r <= splitProbabilityInLevel[level])
                    {
                        // split
                        //int indexToSplit = random.Next(nodeIndices.Count);//random.Next() % nodeIndices.Count;
                        // Perform weighted random selection
                        float randomValue = (float)random.NextDouble() * totalWeight;
                        float cumulativeWeight = 0f;
                        int indexToSplit = -1;

                        for (int i = 0; i < branchWeights.Count; i++)
                        {
                            cumulativeWeight += branchWeights[i];
                            if (randomValue <= cumulativeWeight)
                            {
                                indexToSplit = i;
                                break;
                            }
                        }

                        // TODO: make longer branches more likely to split!

                        //Debug.Log("branchWeights.Count: " + branchWeights.Count); // 27
                        //Debug.Log("splitBranches: indexToSplit: " + indexToSplit); // 21
                        //Debug.Log("nodeIndices.Count: " + nodeIndices.Count); // 20
                        //if (indexToSplit != -1)
                        //{
                        //    //Debug.Log("nodeIndexToSplit: " + nodeIndices[indexToSplit]); // 
                        //}
                        //Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndexSplitsPerBranch[level].Count); // level 0, Count 31

                        if (indexToSplit != -1 && nodeIndices.Count > indexToSplit && branchSplitHeightInLevel.Count > branchCluster
                            && indexToSplit >= 0 && indexToSplit < nodeIndices.Count
                            && nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch < maxSplitsPerBranch)
                        {
                            //Debug.Log("branchSplitHeightInLevel.Count: " + branchSplitHeightInLevel.Count +
                            //"branchSplitHeightInLevel[0].Count: " + branchSplitHeightInLevel[0].Count + ", branchLevel: " + branchCluster + ", level: " + level);

                            // TODO: better split height variation
                            float branchSplitHeight = Mathf.Clamp(branchSplitHeightInLevel[branchCluster][level] + h * branchSplitHeightVariation[branchCluster] *
                                Mathf.Min(branchSplitHeightInLevel[branchCluster][level], 1f - branchSplitHeightInLevel[branchCluster][level]), 0.05f, 0.95f);

                            // float branchSplitHeight = Mathf.Clamp(branchSplitHeightInLevel[branchLevel][level] + h * branchSplitHeightVariation[branchLevel], 0.1f, 0.9f);

                            if (nodesInLevelNextIndexSplitsPerBranch.Count < level)
                            {
                                Debug.Log("ERROR: nodesInLevelNextIndex.Count < level!");
                            }
                            if (nodesInLevelNextIndexSplitsPerBranch[level].Count < nodeIndices[indexToSplit]) // ERROR HERE !!!
                            {
                                Debug.Log("ERROR: nodesInLevelNextIndex[level].Count < nodeIndices[indexToSplit]!");
                                Debug.Log("nodesInLevelNextIndex[level].Count: " + nodesInLevelNextIndexSplitsPerBranch[level].Count + ", nodeIndices[indexToSplit]: " + nodeIndices[indexToSplit]);
                            }
                            if (nodeIndices.Count < indexToSplit)
                            {
                                Debug.Log("ERROR: nodeIndices.Count < indexToSplit!");
                            }



                            //Debug.Log("splitHeight: " + branchSplitHeight + ", h: " + h);
                            //Debug.Log("branchSplitMode.Count: " + branchSplitMode.Count + ", branchCluster: " + branchCluster + ", level: " + level + ", branchSplitRotateAngle.Count: " + branchSplitRotateAngle.Count);
                            node splitNode = split(nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nodeInLevel, nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nextIndex,
                                                branchSplitHeight, splitAngle, splitPointAngle, level, branchSplitMode[branchCluster], branchSplitRotateAngle[branchCluster]);



                            // TODO: in split() -> split between two nodes -> insert new node!

                            if (splitNode == nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].nodeInLevel)
                            {
                                // did not split
                                // nodesInLevelNextIndex[level].RemoveAt(indexToSplit); // TEST OFF
                                totalWeight -= branchWeights[indexToSplit];
                                branchWeights.RemoveAt(indexToSplit);
                                nodeIndices.RemoveAt(indexToSplit); // TEST NEW (AI)
                                Debug.Log("did not split!");
                            }
                            else
                            {
                                // Remove the weight of the original branch
                                totalWeight -= branchWeights[indexToSplit];

                                // Calculate the lengths of the two new branches
                                float lengthA = splitNode.next[0].lengthToTip();
                                float lengthB = splitNode.next[1].lengthToTip();

                                // Calculate the weights of the two new branches
                                float weightA = lengthA;
                                float weightB = lengthB;

                                branchWeights.RemoveAt(indexToSplit); // Remove the original branch's weight

                                // Update the branchWeights list ERROR HERE ??? -> add new weights??
                                // branchWeights[indexToSplit] = weightA; // Replace the original branch's weight with the first new branch's weight
                                // branchWeights.Add(weightB); // Add the second new branch's weight

                                // Update the total weight
                                totalWeight += weightA + weightB;


                                //Debug.Log("nodesInLevelNextIndex.Count: " + nodesInLevelNextIndexSplitsPerBranch.Count); // 43
                                //Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndexSplitsPerBranch[level].Count); // level0: 24
                                //Debug.Log("indexToSplit: " + indexToSplit + ", nodeIndices.Count: " + nodeIndices.Count);

                                nodesInLevelNextIndexSplitsPerBranch[level + 1].Add(new nodeInfo(splitNode, 0, nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch + 1));//
                                nodesInLevelNextIndexSplitsPerBranch[level + 1].Add(new nodeInfo(splitNode, 1, nodesInLevelNextIndexSplitsPerBranch[level][nodeIndices[indexToSplit]].splitsPerBranch + 1));//

                                nodeIndices.RemoveAt(indexToSplit);

                                // branchWeights.Add(weightA);
                                // branchWeights.Add(weightB);
                                // nodeIndices.Add(nodeIndices.Count);
                                // nodeIndices.Add(nodeIndices.Count); //ERROR HERE ???? -> are added at start of next level!
                                splitsInLevel += 1;
                                totalSplitCounter += 1;
                            }
                        }
                    }
                    safetyCounter += 1;
                    if (safetyCounter > 500)
                    {
                        Debug.Log("break!");
                        break;
                    }

                }
            }
        }
    }



    public void addLeaves()
    {
        //Debug.Log("addLeaves: nrLeaves: " + nrLeaves);
        float leafStartHeight = 0.5f; // TODO: make this a parameter
        float leafEndHeight = 1f; // TODO: make this a parameter
        List<StartNodeInfo> leafStartNodesNextIndexStartTvalEndTval = new List<StartNodeInfo>();
        List<bool> leafClusterBools = new List<bool>();
        //for (int i = 0; i < nrBranchClusters; i++)
        //{
        //    leafClusterBools.Add(true);
        //}

        float totalLength = 0f;
        List<float> segmentLengths = new List<float>();
        for (int i = 0; i < nrBranchClusters; i++)
        {
            for (int j = 0; j < nrBranchClusters; j++) // TEST (AI)
            {
                leafClusterBools.Add(j == i);
            }

            List<node> branchNodes = new List<node>();
            rootNode.getAllBranchNodes(branchNodes, i);
            List<StartNodeInfo> clusterStartNodesNextIndexStartTvalEndTval = new List<StartNodeInfo>();
            List<List<StartNodeInfo>> clusterBranchNodesNextIndexStartTvalEndTval = new List<List<StartNodeInfo>>();
            List<int> nrSplitsPassedAtStartNode = new List<int>();
            foreach (node n in branchNodes)
            {
                n.getAllStartNodes(clusterStartNodesNextIndexStartTvalEndTval, clusterBranchNodesNextIndexStartTvalEndTval, -1, nrSplitsPassedAtStartNode, 0, 0f, 0f, 1f, 1f, 0, leafClusterBools, 0);
            }

            // calculateSegmentLengthsAndTotalLength(List<(node, int)> startNodesNextIndex, List<float> segmentLengths, int clusterIndex)
            List<float> clusterSegmentLengths = new List<float>();
            totalLength += calculateSegmentLengthsAndTotalLength(clusterStartNodesNextIndexStartTvalEndTval, clusterBranchNodesNextIndexStartTvalEndTval, clusterSegmentLengths, i, false); // TODO: useTvalBranch ...
            leafStartNodesNextIndexStartTvalEndTval.AddRange(clusterStartNodesNextIndexStartTvalEndTval);
            segmentLengths.AddRange(clusterSegmentLengths);
            //Debug.Log("cluster " + i + ": totalLength: " + totalLength + ", segmentLengths.Count: " + segmentLengths.Count);
        }
        Debug.Log("addLeaves: leafStartNodesNextIndexStartTvalEndTval.Count: " + leafStartNodesNextIndexStartTvalEndTval.Count);


        //-----------
        for (int nodeIndex = 0; nodeIndex < leafStartNodesNextIndexStartTvalEndTval.Count; nodeIndex++)
        {
            // NEW: startNodeIndex calculation (AI) ---------------------------
            float leafPos = (nodeIndex + 0.5f) * totalLength / leafStartNodesNextIndexStartTvalEndTval.Count; // +0.5 for center of segment

            // add random offset to branchPos (AI)
            float avgSegmentLength = totalLength / leafStartNodesNextIndexStartTvalEndTval.Count;
            float leafPosOffset = ((float)random.NextDouble() - 0.5f) * 0.2f * avgSegmentLength;
            leafPos += leafPosOffset;

            // Find which segment this branch falls into
            float accumLength = 0f;
            int startNodeIndex = 0;
            float t = 0f;
            for (int i = 0; i < segmentLengths.Count; i++)
            {
                if (accumLength + segmentLengths[i] >= leafPos)
                {
                    startNodeIndex = i;
                    float segStart = accumLength;
                    float segLen = segmentLengths[i];
                    t = segLen > 0f ? (leafPos - segStart) / segLen : 0f;
                    break;
                }
                accumLength += segmentLengths[i];
            }

            int leafStartNodeNextIndex = leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].nextIndex;
            //-----------------------------------------------------------------

            // TODO: winding -> equal distances -> add random offsets

            Vector3 tangent;
            if (leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next.Count > 1)
            {
                tangent = leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[leafStartNodeNextIndex + 1];
            }
            else
            {
                tangent = leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.tangent[0];
            }
            // Map t from [0,1] to [tA, tB]
            //Debug.Log("startNodeIndex: " + startNodeIndex + ", startNodesNextIndex.Count: " + startNodesNextIndex.Count + ", segmentTStart.Count: " + segmentTStart.Count + ", segmentTEnd.Count: " + segmentTEnd.Count);
            //float tVal = segmentTStart[startNodeIndex] + t * (segmentTEnd[startNodeIndex] - segmentTStart[startNodeIndex]);

            Vector3 startPoint = sampleSplineT(leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.point,
                                               leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[leafStartNodeNextIndex].point,
                                               tangent,
                                               leafStartNodesNextIndexStartTvalEndTval[startNodeIndex].startNode.next[leafStartNodeNextIndex].tangent[0],
                                               t);
        }
    }

    //for (int j = 0; j < parentClusterBools[clusterIndex].Count; j++)
    //{
    //    if (parentClusterBools[clusterIndex][j] == true)
    //    {
    //        if (j == 0)
    //        {
    //            // Start from the stem
    //            rootNode.getAllStartNodes(startNodesNextIndex, nrSplitsPassedAtStartNode, 0,
    //                branchesStartHeight[clusterIndex], branchesEndHeight[clusterIndex], j, parentClusterBools[clusterIndex], 0);
    //        }
    //        else
    //        {
    //            // Start from all nodes in cluster j
    //            List<node> parentNodes = new List<node>();
    //            rootNode.getAllBranchNodes(parentNodes, j);
    //            foreach (node n in parentNodes)
    //            {
    //                n.getAllStartNodes(startNodesNextIndex, nrSplitsPassedAtStartNode, 0,
    //                    branchesStartHeight[clusterIndex], branchesEndHeight[clusterIndex], j, parentClusterBools[clusterIndex], 0);
    //            }
    //        }
    //    }
    //}
    

    public void setTreeShape(int s)
    {
        switch (s)
        {
            case 0: treeShape = Shape.conical; break;
            case 1: treeShape = Shape.cylindrical; break;
            case 2: treeShape = Shape.flame; break;
            case 3: treeShape = Shape.hemispherical; break;
            case 4: treeShape = Shape.inverseConical; break;
            case 5: treeShape = Shape.spherical; break;
            case 6: treeShape = Shape.taperedCylindrical; break;
            case 7: treeShape = Shape.tendFlame; break;
            default: treeShape = Shape.conical; break;
        }
    }

    public void setBranchShape(List<int> s)
    {
        branchShape = new List<Shape>();
        foreach (int i in s)
        {
            switch (i)
            {
                case 0: branchShape.Add(Shape.conical); break;
                case 1: branchShape.Add(Shape.cylindrical); break;
                case 2: branchShape.Add(Shape.flame); break;
                case 3: branchShape.Add(Shape.hemispherical); break;
                case 4: branchShape.Add(Shape.inverseConical); break;
                case 5: branchShape.Add(Shape.spherical); break;
                case 6: branchShape.Add(Shape.taperedCylindrical); break;
                case 7: branchShape.Add(Shape.tendFlame); break;
                default: branchShape.Add(Shape.conical); break;
            }
        }
        Debug.Log("setBranchShape: branchShape.Count = " + branchShape.Count);
    }

    public void setBranchAngleMode(List<int> modes)
    {
        if (branchAngleMode == null)
        {
            branchAngleMode = new List<angleMode>();
        }
        else
        {
            branchAngleMode.Clear();
        }
        foreach (int m in modes)
        {
            switch (m)
            {
                case 0: branchAngleMode.Add(angleMode.symmetric); break;
                case 1: branchAngleMode.Add(angleMode.winding); break;
                default: branchAngleMode.Add(angleMode.winding); break;
            }
        }
    }

    
    public void setBranchSplitMode(List<int> modes)
    {
        if (branchSplitMode == null)
        {
            branchSplitMode = new List<splitMode>();
        }
        else
        {
            branchSplitMode.Clear();
        }
        foreach (int m in modes)
        {
            switch (m)
            {
                case 0: branchSplitMode.Add(splitMode.rotateAngle); break;
                case 1: branchSplitMode.Add(splitMode.horizontal); break;
                default: branchSplitMode.Add(splitMode.horizontal); break;
            }
        }
    }
    //public enum splitMode
    //{
    //    rotateAngle, 
    //    horizontal
    //}

    public void setStemSplitMode(int mode)
    {
        switch (mode)
        {
            case 0: stemSplitMode = splitMode.rotateAngle; break;
            case 1: stemSplitMode = splitMode.horizontal; break;
            default: stemSplitMode = splitMode.horizontal; break;
        }
    }

    public float shapeRatio(float tValGlobal)
    {
        switch (treeShape)
        {
            case Shape.conical:
                return 0.2f + 0.8f * tValGlobal;
            case Shape.spherical:
                return 0.2f + 0.8f * Mathf.Sin(Mathf.PI * tValGlobal);
            case Shape.hemispherical:
                return 0.2f + 0.8f * Mathf.Sin(0.5f * Mathf.PI * tValGlobal);
            case Shape.cylindrical:
                return 1f;
            case Shape.taperedCylindrical:
                return 0.5f + 0.5f * tValGlobal;
            case Shape.flame:
                if (tValGlobal <= 0.7)
                {
                    return tValGlobal / 0.7f;
                }
                else
                {
                    return (1f - tValGlobal) / 0.3f;
                }
            case Shape.inverseConical:
                return 1f - 0.8f * tValGlobal;
            case Shape.tendFlame:
                if (tValGlobal <= 0.7f)
                {
                    return 0.5f + 0.5f * tValGlobal / 0.7f;
                }
                else
                {
                    return 0.5f + 0.5f * (1f - tValGlobal) / 0.3f;
                }
            default:
                Debug.Log("ERROR: invalid tree shape!");
                return 0f;
        }
        //return (1f - tVal);
    }

    public float shapeRatioBranch(int clusterIndex, float tValBranch)
    {
        Debug.Log("branchShape.Count: " + branchShape.Count + ", clusterIndex: " + clusterIndex);
        switch (branchShape[clusterIndex])
        {
            case Shape.conical:
                return 0.2f + 0.8f * tValBranch;
            case Shape.spherical:
                return 0.2f + 0.8f * Mathf.Sin(Mathf.PI * tValBranch);
            case Shape.hemispherical:
                return 0.2f + 0.8f * Mathf.Sin(0.5f * Mathf.PI * tValBranch);
            case Shape.cylindrical:
                return 1f;
            case Shape.taperedCylindrical:
                return 0.5f + 0.5f * tValBranch;
            case Shape.flame:
                if (tValBranch <= 0.7)
                {
                    return tValBranch / 0.7f;
                }
                else
                {
                    return (1f - tValBranch) / 0.3f;
                }
            case Shape.inverseConical:
                return 1f - 0.8f * tValBranch;
            case Shape.tendFlame:
                if (tValBranch <= 0.7f)
                {
                    return 0.5f + 0.5f * tValBranch / 0.7f;
                }
                else
                {
                    return 0.5f + 0.5f * (1f - tValBranch) / 0.3f;
                }
            default:
                Debug.Log("ERROR: invalid tree shape!");
                return 0f;
        }
    }

    public void splitRecursive(node startNode, int nrSplits, float splitAngle, float splitPointAngle)
    {
        int minSegments = (int)Mathf.Ceil(Mathf.Log(nrSplits + 1, 2));
        rootNode.resampleSpline(minSegments, 0, 0, 1);

        //Debug.Log("in splitRecursive: startNode: " + startNode.point);
        splitProbabilityInLevel = new float[nrSplits];
        expectedSplitsInLevel = new int[nrSplits];
        meanLevel = (int)Mathf.Log((float)nrSplits, 2f);// + 1;
        if (meanLevel == 0)
        {
            meanLevel = 1;
        }
        if (nrSplits > 0)
        {
            splitProbabilityInLevel[0] = 1f;
            expectedSplitsInLevel[0] = 1;
        }
        else
        {
            splitProbabilityInLevel[0] = 0f;
            expectedSplitsInLevel[0] = 0;
        }
        for (int i = 1; i < (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel); i++)
        {
            splitProbabilityInLevel[i] = 1f;
            //expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * Mathf.Pow(2f, (float)i)); // TODO: has to depend on nr splits of previous level!
            expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        }

        if ((int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel) > 0)
        {
            for (int i = (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel); i < (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i++)
            {
                splitProbabilityInLevel[i] = 1f - (7f / 8f) * (float)(i - (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel)) /
                                                (Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel) - Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel));

                //Debug.Log("expecteSplitsInLevel length: " + expectedSplitsInLevel.Length + "splitProbabilityInLevel length: " + splitProbabilityInLevel.Length + ", i: " + i);

                expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
            }
            for (int i = (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i < nrSplits; i++)
            {
                splitProbabilityInLevel[i] = 1f / 8f;

                expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
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
        //Debug.Log("nrSplits: " + nrSplits + ", totalExpectedSplits: " + totalExpectedSplits + ", addToLevel: " + addToLevel + ", addAmount: " + addAmount + ", maxPossibleSplits: " + maxPossibleSplits);
        if (addAmount > 0 && expectedSplitsInLevel[addToLevel] + addAmount <= maxPossibleSplits)
        {
            expectedSplitsInLevel[addToLevel] += addAmount;
        }

        //for (int i = 0; i < nrSplits; i++)
        //{
        //    //Debug.Log("splitProbabilityInLevel[" + i + "]: " + splitProbabilityInLevel[i] + ", expectedSplitsInLevel[" + i + "]: " + expectedSplitsInLevel[i]);
        //}

        // adjust splitProbabillityInLevel
        splitProbabilityInLevel[addToLevel] = (float)expectedSplitsInLevel[addToLevel] / (float)maxPossibleSplits;

        List<List<(node, int)>> nodesInLevelNextIndex = new List<List<(node, int)>>();
        for (int i = 0; i <= nrSplits; i++)
        {
            nodesInLevelNextIndex.Add(new List<(node, int)>());
        }
        for (int n = 0; n < startNode.next.Count; n++)
        {
            nodesInLevelNextIndex[0].Add((startNode, n));
        }

        int totalSplitCounter = 0;
        for (int level = 0; level < nrSplits; level++)
        {
            int splitsInLevel = 0;
            int safetyCounter = 0;

            nodeIndices = new List<int>();
            for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
            {
                nodeIndices.Add(i);
            }
            //Debug.Log("begin of level " + level + ": nodeIndices.Count: " + nodeIndices.Count + ", expectedSplitsInLevel: " + expectedSplitsInLevel[level]);
            //for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
            //{
            //    //Debug.Log("nodeIndices[" + i + "]: " + nodeIndices[i]);
            //}

            while (splitsInLevel < expectedSplitsInLevel[level])
            {
                //Debug.Log("begin of iteration: nodeIndices.Count: " + nodeIndices.Count);
                if (nodeIndices.Count == 0)
                {
                    break;
                }

                if (totalSplitCounter == nrSplits)
                {
                    break;
                }
                float r = (float)random.NextDouble();
                float h = (float)random.NextDouble() - 0.5f;
                if (r <= splitProbabilityInLevel[level])
                {
                    // split
                    int indexToSplit = random.Next() % nodeIndices.Count;
                    //Debug.Log("indexToSplit: " + indexToSplit); // 0
                    //Debug.Log("nodeIndices.Count: " + nodeIndices.Count); // 1
                    //Debug.Log("nodeIndexToSplit: " + nodeIndices[indexToSplit]); // 0
                    //Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndex[level].Count); // level 0, Count 31
                    if (nodeIndices.Count > indexToSplit)
                    {
                        float splitHeight = splitHeightInLevel[level];
                        if (h * splitHeightVariation < 0)
                        {
                            if (splitHeight + h * splitHeightVariation > 0f)
                            {
                                splitHeight += h * splitHeightVariation;
                            }
                            else
                            {
                                splitHeight = 0.05f;
                            }
                        }
                        else
                        {
                            if (splitHeight + h * splitHeightVariation < 1f)
                            {
                                splitHeight += h * splitHeightVariation;
                            }
                            else
                            {
                                splitHeight = 0.95f; // TODO...
                            }
                        }
                        //Debug.Log("in splitRecursive: stemSplitMode: " + stemSplitMode);
                        //Debug.Log("splitHeight: " + splitHeight + ", h: " + h + ", stemSplitRotateAngle: " + stemSplitRotateAngle);
                        node splitNode = split(nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1, nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item2,
                                            splitHeight, splitAngle, splitPointAngle, level, stemSplitMode, stemSplitRotateAngle);

                        if (splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1)
                        {
                            // did not split
                            // nodesInLevelNextIndex[level].RemoveAt(indexToSplit); // TEST OFF
                            nodeIndices.RemoveAt(indexToSplit); // TEST NEW (AI)
                            Debug.Log("did not split!");
                        }
                        else
                        {
                            //nodesInLevelNextIndex[level].RemoveAt(nodeIndices[indexToSplit]);
                            nodeIndices.RemoveAt(indexToSplit);
                            nodesInLevelNextIndex[level + 1].Add((splitNode, 0));//
                            nodesInLevelNextIndex[level + 1].Add((splitNode, 1));
                            splitsInLevel += 1;
                            totalSplitCounter += 1;
                        }
                    }
                }
                safetyCounter += 1;
                if (safetyCounter > 100)
                {
                    Debug.Log("break!");
                    break;
                }
            }
        }
    }

    public node split(node startNode, int nextIndex, float splitHeight, float splitAngle, float splitPointAngle, int level, splitMode mode, float rotationAngle) // splitHeight: [0, 1]
    {
        //Debug.Log("in split()!");
        // split after resampleSpline!  //  in resampleSpline(): t_value = (float)i / (float)n
        if (startNode.next.Count > 0 && nextIndex < startNode.next.Count)
        {
            int nrNodesToTip;
            nrNodesToTip = startNode.next[nextIndex].nodesToTip(0);
            
            if (splitHeight >= 0.999f)
            {
                splitHeight = 0.999f;
            }

            int splitAfterNodeNr = (int)((float)nrNodesToTip * splitHeight);

            if (nrNodesToTip > 0) //1)
            {
                if ((float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr < 0.1f) 
                {
                    // split at existing node
                    //Debug.Log("split at existing node!");

                    node splitNode = startNode;
                    int splitAfterNodeIndex = 0;
                    for (int i = 0; i < splitAfterNodeNr; i++)
                    {
                        if (i == 0)
                        {
                            splitNode = splitNode.next[nextIndex];
                            nextIndex = 0;
                        }
                        else
                        {
                            splitNode = splitNode.next[0]; // nextIndex in first iteration, then 0!
                        }
                        splitAfterNodeIndex++;
                    }
                    //if (splitNode == rootNode)
                    //{
                    //    //Debug.Log("split at rootNode");
                    //}
                    
                    if (splitNode == startNode)
                    {
                        //Debug.Log("splitNode == startNode");
                    }
                    else
                    {
                        calculateSplitData(splitNode, splitAngle, splitPointAngle, level, mode, rotationAngle);
                    }
                    Debug.Log("split at existing node: ringResolution: " + splitNode.ringResolution);

                    //Debug.Log("splitNode.point: " + splitNode.point);

                    return splitNode;
                }
                else
                {
                    //Debug.Log("split at new node, splitAfterNodeNr: " + splitAfterNodeNr); // 0 | 0

                    node splitAfterNode = startNode;
                    bool splitAtStartNode = true;
                    int splitAfterNodeIndex = 0;
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
                            splitAfterNode = splitAfterNode.next[0]; // nextIndex in first iteration, then 0!
                            splitAtStartNode = false;
                        }
                        splitAfterNodeIndex++;
                    }

                    // add new node
                    int tangentIndex = 0;
                    if (splitAtStartNode == true && startNode.next.Count > 1)
                    {
                        tangentIndex = nextIndex + 1;
                    }
                    else
                    {
                        tangentIndex = nextIndex;
                    }

                    float debug_tval = (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr;
                    //Debug.Log("splitAfterNodeNr: " + splitAfterNodeNr + ", nrNodesToTip: " + nrNodesToTip + ", splitHeight: " + splitHeight + ", debug_tval: " + debug_tval);


                    //Debug.Log("splitAfterNode.point: " + splitAfterNode.point + ", splitAfterNode.next[nextIndex].point: " + splitAfterNode.next[nextIndex].point + "tVal: " + debug_tval);

                    Vector3 newPoint = sampleSplineT(splitAfterNode.point, splitAfterNode.next[nextIndex].point, splitAfterNode.tangent[tangentIndex], 
                                                        splitAfterNode.next[nextIndex].tangent[0], (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr);

                    if (newPoint.y > splitAfterNode.next[nextIndex].point.y)
                    {
                        Debug.Log("ERROR: newPoint.y: " + newPoint + " > splitAfterNode.next[nextIndex].point.y! tVal: " + debug_tval);
                    }

                    Vector3 newTangent = sampleSplineTangentT(splitAfterNode.point, splitAfterNode.next[nextIndex].point, splitAfterNode.tangent[tangentIndex], 
                                                        splitAfterNode.next[nextIndex].tangent[0], (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr);
                    
                    Vector3 newCotangent = vLerp(splitAfterNode.cotangent, splitAfterNode.next[nextIndex].cotangent, (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr);

                    float newTvalGlobal = fLerp(splitAfterNode.tValGlobal, splitAfterNode.next[nextIndex].tValGlobal, (float)nrNodesToTip * splitHeight - (float)splitAfterNodeNr);

                    //Debug.Log("new node: clusterIndex: " + splitAfterNode.clusterIndex);
                    float tValBranch = fLerp(splitAfterNode.tValBranch, splitAfterNode.next[nextIndex].tValBranch, splitHeight);// new!
                    // int ringResIndex = splitAfterNode.clusterIndex;
                    // if (splitAfterNode.clusterIndex == -1)
                    // {
                    //     ringResolution.Add();
                    //     ringResIndex = 0;
                    // }
                    // while (ringResolution.Count <= splitAfterNode.clusterIndex + 1)
                    // {
                    //     ringResolution.Add(6);
                    // }
                    Debug.Log("ringResolution.Count: " + clusterRingResolution.Count + ", splitAfterNode.clusterIndex: " + splitAfterNode.clusterIndex + ", newSplitNode.ringResolution: " + stemRingResolution);

                    int ringRes = 0;
                    if (splitAfterNode.clusterIndex == -1)
                    {
                        ringRes = stemRingResolution;
                    }
                    else
                    {
                        ringRes = clusterRingResolution[splitAfterNode.clusterIndex];
                    }
                    node newSplitNode = new node(newPoint, newTangent, newCotangent, newTvalGlobal, tValBranch, splitAfterNode.taper, this, splitAfterNode, splitAfterNode.clusterIndex, ringRes); // (TODO: smaller ringResolution after splits -> based on radius)

                    newSplitNode.next.Add(splitAfterNode.next[nextIndex]);
                    splitAfterNode.next[nextIndex] = newSplitNode;

                    //if (newSplitNode.point.y > treeHeight)
                    //{
                    //    //Debug.Log("splitNode: splitAfterNode.point: " + splitAfterNode.point + ", splitAfterNode.next[nextIndex].point: " + splitAfterNode.next[nextIndex].point + "newSplitNode.point: " + newSplitNode.point + ", splitHeight: " + splitHeight + "tVal: " + debug_tval);
                    //    //Debug.Log("splitNode: splineParameter: splitAfterNode.point " + splitAfterNode.point + ", splitAfterNode.next[nextIndex].point: " + splitAfterNode.next[nextIndex].point + ", splitAfterNode.tangent[tangentIndex]: " + splitAfterNode.tangent[tangentIndex] +
                    //    //", splitAfterNode.next[nextIndex].tangent[0] " + splitAfterNode.next[nextIndex].tangent[0] + ", (float)(nrNodesToTip) * splitHeight" + (float)nrNodesToTip * splitHeight + "(float)splitAfterNodeNr " + (float)splitAfterNodeNr);
                    //}
                    
                    calculateSplitData(newSplitNode, splitAngle, splitPointAngle, level, mode, rotationAngle);

                    return newSplitNode;
                }
            }
            
        }
        //Debug.Log("in split() returning startNode");
        return startNode;
    }

    void calculateSplitData(node splitNode, float splitAngle, float splitPointAngle, int level, splitMode sMode, float rotationAngle)
    {
        //Debug.Log("calculateSplitData: splitMode: " + sMode + ", rotationAngle: " + rotationAngle);
        node n = splitNode;
        int nodesAfterSplitNode = 0;
        while(n.next.Count > 0)
        {
            nodesAfterSplitNode++;
            n = n.next[0];
        }

        // TODO splitAxis mode...
        Vector3 splitAxis;
        switch(sMode)
        {
            // case splitMode.alternating: // redundant: rotateAngle = 90
            //     splitAxis = norm(splitNode.cotangent);
            //     if (level % 2 == 1)
            //     {
            //         splitAxis = Quaternion.AngleAxis(90f, splitNode.tangent[0]) * splitAxis;
            //     }
            //     break;

            case splitMode.horizontal:
                splitAxis = splitNode.cotangent; // TODO...

                Vector3 right = Vector3.Cross(splitNode.tangent[0], new Vector3(0f, 1f, 0f));
                splitAxis = Vector3.Cross(right, splitNode.tangent[0]);
                //Debug.Log("calculateSplitData: splitNode.point: " + splitNode.point);
                //Debug.Log("calculateSplitData: splitAxis: " + splitAxis);
                //if (vLength(splitAxis) == 0f)
                //{
                //    //Debug.Log("calculateSplitData: ERROR: splitAxis length = 0!");
                //}

                //debugLinesRed.Add(new line(splitNode.point, splitNode.point + splitAxis));
                //Debug.Log("debugLinesRed length: " + vLength(debugLinesRed[debugLinesRed.Count - 1].start - debugLinesRed[debugLinesRed.Count - 1].end));
                
                // splitAxis = Vector3.Cross(splitNode.tangent[0], new Vector3(0f, 1f, 0f));
                // splitAxis = Vector3.Cross(splitAxis, splitAxis);
                // if (vLength(splitAxis) < 0.001f)
                // {
                //     splitAxis = norm(splitNode.cotangent);
                // }
                // else
                // {
                //     splitAxis = norm(splitAxis);
                // }
                break;
            case splitMode.rotateAngle:
                splitAxis = norm(splitNode.cotangent);
                splitAxis = Quaternion.AngleAxis(rotationAngle * level, splitNode.tangent[0]) * splitAxis; // TODO: multiply by height?
                //Debug.Log("rotateAngle: splitAxis: " + splitAxis + ", rotationAngle: " + rotationAngle + ", splitAxis: " + splitAxis + ", level: " + level);
                break;
            default:
                Debug.Log("ERROR: invalid splitMode!");
                splitAxis = norm(splitNode.cotangent);
                if (level % 2 == 1)
                {
                    splitAxis = Quaternion.AngleAxis(90f, splitNode.tangent[0]) * splitAxis;
                }
                break;
        }

        //debugLinesBlue.Add(new line(splitNode.point, splitAxis)); 

        Vector3 splitDirA = Quaternion.AngleAxis(splitPointAngle, splitAxis) * splitNode.tangent[0];
        Vector3 splitDirB = Quaternion.AngleAxis(-splitPointAngle, splitAxis) * splitNode.tangent[0];
        debugSplitDirA = splitDirA;
        debugSplitDirB = splitDirB;

        splitNode.tangent.Add(splitDirA);
        splitNode.tangent.Add(splitDirB); // tangent[]: center, dirA, dirB

        node s = splitNode;
        node prevA = splitNode;
        node prevB = splitNode;
        
        Vector3 curvOffset = norm(splitNode.tangent[0]) * vLength(s.next[0].point - s.point) * (splitAngle / 360f) * curvOffsetStrength;

        for (int i = 0; i < nodesAfterSplitNode; i++)
        {
            s = s.next[0];
            Vector3 relPos = s.point - splitNode.point;

            Vector3 tangentA = Quaternion.AngleAxis(splitAngle, splitAxis) * s.tangent[0];
            Vector3 tangentB = Quaternion.AngleAxis(-splitAngle, splitAxis) * s.tangent[0];
            Vector3 cotangentA = Quaternion.AngleAxis(splitAngle, splitAxis) * s.cotangent;
            Vector3 cotangentB = Quaternion.AngleAxis(-splitAngle, splitAxis) * s.cotangent;

            Vector3 offsetA = Quaternion.AngleAxis(splitAngle, splitAxis) * relPos;
            Vector3 offsetB = Quaternion.AngleAxis(-splitAngle, splitAxis) * relPos;

            //Debug.Log("new node: clusterIndex: " + splitNode.clusterIndex);
            float tValBranch = 0f; // TODO... (?)
            int ringResIndex = splitNode.clusterIndex;
            int ringResolution;
            if (ringResIndex == -1)
            {
                ringResolution = stemRingResolution;
                //ringResIndex = 0;
            }
            else
            {
                ringResolution = clusterRingResolution[ringResIndex];
            }
            node nodeA = new node(splitNode.point + offsetA + curvOffset, tangentA, cotangentA, s.tValGlobal, tValBranch, s.taper, this, s.parent, splitNode.clusterIndex, ringResolution);
            node nodeB = new node(splitNode.point + offsetB + curvOffset, tangentB, cotangentB, s.tValGlobal, tValBranch, s.taper, this, s.parent, splitNode.clusterIndex, ringResolution);
            Debug.Log("in calculateSplitData: splitNode.clusterIndex: " + splitNode.clusterIndex + ", ringResIndex: " + ringResIndex + ", ringResolution: " + ringResolution);

            //Debug.Log("curvOffset: " + curvOffset);
            if (i == 0)
            {
                splitNode.next[0] = nodeA;
                splitNode.next.Add(nodeB);
                prevA = nodeA;
                prevB = nodeB;
            }
            else
            {
                prevA.next.Add(nodeA);
                prevB.next.Add(nodeB);
                prevA = nodeA;
                prevB = nodeB;
            }
        }
    }


    public int intPow(int x, int exponent)
    {
        int y = 1;
        for (int i = 0; i < exponent; i++)
        {
            y *= x; // Multiply y by x, exponent times
        }
        return y;
    }


    // Update is called once per frame
    void Update()
    {

    }

    public void updateTree()
    {
        random = new Random(seed);

        debugSamplePoints.Clear();
        debugSampleTangents.Clear();
        debugList.Clear();
        debugListRadius.Clear();
        debugListGreen.Clear();
        debugListRed.Clear();
        debugListBlue.Clear();
        debugErrorPoints.Clear();
        debugErrorPointsCompare.Clear();
        debugPointsRed.Clear();
        debugLinesBlue.Clear();
        debugLinesRed.Clear();
        debugLinesGreen.Clear();
        //Debug.Log("new node (rootNode): clusterIndex: -1");
        rootNode = new node(new Vector3(0f, 0f, 0f), new Vector3(0f, 1f, 0f), Vector3.Cross(treeGrowDir, new Vector3(treeGrowDir.x, 0f, treeGrowDir.z)), 0f, 0f, taper, this, null, -1, stemRingResolution);

        if (splitHeightInLevel == null)
        {
            Debug.Log("ERROR: splitHeightInLevel is null!");
        }
        if (splitHeightInLevel.Count < nrSplits)
        {
            int s = nrSplits - splitHeightInLevel.Count;
            for (int i = 0; i < s; i++)
            {
                splitHeightInLevel.Add(0.5f);
            }
        }

        for (int branchLevel = 0; branchLevel < nrBranchClusters; branchLevel++)
        {
            if (branchSplitHeightInLevel == null)
            {
                branchSplitHeightInLevel = new List<List<float>>();
            }
            if (branchSplitHeightInLevel.Count < branchLevel + 1)
            {
                branchSplitHeightInLevel.Add(new List<float>());
                //branchSplitHeightVariation.Add(0f);
            }

            if ((float)branchSplitHeightInLevel[branchLevel].Count < nrSplitsPerBranch[branchLevel] * (float)nrBranches[branchLevel])
            {
                int s = (int)(nrSplitsPerBranch[branchLevel] * (float)nrBranches[branchLevel] - (float)branchSplitHeightInLevel[branchLevel].Count);
                for (int i = 0; i < s; i++)
                {
                    branchSplitHeightInLevel[branchLevel].Add(0.5f);
                }
            }
        }

        if (rootNode.cotangent == new Vector3(0f, 0f, 0f))
        {
            rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(1f, 0f, 0f)));
            if (rootNode.cotangent == new Vector3(0f, 0f, 0f))
            {
                rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, 1f)));
            }
        }
        else
        {
            rootNode.cotangent = norm(rootNode.cotangent);
        }
        // improve cotangent
        Vector3 dirB = Vector3.Cross(rootNode.tangent[0], rootNode.cotangent);
        rootNode.cotangent = norm(Vector3.Cross(dirB, rootNode.tangent[0]));

        //rootNode.next[0].tangent[0] = norm(rootNode.next[0].point - (rootNode.point + rootNode.tangent[0] * vLength(rootNode.next[0].point - rootNode.point) / 3f));

        Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));

        rootNode.next.Add(new node(norm(treeGrowDir) * treeHeight, nextTangent, new Vector3(1f, 1f, 1f), 1f, 0f, taper, this, rootNode, -1, stemRingResolution));
        //Debug.Log("rootNode.next: clusterIndex: " + rootNode.next[0].clusterIndex);
        rootNode.next[0].cotangent = norm(Vector3.Cross(rootNode.next[0].tangent[0], Vector3.Cross(rootNode.cotangent, rootNode.next[0].tangent[0])));

        rootNode.resampleSpline(resampleNr, noiseAmplitudeLower, noiseAmplitudeUpper, noiseScale);
        if (nrSplits > 0)
        {
            splitRecursive(rootNode, nrSplits, testSplitAngle, testSplitPointAngle);
        }

        Vector3 axis = rootNode.cotangent;

        rootNode.applyCurvature(splitCurvature, axis);

        addBranches(); 

        shyBranches();

        rootNode.calculateRadius(9999f);

        if (allSegments != null)
        {
            allSegments.Clear();
            allSegments = getAllSegments();
        }
        else
        {
            allSegments = new List<segment>();
            allSegments = getAllSegments();
        }

        vertices.Clear();
        triangles.Clear();
        normals.Clear();
        UVs.Clear();
        if (allSegments != null)
        {
            generateAllVerticesAndTriangles();
        }
        mesh.Clear(false);

        for (int i = 0; i < vertices.Count; i++)
        {
            if (float.IsNaN(vertices[i].x) == true)
            {
                vertices[i] = new Vector3(0f, 0f, 0f);
            }
        }

        mesh.SetVertices(vertices);
        mesh.SetUVs(0, UVs);
        mesh.SetTriangles(triangles, 0);
        mesh.SetNormals(normals);

        meshFilter.mesh = mesh;

        addLeaves();

    }

    float interpolateRadius(float radius1, float raidus2, float t)
    {
        return Mathf.Sqrt(fLerp(radius1 * radius1, raidus2 * raidus2, t));
    }

    public void shyBranches()
    {
        // TODO: rotate branch split axis to maximise distance of split branches to all other nodes of same level (iterations...)
      
        const float repulsionStrength = 0.01f; // Strength of the repulsion force
        //const float minDistance = 0.1f; // Minimum distance to avoid excessive repulsion
        const int nrNearestNeighbors = 3;

        List<node> allBranches = new List<node>();
        rootNode.getAllBranchNodes(allBranches, 1);

        List<node> allLeafNodes = new List<node>();
        foreach (node n in allBranches)
        {
            n.getAllLeafNodes(allLeafNodes);
        }

        //Debug.Log("allLeafNodes.Count: " + allLeafNodes.Count);
        //foreach (node n in allLeafNodes)
        //{
        //    Debug.Log("leaf node: " + n.point);
        //}
        
        Dictionary<node, List<(node neighbor, float distance)>> nearestNeighbors = new Dictionary<node, List<(node, float)>>();
        
        // Find nearest neighbors for each leaf node
        foreach (node n1 in allLeafNodes)
        {
            List<(node neighbor, float distance)> neighbors = new List<(node, float)>();
            foreach (node n2 in allLeafNodes)
            {
                foreach (List<node> c in n1.branches)
                {
                    if (c.Contains(n2) == true)
                    {
                        continue; // Skip if they are connected
                    }
                }
                foreach (List<node> c in n2.branches)
                {
                    if (c.Contains(n1) == true)
                    {
                        continue; // Skip if they are connected
                    }
                }
                if (n1 == n2 || n1.parent == n2 || n2.parent == n1)
                {
                    continue; // Skip if they are connected
                }

                float distance = Vector3.Distance(n1.point, n2.point);
                if (distance < shyBranchesMaxDistance)
                {
                    int insertIndex = neighbors.FindIndex(pair => distance < pair.distance);
                    if (insertIndex == -1)
                    {
                        // If no smaller distance is found, add to the end
                        neighbors.Add((n2, distance));
                    }
                    else
                    {
                        // Insert at the correct position
                        neighbors.Insert(insertIndex, (n2, distance));
                    }

                    // Ensure the list does not exceed the maximum size
                    if (neighbors.Count > nrNearestNeighbors)
                    {
                        neighbors.RemoveAt(neighbors.Count - 1); // Remove the furthest node
                        
                    }
                    else
                    {

                    }
                    // Debug.Log("displacement line: " + n1.point + " -> " + n2.point);
                    //     debugDisplacementLines.Add(new line(n1.point, n2.point));
                }
            }
            nearestNeighbors[n1] = neighbors;
        }

        for (int iter = 0; iter < shyBranchesIterations; iter++)
        {
            Dictionary<node, Vector3> displacementMap = new Dictionary<node, Vector3>();

            // Calculate repulsion forces for each node
            foreach (node n1 in allLeafNodes)
            {
                Vector3 displacement = Vector3.zero;

                foreach (node n2 in allLeafNodes)
                {
                    if (n1 == n2) continue;

                    Vector3 direction = n1.point - n2.point;
                    float distance = direction.magnitude;

                    if (distance < shyBranchesMaxDistance)
                    {
                        displacement += direction.normalized / distance; // Repulsion force
                    }
                }

                displacementMap[n1] = displacement * repulsionStrength;
                debugRepulsionForces.Add(new line(n1.point, n1.point + displacementMap[n1]));
            }

            // Apply displacements while maintaining structure
            foreach (node n in allLeafNodes)
            {
                // Apply displacement to the current node
                n.point += displacementMap[n];

                // TODO: propagate the displacement from the leaf node to its parents
                node parent = n.parent; // ERROR HERE! -> parent is rootNode!
                int parentIterations = 9;
                float parentAttenuation = 0.4f; // has to be < 0.5f
                // Adjust this value to control the attenuation of the displacement for parent nodes

                debugRepulsionForces.Add(new line(n.point, parent.point));

                for (int i = 0; i < parentIterations; i++)
                {
                    if (parent != null)
                    {
                        //Debug.Log("displacement to parent");
                        parent.point += displacementMap[n];

                        // Reduce the displacement for parent nodes -> they get contributions from all branches
                        displacementMap[n] = displacementMap[n] * Mathf.Pow(parentAttenuation, (float)i); 

                        parent = parent.parent;
                    }
                    else
                    {
                        break;
                    }
                }
            }
        }

    }

    void generateAllVerticesAndTriangles() // connect to previous segment!
    {
        int offset = 0;
        int counter = 0;

        //Vector3 globalDir = norm(root.next[0].point - root.point);
        
        for(int s = 0; s < allSegments.Count; s++)
        {
            // TEST (A)
            if (allSegments[s].connectedToPrevious == false)
            {
                offset = vertices.Count;
            }

            //Debug.Log("in generateMesh(): segment: ");

                // TODO: automatic tangents -> connecttion line from previous to next vertex -> tangent!

            Vector3 controlPt1 = allSegments[s].start + norm(allSegments[s].startTangent) * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
            Vector3 controlPt2 = allSegments[s].end - norm(allSegments[s].endTangent) * vLength(allSegments[s].end - allSegments[s].start) / 3f;     //(2f / 3f) * (end - start);

            //Debug.Log("startTangent: " + allSegments[s].startTangent);
            //Debug.Log("endTangent: " + allSegments[s].endTangent);


            // Debug.Log("start: " + allSegments[s].start);
            // Debug.Log("end: " + allSegments[s].end); // ERROR HERE  = NaN !!!
            if (float.IsNaN(allSegments[s].end.x) || float.IsNaN(allSegments[s].end.y) || float.IsNaN(allSegments[s].end.z) == true)
            {
                allSegments[s].end = new Vector3(0f, 0f, 0f);
                Debug.Log("ERROR! end is NaN!, start: " + allSegments[s].start);
            }

            float length = vLength(allSegments[s].end - allSegments[s].start);

            // float ringSpacing = length / (float)(allSegments[s].sections); // TODO: global variable ringSpacing -> sections = rountToInt(length / ringSpacing)
                                                                            // branchRingSpacing = length / sections -> use branchRingSpacing here ...
            if (ringSpacing == 0f)
            {
                ringSpacing = 1f;
            }
            int sections = (int)Mathf.RoundToInt(length / ringSpacing);
            if (sections <= 0)
            {
                sections = 1;
            }
            float branchRingSpacing = length / sections;
            //ringSpacing = rSpacing;

            //Debug.Log("sections: " + sections);
            Vector3[] dirA = new Vector3[sections + 1];
            Vector3[] dirB = new Vector3[sections + 1];
            Vector3[] tangent = new Vector3[sections + 1];
            Vector3[] curvature = new Vector3[sections + 1];

            Vector3[] pos = new Vector3[sections + 1];

            //int debug = allSegments[s].sections + 1;
            //Debug.Log("sections loop: " + debug);
            //debugListRed.Add(allSegments[s].start);
            //debugListRed.Add(allSegments[s].end);

            tangentDebugLines.Add(new line(allSegments[s].start, controlPt1));
            tangentDebugLines.Add(new line(allSegments[s].end, controlPt2));

            //debugListBlue.Add(controlPt1);
            //debugListBlue.Add(controlPt2);

            bool connectedToPrevious = allSegments[s].connectedToPrevious;
            int startSection = 0;

            if (connectedToPrevious == true)
            {
                // connect to previous segment
                startSection = 1;
            }

            float arcLength = 0f;

            for (int j = startSection; j < sections + 1; j++)
            {
                pos[j] = sampleSplineC(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)sections);
                
                debugListGreen.Add(pos[j]);

                if (j > 0)
                {
                    arcLength += vLength(pos[j] - pos[j - 1]);
                }

                tangent[j] = norm(sampleSplineTangentC(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)sections));

                dirA[j] = vLerp(allSegments[s].startCotangent, allSegments[s].endCotangent, (float)j / (float)sections);// green
                
                dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); // blue

                // improve dirA!
                dirA[j] = norm(Vector3.Cross(dirB[j], tangent[j])); // green

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                Vector3 dir = norm(tangent[j]);

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                dirBdebugLines.Add(new line(pos[j], pos[j] + dirB[j] / 5f)); // blue

                for (int i = 0; i <= allSegments[s].ringResolution; i++)
                {
                    float angle = (float)i * 2f * Mathf.PI / (float)allSegments[s].ringResolution;

                    float f = (float)j / (float)(length / branchRingSpacing) * Mathf.Cos(angle) + fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing));
                    
                    Vector3 v = pos[j] + dirA[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / branchRingSpacing)) * Mathf.Cos(angle) +
                                         dirB[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / branchRingSpacing)) * Mathf.Sin(angle);

                    
                    Vector2 uv = new Vector2(angle / (2f * Mathf.PI), arcLength);
                    if (i == allSegments[s].ringResolution)
                    {
                        uv.x = 1f;
                    }
                    
                    vertices.Add(v);

                    Vector3 n = norm(v - pos[j]);
                    if (vLength(n) > 0f)
                    {
                        normals.Add(n);
                    }
                    else
                    {
                        Vector3 normal = dirA[j]  * Mathf.Cos(angle) + dirB[j] * Mathf.Sin(angle);

                        normals.Add(norm(normal));
                    }

                    UVs.Add(uv);

                    
                    // TODO: total arclength of segment -> divide by n so scale is even
                    // -> arclength offset for each section
                    

                    counter += 1;
                }
            }

            //Debug.Log("vertex count: " + vertices.Count);
            generateTriangles(sections, allSegments[s].ringResolution, offset, connectedToPrevious);
            offset += counter;
            //offset += (sections + 1) * (allSegments[s].ringResolution + 1);
            counter = 0;
            //Debug.Log("triangle count: " + triangles.Count);
        }
    }

    
    void generateTriangles(int Sections, int ringRes, int offset, bool connectedToPrevious) // TODO: connectedToPrevious
    {
        //Debug.Log("in generateTriangles: sections: " + Sections);
        //Debug.Log("in generateTriangles: ringResolution: " + ringResolution);

        if (connectedToPrevious == true)
        {
            // TODO
            offset -= ringRes + 1;
        }

        int count = 0;
        for (int j = 0; j < Sections; j++)
        {
            for (int i = 0; i < ringRes ; i++) 
            {
                if (j % 2 == 1)
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + i);

                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (2 * ringRes + 1)));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + i);
                    }
                    else
                    {
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (ringRes + 1)));

                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + (i % (ringRes + 1)));
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (ringRes + 1)));
                    }
                }
                else
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (ringRes + 1)));

                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + (i % (ringRes + 1)));
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (ringRes + 1)));
                    }
                    else
                    {
                        triangles.Add(offset + j * (ringRes + 1) + i);
                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + i);

                        triangles.Add(offset + j * (ringRes + 1) + (i + 1) % (ringRes + 1));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + ((i + 1) % (ringRes + 1)));
                        triangles.Add(offset + j * (ringRes + 1) + ringRes + 1 + i);
                    }
                }
                count += 6;
            }
            count = 0;
        }
    }

    void OnDrawGizmos()
    {
        
        //Debug.Log("OnDrawGizmos");
        // Gizmos.color = Color.red;
        // Gizmos.DrawSphere(new Vector3(0f, 0f, 0f), gizmoRadius);
    // 
        // //Gizmos.color = Color.blue;
        // //for (int i = 0; i < vertices.Count; i++)
        // //{
        // //    Gizmos.DrawRay(vertices[i], normals[i] * normalGizmoSize);
        // //}
// 
        // Gizmos.color = Color.red;
        // Gizmos.DrawSphere(new Vector3(0f, 0f, 0f), gizmoRadius * 20f);

        if (allSegments != null)
        {
            
            //Gizmos.color = new Color(1f, 1f, 0f);
            //foreach (Vector3 v in debugErrorPoints)
            //{
            //    Gizmos.DrawSphere(v, gizmoRadius * 2f);
            //}

            Gizmos.color = Color.green;
            foreach (line l in debugDisplacementLines)
            {
                Gizmos.DrawLine(l.start, l.end);
            }
            Gizmos.color = Color.red;
            foreach (line l in debugRepulsionForces)
            {
                Gizmos.DrawLine(l.start, l.end);
            }

            Gizmos.color = Color.blue;
            //Debug.Log("debugLines blue count " + debugLinesBlue.Count);
            foreach (line l in debugLinesBlue)
            {
                //Debug.Log("in gizmos: debugLinesBlue: " + l.start + ", " + l.end);
                Gizmos.DrawLine(l.start, l.end);
            }
            Gizmos.color = Color.red;
            foreach (line l in debugLinesRed)
            {
                Gizmos.DrawLine(l.start, l.end);
            }
            Gizmos.color = Color.green;
            foreach (line l in debugLinesGreen)
            {
                Gizmos.DrawLine(l.start, l.end);
            }

            //foreach (segment s in allSegments)
            //{
            //    Gizmos.color = Color.red;
            //    // Vector3 controlPt1 = s.start + s.startTangent * vLength(s.end - s.start) / 3f; //(1f / 3f) * (end - start);
            //    // Vector3 controlPt2 = s.end - s.endTangent * vLength(s.end - s.start) / 3f;     //(2f / 3f) * (end - start);
            //    // Gizmos.DrawSphere(s.start, gizmoRadius);
            //    // Gizmos.DrawSphere(s.end, gizmoRadius);
            //
            //    // Gizmos.color = Color.green;
            //    // Gizmos.DrawRay(s.start, s.startTangent * normalGizmoSize);
            //    // Gizmos.DrawRay(s.end, s.endTangent * normalGizmoSize);
            //    //Gizmos.color = Color.red;
            //    //Gizmos.DrawRay(s.start, s.startCotangent * normalGizmoSize);
            //
            //    Gizmos.color = Color.blue;
            //    //Gizmos.DrawRay(s.end, s.endCotangent * normalGizmoSize);
            //    //Gizmos.DrawSphere(controlPt1, gizmoRadius);
            //    //Gizmos.DrawSphere(controlPt2, gizmoRadius);
            //}  

            Gizmos.color = Color.red;
            foreach (Vector3 v in debugPointsRed)
            {
                Gizmos.DrawSphere(v, gizmoRadius * 0.6f);
            } 

            

            Gizmos.color = new Color(1f, 0f, 1f);
            foreach (Vector3 v in debugErrorPointsCompare)
            {
                Gizmos.DrawSphere(v, gizmoRadius * 0.3f);
            }
            

            
            for (int i = 0; i < debugSamplePoints.Count; i++)
            {
                Gizmos.color = Color.green;
                Gizmos.DrawSphere(debugSamplePoints[i], gizmoRadius);
                Gizmos.color = Color.red;
                Gizmos.DrawRay(debugSamplePoints[i], debugSampleTangents[i] * normalGizmoSize);
            }

            // Gizmos.color = new Color(1f, 1f, 0f);
            // Gizmos.DrawSphere(debugNext, gizmoRadius);
            // Gizmos.DrawSphere(debugPrev, gizmoRadius / 2f);

            
            
        }
    }


    static float fLerp(float a, float b, float t)
    {
        return a + (b - a) * t;
    }

    static Vector3 vLerp(Vector3 a, Vector3 b, float t)
    {
        return a + (b - a) * t;
    }

    static Vector3 norm(Vector3 v)
    {
        return v / Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    }

    static float vLength(Vector3 v)
    {
        return Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    }
    static Vector3 sampleSplineC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        return (1f - t) * (1f - t) * (1f - t) * controlA + 3f * (1f - t) * (1f - t) * t * controlB + 3f * (1f - t) * t * t * controlC + t * t * t * controlD;
    }

    static Vector3 sampleSplineT(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + norm(startTangent) * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - norm(endTangent) * vLength(end - start) / 3f;

        Vector3 p = (1f - t) * (1f - t) * (1f - t) * start + 3f * (1f - t) * (1f - t) * t * controlPt1 + 3f * (1f - t) * t * t * controlPt2 + t * t * t * end;

        if (p.y > end.y)
        {
            Debug.Log("ERROR! p.y > start.y && p.y > end.y, start: " + start + ", end: " + end + ", p: " + p);
        }
        
        return p;

    }

    //Vector3 controlPt1 = allSegments[s].start + allSegments[s].startTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
    //        Vector3 controlPt2 = allSegments[s].end - allSegments[s].endTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f;

    static Vector3 sampleSplineTangentC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
        return norm(-3f * (1f - t) * (1f - t) * controlA + 3f * (3f * t * t - 4f * t + 1f) * controlB + 3f * (-3f * t * t + 2f * t) * controlC + 3f * t * t * controlD);
    }

    static Vector3 sampleSplineTangentT(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + norm(startTangent) * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - norm(endTangent) * vLength(end - start) / 3f;

        return norm(-3f * (1f - t) * (1f - t) * start + 3f * (3f * t * t - 4f * t + 1f) * controlPt1 + 3f * (-3f * t * t + 2f * t) * controlPt2 + 3f * t * t * end);
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return 6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD;
    }
}
