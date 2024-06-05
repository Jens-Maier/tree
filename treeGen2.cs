using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class node 
{
    public Vector3 point;
    public Vector3 tangent; // TODO: List tangent -> for splits !!!
    public List<node> next;
    public float radius;
    public treeGen2 gen;

    public node(Vector3 p, float r, treeGen2 g)
    {
        point = p;
        radius = r;
        next = new List<node>();
        gen = g;
    }

    public void grow(Quaternion dir, float length, Vector3 prevPoint, float r)
    {
        if (next.Count > 0)
        {
            next[0].grow(dir, length, point, r);
        }
        else
        {
            Vector3 newPoint = point + norm(dir * (point - prevPoint)) * length;
            next.Add(new node(newPoint, r, gen));
            next[0].tangent = norm(next[0].point - point);
            tangent = norm(next[0].point - prevPoint);
        }
        // Vector3 rotatedVector = Quaternion.AngleAxis(angleDeg, axis) * vector;
    }

    public void split(float length, Vector3 branchDir, Vector3 localDir, float r, Vector3 splitAxis, float splitRotation, float splitAngleDegA, float splitAngleDegB, bool left, bool center, bool right)
    {
        if (next.Count > 0)
        {
            for(int n = 0; n < next.Count; n++)
            {
                next[n].split(length, branchDir, norm(next[n].point - point), r, splitAxis, splitRotation * 0.5f, splitAngleDegA, splitAngleDegB,left, center, right);
            }
        }
        else
        {
            // new
            //Vector3 dir = norm(point - prevPoint);

            // TODO !!!
            Vector3 globalDir = branchDir;
            Vector3 refVector = new Vector3(0f, 0f, 0f);

            if (Mathf.Abs(globalDir.x) > Mathf.Abs(globalDir.y) && Mathf.Abs(globalDir.x) > Mathf.Abs(globalDir.z))
            {
                // x dir
                refVector = new Vector3(0f, 1f, 0f);
            }
            else
            {
                if (Mathf.Abs(globalDir.y) > Mathf.Abs(globalDir.z) && Mathf.Abs(globalDir.y) > Mathf.Abs(globalDir.x))
                {
                    // y dir
                    refVector = new Vector3(0f, 0f, -1f);
                }
                else
                {
                    if (Mathf.Abs(globalDir.z) > Mathf.Abs(globalDir.x) && Mathf.Abs(globalDir.z) > Mathf.Abs(globalDir.y))
                    {
                        // z dir
                        refVector = new Vector3(1f, 0f, 0f);
                    }
                }
            }


            Vector3 rightDir = norm(Vector3.Cross(branchDir, refVector));
            splitAxis = norm(Vector3.Cross(rightDir, localDir));
            Vector3 dirA = Quaternion.AngleAxis(splitAngleDegA, splitAxis) * localDir;
            Vector3 dirB = Quaternion.AngleAxis(-splitAngleDegB, splitAxis) * localDir;

            //dirA = Quaternion.AngleAxis(splitRotation, localDir) * dirA;
            //dirB = Quaternion.AngleAxis(-splitRotation, localDir) * dirB; // -rot? // TODO

            // old
            //splitAxis = Quaternion.AngleAxis(splitRotation, new Vector3(0f, 1f, 0f)) * splitAxis;
            //
            //Vector3 dirA = Quaternion.AngleAxis(splitAngleDegA, norm(splitAxis)) * dir;
            //Vector3 dirB = Quaternion.AngleAxis(-splitAngleDegB, norm(splitAxis)) * dir;
            if (left)
            {
                Vector3 newPointA = point + dirA * length * 0.8f;
                node nodeA = new node(newPointA, r, gen);
                next.Add(nodeA);
            }
            if (right)
            {
                Vector3 newPointB = point + dirB * length * 0.8f;
                node nodeB = new node(newPointB, r, gen);
                next.Add(nodeB);
            }
            if (center)
            {
                Vector3 newPointC = point + localDir * length;
                node nodeC = new node(newPointC, r, gen);
                next.Add(nodeC);
            }
            //points.Add(newPointA);
            //points.Add(newPointB);
        }
    }

    public void getAllSegments(List<segment> allSegments, int sections, int ringRes)
    {
        foreach (node n in next)
        {
            allSegments.Add(new segment(point, n.point, tangent, n.tangent, sections, radius, n.radius, ringRes, gen));
            n.getAllSegments(allSegments, sections, ringRes);
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
}

public class segment
{
    public Vector3 start;
    public Vector3 end;
    public Vector3 startTangent;
    public Vector3 endTangent;
    public int sections;
    public float startRadius;
    public float endRadius;
    public float taper;
    public int stemRingResolution;
    public treeGen2 treeGen;

    public List<Vector3> vertices;
    public List<int> triangles;

    public segment(Vector3 Start, Vector3 End, Vector3 startTan, Vector3 endTan, int Sections, float StartRadius, float EndRadius, int ringRes, treeGen2 gen)
    {
        start = Start;
        end = End;
        startTangent = startTan;
        endTangent = endTan;
        sections = Sections;
        startRadius = StartRadius;
        endRadius = EndRadius;
        stemRingResolution = ringRes;
        taper = 1f;
        vertices = new List<Vector3>();
        triangles = new List<int>();
        treeGen = gen;
    }

}

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

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class treeGen2 : MonoBehaviour
{
    public node root;
    //public List<Vector3> 

    public float treeHeight;
    public Vector3 treeGrowDir;

    public float splitAngleDegA;
    public float splitAngleDegB;

    public float splitLength;

    public float splitRotation;

    public float growLength;

    public List<segment> allSegments;

    public List<Vector3> allSegmentItem1Debug;
    public List<Vector3> allSegmentItem2Debug;
    public List<Vector3> debugList;

    public float radius;
    [Range(1, 10)]
    public int sections;
    [Range(2, 10)]
    public int stemRingResolution;

    public List<Vector3> vertices;
    public List<int> triangles;
    public List<Vector3> normals;

    public Mesh mesh;
    public MeshFilter meshFilter;

    public bool drawGizmos;
    public List<line> tangentDebugLines;
    public List<line> dirAdebugLines;
    public List<line> dirBdebugLines;

    // Start is called before the first frame update
    void Start()
    {
        allSegments = new List<segment>();
        allSegmentItem1Debug = new List<Vector3>();
        allSegmentItem2Debug = new List<Vector3>();
        debugList = new List<Vector3>();
        tangentDebugLines = new List<line>();
        dirAdebugLines = new List<line>();
        dirBdebugLines = new List<line>();

        vertices = new List<Vector3>();
        triangles = new List<int>();
        normals = new List<Vector3>();

        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();
    }


    // Update is called once per frame
    void Update()
    {
        debugList.Clear();
        tangentDebugLines.Clear();
        dirAdebugLines.Clear();
        dirBdebugLines.Clear();

        root = new node(new Vector3(0f, 0f, 0f), radius, this);
        root.next.Add(new node(norm(treeGrowDir) * treeHeight, radius * 0.5f, this));
        root.tangent = norm(root.next[0].point - root.point);
        root.next[0].tangent = norm(root.next[0].point - root.point);

        root.grow(Quaternion.identity                               , treeHeight / 2f, root.next[0].point, root.next[0].radius * 0.5f);
        root.grow(Quaternion.AngleAxis(15f, new Vector3(1f, 0f, 0f)), growLength     , root.next[0].point, root.next[0].radius * 0.5f);
        root.grow(Quaternion.AngleAxis(20f, new Vector3(0f, 0f, 1f)), growLength     , root.next[0].point, root.next[0].radius * 0.5f);

        root.split(splitLength       , root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, new Vector3(1f, 0f, 0f), splitRotation, splitAngleDegA, splitAngleDegB, true, false, true);
        
        root.split(splitLength * 0.8f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, new Vector3(1f, 0f, 0f), splitRotation, splitAngleDegA, splitAngleDegB, true, false, true);
        root.split(splitLength * 0.6f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, new Vector3(1f, 0f, 0f), splitRotation, splitAngleDegA, splitAngleDegB, false, true, true);
        root.split(splitLength * 0.6f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, new Vector3(1f, 0f, 0f), splitRotation, splitAngleDegA, splitAngleDegB, false, true, true);
        
        allSegments.Clear();
        allSegments = getAllSegments(sections);
        Debug.Log("allSegments Count: " + allSegments.Count);

        vertices.Clear();
        triangles.Clear();
        normals.Clear();
        foreach (segment s in allSegments)
        {
            debugList.Add(s.start);
            debugList.Add(s.end);

            vertices.AddRange(s.vertices);
        }

        generateAllVerticesAndTriangles();
        
        //debugLines.Clear();
        //foreach (segment v in allSegments)
        //{
        //    debugLines.Add(new line(v.start, v.end));
        //}
        
        mesh.Clear(false);
        mesh.SetVertices(vertices);
        //mesh.triangles = triangles.ToArray();
        mesh.SetTriangles(triangles, 0);
        mesh.SetNormals(normals);
        //mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }

    List<segment> getAllSegments(int sections)
    {
        List<segment> allSegments = new List<segment>();
        if (root != null)
        {
            root.getAllSegments(allSegments, sections, stemRingResolution);
        }
        Debug.Log("allSegmants count " + allSegments.Count);
        return allSegments;
    }

    void generateAllVerticesAndTriangles()
    {
        int offset = 0;
        int counter = 0;

        Vector3 globalDir = norm(root.next[0].point - root.point);
        Vector3 refVector = new Vector3(0f, 0f, 0f);

        if (Mathf.Abs(globalDir.x) > Mathf.Abs(globalDir.y) && Mathf.Abs(globalDir.x) > Mathf.Abs(globalDir.z))
        {
            // x dir
            refVector = new Vector3(0f, 1f, 0f);
        }
        else
        {
            if (Mathf.Abs(globalDir.y) > Mathf.Abs(globalDir.z) && Mathf.Abs(globalDir.y) > Mathf.Abs(globalDir.x))
            {
                // y dir
                refVector = new Vector3(0f, 0f, -1f);
            }
            else
            {
                if (Mathf.Abs(globalDir.z) > Mathf.Abs(globalDir.x) && Mathf.Abs(globalDir.z) > Mathf.Abs(globalDir.y))
                {
                    // z dir
                    refVector = new Vector3(1f, 0f, 0f);
                }
            }
        }

        Debug.Log("refVector: " + refVector);

        for(int s = 0; s < allSegments.Count; s++)
        {
            Debug.Log("in generateMesh(): segment: ");

            // TODO: automatic tangents -> connecttion line from previous to next vertex -> tangent!

            // TODO
            Vector3 controlPt1 = allSegments[s].start + allSegments[s].startTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
            Vector3 controlPt2 = allSegments[s].end - allSegments[s].endTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f;     //(2f / 3f) * (end - start);

            //Debug.Log("start: " + start);
            //Debug.Log("end: " + end);

            float length = vLength(allSegments[s].end - allSegments[s].start);

            float ringSpacing = length / (float)allSegments[s].sections;
            //ringSpacing = rSpacing;

            Vector3[] dirA = new Vector3[allSegments[s].sections + 1];
            Vector3[] dirB = new Vector3[allSegments[s].sections + 1];
            Vector3[] tangent = new Vector3[allSegments[s].sections + 1];
            Vector3[] bitangent = new Vector3[allSegments[s].sections + 1];
            Vector3[] curvature = new Vector3[allSegments[s].sections + 1];

            Vector3[] pos = new Vector3[allSegments[s].sections + 1];

            bool flippedTangent = false;
            bool flippedBitangent = false;
            bool flippedDirB = false;

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                pos[j] = sampleSpline(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)sections);


                tangent[j] = norm(sampleSplineTangent(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections));

                

                tangentDebugLines.Add(new line(pos[j], pos[j] + tangent[j]));

                Vector3 cross = Vector3.Cross(tangent[j], refVector);

                if (cross == new Vector3(0f, 0f, 0f))
                {
                    cross = Vector3.Cross(tangent[j], Quaternion.AngleAxis(90f, new Vector3(0f, 1f, 0f)) * refVector);
                    Debug.Log("cross is ZERO !!!");
                }

                dirA[j] = norm(cross);

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j]));

                dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j]));

                

                Vector3 dir = norm(tangent[j]);

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j]));
                dirBdebugLines.Add(new line(pos[j], pos[j] + dirB[j]));


                for (int i = 0; i < 2 * stemRingResolution; i++)
                {
                    float angle = (Mathf.PI / (float)allSegments[s].stemRingResolution) * (float)i;

                    Vector3 v = pos[j] + dirA[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
                                dirB[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);

                    vertices.Add(v);
                    counter += 1;
                }
            }

            int st = stemRingResolution;

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                for (int i = 0; i < 2 * st; i++)
                {
                    // normals
                    Vector3 n;
                    if (j < allSegments[s].sections)
                    {
                        n = norm(Vector3.Cross(vertices[j * 2 * st + (i + 1) % (2 * st)] - vertices[j * 2 * st + i],
                                               vertices[(j + 1) * 2 * st + i]            - vertices[j * 2 * st + i]) + //  |_

                                 Vector3.Cross(vertices[(j + 1) * 2 * st + i]                     - vertices[j * 2 * st + i],
                                               vertices[j * 2 * st + (i - 1 + 2 * st) % (2 * st)] - vertices[j * 2 * st + i]));  //  _|
                    }
                    else
                    {
                        n = norm(Vector3.Cross(vertices[(j - 1) * 2 * st + i]            - vertices[j * 2 * st + i],
                                               vertices[j * 2 * st + (i + 1) % (2 * st)] - vertices[j * 2 * st + i]) +  //  |-

                                 Vector3.Cross(vertices[j * 2 * st + (i - 1 + 2 * st) % (2 * st)] - vertices[j * 2 * st + i],
                                               vertices[(j - 1) * 2 * st + i]                     - vertices[j * 2 * st + i]));  //  -|
                    }
                    normals.Add(n);
                }
            }

            //Debug.Log("vertex count: " + vertices.Count);
            generateTriangles(allSegments[s].sections, offset);
            offset += counter;
            counter = 0;
            //Debug.Log("triangle count: " + triangles.Count);
        }
    }

    void generateTriangles(int Sections, int offset)
    {

        Debug.Log("in generateTriangles: sections: " + Sections);
        Debug.Log("in generateTriangles: stemRingResolution: " + stemRingResolution);

        int count = 0;
        for (int j = 0; j < Sections; j++)
        {
            for (int i = 0; i < 2 * stemRingResolution; i++)
            {
                if (j % 2 == 1)
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                    else
                    {
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                }
                else
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                    else
                    {
                        triangles.Add(offset + j * 2 * stemRingResolution + i);
                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(offset + j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(offset + j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                }
                count += 6;
            }
            count = 0;
        }
    }



    void OnDrawGizmos()
    {
        if (drawGizmos)
        {
            Gizmos.color = Color.red;

            //if (allSegments != null)
            //{
            //    foreach (segment s in allSegments)
            //    {
            //        Gizmos.DrawLine(s.start, s.end);
            //    }
            //}

            if (debugList != null)
            {
                if (debugList.Count > 0)
                {
                    Debug.Log("debugList count: " + debugList.Count);
                }
                foreach (Vector3 v in debugList)
                {
                    Gizmos.DrawSphere(v, 0.01f);
                }

                foreach (Vector3 v in vertices)
                {
                    Gizmos.DrawSphere(v, 0.02f);
                }
            }
            if (tangentDebugLines != null)
            { 
                foreach (line l in tangentDebugLines)
                {
                    Gizmos.DrawLine(l.start, l.end);
                }
                Gizmos.color = Color.green;
                foreach (line l in dirAdebugLines)
                {
                    Gizmos.DrawLine(l.start, l.end);
                }
                Gizmos.color = Color.blue;
                foreach (line l in dirBdebugLines)
                {
                    Gizmos.DrawLine(l.start, l.end);
                }
            }

            //if (root != null)
            //{
            //    if (root.next != null)
            //    {
            //        Gizmos.DrawLine(root.point, root.next[0].point);
            //
            //        if (root.next[0].next.Count > 0)
            //        {
            //            Gizmos.DrawLine(root.next[0].point, root.next[0].next[0].point);
            //
            //            if (root.next[0].next[0].next.Count > 0)
            //            {
            //                Gizmos.DrawLine(root.next[0].next[0].point, root.next[0].next[0].next[0].point);
            //            }
            //        }
            //    }
            //}
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



//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
// // TODO: move to treeGen2 -> align bitangents possible
// //
// //
// //
//
//
//
//
//
//
//
//
//
//
//
//
//

//public void generateVerticesAndTriangles(int Sections) // TODO: move to treeGen2 -> align bitangents possible
//{
//
//    sections = Sections;
//    Debug.Log("in generateMesh(): segment: ");
//
//    // TODO: automatic tangents -> connecttion line from previous to next vertex -> tangent!
//
//
//    // TODO
//    Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f; //(1f / 3f) * (end - start);
//    Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;     //(2f / 3f) * (end - start);
//    
//    //Debug.Log("start: " + start);
//    //Debug.Log("end: " + end);
//
//    float length = vLength(end - start);
//
//    float ringSpacing = length / (float)sections;
//    //ringSpacing = rSpacing;
//
//    Vector3[] dirA = new Vector3[sections + 1];
//    Vector3[] dirB = new Vector3[sections + 1];
//    Vector3[] tangent = new Vector3[sections + 1];
//    Vector3[] bitangent = new Vector3[sections + 1];
//    Vector3[] curvature = new Vector3[sections + 1];
//
//    Vector3[] pos = new Vector3[sections + 1];
//
//    bool flippedTangent = false;
//    bool flippedBitangent = false;
//    bool flippedDirB = false;
//
//    for (int j = 0; j < sections + 1; j++)
//    {
//        pos[j] = sampleSpline(start, controlPt1, controlPt2, end, (float)j / (float)sections);
//        
//
//        tangent[j] = norm(sampleSplineTangent(start, controlPt1, controlPt2, end, (float)j / (float)sections));
//
//        if (j > 0)
//        {
//            //treeGen.tangentDebugLines.Add(new line(pos[j - 1], pos[j]));
//            if (Vector3.Dot(tangent[j - 1], tangent[j]) < 0f)
//            {
//                flippedTangent = true;
//                //Debug.Log("flippedTangent!");
//            }
//            if (flippedTangent)
//            {
//                tangent[j] = -tangent[j];
//            }
//            treeGen.tangentDebugLines.Add(new line(pos[j], pos[j] + tangent[j]));
//        }
//
//        Vector3 cross = Vector3.Cross(tangent[j], new Vector3(1f, 0f, 0f));
//        if (cross == new Vector3(0f, 0f, 0f))
//        {
//            cross = Vector3.Cross(tangent[j], new Vector3(0f, 0f, 1f));
//        }
//
//        Vector3 b;
//        if (j > 0)
//        {
//            cross = norm(Vector3.Cross(bitangent[j - 1], pos[j] - pos[j - 1]));
//            b = norm(Vector3.Cross(pos[j] - pos[j - 1], cross));
//        }
//        else
//        {
//            b = norm(Vector3.Cross(pos[j + 1] - pos[j], new Vector3(1f, 0f, 0f))); // todo; inf...
//        }
//
//        //= norm(cross);
//
//        if (j > 0)
//        {
//            if (Vector3.Dot(bitangent[j - 1], bitangent[j]) < 0f)
//            {
//                flippedBitangent = true;
//                //Debug.Log("flippedBitangent!");
//            }
//            if (flippedBitangent)
//            {
//                b = -b;
//            }
//        }
//
//        bitangent[j] = b;
//
//        curvature[j] = norm(sampleSplineCurvature(start, controlPt1, controlPt2, end, (float)j / (length / ringSpacing)));
//
//        dirA[j] = norm(bitangent[j]); //red
//
//        dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); //green 
//
//        //if (j > 0)
//        //{
//        //    if (Vector3.Dot(dirB[j - 1], dirB[j]) < 0f)
//        //    {
//        //        flippedDirB = true;
//        //        //Debug.Log("flippedDirB!");
//        //    }
//        //    if (flippedDirB)
//        //    {
//        //        dirB[j] = -dirB[j];
//        //        dirA[j] = -dirA[j];
//        //    }
//        //}
//
//        Vector3 dir = norm(tangent[j]);
//
//        treeGen.dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j]));
//        treeGen.dirBdebugLines.Add(new line(pos[j], pos[j] + dirB[j]));
//
//
//        for (int i = 0; i < 2 * stemRingResolution; i++)
//        {
//            float angle = (Mathf.PI / (float)stemRingResolution) * (float)i;
//
//            Vector3 v = pos[j] + dirA[j] * fLerp(startRadius, endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
//                        dirB[j] * fLerp(startRadius, endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);
//
//            vertices.Add(v);
//        }
//    }
//    //Debug.Log("vertex count: " + vertices.Count);
//    generateTriangles(Sections);
//    //Debug.Log("triangle count: " + triangles.Count);
//}

//void generateTriangles(int Sections)
//{
//    sections = Sections;
//
//    Debug.Log("in generateTriangles: sections: " + sections);
//    Debug.Log("in generateTriangles: stemRingResolution: " + stemRingResolution);
//    
//    int count = 0;
//    for (int j = 0; j < sections; j++)
//    {
//        for (int i = 0; i < 2 * stemRingResolution; i++)
//        {
//            if (j % 2 == 1)
//            {
//                if (i % 2 == 1)
//                {
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
//
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
//                }
//                else
//                {
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//                }
//            }
//            else
//            {
//                if (i % 2 == 1)
//                {
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//                }
//                else
//                {
//                    triangles.Add(j * 2 * stemRingResolution + i);
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
//
//                    triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
//                    triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
//                }
//            }
//            count += 6;
//        }
//        count = 0;
//    }
//}



//void getVerticesAndTriangles()
//{
//    vertices.Clear();
//    triangles.Clear();
//    int vertexCounter = 0;
//    foreach(segment s in allSegments)
//    {
//        //s.generateVerticesAndTriangles(sections);
//        vertices.AddRange(s.vertices);
//        foreach (int t in s.triangles)
//        {
//            triangles.Add(t + vertexCounter);
//        }
//        vertexCounter += s.vertices.Count;
//    }
//    int maxIndex = 0;
//    foreach (int t in triangles)
//    {
//        if (maxIndex < t)
//        {
//            maxIndex = t;
//        }
//    }
//
//    Debug.Log("allVertices count " + vertices.Count);
//    Debug.Log("maxIndex: " + maxIndex); // ERROR
//}

//if (j > 0)
//{
//    //tangentDebugLines.Add(new line(pos[j - 1], pos[j]));
//    if (Vector3.Dot(tangent[j - 1], tangent[j]) < 0f)
//    {
//        flippedTangent = true;
//        //Debug.Log("flippedTangent!");
//    }
//    if (flippedTangent)
//    {
//        tangent[j] = -tangent[j];
//    }
//    tangentDebugLines.Add(new line(pos[j], pos[j] + tangent[j]));
//}


//Vector3 b;
//if (j > 0)
//{
//    cross = norm(Vector3.Cross(bitangent[j - 1], pos[j] - pos[j - 1]));
//    b = norm(Vector3.Cross(pos[j] - pos[j - 1], cross));
//}
//else
//{
//    b = norm(Vector3.Cross(pos[j + 1] - pos[j], new Vector3(1f, 0f, 0f))); // todo; inf...
//}



//= norm(cross);

//if (j > 0)
//{
//    if (Vector3.Dot(bitangent[j - 1], bitangent[j]) < 0f)
//    {
//        flippedBitangent = true;
//        //Debug.Log("flippedBitangent!");
//    }
//    if (flippedBitangent)
//    {
//        b = -b;
//    }
//}
//
//bitangent[j] = b;
//
//curvature[j] = norm(sampleSplineCurvature(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (length / ringSpacing)));
//
//dirA[j] = norm(bitangent[j]); //red
//
//dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); //green 

//if (j > 0)
//{
//    if (Vector3.Dot(dirB[j - 1], dirB[j]) < 0f)
//    {
//        flippedDirB = true;
//        //Debug.Log("flippedDirB!");
//    }
//    if (flippedDirB)
//    {
//        dirB[j] = -dirB[j];
//        dirA[j] = -dirA[j];
//    }
//}