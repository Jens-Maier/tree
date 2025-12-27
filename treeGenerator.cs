//using System.Numerics;
using System.Collections.Generic;
//using System.Numerics;

//using System.Diagnostics;
using System.Security.Cryptography.X509Certificates;
using UnityEngine;

namespace treeGenNamespace
{

public class node
{
    public Vector3 point;
    public float radius;
    public List<Vector3> tangent;
    public Vector3 cotangent;
    public int clusterIndex;
    public int ringResolution;
    public float taper;
    public float tValGlobal;
    public float tValBranch;
    public List<node> next;
    public List<node> branches;
    public float branchLength;
    public bool isLastRotated = false;
    public List<Vector3> outwardDir;
    public List<float> rotateAngleRange;


    public node(Vector3 Point, float Radius, Vector3 Cotangent, int ClusterIndex, int RingResolution, float Taper, float TvalGlobal, float TvalBranch, float BranchLength)
    {
        point = Point;
        radius = Radius;
        tangent = new List<Vector3>();
        cotangent = Cotangent;
        clusterIndex = ClusterIndex;
        ringResolution = RingResolution;
        taper = Taper;
        tValGlobal = TvalGlobal;
        tValBranch = TvalBranch;
        next = new List<node>();
        branches = new List<node>();
        branchLength = BranchLength;
        isLastRotated = false;
        outwardDir = new List<Vector3>();
        rotateAngleRange = new List<float>();
    }
}

public class treeGenerator : MonoBehaviour
{
    public treeSettings settings;
    public List<node> nodes;

    
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


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        Debug.Log("Start() of treeGenerator.cs");
        settings = new treeSettings();
        nodes = new List<node>();
        nodes.Add(new node(new Vector3(0f, 0f, 0f), 
                           0.1f, 
                           new Vector3(1f, 0f, 0f), 
                           -1, 
                           settings.stemRingRes, 
                           settings.taper, 
                           0f, 
                           0f, 
                           settings.height));

        nodes[0].tangent.Add(new Vector3(0f, 0f, 1f));
        nodes[0].cotangent = new Vector3(1f, 0f, 0f);

        nodes.Add(new node(settings.treeGrowDir * settings.height, 
                           0.1f, 
                           new Vector3(1f, 0f, 0f), 
                           -1, 
                           settings.stemRingRes, 
                           settings.taper, 
                           1.0f, 
                           0.0f, 
                           settings.height));

    }

    // Update is called once per frame
    void Update()
    {
        
    }
}



}