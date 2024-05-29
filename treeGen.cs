using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class treeGen : MonoBehaviour
{
    // branch segment
    public Vector3 start;
    public Vector3 end;
    public Vector3 controlPt1;
    public Vector3 controlPt2;
    public Vector3[] dirA;
    public Vector3[] dirB;
    public Vector3[] pos;


    public Vector3[] tangent;
    public Vector3[] bitangent;
    public Vector3[] curvature;

    public float stemRadius;
    public int stemRingResolution; // #vertices = 2 * stemRingResolution
    public float taper; // %
    
    float length;
    public float ringSpacing;

    public List<Vector3> vertices;
    public List<int> triangles;

    public GameObject selfGameObject;
    public Mesh mesh;
    public MeshFilter meshFilter;

    public float gizmoScale = 0.2f;

    // Start is called before the first frame update
    void Start()
    {
        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();

        // TODO: spline!!! -> branch segment class! start direction, curvature, branch angle...


        //mesh.SetVertices(vertices);
        //mesh.SetTriangles(triangles, 0);
        //mesh.RecalculateNormals();

        //meshFilter.mesh = mesh;
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

    void generateBranch()
    {
        length = vLength(end - start);

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
            //Debug.Log("dirA: " + dirA);

            dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); //green 
            //Debug.Log("dirB: " + dirB);

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
            
                // Vector3 v = new Vector3(fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle),
                //                        (float)j * ringSpacing,
                //                        fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle));
                //Vector3 v = pos + dirA * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
                //            dirB * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);// +
                //            //dir * (float)j * ringSpacing;
            
                Vector3 v = pos[j] + dirA[j] * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
                            dirB[j] * fLerp(stemRadius, taper * stemRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);// +
                
            
                vertices.Add(v);
            }
        }

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

    void generateTree()
    {

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

        for (int j = 0; j < (int)(length / ringSpacing); j++)
        {
            Gizmos.color = Color.blue;
            Gizmos.DrawRay(pos[j], gizmoScale * dirA[j]);// dirA
            Gizmos.color = Color.green;
            Gizmos.DrawRay(pos[j], gizmoScale * dirB[j]);// dirB
            Gizmos.color = Color.red;
            Gizmos.DrawRay(pos[j], gizmoScale * tangent[j]);
            Gizmos.DrawRay(pos[j], gizmoScale * curvature[j]);
        }

    }


    // Update is called once per frame
    void Update()
    {
        vertices.Clear();
        triangles.Clear();

        generateBranch();

        mesh.Clear(false);
        mesh.SetVertices(vertices);
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
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