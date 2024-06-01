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
        
    public branch rootBranch;

    public List<branch> allBranches;

    // settings
    [Header("____________________________________________________________________________________________________________________________________________________________________")]
    [Header("Settings")]
    public int levels;
    public List<int> numberBranchesOnLevels;

    public Vector3 start;
    public Vector3 end;

    public Vector3 controlPt1;
    public Vector3 controlPt2;

    public float ringSpacing; // 0.04
    public float taper; // 0.4 %
    public int ringRes;
    public float radius;

    [Header("Branch Settings")]
    public float branchRotation;
    public float branchRotationVariation;
    public float branchRotationVariationFrequency;
    public float downAngle;
    public float branchLengthScalingFactor;
    public float branchThicknessScalingFactor;
    public float branchTipUpwardAttraction;

    [Header("Branch Splitting")]
    [Range(0f, 1f)]
    public float splitHeight;// = 0.5f;
    public float splitAngleDeg;// = 30f;

    // gizmos
    [Header("____________________________________________________________________________________________________________________________________________________________________")]
    [Header("Gizmos")]
    public bool drawGizmos;
    public float gizmoScale = 0.2f;

    public List<Vector3> gizmosBlue;
    public List<Vector3> gizmosRed;
    public List<Vector3> gizmosGreen;

    // Start is called before the first frame update
    void Start()
    {
        // settings
        levels = 1;
        if (numberBranchesOnLevels == null)
        {
            numberBranchesOnLevels = new List<int>();
            for (int i = 0; i < levels; i++)
            {
                numberBranchesOnLevels.Add(0);
            }
        }

        rootBranch = new branch(start, controlPt1, controlPt2, end, ringSpacing, ringRes, taper, radius, this, 0);
        allBranches = new List<branch>();

        rootBranch.split();

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
        gizmosGreen.Clear();

        if (rootBranch != null)
        {
            rootBranch.generateBranchMesh(start, controlPt1, controlPt2, end, ringSpacing, ringRes, taper, radius);
        }
        gizmosBlue.Clear();
        gizmosRed.Clear();
        gizmosGreen.Clear();


        //if (levels > 0)
        //{
        //    rootBranch.generateChildBranches();
        //}
        rootBranch.branches.Clear();
        
        rootBranch.resampleSpline(4); // TODO: combine with split!
        //rootBranch.split();

        getVerticesAndTriangles();
        
        mesh.Clear(false);
        mesh.SetVertices(allVertices);
        mesh.SetTriangles(allTriangles, 0);
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }

    void getVerticesAndTriangles()
    {
        rootBranch.getAllBranches();

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
        if (drawGizmos)
        {
            Gizmos.color = Color.red;
            //foreach (Vector3 v in vertices)
            //{
            //    Gizmos.DrawSphere(v, 0.005f);
            //}

            //Gizmos.DrawSphere(start, 0.05f);
            //Gizmos.DrawSphere(controlPt1, 0.05f);
            //Gizmos.DrawSphere(controlPt2, 0.05f);
            //Gizmos.DrawSphere(end, 0.05f);

            //if (rootBranch != null)
            //{
            //    for (int j = 0; j < rootBranch.pos.Length; j++) // ERROR out of range ???
            //    {
            //        Gizmos.color = Color.blue;
            //        Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.dirA[j]);// dirA
            //        Gizmos.color = Color.green;
            //        Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.dirB[j]);// dirB
            //        Gizmos.color = Color.red;
            //        Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.tangent[j]);
            //        Gizmos.DrawRay(rootBranch.pos[j], gizmoScale * rootBranch.curvature[j]);
            //    }
            Gizmos.color = Color.green;
            foreach (Vector3 g in gizmosGreen)
            {
                Gizmos.DrawSphere(g, 0.007f);
            }
            Gizmos.color = Color.red;
            foreach (Vector3 g in gizmosRed)
            {
                Gizmos.DrawSphere(g, 0.02f);
            }
            
            Gizmos.color = Color.blue;
                foreach (Vector3 g in gizmosBlue)
                {
                    Gizmos.DrawSphere(g, 0.01f);
                }
            //    Gizmos.color = Color.red;
            //    foreach (Vector3 g in gizmosRed)
            //    {
            //        Gizmos.DrawSphere(g, 0.02f);
            //    }
            //
            //}
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

    public Vector3[] dirA; // dirA = norm(bitangent)
    public Vector3[] dirB; // local coordinate system on spline

    public Vector3[] tangent;
    public Vector3[] bitangent;
    
    public Vector3[] pos; // spline sample points

    public float length;

    public float stemRadius; // 0.08

    public int stemRingResolution; // 5 // #vertices = 2 * stemRingResolution

    public float ringSpacing; // 0.04

    public int sections;

    public float taper; // 0.4 %

    public Vector3[] curvature;

    public List<Vector3> vertices;
    public List<int> triangles;

    public branch nextSegment;
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
        tree.gizmosGreen.Add(end);
        generateBranchMesh(start, controlPt1, controlPt2, end, rSpacing, ringRes, tapr, radius);
    }

    public void getAllBranches()
    {
        tree.allBranches.Add(this);
        if (nextSegment != null)
        {
            nextSegment.getAllBranches();
        }

        if (branches != null)
        {
            foreach (branch b in branches)
            {
                b.getAllBranches();
            }
        }
    }

    public void resampleSpline(int sections)
    {
        // subdivide spline before splitting -> stem stays straight 
        Vector3[] samplePts = new Vector3[sections + 1];
        Vector3[] sampleTangents = new Vector3[sections];
        float[] sampleStemRadius = new float[sections];

        for (int i = 0; i < sections; i++)
        {
            samplePts[i] = sampleSpline(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)sections);
            sampleTangents[i] = sampleSplineTangent(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)sections);
            sampleStemRadius[i] = fLerp(stemRadius, taper * stemRadius, (float)i / (float)sections);
        }

        for (int i = 0; i < sections - 1; i++)
        {
            Vector3 control_1 = samplePts[i] + sampleTangents[i] * (1f / 12f);
            Vector3 control_2 = samplePts[i + 1] - sampleTangents[i + 1] * (1f / 12f);
            tree.gizmosGreen.Add(control_1);
            tree.gizmosGreen.Add(control_2);

            if (i == 0)
            {
                branchStart = samplePts[0];
                branchControlPt1 = control_1;
                branchControlPt2 = control_2;
                branchEnd = samplePts[1];
                
                //tree.rootBranch = new branch(samplePts[i], control_1, control_2, samplePts[i + 1],
                //                             ringSpacing, stemRingResolution, taper, sampleStemRadius[i], tree, level);
            }
            else
            {
                nextSegment = new branch(samplePts[i], control_1, control_2, samplePts[i + 1],
                                         ringSpacing, stemRingResolution, taper, sampleStemRadius[i], tree, level);

                //tree.rootBranch.branches.Add(new branch(samplePts[i], control_1, control_2, samplePts[i + 1],
                //                                        ringSpacing, stemRingResolution, taper, sampleStemRadius[i], tree, level));
            }

        }
    }

    public void split()
    {
        //float splitHeight = 0.5f;
        //float splitAngleDeg = 30f;
        Vector3 splitAngleAxis = norm(Vector3.Cross(sampleSplineTangent(branchStart, branchControlPt1, branchControlPt2, branchEnd, tree.splitHeight), new Vector3(1f, 0f, 0f)));

        Vector3 splitPoint = sampleSpline(branchStart, branchControlPt1, branchControlPt2, branchEnd, tree.splitHeight);
        Vector3 splitPointTangent = sampleSplineTangent(branchStart, branchControlPt1, branchControlPt2, branchEnd, tree.splitHeight);
        float radiusAtSplitPoint = fLerp(stemRadius, taper * stemRadius, tree.splitHeight);

        Vector3 rotatedSplitPointTangentBranchA = Quaternion.AngleAxis(tree.splitAngleDeg, splitAngleAxis) * splitPointTangent;
        Vector3 rotatedSplitPointTangentBranchB = Quaternion.AngleAxis(-tree.splitAngleDeg, splitAngleAxis) * splitPointTangent;

        Vector3 controlPt1HighBranchA = splitPoint - (1f / 6f) * length * norm(rotatedSplitPointTangentBranchA);
        Vector3 controlPt2LowBranchA = splitPoint + (1f / 6f) * length * norm(rotatedSplitPointTangentBranchA);

        Vector3 controlPt1HighBranchB = splitPoint - (1f / 6f) * length * norm(rotatedSplitPointTangentBranchB);
        Vector3 controlPt2LowBranchB = splitPoint + (1f / 6f) * length * norm(rotatedSplitPointTangentBranchB);

        Vector3 rotatedBranchEndBranchA = Quaternion.AngleAxis(tree.splitAngleDeg, splitAngleAxis) * branchEnd;
        Vector3 rotatedBranchEndBranchB = Quaternion.AngleAxis(-tree.splitAngleDeg, splitAngleAxis) * branchEnd;

        if (branches == null)
        {
            branches = new List<branch>();
        }
        branches.Add(new branch(splitPoint, 
                                controlPt2LowBranchA,
                                rotatedBranchEndBranchA + (branchControlPt2 - rotatedBranchEndBranchA) * tree.splitHeight,
                                rotatedBranchEndBranchA, 
                                ringSpacing, 
                                stemRingResolution, 
                                taper, 
                                radiusAtSplitPoint, 
                                tree, 
                                level + 1));

        branches.Add(new branch(splitPoint,
                                controlPt2LowBranchB,
                                rotatedBranchEndBranchB + (branchControlPt2 - rotatedBranchEndBranchB) * tree.splitHeight,
                                rotatedBranchEndBranchB,
                                ringSpacing,
                                stemRingResolution,
                                taper,
                                radiusAtSplitPoint,
                                tree,
                                level + 1));

        branchControlPt1 = branchStart + (branchControlPt1 - branchStart) * tree.splitHeight;
        branchControlPt2 = controlPt1HighBranchA;
        branchEnd = splitPoint;
        tree.gizmosBlue.Add(splitPoint);
        tree.gizmosBlue.Add(rotatedBranchEndBranchA);
        tree.gizmosBlue.Add(rotatedBranchEndBranchB);
        generateBranchMesh(branchStart, branchControlPt1, branchControlPt2, branchEnd, ringSpacing, stemRingResolution, fLerp(1f, taper, tree.splitHeight), stemRadius);
    }

    public void generateChildBranches()
    {
        Vector3[] startPoints = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] endPoints = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] controlPts1 = new Vector3[tree.numberBranchesOnLevels[level]];
        Vector3[] controlPts2 = new Vector3[tree.numberBranchesOnLevels[level]];

        //tree.gizmosBlue.Clear();
        branches = new List<branch>();

        for (int i = 0; i < tree.numberBranchesOnLevels[level]; i++)
        {
            Vector3 tangent = norm(sampleSplineTangent(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)tree.numberBranchesOnLevels[level]));
            Vector3 bitangent = norm(Vector3.Cross(tangent, new Vector3(1f, 0f, 0f)));

            Vector3 rotatedBitangent = Quaternion.AngleAxis((tree.branchRotation + tree.branchRotationVariation * Mathf.Sin(tree.branchRotationVariationFrequency * 2f * Mathf.PI * (float)i / (float)tree.numberBranchesOnLevels[level])) * (float)i, norm(tangent)) * bitangent;

            float length = tree.branchLengthScalingFactor * fLerp(1f, taper, (float)i / (float)tree.numberBranchesOnLevels[level]);

            startPoints[i] = sampleSpline(branchStart, branchControlPt1, branchControlPt2, branchEnd, (float)i / (float)tree.numberBranchesOnLevels[level]);
            endPoints[i] = startPoints[i] + length * ((tree.downAngle / 90f) * rotatedBitangent + (1f - (tree.downAngle / 90f)) * tangent);
            controlPts1[i] = vLerp(startPoints[i], endPoints[i], 1f / 3f);
            controlPts2[i] = vLerp(startPoints[i], endPoints[i], 2f / 3f);

            endPoints[i] += new Vector3(0f, 0.01f, 0f) * tree.branchTipUpwardAttraction;

            float radius = tree.branchThicknessScalingFactor * fLerp(stemRadius, taper * stemRadius, (float)i / (float)tree.numberBranchesOnLevels[level]);
            
            tree.gizmosBlue.Add(startPoints[i]);

            branches.Add(new branch(startPoints[i], controlPts1[i], controlPts2[i], endPoints[i], ringSpacing, stemRingResolution / 2, taper, radius, tree, level + 1));
        }

    }

    public void generateBranchMesh(Vector3 start, Vector3 controlPt1, Vector3 controlPt2, Vector3 end, float rSpacing, int ringRes, float tapr, float radius)
    {
        vertices.Clear();
        triangles.Clear();
        

        branchStart = start;
        branchControlPt1 = controlPt1;
        branchControlPt2 = controlPt2;
        branchEnd = end;

        tree.gizmosRed.Add(tree.start);
        tree.gizmosRed.Add(tree.controlPt1);
        tree.gizmosRed.Add(tree.controlPt2);
        tree.gizmosRed.Add(tree.end);

        tree.gizmosRed.Add(end);

        length = vLength(end - start);
        sections = (int)(length / rSpacing);
        ringSpacing = length / (float)sections;
        //ringSpacing = rSpacing;
        stemRingResolution = ringRes;
        taper = tapr;
        stemRadius = radius;

        dirA = new Vector3[sections + 1];
        dirB = new Vector3[sections + 1];
        tangent = new Vector3[sections + 1];
        bitangent = new Vector3[sections + 1];
        curvature = new Vector3[sections + 1];

        pos = new Vector3[sections + 1];

        bool flippedTangent = false;
        bool flippedBitangent = false;
        bool flippedDirB = false;

        for (int j = 0; j < sections + 1; j++)
        {
            pos[j] = sampleSpline(start, controlPt1, controlPt2, end, (float)j / (float)sections);

            if (level == 0)
            {
                tree.gizmosGreen.Add(pos[j]);
            }

            tangent[j] = norm(sampleSplineTangent(start, controlPt1, controlPt2, end, (float)j / (float)sections));// ERROR HERE

            if (j > 0)
            {
                if (Vector3.Dot(tangent[j - 1], tangent[j]) < 0f)
                {
                    flippedTangent = true;
                    //Debug.Log("flippedTangent!");
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
                    //Debug.Log("flippedBitangent!");
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
                    //Debug.Log("flippedDirB!");
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
        //Debug.Log("vertex count: " + vertices.Count);
        generateTriangles();
        //Debug.Log("triangle count: " + triangles.Count);
    }

    void generateTriangles()
    {
        //int rings = (int)(length / ringSpacing) - 1;

        //Debug.Log("level: " + level + ", rings: " + rings); // ist: 24, soll: 19

        triangles = new List<int>();
        for (int j = 0; j < sections; j++)
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
