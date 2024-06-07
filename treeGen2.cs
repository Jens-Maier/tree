using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class node 
{
    public Vector3 point;
    public Vector3 tangent; // TODO: List tangent -> for splits !!!
    public Vector3 cotangent; // TODO!
    public List<node> next;
    public node parent;
    public float radius;
    public treeGen2 gen;
    public List<node> children;

    public node(Vector3 p, float r, treeGen2 g, node par)
    {
        point = p;
        radius = r;
        next = new List<node>();
        gen = g;
        parent = par;
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
            next.Add(new node(newPoint, r, gen, this));
            next[0].tangent = norm(next[0].point - point);
            tangent = norm(next[0].point - prevPoint);

            cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

            next[0].cotangent = norm(Vector3.Cross(next[0].tangent, Vector3.Cross(cotangent, next[0].tangent)));
        }
        // Vector3 rotatedVector = Quaternion.AngleAxis(angleDeg, axis) * vector;
    }

    public void addChildren(int n)
    {
        Vector3[] startPoints = new Vector3[n];

        for (int i = 1; i < n; i++)
        {
            startPoints[i] = sampleSpline(point, 
                                          point + vLength(next[0].point - point) * norm(tangent) * (1f / 3f),
                                          next[0].point - vLength(next[0].point - point) * norm(next[0].tangent) * (1f / 3f),
                                          next[0].point, (float)i / (float)n);
        }
    }

    public void split(float length, Vector3 branchDir, Vector3 localDir, float r, Vector3 prevPoint, Vector3 splitAxis, float splitRotation, float splitAngleDegA, float splitAngleDegB, bool left, bool center, bool right)
    {
        if (next.Count > 0)
        {
            int n = 0;
            //int safetyLimit = 1000;
            //int c = 0;
            while (n < next.Count)
            {
                // Random.Range(): float: min and max inclusive || int: min inclusive, max exclusive
                //float splitRotationVariation = 0f;

                //Debug.Log("random " + gen.splitRotationVariation[gen.randomIndex]);

                //Debug.Log("randomNumbers size: " + gen.randomNumbers.Length);
                //Debug.Log("random index: " + gen.randomNumbers[n]);
                //Debug.Log("splitRotVar size: " + gen.splitRotationVariation.Length);
                Debug.Log("randomNumberIndex: " + gen.randomNumbers[n]);
                Debug.Log("random variation: " + gen.splitRotationVariation[gen.randomNumbers[n]]);
                next[n].split(length, branchDir, norm(next[n].point - point), r, point, splitAxis, splitRotation + gen.splitRotationVariation[gen.randomNumbers[gen.randomNumberIndex]], splitAngleDegA, splitAngleDegB, left, center, right);
                // bad solution !!!

                gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
                gen.randomIndex = (gen.randomIndex + 1) % gen.randomArraySize;
                n += 1;

            }

            //for (int n = 0; n < next.Count; n++)
            //{
            //    next[n].split(length, branchDir, norm(next[n].point - point), r, point, splitAxis, splitRotation, splitAngleDegA, splitAngleDegB, left, center, right);
            //}
        }
        else
        {
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


            //Vector3 rightDir = norm(Vector3.Cross(branchDir, refVector));
            //Vector3 rightDir = norm(Vector3.Cross(tangent, refVector));


            //splitAxis = norm(Vector3.Cross(rightDir, localDir));


            //Vector3 dirA = Quaternion.AngleAxis(splitAngleDegA, splitAxis) * localDir;
            //Vector3 dirB = Quaternion.AngleAxis(-splitAngleDegB, splitAxis) * localDir;


            // TODO: use splitOrientationAngle -> relative to cotangent!

            splitAxis = Quaternion.AngleAxis(splitRotation, tangent) * cotangent; // test! (???)

            Vector3 dirA = Quaternion.AngleAxis(splitAngleDegA, splitAxis) * norm(tangent);
            Vector3 dirB = Quaternion.AngleAxis(-splitAngleDegB, splitAxis) * norm(tangent);

            //if (left) gen.randomNumbers[gen.randomNumberIndex] // randomSplitVariationArraySize
            if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize * (1f - gen.splitProbability))
            {
                Vector3 newPointA = point + dirA * length;
                node nodeA = new node(newPointA, r, gen, this);
                //nodeA.tangent = norm(dirA);
                nodeA.tangent = norm(nodeA.point - (point + norm(dirA) * length));
                next.Add(nodeA);
                left = true;
            }
            else
            {
                left = false;
            }
            gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
            //if (right)
            if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize * (1f - gen.splitProbability))
            {
                Vector3 newPointB = point + dirB * length;
                node nodeB = new node(newPointB, r, gen, this);
                //nodeB.tangent = norm(dirB);


                nodeB.tangent = norm(nodeB.point - (point + norm(dirB) * length));
                next.Add(nodeB);
                right = true;
            }
            else
            {
                right = false;
            }
            gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
            if (left == false || right == false)
            //if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize / 2)
            {
              Vector3 newPointC = point + localDir * length;
              node nodeC = new node(newPointC, r, gen, this);
              nodeC.tangent = norm(localDir);
              next.Add(nodeC);
              center = true;
            }
            else
            {
                center = false;
            }

            gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;

            //tangent = norm((next[0].point - point) + (next[1].point - point));

            int c = 0;
            if (right)
            {
                gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) / 3f, next[c].point)); // OK

                //next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) / 3f));

                next[c].tangent = norm(next[c].point - point);
                tangent = norm(next[c].point - prevPoint);

                cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));

                c += 1;
            }
            if (left)
            {
                //gen.tangentDebugLines.Add(new line(point, next[1].point)); // OK
                gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) / 3f, next[c].point)); // OK

                //next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) / 3f));

                next[c].tangent = norm(next[c].point - point);
                tangent = norm(next[c].point - prevPoint);

                cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));

                c += 1;
            }
            if (left == false || right == false)
            {
                gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) / 3f, next[c].point)); // OK

                //next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) / 3f));

                next[c].tangent = norm(next[c].point - point);
                tangent = norm(next[c].point - prevPoint);

                cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));
            }


                // TODO: offset points up in direction of parent branch -> account for curve!

                //points.Add(newPointA);
                //points.Add(newPointB);
            
        }
    }

    public void getAllSegments(List<segment> allSegments, int sections, int ringRes)
    {
        //Debug.Log("new next node");
        foreach (node n in next)
        {
            //if (next.Count > 1)
            //{
            //    Debug.Log("next: count: " + next.Count);
            //    Debug.Log("next: start point same? " + point);
            //}
            allSegments.Add(new segment(point, n.point, tangent, n.tangent, cotangent, n.cotangent, sections, radius, n.radius, ringRes, gen));
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
    public treeGen2 treeGen;

    public List<Vector3> vertices;
    public List<int> triangles;

    public segment(Vector3 Start, Vector3 End, Vector3 startTan, Vector3 endTan, Vector3 startCotan, Vector3 endCotan, int Sections, float StartRadius, float EndRadius, int ringRes, treeGen2 gen)
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

    public int levels; // -> children in node

    public List<float> splitAngleDegA;
    public List<float> splitAngleDegB;

    public float splitLength;

    public List<float> splitRotation;
    public float[] splitRotationVariation;
    float splitRotationVariationRange;
    public float SplitRotationVariationRange;
    [HideInInspector]
    public int randomIndex;
    [HideInInspector]
    public int randomArraySize;
    public int[] randomNumbers;
    public int randomNumberIndex;
    int randomSeed = 1;
    public int RandomSeed = 1;

    [Range(0f, 1f)]
    public float splitProbability;

    public float growLength;

    public List<segment> allSegments;

    public List<Vector3> allSegmentItem1Debug;
    public List<Vector3> allSegmentItem2Debug;
    public List<Vector3> debugList;
    public List<Vector3> debugListRed;
    public List<Vector3> debugListGreen;
    public List<Vector3> debugListBlue;

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
        Random.InitState(randomSeed);
        allSegments = new List<segment>();
        allSegmentItem1Debug = new List<Vector3>();
        allSegmentItem2Debug = new List<Vector3>();
        debugList = new List<Vector3>();
        debugListGreen = new List<Vector3>();
        debugListRed = new List<Vector3>();
        debugListBlue = new List<Vector3>();

        Random.InitState(randomSeed);
        randomIndex = 0;
        randomNumberIndex = 0;
        randomArraySize = 1000;
        randomNumbers = new int[randomArraySize];
        splitRotationVariation = new float[randomArraySize];
        generateRandomNumbers();

        if (splitRotation == null)
        {
            splitRotation = new List<float>();
            splitRotation.Add(40f);
            splitRotation.Add(40f);
            splitRotation.Add(40f);
            splitRotation.Add(40f);
        }
        if (splitAngleDegA == null)
        {
            splitAngleDegA = new List<float>();
            splitAngleDegA.Add(50f);
            splitAngleDegA.Add(50f);
            splitAngleDegA.Add(50f);
            splitAngleDegA.Add(50f);
        }

        if (splitAngleDegB == null)
        {
            splitAngleDegB = new List<float>();
            splitAngleDegB.Add(50f);
            splitAngleDegB.Add(50f);
            splitAngleDegB.Add(50f);
            splitAngleDegB.Add(50f);
        }

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
        randomIndex = 0;
        randomNumberIndex = 0;
        debugList.Clear();
        debugListGreen.Clear();
        debugListRed.Clear();
        debugListBlue.Clear();

        if (RandomSeed != randomSeed)
        {
            randomSeed = RandomSeed;
            generateRandomNumbers();
        }

        if (splitRotationVariationRange != SplitRotationVariationRange)
        {
            splitRotationVariationRange = SplitRotationVariationRange;
            generateRandomNumbers();
        }

        if (tangentDebugLines != null)
        {
            tangentDebugLines.Clear();
        }
        if (dirAdebugLines != null)
        {
            dirAdebugLines.Clear();
        }
        if (dirBdebugLines != null)
        {
            dirBdebugLines.Clear();
        }

        root = new node(new Vector3(0f, 0f, 0f), radius, this, null);
        root.next.Add(new node(norm(treeGrowDir) * treeHeight, radius, this, root));
        root.tangent = norm(root.next[0].point - root.point);
        root.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(1f, 0f, 0f)));
        if (root.cotangent == new Vector3(0f, 0f, 0f))
        {
            root.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, 1f)));
        }
        root.next[0].tangent = norm(root.next[0].point - root.point);
        root.next[0].cotangent = norm(Vector3.Cross(root.next[0].tangent, Vector3.Cross(root.cotangent, root.next[0].tangent)));

        //root.grow(Quaternion.identity, treeHeight / 2f, root.next[0].point, root.next[0].radius * 0.5f);
        root.grow(Quaternion.AngleAxis(0f, new Vector3(1f, 0f, 0f)), growLength, root.next[0].point, root.next[0].radius * 0.5f);
        root.grow(Quaternion.AngleAxis(0f, new Vector3(0f, 0f, 1f)), growLength, root.next[0].point, root.next[0].radius * 0.5f);

        root.split(splitLength, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, root.point, new Vector3(1f, 0f, 0f), splitRotation[0], splitAngleDegA[0], splitAngleDegB[0], true, false, true);

        root.split(splitLength * 0.8f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 2f, root.point, new Vector3(1f, 0f, 0f), splitRotation[1], splitAngleDegA[1], splitAngleDegB[1], true, false, true);
        root.split(splitLength * 0.6f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].radius / 4f, root.point, new Vector3(0f, 0f, 1f), splitRotation[2], splitAngleDegA[2], splitAngleDegB[2], true, true, true);
        root.split(splitLength * 0.6f, root.next[0].point - root.point, root.next[0].point - root.point, 0, root.point, new Vector3(1f, 0f, 0f), splitRotation[3], splitAngleDegA[3], splitAngleDegB[3], true, false, true);

        allSegments.Clear();
        allSegments = getAllSegments(sections);
        //Debug.Log("allSegments Count: " + allSegments.Count);

        vertices.Clear();
        triangles.Clear();
        normals.Clear();
        foreach (segment s in allSegments)
        {
            //debugList.Add(s.start);
            //debugList.Add(s.end);

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

    public void generateRandomNumbers()
    {
        for (int i = 0; i < randomArraySize; i++)
        {
            splitRotationVariation[i] = Random.Range(-splitRotationVariationRange, splitRotationVariationRange);
            randomNumbers[i] = Random.Range(0, randomArraySize - 1);
        }
        Debug.Log("random numbers generated!");
    }

    List<segment> getAllSegments(int sections)
    {
        List<segment> allSegments = new List<segment>();
        if (root != null)
        {
            root.getAllSegments(allSegments, sections, stemRingResolution);
        }
        //Debug.Log("allSegmants count " + allSegments.Count);
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

        //Debug.Log("refVector: " + refVector);

        for(int s = 0; s < allSegments.Count; s++)
        {
            //Debug.Log("in generateMesh(): segment: ");

            // TODO: automatic tangents -> connecttion line from previous to next vertex -> tangent!

            Vector3 controlPt1 = allSegments[s].start + allSegments[s].startTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f; //(1f / 3f) * (end - start);
            Vector3 controlPt2 = allSegments[s].end - allSegments[s].endTangent * vLength(allSegments[s].end - allSegments[s].start) / 3f;     //(2f / 3f) * (end - start);

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

            int debug = allSegments[s].sections + 1;
            //Debug.Log("sections loop: " + debug);
            debugListRed.Add(allSegments[s].start);
            debugListRed.Add(allSegments[s].end);

            tangentDebugLines.Add(new line(allSegments[s].start, controlPt1));
            tangentDebugLines.Add(new line(allSegments[s].end, controlPt2));

            debugListBlue.Add(controlPt1);
            debugListBlue.Add(controlPt2);

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                pos[j] = sampleSpline(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections);
                debugListGreen.Add(pos[j]);

                tangent[j] = norm(sampleSplineTangent(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections));

                if (vLength(tangent[j]) == 0f)
                {
                    Debug.Log("ERROR tangent is zero! j = " + j);
                }

                dirA[j] = vLerp(allSegments[s].startCotangent, allSegments[s].endCotangent, (float)j / (float)allSegments[s].sections);// green
                
                dirB[j] = norm(Vector3.Cross(tangent[j], dirA[j])); // blue

                // improve dirA!
                dirA[j] = norm(Vector3.Cross(dirB[j], tangent[j])); // green

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                Vector3 dir = norm(tangent[j]);

                dirAdebugLines.Add(new line(pos[j], pos[j] + dirA[j] / 5f)); // green

                dirBdebugLines.Add(new line(pos[j], pos[j] + dirB[j] / 5f)); // blue

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

        //Debug.Log("in generateTriangles: sections: " + Sections);
        //Debug.Log("in generateTriangles: stemRingResolution: " + stemRingResolution);

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

            //if (debugList != null)
            //{
            //    if (debugList.Count > 0)
            //    {
            //        Debug.Log("debugList count: " + debugList.Count);
            //    }
            //    foreach (Vector3 v in debugList)
            //    {
            //        Gizmos.DrawSphere(v, 0.01f);
            //    }
            //
            //    //foreach (Vector3 v in vertices)
            //    //{
            //    //    Gizmos.DrawSphere(v, 0.02f);
            //    //}
            //}
            //if (debugListGreen != null)
            //{
            //    Gizmos.color = Color.green;
            //    foreach (Vector3 v in debugListGreen)
            //    {
            //        Gizmos.DrawSphere(v, 0.02f);
            //    }
            //}
            if (debugListRed != null)
            {
                Gizmos.color = Color.red;
                foreach (Vector3 v in debugListRed)
                {
                    Gizmos.DrawSphere(v, 0.03f);
                }
            }
            if (debugListBlue != null)
            {
                Gizmos.color = Color.blue;
                foreach (Vector3 v in debugListBlue)
                {
                    Gizmos.DrawSphere(v, 0.03f);
                }
            }
            Gizmos.color = Color.blue;
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
