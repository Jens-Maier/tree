using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class treeGen : MonoBehaviour
{
    public List<Vector3> allVertices;
    public List<int> allTriangles;

    public GameObject selfGameObject;
    public Mesh mesh;
    public MeshFilter meshFilter;

    public float gizmoScale = 0.2f;

    // settings
    public int levels;
    public List<int> numberBranchesOnLevels;

    branch rootBranch;
    public Vector3 start;
    public Vector3 end;

    public Vector3 controlPt1;
    public Vector3 controlPt2;

    public float ringSpacing; // 0.04
    public float taper; // 0.4 %
    public int ringRes;
    public float radius;
    public float branchRotation;

    // gizmos
    public List<Vector3> gizmosBlue;
    public List<Vector3> gizmosRed;

    // Start is called before the first frame update
    void Start()
    {
        // settings
        levels = 0;
        if (numberBranchesOnLevels == null)
        {
            numberBranchesOnLevels = new List<int>();
            for (int i = 0; i < levels; i++)
            {
                numberBranchesOnLevels.Add(0);
            }
        }

        rootBranch = new branch(start, controlPt1, controlPt2, end, ringSpacing, ringRes, taper, radius, this, 0);

        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();

        allVertices = new List<Vector3>();
        allTriangles = new List<int>();
    }

    // Update is called once per frame
    void Update()
    {
        allVertices.Clear();
        allTriangles.Clear();

        gizmosBlue.Clear();
        gizmosRed.Clear();

        rootBranch.generateBranchMesh(start, controlPt1, controlPt2, end, ringSpacing, ringRes, taper, radius);

        if (levels > 0)
        {
            rootBranch.generateChildBranches();
        }
        getVerticesAndTriangles();
        
        mesh.Clear(false);
        mesh.SetVertices(allVertices);
        mesh.SetTriangles(allTriangles, 0);
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }

    void getVerticesAndTriangles()
    {
        allVertices = rootBranch.vertices;
        allTriangles = rootBranch.triangles;
        int indexOffset = rootBranch.vertices.Count;

        if (rootBranch.branches != null)
        {
            foreach (branch b in rootBranch.branches)
            {
                allVertices.AddRange(b.vertices);

                foreach (int i in b.triangles)
                {
                    allTriangles.Add(indexOffset + i);
                }
                indexOffset = indexOffset + b.vertices.Count;
            }
        }
    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        //foreach (Vector3 v in vertices)
        //{
        //    Gizmos.DrawSphere(v, 0.005f);
        //}

        Gizmos.DrawSphere(start, 0.05f);
        Gizmos.DrawSphere(controlPt1, 0.05f);
        Gizmos.DrawSphere(controlPt2, 0.05f);
        Gizmos.DrawSphere(end, 0.05f);

        if (rootBranch != null)
        {
            for (int j = 0; j < (int)(rootBranch.length / ringSpacing); j++)
            {
                Gizmos.color = Color.blue;
                Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.dirA[j]);// dirA
                Gizmos.color = Color.green;
                Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.dirB[j]);// dirB
                Gizmos.color = Color.red;
                Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.tangent[j]);
                Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.curvature[j]);
            }
            Gizmos.color = Color.blue;
            foreach (Vector3 g in gizmosBlue)
            {
                Gizmos.DrawSphere(g, 0.01f);
            }
            Gizmos.color = Color.red;
            foreach (Vector3 g in gizmosRed)
            {
                Gizmos.DrawSphere(g, 0.02f);
            }

        }
    }
}

public class branch
{
    // branch segment
    public Vector3 branchStart;
    public Vector3 branchEnd;

    public Vector3 branchControlPt1;
    public Vector3 branchControlPt2;

    public Vector3[] dirA;
    public Vector3[] dirB;

    public Vector3[] pos;

    public float length;

    public float stemRadius; // 0.08

    public int stemRingResolution; // 5 // #vertices = 2 * stemRingResolution

    public float ringSpacing; // 0.04

    public float taper; // 0.4 %

    public Vector3[] tangent;
    public Vector3[] bitangent;

    public Vector3[] curvature;

    public List<Vector3> vertices;
    public List<int> triangles;

    public List<branch> branches;
    int level;

    public treeGen tree;


    public branch(Vector3 start, Vector3 controlPt1, Vector3 controlPt2, Vector3 end, float rSpacing, int ringRes, float tapr, float radius, treeGen t, int l)
    {
        tree = t;
        level = l;
        vertices = new List<Vector3>();
        triangles = new List<int>();
        branchStart = start;
        branchControlPt1 = controlPt1;
        branchControlPt2 = controlPt2;
        branchEnd = end;
        tree.gizmosBlue.Add(end);
        generateBranchMesh(start, controlPt1, controlPt2, end, rSpacing, ringRes, tapr, radius);
    }

    public void generateChildBranches()
    {
        Vector3[] startPoints = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] endPoints = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] controlPts1 = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] controlPts2 = new Vector3[tree.numberBranchesOnLevels[level]];

        tree.gizmosBlue.Clear();
        branches = new List<branch>();

        for (int i = 0; i < tree.numberBranchesOnLevels[level]; i++)
        {
            startPoints[i] = sampleSpline(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)tree.numberBranchesOnLevels[level]);
            tree.gizmosBlue.Add(startPoints[i]);

            Vector3 tangent = sampleSplineTangent(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)tree.numberBranchesOnLevels[level]);
            Vector3 bitangent = norm(Vector3.Cross(tangent, new Vector3(1f, 0f, 0f)));

            Vector3 rotatedBitangent = Quaternion.AngleAxis(tree.branchRotation * i, norm(tangent)) * bitangent;

            endPoints[i] = startPoints[i] + rotatedBitangent + tangent;
            //controlPts1[i] = vLerp(startPoints[i], endPoints[i], 1f / 3f);
            controlPts1[i] = startPoints[i] + tangent * 0.5f;
            controlPts2[i] = vLerp(startPoints[i], endPoints[i], 2f / 3f);

            branches.Add(new branch(startPoints[i], controlPts1[i], controlPts2[i], endPoints[i], ringSpacing, stemRingResolution / 2, taper, stemRadius / 4f, tree, level + 1));
        }

    }


    public void generateBranchMesh(Vector3 start, Vector3 controlPt1, Vector3 controlPt2, Vector3 end, float rSpacing, int ringRes, float tapr, float radius)
    {
        branchStart = start;
        branchControlPt1 = controlPt1;
        branchControlPt2 = controlPt2;
        branchEnd = end;

        tree.gizmosRed.Add(end);

        length = vLength(end - start);
        ringSpacing = rSpacing;
        stemRingResolution = ringRes;
        taper = tapr;
        stemRadius = radius;

        dirA = new Vector3[(int)(length / ringSpacing)];
        dirB = new Vector3[(int)(length / ringSpacing)];
        tangent = new Vector3[(int)(length / ringSpacing)];
        bitangent = new Vector3[(int)(length / ringSpacing)];
        curvature = new Vector3[(int)(length / ringSpacing)];

        pos = new Vector3[(int)(length / ringSpacing)];

        bool flippedTangent = false;
        bool flippedBitangent = false;
        bool flippedDirB = false;

        for (int j = 0; j < (int)(length / ringSpacing); j++)
        {
            pos[j] = sampleSpline(start, controlPt1, controlPt2, end, (float)j / (length / ringSpacing));

            tree.gizmosBlue.Add(pos[j]);

            tangent[j] = norm(sampleSplineTangent(start, controlPt1, controlPt2, end, (float)j / (length / ringSpacing)));

            if (j > 0)
            {
                if (Vector3.Dot(tangent[j - 1], tangent[j]) < 0f)
                {
                    flippedTangent = true;
                    Debug.Log("flippedTangent!");
                }
                if (flippedTangent)
                {
                    tangent[j] = -tangent[j];
                }
            }

            Vector3 cross = Vector3.Cross(tangent[j], new Vector3(1f, 0f, 0f));
            Vector3 b = norm(cross);

            if (j > 0)
            {
                if (Vector3.Dot(bitangent[j - 1], bitangent[j]) < 0f)
                {
                    flippedBitangent = true;
                    Debug.Log("flippedBitangent!");
                }
                if (flippedBitangent)
                {
                    b = -b;
                }
            }

            bitangent[j] = b;

            curvature[j] = norm(sampleSplineCurvature(start, controlPt1, controlPt2, end, (float)j / (length / ringSpacing)));

            dirA[j] = norm(bitangent[j]); //red

            dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); //green 

            if (j > 0)
            {
                if (Vector3.Dot(dirB[j - 1], dirB[j]) < 0f)
                {
                    flippedDirB = true;
                    Debug.Log("flippedDirB!");
                }
                if (flippedDirB)
                {
                    dirB[j] = -dirB[j];
                    dirA[j] = -dirA[j];
                }
            }

            Vector3 dir = norm(tangent[j]);


            for (int i = 0; i < 2 * stemRingResolution; i++)
            {
                float angle = (Mathf.PI / (float)stemRingResolution) * (float)i;

                Vector3 v = pos[j] + dirA[j] * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
                            dirB[j] * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);

                vertices.Add(v);
            }
        }
        Debug.Log("vertex count: " + vertices.Count);
        generateTriangles();
        Debug.Log("triangle count: " + triangles.Count);
    }

    void generateTriangles()
    {
        int rings = (int)(length / ringSpacing) - 1;

        Debug.Log("level: " + level + ", rings: " + rings); // ist: 24, soll: 19

        triangles = new List<int>();
        for (int j = 0; j < (int)(length / ringSpacing) - 1; j++)
        {
            for (int i = 0; i < 2 * stemRingResolution; i++)
            {
                if (j % 2 == 1)
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                    else
                    {
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                }
                else
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                    else
                    {
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                }
            }
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
        return (Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }

    static Vector3 norm(Vector3 v)
    {
        return (v / Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }

    static Vector3 sampleSpline(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        return ((1f - t) * (1f - t) * (1f - t) * controlA + 3f * (1f - t) * (1f - t) * t * controlB + 3f * (1f - t) * t * t * controlC + t * t * t * controlD);
    }

    static Vector3 sampleSplineTangent(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
        return (-3f * (1f - t) * (1f - t) * controlA + 3f * (3f * t * t - 4f * t + 1f) * controlB + 3f * (-3f * t * t + 2f * t) * controlC + 3f * t * t * controlD);
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return (6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD);
    }

}


//if (vLength(curvature) > 0.001f)
//{
//    bitangent = norm(curvature);
//}
//else
//{
//    bitangent = new Vector3(0f, 0f, 0f);
//    //if (vLength(Vector3.Cross(tangent, new Vector3(1f, 0f, 0f))) > 0.001f)
//    //{
//    //    bitangent = Vector3.Cross(tangent, new Vector3(1f, 0f, 0f));
//    //}
//    //else
//    //{
//    //    bitangent = Vector3.Cross(tangent, new Vector3(0f, 0f, 1f));
//    //}
//}


//public void split()
//{
//    branches = new List<branch>();
//    //branches.Add(new branch());

//    float splitAngleDeg = 40f;
//    float radius;

//    Vector3 vertexA = vertices[2 * stemRingResolution * ((int)(length / ringSpacing) - 1) - 1];
//    Vector3 VertexB = vertices[2 * stemRingResolution * ((int)(length / ringSpacing) - 1) - 1 - stemRingResolution];

//    // connecting line: ellipse!
//    //float ellipseHeight = (radius / 2f) * Mathf.tan(2f * Mathf.PI * splitAngleDeg / 360f);

//}
