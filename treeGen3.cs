using System.Collections;
using System.Collections.Generic;
using UnityEngine;


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

public class node
{
    public Vector3 point;
    public List<Vector3> tangent; //list<tangent> for splits! [tangentIn, tangentOutA, tangentOutB] ((only[tangent] without split!)
    public Vector3 cotangent;
    public List<node> next;
    public node parent;
    public float radius;
    public treeGen3 gen;
    public List<List<node>> children;

    public node(Vector3 Point, Vector3 newTangent, treeGen3 g, node par)
    {
        point = Point;
        tangent = new List<Vector3>();
        tangent.Add(newTangent);
        radius = 0f;
        next = new List<node>();
        gen = g;
        parent = par;
        children = new List<List<node>>(); // one list for each node in next 
    }

    public void getAllSegments(List<segment> allSegments, int sections, int ringRes)
    {
        //foreach (node n in next)
        for (int i = 0; i < next.Count; i++)
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

                //Debug.Log("tangent count: " + tangent.Count); // 3
                //Debug.Log("next count: " + next.Count); // 2
                
                allSegments.Add(new segment(point, next[i].point, tangent[i + 1], next[i].tangent[0], cotangent, next[i].cotangent, sections, radius, next[i].radius, ringRes, gen));
                

            }
            else
            {
                //Debug.Log("tangent count: " + tangent.Count); // 1
                //Debug.Log("next count: " + next.Count); // 1

                allSegments.Add(new segment(point, next[i].point, tangent[0], next[i].tangent[0], cotangent, next[i].cotangent, sections, radius, next[i].radius, ringRes, gen));
            }

            next[i].getAllSegments(allSegments, sections, ringRes);
        }

        foreach (List<node> l in children)
        {
            foreach (node c in l)
            {
                c.getAllSegments(allSegments, sections, ringRes);
            }
        }
    }

    public void resampleSpline(int n, float noiseAmplitudeLower, float noiseAmplitudeUpper, float noiseScale)
    {
        if (n > 1)
        {
            node nodeNext = next[0];
            node currentNode = this;
            Vector3 prevPoint = point;

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

                gen.debugSamplePoints.Add(samplePoint); // OK

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

                // improve sampleCotangent!
                sampleCotangent = norm(Vector3.Cross(dirB, sampleTangent));
                node newNode;
                if (i == 1)
                {
                    newNode = new node(samplePoint, sampleTangent, gen, this);
                    newNode.cotangent = sampleCotangent;
                }
                else
                {
                    newNode = new node(samplePoint, sampleTangent, gen, currentNode);
                    newNode.cotangent = sampleCotangent;
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

    public void grow()
    {
        
    }

    public void addChildren()
    {

    }

    
    public int nodesToTip()
    {
        if (next.Count > 0)
        {
            return (1 + next[0].nodesToTip());
        }
        else
        {
            return 1;
        }
    }

    
    public float calculateRadius()
    {
        if (next.Count > 0 || children.Count > 0)
        {
            float sum = 0f;
            if (next.Count > 0)
            {
                foreach (node n in next)
                {
                    sum += n.calculateRadius();
                    sum += vLength(n.point - point) * gen.taper * gen.taper;
                }
            }
            if (children.Count > 0)
            {
                foreach (List<node> c in children)
                {
                    foreach (node n in c)
                    {
                        sum += n.calculateRadius();
                    }
                }
            }
            radius = sum;
            Debug.Log("crossSection: " + sum);
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
        return (Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }

    static Vector3 norm(Vector3 v)
    {
        return (v / Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }

    //static Vector3 sampleSplineC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    //{
    //    return ((1f - t) * (1f - t) * (1f - t) * controlA + 3f * (1f - t) * (1f - t) * t * controlB + 3f * (1f - t) * t * t * controlC + t * t * t * controlD);
    //}

    static Vector3 sampleSpline(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;

        return ((1f - t) * (1f - t) * (1f - t) * start + 3f * (1f - t) * (1f - t) * t * controlPt1 + 3f * (1f - t) * t * t * controlPt2 + t * t * t * end);
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
        return norm((-3f * (1f - t) * (1f - t) * start + 3f * (3f * t * t - 4f * t + 1f) * controlPt1 + 3f * (-3f * t * t + 2f * t) * controlPt2 + 3f * t * t * end));
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return (6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD);
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
    public int stemRingResolution;
    public treeGen3 treeGen;

    public List<Vector3> vertices;
    public List<Vector2> UVs;
    public List<int> triangles;

    public segment(Vector3 Start, Vector3 End, Vector3 startTan, Vector3 endTan, Vector3 startCotan, Vector3 endCotan, int Sections, float StartRadius, float EndRadius, int ringRes, treeGen3 gen)
    {
        start = Start;
        end = End;
        startTangent = startTan;
        startCotangent = startCotan;
        endTangent = endTan;
        endCotangent = endCotan;
        sections = Sections;
        startRadius = StartRadius;
        endRadius = EndRadius;
        stemRingResolution = ringRes;
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

    public node rootNode;
    public List<segment> allSegments;

    public float treeHeight;
    public Vector3 treeGrowDir;

    [Range(0f, 0.1f)]
    public float taper;
    [Range(0f, 0.001f)]
    public float branchTipRadius;
    [Range(1, 20)]
    public int sections;
    [Range(2, 10)]
    public int stemRingResolution;
    [Range(1, 10)]
    public int resampleNr;
    [Range(0f, 1f)]
    public float noiseAmplitudeLower;
    [Range(0f, 1f)]
    public float noiseAmplitudeUpper;
    [Range(0f, 4f)]
    public float noiseAmplitudeLowerUpperExponent;
    [Range(0.1f, 10f)]
    public float noiseScale;
    [Range(0f, 1f)]
    public float testSplitHeight;

    public List<line> tangentDebugLines;
    public List<line> dirAdebugLines;
    public List<line> dirBdebugLines;

    public List<Vector3> debugList;
    public List<Vector3> debugListRadius;
    public List<Vector3> debugListGreen;
    public List<Vector3> debugListRed;
    public List<Vector3> debugListBlue;

    public List<Vector3> debugSamplePoints;
    public List<Vector3> debugSampleTangents;

    public Vector3 debugPrev;
    public Vector3 debugNext;
    public Vector3 debugSplitPoint;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        int x = 3;
        int y = x / 2;
        Debug.Log("int 3/2 = " + y);

        tangentDebugLines = new List<line>();
        dirAdebugLines = new List<line>();
        dirBdebugLines = new List<line>();
        debugList = new List<Vector3>();
        debugListRadius = new List<Vector3>();
        debugListGreen = new List<Vector3>();
        debugListRed = new List<Vector3>();
        debugListBlue = new List<Vector3>();
        debugSamplePoints = new List<Vector3>();
        debugSampleTangents = new List<Vector3>();

        vertices = new List<Vector3>();
        triangles = new List<int>();
        normals = new List<Vector3>();
        UVs = new List<Vector2>();

        allSegments = new List<segment>();

        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();
    }

    List<segment> getAllSegments(int sections)
    {
        List<segment> allSegments = new List<segment>();
        if (rootNode != null)
        {
            rootNode.getAllSegments(allSegments, sections, stemRingResolution);
        }
        //Debug.Log("allSegmants count " + allSegments.Count);
        return allSegments;
    }

    public void split(node startNode, float splitHeight)
    {
        // split after resampleSpline!
        if (startNode.next.Count > 0)
        {
            int nrNodesToTip;
            nrNodesToTip = startNode.next[0].nodesToTip();

            int splitAfterNodeNr = (int)((float)(nrNodesToTip) * splitHeight);
            Debug.Log("splitAfterNodeNr " + splitAfterNodeNr);
            Debug.Log("nrNodesToTip " + nrNodesToTip); // 2 OK

            node splitAfterNode = rootNode;
            int splitAfterNodeIndex = 0;
            while(splitAfterNodeNr > 0)
            {
                splitAfterNode = splitAfterNode.next[0];
                splitAfterNodeIndex++;
                splitAfterNodeNr--;
            }

            Vector3 splitPoint = sampleSplineT(splitAfterNode.point, splitAfterNode.next[0].point, splitAfterNode.tangent[0], splitAfterNode.next[0].tangent[0], 
                                               (splitHeight * nrNodesToTip) % Mathf.Floor(splitHeight * nrNodesToTip)  - (float)splitAfterNodeIndex / (float)nrNodesToTip);

            debugSplitPoint = splitPoint; // TODO...
            
        }
    }


    // Update is called once per frame
    void Update()
    {
        debugSamplePoints.Clear();
        debugSampleTangents.Clear();
        debugList.Clear();
        debugListRadius.Clear();
        debugListGreen.Clear();
        debugListRed.Clear();
        debugListBlue.Clear();
        rootNode = new node(new Vector3(0f, 0f, 0f), new Vector3(0f, 1f, 0f), this, null);
        rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(1f, 0f, 0f)));

        if (rootNode.cotangent == new Vector3(0f, 0f, 0f))
        {
            rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, 1f)));
        }
        //rootNode.next[0].tangent[0] = norm(rootNode.next[0].point - (rootNode.point + rootNode.tangent[0] * vLength(rootNode.next[0].point - rootNode.point) / 3f));

        Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));
        
        rootNode.next.Add(new node(norm(treeGrowDir) * treeHeight, nextTangent, this, rootNode));

        rootNode.next[0].cotangent = norm(Vector3.Cross(rootNode.next[0].tangent[0], Vector3.Cross(rootNode.cotangent, rootNode.next[0].tangent[0])));
        rootNode.resampleSpline(resampleNr, noiseAmplitudeLower, noiseAmplitudeUpper, noiseScale);
        split(rootNode, testSplitHeight);
        rootNode.calculateRadius();

        if (allSegments != null)
        {
            allSegments.Clear();
            allSegments = getAllSegments(sections);
        }
        else
        {
            allSegments = new List<segment>();
            allSegments = getAllSegments(sections);
        }

        vertices.Clear();
        triangles.Clear();
        normals.Clear();
        UVs.Clear();
        if (allSegments != null)
        {
            // foreach (segment s in allSegments) // ???
            // {
            //     //debugList.Add(s.start);
            //     //debugList.Add(s.end);
            //     vertices.AddRange(s.vertices);
            //     UVs.AddRange(s.UVs);
            // }
            generateAllVerticesAndTriangles();
        }
        mesh.Clear(false);
        mesh.SetVertices(vertices);
        mesh.SetUVs(0, UVs);
        mesh.SetTriangles(triangles, 0);
        mesh.SetNormals(normals);

        meshFilter.mesh = mesh;

    }

    float interpolateRadius(float radius1, float raidus2, float t)
    {
        return Mathf.Sqrt(fLerp(radius1 * radius1, raidus2 * raidus2, t));
    }

    void generateAllVerticesAndTriangles()
    {
        int offset = 0;
        int counter = 0;

        //Vector3 globalDir = norm(root.next[0].point - root.point);
        
        for(int s = 0; s < allSegments.Count; s++)
        {
            //Debug.Log("in generateMesh(): segment: ");

            // TODO: automatic tangents -> connecttion line from previous to next vertex -> tangent!

            Vector3 controlPt1 = allSegments[s].start + norm(allSegments[s].startTangent) * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
            Vector3 controlPt2 = allSegments[s].end - norm(allSegments[s].endTangent) * vLength(allSegments[s].end - allSegments[s].start) / 3f;     //(2f / 3f) * (end - start);

            //Debug.Log("startTangent: " + allSegments[s].startTangent);
            //Debug.Log("endTangent: " + allSegments[s].endTangent);


            //Debug.Log("start: " + start);
            //Debug.Log("end: " + end);

            float length = vLength(allSegments[s].end - allSegments[s].start);

            float ringSpacing = length / (float)(allSegments[s].sections);
            //ringSpacing = rSpacing;

            Vector3[] dirA = new Vector3[allSegments[s].sections + 1];
            Vector3[] dirB = new Vector3[allSegments[s].sections + 1];
            Vector3[] tangent = new Vector3[allSegments[s].sections + 1];
            Vector3[] curvature = new Vector3[allSegments[s].sections + 1];

            Vector3[] pos = new Vector3[allSegments[s].sections + 1];

            //int debug = allSegments[s].sections + 1;
            //Debug.Log("sections loop: " + debug);
            //debugListRed.Add(allSegments[s].start);
            //debugListRed.Add(allSegments[s].end);

            tangentDebugLines.Add(new line(allSegments[s].start, controlPt1));
            tangentDebugLines.Add(new line(allSegments[s].end, controlPt2));

            //debugListBlue.Add(controlPt1);
            //debugListBlue.Add(controlPt2);

            float arcLength = 0f;

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                pos[j] = sampleSplineC(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections);
                
                debugListGreen.Add(pos[j]);

                if (j > 0)
                {
                    arcLength += vLength(pos[j] - pos[j - 1]);
                }

                tangent[j] = norm(sampleSplineTangent(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections));

                dirA[j] = vLerp(allSegments[s].startCotangent, allSegments[s].endCotangent, (float)j / (float)allSegments[s].sections);// green
                
                dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); // blue

                // improve dirA!
                dirA[j] = norm(Vector3.Cross(dirB[j], tangent[j])); // green // test off

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                Vector3 dir = norm(tangent[j]);

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                dirBdebugLines.Add(new line(pos[j], pos[j] + dirB[j] / 5f)); // blue

                for (int i = 0; i <= 2 * stemRingResolution; i++)
                {
                    float angle = (Mathf.PI / (float)allSegments[s].stemRingResolution) * (float)i;

                    float f = (float)j / (float)(length / ringSpacing) * Mathf.Cos(angle) + fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing));
                    
                    Vector3 v = pos[j] + dirA[j] * Mathf.Sqrt(fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing))) * Mathf.Cos(angle) +
                                dirB[j] * Mathf.Sqrt(fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing))) * Mathf.Sin(angle);

                    
                    Vector2 uv = new Vector2(angle / (2f * Mathf.PI), arcLength);
                    if (i == 2 * stemRingResolution)
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

            //int st = stemRingResolution;

            //for (int j = 0; j < allSegments[s].sections + 1; j++)
            //{
            //    for (int i = 0; i <= 2 * st; i++)
            //    {
            //        // normals
            //        Vector3 n = new Vector3(0f, 0f, 0f);
//
            //        if (j < allSegments[s].sections)
            //        {
            //            n = Vector3.Cross(vertices[j * (2 * st + 1) + (i + 1) % (2 * st)] - vertices[j * (2 * st + 1) + i],
            //                              vertices[(j + 1) * (2 * st + 1) + i]            - vertices[j * (2 * st + 1) + i]) + //  |_
            //        
            //                Vector3.Cross(vertices[(j + 1) * (2 * st + 1) + i]                     - vertices[j * (2 * st + 1) + i],
            //                              vertices[j * (2 * st + 1) + (i - 1 + 2 * st) % (2 * st)] - vertices[j * (2 * st + 1) + i]);  //  _|
            //        }
            //        if (j > 0)
            //        {
            //            n += Vector3.Cross(vertices[(j - 1) * (2 * st + 1) + i]            - vertices[j * (2 * st + 1) + i],
            //                               vertices[j * (2 * st + 1) + (i + 1) % (2 * st)] - vertices[j * (2 * st + 1) + i]) +  //  |-
            //         
            //                 Vector3.Cross(vertices[j * (2 * st + 1) + (i - 1 + 2 * st) % (2 * st)] - vertices[j * (2 * st + 1) + i],
            //                               vertices[(j - 1) * (2 * st + 1) + i]                     - vertices[j * (2 * st + 1) + i]);  //  -|
            //        }
//
            //        if (n == new Vector3(0f, 0f, 0f)) // tip
            //        {
            //            n = Vector3.Cross(vertices[(j - 1) * (2 * st + 1) + (i + 1) % (2 * st)] - vertices[(j - 1) * (2 * st + 1) + i],
            //                              vertices[j * (2 * st + 1) + i]                        - vertices[(j - 1) * (2 * st + 1) + i]) + //  |_
            //        
            //                Vector3.Cross(vertices[j * (2 * st + 1) + i]                                 - vertices[(j - 1) * (2 * st + 1) + i],
            //                              vertices[(j - 1) * (2 * st + 1) + (i - 1 + 2 * st) % (2 * st)] - vertices[(j - 1) * (2 * st + 1) + i]);  //  _|
            //        }
            //        normals.Add(norm(n));
            //    }
            //}

            //Debug.Log("vertex count: " + vertices.Count);
            generateTriangles(allSegments[s].sections, offset);
            offset += counter;
            counter = 0;
            //Debug.Log("triangle count: " + triangles.Count);
        }
    }

    
    void generateTriangles(int Sections, int offset)
    {

        //Debug.Log("in generateTriangles: sections: " + Sections);
        //Debug.Log("in generateTriangles: stemRingResolution: " + stemRingResolution);

        int count = 0;
        for (int j = 0; j < Sections; j++)
        {
            for (int i = 0; i < 2 * stemRingResolution + 1; i++)
            {
                if (j % 2 == 1)
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + i);

                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + i);
                    }
                    else
                    {
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));

                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i) % (2 * stemRingResolution + 1)));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));
                    }
                }
                else
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));

                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i) % (2 * stemRingResolution + 1)));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));
                    }
                    else
                    {
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + i);
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + i);

                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + (i + 1) % (2 * stemRingResolution + 1));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + ((i + 1) % (2 * stemRingResolution + 1)));
                        triangles.Add(offset + j * (2 * stemRingResolution + 1) + 2 * stemRingResolution + 1 + i);
                    }
                }
                count += 6;
            }
            count = 0;
        }
    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.blue;
        for (int i = 0; i < vertices.Count; i++)
        {
            Gizmos.DrawRay(vertices[i], normals[i] * normalGizmoSize);
        }

        if (allSegments != null)
        {
            foreach (segment s in allSegments)
            {
                Gizmos.color = Color.red;
                Vector3 controlPt1 = s.start + s.startTangent * vLength(s.end - s.start) / 3f; //(1f / 3f) * (end - start);
                Vector3 controlPt2 = s.end - s.endTangent * vLength(s.end - s.start) / 3f;     //(2f / 3f) * (end - start);
                Gizmos.DrawSphere(s.start, gizmoRadius);
                Gizmos.DrawSphere(s.end, gizmoRadius);

                Gizmos.DrawRay(s.start, s.startTangent);

                Gizmos.color = Color.blue;
                Gizmos.DrawSphere(controlPt1, gizmoRadius);
                Gizmos.DrawSphere(controlPt2, gizmoRadius);
            }   

            Gizmos.color = Color.green;
            for (int i = 0; i < debugSamplePoints.Count; i++)
            {
                Gizmos.DrawSphere(debugSamplePoints[i], gizmoRadius);
                Gizmos.DrawRay(debugSamplePoints[i], debugSampleTangents[i]);
            }

            Gizmos.color = new Color(1f, 1f, 0f);
            Gizmos.DrawSphere(debugNext, gizmoRadius);
            Gizmos.DrawSphere(debugPrev, gizmoRadius / 2f);

            Gizmos.DrawSphere(debugSplitPoint, gizmoRadius * 2f);
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

    static Vector3 norm(Vector3 v)
    {
        return (v / Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }

    static float vLength(Vector3 v)
    {
        return (Mathf.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
    }
    static Vector3 sampleSplineC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        return ((1f - t) * (1f - t) * (1f - t) * controlA + 3f * (1f - t) * (1f - t) * t * controlB + 3f * (1f - t) * t * t * controlC + t * t * t * controlD);
    }

    static Vector3 sampleSplineT(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;

        return ((1f - t) * (1f - t) * (1f - t) * start + 3f * (1f - t) * (1f - t) * t * controlPt1 + 3f * (1f - t) * t * t * controlPt2 + t * t * t * end);
    }

    //Vector3 controlPt1 = allSegments[s].start + allSegments[s].startTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
    //        Vector3 controlPt2 = allSegments[s].end - allSegments[s].endTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f;

    static Vector3 sampleSplineTangent(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
        return norm(-3f * (1f - t) * (1f - t) * controlA + 3f * (3f * t * t - 4f * t + 1f) * controlB + 3f * (-3f * t * t + 2f * t) * controlC + 3f * t * t * controlD);
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return (6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD);
    }
}
