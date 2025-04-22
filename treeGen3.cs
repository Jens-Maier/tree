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

public enum shape
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

public enum splitMode
{
    alternating,
    horizontal
}

public class node
{
    public Vector3 point;
    public List<Vector3> tangent; //list<tangent> for splits! [tangentIn, tangentOutA, tangentOutB] ((only[tangent] without split!)
    public Vector3 cotangent;
    public List<node> next;
    public node parent;
    public float radius;
    public float tVal; // point height along tree [0..1]
    public float taper;
    public treeGen3 gen;
    public List<List<node>> children;

    public node(Vector3 Point, Vector3 newTangent, Vector3 newCotangent, float t, float newTaper, treeGen3 g, node par)
    {
        point = Point;
        tangent = new List<Vector3>();
        tangent.Add(newTangent);
        cotangent = newCotangent;
        tVal = t;
        radius = 0f;
        next = new List<node>();
        taper = newTaper;
        gen = g;
        parent = par;
        children = new List<List<node>>(); // one list for each node in next 
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

    public void getAllStartNodes(List<node> startNodes, List<int> nrSplitsPassedAtStartNode, int nrSplitsPassed, int startLevel, int level)
    {
        // TODO: calculate dirStart, dirEnd
        if (level >= startLevel)
        {
            if (next.Count > 0)
            {
                startNodes.Add(this);
                nrSplitsPassedAtStartNode.Add(nrSplitsPassed);
            }
        }
        if (next.Count > 1)
        {
            nrSplitsPassed += 1;
        }
        foreach (node n in next)
        {
            n.getAllStartNodes(startNodes, nrSplitsPassedAtStartNode, nrSplitsPassed, startLevel, level + 1);
        }
    }

    public void getAllChildNodes(List<node> allChildNodes)
    {
        foreach (List<node> c in children)
        {
            foreach (node n in c)
            {
                allChildNodes.Add(n);
            }
        }
        foreach (node n in next)
        {
            n.getAllChildNodes(allChildNodes);
        }
    }

    public void getAllSegments(List<segment> allSegments, int ringRes)
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
                int index = i + 1;
                //Debug.Log("tangent count: " + tangent.Count + ", using tangent index " + index + ", next count: " + next.Count);
                //Debug.Log("next[0].point: " + next[0].point + ", next[1].point: " + next[1].point);
                                
                allSegments.Add(new segment(point, next[i].point, tangent[i + 1], next[i].tangent[0], cotangent, next[i].cotangent, radius, next[i].radius, ringRes, gen));
                // Vector3 a = norm(next[i].point - point);
                // Vector3 b = norm(tangent[i + 1]);
                // if (a != b)
                // {
                //     Debug.Log("ERROR: next[i].point - point: " + a + ", tangent[i + 1]: " + b  +"radius: " + radius);
                //     gen.debugErrorPoints.Add(point);
                //     gen.debugErrorPoints.Add(next[i].point);
                // }

            }
            else
            {
                //Debug.Log("tangent count: " + tangent.Count); // 1
                //Debug.Log("next count: " + next.Count); // 1

                allSegments.Add(new segment(point, next[i].point, tangent[0], next[i].tangent[0], cotangent, next[i].cotangent, radius, next[i].radius, ringRes, gen));
            }

            next[i].getAllSegments(allSegments, ringRes);
        }

        foreach (List<node> l in children)
        {
            foreach (node c in l)
            {
                //Debug.Log("child start point: " + c.point);
                //Debug.Log("child next count: " + c.next.Count);
                c.getAllSegments(allSegments, ringRes);
            }
        }
    }

    public node subdivideSegment(int nextIndex, float splitHeight)
    {
        Vector3 splitPoint = sampleSpline(point, next[nextIndex].point, tangent[nextIndex], next[nextIndex].tangent[0], splitHeight);
        Vector3 splitTangent = sampleSplineTangentT(point, next[nextIndex].point, tangent[nextIndex], next[nextIndex].tangent[0], splitHeight);
        Vector3 splitCotangent = vLerp(cotangent, next[nextIndex].cotangent, splitHeight);
        float t = fLerp(tVal, next[nextIndex].tVal, splitHeight);
        node newNode = new node(splitPoint, splitTangent, splitCotangent, t, taper, gen, this);
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

                float sampleTval = fLerp(tVal, nodeNext.tVal, (float)i / (float)n);

                // improve sampleCotangent!
                sampleCotangent = norm(Vector3.Cross(dirB, sampleTangent));
                node newNode;
                if (i == 1)
                {
                    newNode = new node(samplePoint, sampleTangent, sampleCotangent, sampleTval, taper, gen, this);
                }
                else
                {
                    newNode = new node(samplePoint, sampleTangent, sampleCotangent, sampleTval, taper, gen, currentNode);
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

        Vector3 nextTangent = norm(norm(gen.treeGrowDir) * gen.treeHeight - (gen.rootNode.point + gen.rootNode.tangent[0] * vLength(norm(gen.treeGrowDir) * gen.treeHeight - gen.rootNode.point) * (1.5f / 3f)));
        Vector3 centerPoint = sampleSpline(gen.rootNode.point, norm(gen.treeGrowDir) * gen.treeHeight, new Vector3(0f, 1f, 0f), nextTangent, tVal);

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
            for (int i = 0; i < tangent.Count; i++)
            {
                tangent[i] = Quaternion.AngleAxis(curvature / 2f, curveAxis) * tangent[i];
            }
        }
        else
        {
            for (int i = 0; i < tangent.Count; i++)
            {
                tangent[i] = Quaternion.AngleAxis(curvature, curveAxis) * tangent[i];
            }
        }
        
        foreach (node n in next)
        {
            n.curveStep(curvature, curveAxis, rotationPoint, false);
        }
    }


    public void shyBranches()
    {
        // TODO: rotate branch split axis to maximise distance of split branches to all other nodes of same level (iterations...)
    }

    public void grow()
    {
        
    }

    public float lengthToTip()
    {
        if (next.Count > 0)
        {
            return (next[0].lengthToTip() + vLength(next[0].point - point));
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
        if (next.Count > 0 || children.Count > 0)
        {
            float sum = 0f;
            if (next.Count > 0)
            {
                float max = 0f;
                foreach (node n in next)
                {
                    float s =  n.calculateRadius(maxRadius);
                    s += vLength(n.point - point) * n.taper * n.taper;
                    if (s > max)
                    {
                        max = s;
                    }
                }
                sum = max;
            }
            if (children.Count > 0)
            {
                foreach (List<node> c in children)
                {
                    foreach (node n in c)
                    {
                        n.calculateRadius(sum);
                    }
                }
            }
            if (sum < maxRadius)
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

    public static Vector3 sampleSpline(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
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

    public segment(Vector3 Start, Vector3 End, Vector3 startTan, Vector3 endTan, Vector3 startCotan, Vector3 endCotan, float StartRadius, float EndRadius, int ringRes, treeGen3 gen)
    {
        start = Start;
        end = End;
        startTangent = startTan;
        startCotangent = startCotan;
        endTangent = endTan;
        endCotangent = endCotan;
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

    public Random random;

    public node rootNode;
    public List<segment> allSegments;

    public float treeHeight;
    public shape treeShape;
    public Vector3 treeGrowDir;

    [Range(0f, 0.5f)]
    public float taper; // TODO: taper for stem and children
    [Range(0f, 0.01f)]
    public float branchTipRadius;
    [Range(0.001f, 1f)]
    public float ringSpacing;
    [Range(2, 10)]
    public int stemRingResolution;
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
    [Range(0, 50)]
    public int nrSplits;
    [Range(0f, 0.75f)]
    public float variance;

    [Range(0f, 10f)]
    public float curvOffsetStrength;
    
    public List<float> splitHeightInLevel;
    [Range(0f, 1f)]
    public float splitHeightVariation;
    [Range(0f, 90f)]
    public float testSplitAngle;
    [Range(0f, 90f)]
    public float testSplitPointAngle;

    public float[] splitProbabilityInLevel;
    public int[] expectedSplitsInLevel;

    public int nrChildLevels;

    public List<int> nrChildren;
    [Range(0f, 1f)]
    public List<float> relChildLength;
    [Range(0f, 45f)]
    public List<float> verticalRange;
    [Range(-90f, 90f)]
    public List<float> verticalAngleCrownStart;
    [Range(-90f, 90f)]
    public List<float> verticalAngleCrownEnd;
    public List<float> rotateAngle;
    //public bool symmetric; // TODO
    public List<int> childrenStartLevel;
    [Range(-90f, 90f)]
    public List<float> childCurvature;
    public List<int> nrChildSplits;
    public int seed;

    public List<int> nodeIndices;
    public int meanLevel;


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
            rootNode.getAllSegments(allSegments, stemRingResolution);
        }
        //Debug.Log("allSegmants count " + allSegments.Count);
        return allSegments;
    }

    public void addChildren()
    {
        Debug.Log("in addChildren: nrChildLevels: " + nrChildLevels);
        Debug.Log("in addChildren: nrchildren.Count: " + nrChildren.Count);
        for (int i = 0; i < nrChildren.Count; i++)
        {
            Debug.Log("in addChildren: nrChildren[" + i + "]: " + nrChildren[i]);
        }
        
        for (int l = 0; l < nrChildLevels; l++)
        {
            Debug.Log("in addChildren: add children level " + l + ": nr: " + nrChildren[l]);
            Vector3[] childPoints = new Vector3[nrChildren[l]];
            List<node> startNodes = new List<node>();
            List<int> nrSplitsPassedAtStartNode = new List<int>();
            if (l == 0)
            {
                rootNode.getAllStartNodes(startNodes, nrSplitsPassedAtStartNode, 0, childrenStartLevel[0], 0); // TODO...
            }
            else
            {
                rootNode.getAllChildNodes(startNodes); // TODO
                for (int i = 0; i < startNodes.Count; i++)
                {
                    nrSplitsPassedAtStartNode.Add(0); // TODO
                }
            }

            float windingAngle = 0f;
            Debug.Log("startNodes: " + startNodes.Count);
            if (startNodes.Count > 0)
            {
                for (int i = 0; i < nrChildren[0]; i++)
                {
                    // int r = random.Next() % startNodes.Count;
                    // int n = random.Next() % startNodes[r].next.Count;
                    // float t = (float)random.NextDouble();

                    int startNodeIndex = (int)((float)startNodes.Count * (float)i / (float)nrChildren[0]);
                    int n = random.Next(startNodes[startNodeIndex].next.Count);//random.Next() % startNodes[startNodeIndex].next.Count;

                    //float t = (float)random.NextDouble();
                    float t = (float)startNodes.Count * (float)i / (float)nrChildren[0] - (float)startNodeIndex;

                    // TODO: winding -> equal distances -> add random offsets

                    Vector3 tangent;
                    if (startNodes[startNodeIndex].next.Count > 1)
                    {
                        tangent = startNodes[startNodeIndex].tangent[n + 1];
                    }
                    else
                    {
                        tangent = startNodes[startNodeIndex].tangent[0];
                    }

                    Vector3 startPoint = sampleSplineT(startNodes[startNodeIndex].point, startNodes[startNodeIndex].next[n].point, tangent, startNodes[startNodeIndex].next[n].tangent[0], t);
                    Vector3 startPointTangent = sampleSplineTangentT(startNodes[startNodeIndex].point, startNodes[startNodeIndex].next[n].point, tangent, startNodes[startNodeIndex].next[n].tangent[0], t);

                    Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));

                    Vector3 centerPoint = sampleSplineT(rootNode.point, norm(treeGrowDir) * treeHeight, new Vector3(0f, 1f, 0f), nextTangent, startNodes[startNodeIndex].tVal);

                    Vector3 outwardDir = startNodes[startNodeIndex].point - centerPoint;


                    if (outwardDir == Vector3.zero)
                    {
                        outwardDir = vLerp(startNodes[startNodeIndex].cotangent, startNodes[startNodeIndex].next[n].cotangent, t);
                    }
                    Debug.Log("outwardDir: " + outwardDir);

                    float dirRange = 180f / ((float)nrSplitsPassedAtStartNode[startNodeIndex] + 1f);
                    if (dirRange < 15f)
                    {
                        dirRange = 15f;
                    }

                    float verticalAngle = fLerp(verticalAngleCrownStart[0], verticalAngleCrownEnd[0], startNodes[startNodeIndex].tVal);

                    Vector3 dirStart = norm(Quaternion.AngleAxis(-dirRange, startPointTangent) * outwardDir);
                    Vector3 dirEnd = norm(Quaternion.AngleAxis(dirRange, startPointTangent) * outwardDir);
                    Vector3 verticalStart = norm(Quaternion.AngleAxis(-verticalAngle + verticalRange[0], norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);
                    Vector3 verticalEnd = norm(Quaternion.AngleAxis(-verticalAngle - verticalRange[0], norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);

                    float angle = windingAngle % (2f * dirRange);
                    Vector3 centerDir = norm(Quaternion.AngleAxis(-verticalAngle, norm(Vector3.Cross(startPointTangent, outwardDir))) * outwardDir);
                    Debug.Log("centerDir: " + centerDir); // (0, 0, -1)
                    Debug.Log("startPointTangent: " + startPointTangent); // (0, 1, 0)
                    Debug.Log("dirRange: " + dirRange);
                    Debug.Log("angle: " + angle); // 
                    Vector3 childDir = Quaternion.AngleAxis(-dirRange + angle, startPointTangent) * centerDir;

                    Debug.Log("dir: " + childDir);

                    // There is no single continuous function that can generate a vector in R3 that is orthogonal to a given one for all vector inputs. https://en.wikipedia.org/wiki/Hairy_ball_theorem
                    Vector3 childCotangent;
                    if (childDir.x != 0f)
                    {
                        childCotangent = new Vector3(-childDir.y, childDir.x, 0f);
                    }
                    else
                    {
                        if (childDir.y != 0f)
                        {
                            childCotangent = new Vector3(0f, -childDir.z, childDir.y);
                        }
                        else
                        {
                            childCotangent = new Vector3(childDir.z, 0f, -childDir.x);
                        }
                    }

                    Debug.Log("child cotangent: " + childCotangent);
                    node child = new node(startPoint, childDir, childCotangent, startNodes[startNodeIndex].tVal, taper / 1.5f, this, null); // TODO: taper[] for each level
                    //float branchLength = (1f - startNodes[startNodeIndex].tVal);
                    float branchLength = treeHeight * relChildLength[0] * shapeRatio(startNodes[startNodeIndex].tVal);
                    float lengthToTip = startNodes[startNodeIndex].lengthToTip();
                    // lengthToTip -= t * vLength(startNodes[startNodeIndex].next[n].point - startNodes[startNodeIndex].point);
                    // if (branchLength > lengthToTip)
                    // {
                    //     branchLength = lengthToTip;
                    // }
                    child.next.Add(new node(startPoint + childDir * branchLength, childDir, childCotangent, startNodes[startNodeIndex].tVal, taper / 1.5f, this, child));
                    Debug.Log("children count: " + startNodes[startNodeIndex].children.Count + ", n: " + n);
                    if (startNodes[startNodeIndex].children.Count < n + 1)
                    {
                        for (int m = 0; m < startNodes[startNodeIndex].next.Count; m++)
                        {
                            startNodes[startNodeIndex].children.Add(new List<node>());
                        }
                        
                        startNodes[startNodeIndex].children[n].Add(child);

                        debugPointsRed.Add(startPoint);
                        //debugLinesGreen.Add(new line(startPoint, startPoint + childDir * branchLength));

                        //debugLinesRed.Add(new line(startPoint, startPoint + dirStart * branchLength));
                        //debugLinesRed.Add(new line(startPoint, startPoint + dirEnd * branchLength));
                        //
                        //debugLinesRed.Add(new line(startPoint, startPoint + verticalStart * branchLength));
                        //debugLinesRed.Add(new line(startPoint, startPoint + verticalEnd * branchLength));

                        windingAngle += rotateAngle[0]; // TODO: fibonacci numbers: 1/2, 1/3, 2/5, 3/8 -> 180, 120, 144, 135, -> f(n)/f(n+2)

                        Debug.Log("children[" + n + "] count: " + startNodes[startNodeIndex].children[n].Count);
                        startNodes[startNodeIndex].children[n][0].resampleSpline(3, 0f, 0f, 1f);

                        // curvature
                        child.curveBranches(childCurvature[0], Vector3.Cross(startPointTangent, childDir));
                        debugLinesGreen.Add(new line(startPoint, startPoint + norm(Vector3.Cross(startPointTangent, childDir))));
                    }
                }
                // add one child at tip of spline -> do not clamp length by length to tip! -> TODO: smaller taper! -> store taper in nodes!
                // TODO: add to child list!
                List<node> leafNodes = new List<node>();
                rootNode.getAllLeafNodes(leafNodes);
                Debug.Log("leafNodes count: " + leafNodes.Count);
                foreach (node n in leafNodes)
                {

                    float branchLength = treeHeight * relChildLength[0] * shapeRatio(1f);
                    Vector3 childDir = n.tangent[0];
                    Vector3 childCotangent;
                    if (n.tangent[0].x != 0f)
                    {
                        childCotangent = new Vector3(-childDir.y, childDir.x, 0f);
                    }
                    else
                    {
                        if (childDir.y != 0f)
                        {
                            childCotangent = new Vector3(0f, -childDir.z, childDir.y);
                        }
                        else
                        {
                            childCotangent = new Vector3(childDir.z, 0f, -childDir.x);
                        }
                    }

                    Vector3 nextTangent = norm(norm(treeGrowDir) * treeHeight - (rootNode.point + rootNode.tangent[0] * vLength(norm(treeGrowDir) * treeHeight - rootNode.point) * (1.5f / 3f)));
                    Vector3 centerPoint = sampleSplineT(rootNode.point, norm(treeGrowDir) * treeHeight, new Vector3(0f, 1f, 0f), nextTangent, 1f);
                    Vector3 outwardDir = n.point - centerPoint;

                    if (outwardDir == Vector3.zero)
                    {
                        outwardDir = n.cotangent;
                    }
                    node child = new node(n.point + n.tangent[0] * branchLength, childDir, childCotangent, n.tVal, taper / 2f, this, n);

                    // before
                    //n.next.Add(child);
                    //n.applyCurvature(splitCurvature, outwardDir);

                    // -> add as child! (TEST!)
                    if (n.children.Count == 0)
                    {
                        n.children.Add(new List<node>());
                    }
                    n.children[n.children.Count - 1].Add(new node(n.point, n.tangent[0], n.cotangent, n.tVal, n.taper, n.gen, n));
                    n.children[n.children.Count - 1][n.children[n.children.Count - 1].Count - 1].next.Add(child);
                    Debug.Log("add child at leafNode "); // TODO...
                    n.applyCurvature(splitCurvature, outwardDir);
                }

            }
        }
    
    }
    
    

    public void setTreeShape(int s)
    {
        switch (s)
        {
            case 0: treeShape = shape.conical; break;
            case 1: treeShape = shape.cylindrical; break;
            case 2: treeShape = shape.flame; break;
            case 3: treeShape = shape.hemispherical; break;
            case 4: treeShape = shape.inverseConical; break;
            case 5: treeShape = shape.spherical; break;
            case 6: treeShape = shape.taperedCylindrical; break;
            case 7: treeShape = shape.tendFlame; break;
            default: treeShape = shape.conical; break;
        }
    }

    public float shapeRatio(float tVal)
    {
        switch (treeShape)
        {
            case shape.conical:
                return (0.2f + 0.8f * tVal);
            case shape.spherical:
                return (0.2f + 0.8f * Mathf.Sin(Mathf.PI * tVal));
            case shape.hemispherical:
                return (0.2f + 0.8f * Mathf.Sin(0.5f * Mathf.PI * tVal));
            case shape.cylindrical:
                return 1f;
            case shape.taperedCylindrical:
                return 0.5f + 0.5f * tVal;
            case shape.flame:
                if (tVal <= 0.7)
                {
                    return tVal / 0.7f;
                }
                else
                {
                    return (1f - tVal) / 0.3f;
                }
            case shape.inverseConical:
                return 1f - 0.8f * tVal;
            case shape.tendFlame:
                if (tVal <= 0.7f)
                {
                    return 0.5f + 0.5f * tVal / 0.7f;
                }
                else
                {
                    return 0.5f + 0.5f * (1f - tVal) / 0.3f;
                }
            default: 
                Debug.Log("ERROR: invalid tree shape!");
                return 0f;
        }
        //return (1f - tVal);
    }

    public void splitChildren(int nrChildSplits, float splitAngle, float splitPointAngle) // TODO: split child at tip of spline -> TODO: get all nodes... 
    {
        List<node> allChildNodes = new List<node>();
        rootNode.getAllChildNodes(allChildNodes);

        splitProbabilityInLevel = new float[nrChildSplits];
        expectedSplitsInLevel = new int[nrChildSplits];

        int meanLevelChild = (int)Mathf.Log((float)nrChildSplits / (float)allChildNodes.Count, 2f);
        Debug.Log("splitChildren: nrChildSplits: " + nrChildSplits + ", meanLevelChild: " + meanLevelChild + ", nrChildren: " + allChildNodes.Count); // 12, 0, 22

        Debug.Log("nrChildren: " + allChildNodes.Count);
        
        if (nrChildSplits < allChildNodes.Count)
        {
            expectedSplitsInLevel[0] = nrChildSplits;
            splitProbabilityInLevel[0] = 1f;
            for (int i = 1; i < nrChildSplits; i++)
            {
                expectedSplitsInLevel[i] = 0;
            }
        }
        else
        {
            if (nrChildSplits > 0)
            {
                splitProbabilityInLevel[0] = 1f;
                expectedSplitsInLevel[0] = allChildNodes.Count;
            }
            else
            {
                splitProbabilityInLevel[0] = 0f;
                expectedSplitsInLevel[0] = 0;
            }

            for (int i = 1; i < (int)Mathf.RoundToInt((float)meanLevelChild - variance * (float)meanLevelChild); i++)
            {
                splitProbabilityInLevel[i] = 1f;
                expectedSplitsInLevel[i] = allChildNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
            }
            for (int i = (int)Mathf.RoundToInt((float)meanLevelChild - variance * (float)meanLevelChild); i < (int)Mathf.RoundToInt((float)meanLevelChild + variance * (float)meanLevelChild); i++)
            {
                splitProbabilityInLevel[i] = 1f - (7f / 8f) * (float)(i - (int)Mathf.RoundToInt((float)meanLevelChild - variance * (float)meanLevelChild)) / 
                                                (Mathf.RoundToInt((float)meanLevelChild + variance * (float)meanLevelChild) - Mathf.RoundToInt((float)meanLevelChild - variance * (float)meanLevelChild));
                expectedSplitsInLevel[i] = allChildNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
            }
            for (int i = (int)Mathf.RoundToInt((float)meanLevelChild + variance * (float)meanLevelChild); i < nrChildSplits; i++)
            {
                
                Debug.Log("i: " + i + ", nrChildSplits: " + nrChildSplits + ", expectedSplitsInLevel length: " + expectedSplitsInLevel.Length + ", splitProbability length: " + splitProbabilityInLevel.Length);
                if (i > 0)
                {
                    splitProbabilityInLevel[i] = 1f / 8f;
                    expectedSplitsInLevel[i] = allChildNodes.Count * (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]); 
                }
                
                //i: 0, nrChildSplits: 23, expectedSplitsInLevel length: 23, splitProbability length: 23
            }
        }

        for (int i = 0; i < nrChildSplits; i++)
        {
            Debug.Log("splitChildren: splitProbabilityInLevel[" + i + "]: " + splitProbabilityInLevel[i]);
        }

        // if (nrChildSplits > 0)
        // {
        //     splitProbabilityInLevel[0] = 1f;
        //     expectedSplitsInLevel[0] = 1;
        // }
        // else
        // {
        //     splitProbabilityInLevel[0] = 0f;
        //     expectedSplitsInLevel[0] = 0;
        // }
        // for (int i = 1; i < (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel); i++)
        // {
        //     splitProbabilityInLevel[i] = 1f;
        //     expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        // }
        // for (int i = (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel); i < (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i++)
        // {
        //     splitProbabilityInLevel[i] = 1f - (7f / 8f) * (float)(i - (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel)) / 
        //                                     (Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel) - Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel));
        //     expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        // }
        // for (int i = (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i < nrChildSplits; i++)
        // {
        //     splitProbabilityInLevel[i] = 1f / 8f;
        //     expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        // }

        List<List<(node, int)>> nodesInLevelNextIndex = new List<List<(node, int)>>();
        for (int i = 0; i <= nrChildSplits; i++)
        {
            nodesInLevelNextIndex.Add(new List<(node, int)>());
        }

        foreach(node child in allChildNodes)
        {
            for (int n = 0; n < child.next.Count; n++)
            {
                nodesInLevelNextIndex[0].Add((child, n));
            }
        }

        
        //TODO...

        int totalSplitCounter = 0;
        for (int level = 0; level < nrChildSplits; level++)
        {
            int splitsInLevel = 0;
            int safetyCounter = 0;
            
            nodeIndices = new List<int>();
            for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
            {
                nodeIndices.Add(i);
            }
            Debug.Log("splitChildren: begin of level " + level + ": nodeIndices.Count: " + nodeIndices.Count + ", expectedSplitsInLevel: " + expectedSplitsInLevel[level]);
            // for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
            // {
            //     Debug.Log("nodeIndices[" + i + "]: " + nodeIndices[i]);
            // }

            while(splitsInLevel < expectedSplitsInLevel[level])
            {
                Debug.Log("begin of iteration: nodeIndices.Count: " + nodeIndices.Count);
                if (nodeIndices.Count == 0)
                {
                    break;
                }
                
                if (totalSplitCounter == nrChildSplits)
                {
                    break;
                }
                float r = (float)random.NextDouble();
                float h = (float)random.NextDouble() - 0.5f;
                if (r <= splitProbabilityInLevel[level])
                {
                    // split
                    int indexToSplit = random.Next(nodeIndices.Count);//random.Next() % nodeIndices.Count;
                    Debug.Log("splitChildren: indexToSplit: " + indexToSplit); // 0
                    Debug.Log("nodeIndices.Count: " + nodeIndices.Count); // 1
                    Debug.Log("nodeIndexToSplit: " + nodeIndices[indexToSplit]); // 0
                    Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndex[level].Count); // level 0, Count 31
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
                        Debug.Log("splitHeight: " + splitHeight + ", h: " + h);
                        node splitNode = split(nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1, nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item2, 
                                            splitHeight, splitAngle, splitPointAngle, level);

                        // TODO: in split() -> split between two nodes -> insert new node!

                        if (splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1)
                        {
                            // did not split
                            // nodesInLevelNextIndex[level].RemoveAt(indexToSplit); // TEST OFF
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
                if (safetyCounter > 160)
                {
                    Debug.Log("break!");
                    break;
                }
                
            }
        }
    }

    public void splitRecursive(node startNode, int nrSplits, float splitAngle, float splitPointAngle)
    {
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
        for (int i = (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel); i < (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i++)
        {
            splitProbabilityInLevel[i] = 1f - (7f / 8f) * (float)(i - (int)Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel)) / 
                                            (Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel) - Mathf.RoundToInt((float)meanLevel - variance * (float)meanLevel));
            //float expected = splitProbabilityInLevel[i] * Mathf.Pow(2f, (float)i);
            //if (expected > 0f && expected < 1f)
            //{
            //    expectedSplitsInLevel[i] = 1;
            //}
            //else
            //{
            //    expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * Mathf.Pow(2f, (float)i));
            //}
            Debug.Log("expecteSplitsInLevel length: " + expectedSplitsInLevel.Length + "splitProbabilityInLevel length: " + splitProbabilityInLevel.Length + ", i: " + i);

            expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        }
        for (int i = (int)Mathf.RoundToInt((float)meanLevel + variance * (float)meanLevel); i < nrSplits; i++)
        {
            splitProbabilityInLevel[i] = 1f / 8f;
            //float expected = splitProbabilityInLevel[i] * Mathf.Pow(2f, (float)i);
            //if (expected > 0f && expected < 1f)
            //{
            //    expectedSplitsInLevel[i] = 1;
            //}
            //else
            //{
            //    expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * Mathf.Pow(2f, (float)i));
            //}
            expectedSplitsInLevel[i] = (int)(splitProbabilityInLevel[i] * 2f * (float)expectedSplitsInLevel[i - 1]);
        }

        if (nrSplits == 2)
        {
            expectedSplitsInLevel[0] = 1;
            expectedSplitsInLevel[1] = 1;
        }


        // for (int i = 0; i < meanLevel - 1; i++)
        // {
        //     splitProbabilityInLevel[i] = 1f;
        //     expectedSplitsInLevel[i] = (int)(1f * Mathf.Pow(2f, (float)i));
        // }
        // splitProbabilityInLevel[meanLevel - 1] = 7f / 8f; 
        // 
        // expectedSplitsInLevel[meanLevel - 1] = (int)Mathf.RoundToInt((7f / 8f) * Mathf.Pow(2f, (float)(meanLevel - 1))); 
        // for (int i = meanLevel; i < nrSplits; i++)
        // {
        //     splitProbabilityInLevel[i] = 1f / 8f;
        //     expectedSplitsInLevel[i] = (int)(Mathf.RoundToInt(1f / 8f * Mathf.Pow(2f, (float)i)));
        // }
        // splitProbabilityInLevel[0] = 1f; // for nrSplits = 1

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
            Debug.Log("begin of level " + level + ": nodeIndices.Count: " + nodeIndices.Count + ", expectedSplitsInLevel: " + expectedSplitsInLevel[level]);
            for (int i = 0; i < nodesInLevelNextIndex[level].Count; i++)
            {
                Debug.Log("nodeIndices[" + i + "]: " + nodeIndices[i]);
            }

            while(splitsInLevel < expectedSplitsInLevel[level])
            {
                Debug.Log("begin of iteration: nodeIndices.Count: " + nodeIndices.Count);
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
                    Debug.Log("indexToSplit: " + indexToSplit); // 0
                    Debug.Log("nodeIndices.Count: " + nodeIndices.Count); // 1
                    Debug.Log("nodeIndexToSplit: " + nodeIndices[indexToSplit]); // 0
                    Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndex[level].Count); // level 0, Count 31
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
                        Debug.Log("splitHeight: " + splitHeight + ", h: " + h);
                        node splitNode = split(nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1, nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item2, 
                                            splitHeight, splitAngle, splitPointAngle, level);

                        // TODO: in split() -> split between two nodes -> insert new node!

                        if (splitNode == nodesInLevelNextIndex[level][nodeIndices[indexToSplit]].Item1)
                        {
                            // did not split
                            // nodesInLevelNextIndex[level].RemoveAt(indexToSplit); // TEST OFF
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
                if (safetyCounter > 40)
                {
                    Debug.Log("break!");
                    break;
                }
                
            }
        }




        // List<List<int>> splitIndex = new List<List<int>>();
        // for (int i = 0; i < nrSplits; i++)
        // {
        //     splitIndex.Add(new List<int>());
        // }
        // 
        // List<List<(node, int)>> nodesInLevelNextIndex = new List<List<(node, int)>>();
        // for (int i = 0; i <= nrSplits; i++)
        // {
        //     nodesInLevelNextIndex.Add(new List<(node, int)>());
        // }
        // nodesInLevelNextIndex[0].Add((startNode, 0));
        // int maxLevel = 1;

        // int totalSplitCounter = 0;
        // for (int level = 0; level < maxLevel; level++)
        // {
        //     //Debug.Log("level " + level + " splitProbability: " + splitProbabilityInLevel[level]);
        //     
        //     int i = 0;
        //     Debug.Log("nodesInLevelNextIndex.Count: " + nodesInLevelNextIndex.Count + "level: " + level);
        //     for (int c = 0; c < nodesInLevelNextIndex.Count; c++)
        //     {
        //         Debug.Log("nodesInLevelNextIndex[" + c + "].Count: " + nodesInLevelNextIndex[c].Count);
        //     }
        //     nodeIndices = new List<int>();
        //     for (int x = 0; x < nodesInLevelNextIndex[level].Count; x++)
        //     {
        //         nodeIndices.Add(x); // ERROR HERE !!!
        //     }
        //     if (nodesInLevelNextIndex[level].Count > 0 && totalSplitCounter < nrSplits)
        //     {
        //         Debug.Log("nodeIndices count: " + nodeIndices.Count);
        //         i = random.Next() % nodeIndices.Count;//
        //         Debug.Log("i: " + i);
        //         if (i == nodeIndices.Count || i > nodeIndices.Count)
        //         {
        //             i = nodeIndices.Count - 1;
        //         }
        //         int iteration = 0;
        //         int maxIterations = 20;
        //         int safetyCounter = 0;
        // 
        //         Debug.Log("level: " + level);
        //         Debug.Log("expectedSplitsInLevel.Count: " + expectedSplitsInLevel.Length);
        //         //for (int s = 0; s < expectedSplitsInLevel[level]; s++)
        //         //while(counter < expectedSplitsInLevel[level])
        //         for (int counter = 0; counter < 40; counter++)
        //         {
        //             if (counter >= expectedSplitsInLevel[level])
        //             {
        //                 break;
        //             }
        //             if (safetyCounter > maxIterations)
        //             {
        //                 break;
        //             }
        //             float r = ((float)(random.Next() % 9999)) / 10000f;
        // 
        //             if (r <= splitProbabilityInLevel[level] && iteration < maxIterations) // is only called once per level! -> must be called multiple times!
        //             {
        //                 Debug.Log("split! level " + level); // 2
        //                 Debug.Log("i: " + i); // 3
        //                 Debug.Log("nodeIndices count: " + nodeIndices.Count); 
        //                 Debug.Log("nodeIndices[i]: " + nodeIndices[i]);
        //                 
        //                 if (nodesInLevelNextIndex[level].Count > nodeIndices[i])
        //                 {
        //                     node splitNode = split(nodesInLevelNextIndex[level][nodeIndices[i]].Item1, nodesInLevelNextIndex[level][nodeIndices[i]].Item2, 0.5f, 30f);
        //                     if (splitNode == nodesInLevelNextIndex[level][nodeIndices[i]].Item1)
        //                     {
        //                         // did not split
        //                     }
        //                     else
        //                     {
        //                         nodeIndices.RemoveAt(i);
        //                         // -> update range of i! 
        // 
        //                         nodesInLevelNextIndex[level + 1].Add((splitNode, 0));//
        //                         nodesInLevelNextIndex[level + 1].Add((splitNode, 1));
        //                         int l = level + 1;
        //                         Debug.Log("adding two splitNodes to nodesInLevelNextIndex[level = " + l + "]");
        // 
        //                         //expectedSplitsInLevel[level] += 1;
        // 
        //                         // node split(node startNode, int nextIndex, float splitHeight, float splitAngle) 
        //                         // returns splitNode
        // 
        //                         counter += 1;
        //                         totalSplitCounter += 1;
        //                         Debug.Log("totalSplitCounter: " + totalSplitCounter);
        //                     }
        //                     //-------^^^^ add code above here  ^^^^-----------------------------------------------------------------------
        //                     if (nodeIndices.Count > 0)
        //                     {
        //                         i = random.Next() % nodeIndices.Count;
        //                     }
        //                     else
        //                     {
        //                         Debug.Log("nodeIndices.Count = 0! -> all branches are split (??) -> break");
        //                         break;
        //                     }
        //                 }
        //                 else
        //                 {
        //                     Debug.Log("ERROR: nodesInLevelNextIndex[level].Count: " + nodesInLevelNextIndex[level].Count + ", nodeIndices[i]: " + nodeIndices[i]);
        //                 }
        // 
        //                 Debug.Log("nodesInLevelNextIndex.Count: " + nodesInLevelNextIndex.Count + ", level: " + level);
        //                 for (int c = 0; c < nodesInLevelNextIndex.Count; c++)
        //                 {
        //                     Debug.Log("nodesInLevelNextIndex[" + c + "].Count: " + nodesInLevelNextIndex[c].Count);
        //                 }
        //             }
        //             if (totalSplitCounter == nrSplits)
        //             {
        //                 Debug.Log("totalSplitCounter == nrSplits: " + nrSplits + " -> break");
        //                 break;
        //             }
        //             iteration += 1;
        //             if (iteration >= maxIterations)
        //             {
        //                 Debug.Log("maxIteraitons -> break");
        //                 break;
        //             }
        //             safetyCounter += 1;
        //             if (safetyCounter > 20)
        //             {
        //                 Debug.Log("safetyCounter = 20 -> break");
        //                 break;
        //             }
        //         }
        //         if (level == maxLevel - 1)
        //         {
        //             maxLevel += 1;
        //             if (maxLevel > nrSplits)
        //             {
        //                 maxLevel = nrSplits;
        //             }
        //             if (maxLevel >= 20)
        //             {
        //                 Debug.Log("maxLevel: " + maxLevel);
        //                 break;
        //             }
        //             Debug.Log("new maxLevel: " + maxLevel);
        //         }
        //     }
        //     else
        //     {
        //         Debug.Log("nodesInLevelNextIndex[level = " + level + "].Count: " + nodesInLevelNextIndex[level].Count + ",  totalSplitCounter: " + totalSplitCounter);
        //     }
        // }
        // List<node> leafNodeParents = new List<node>();
        // leafNodeParents.Add(startNode);
        // float[] splitProbabilityInLevel = new float[nrSplits];
        // int[] expectedSplitsInLevel = new int[nrSplits];
        // int meanLevel = (int)Mathf.Log((float)nrSplits, 2f) + 1;
        // Debug.Log("meanLevel: " + meanLevel + ", nrSplits: " + nrSplits); // meanLevel: 2, nrSplits: 2
        // for (int i = 0; i < meanLevel - 1; i++)
        // {
        //     splitProbabilityInLevel[i] = 1f;
        //     Debug.Log("splitProbabilityInLevel[" + i + "]: " + splitProbabilityInLevel[i]); // [0]: 1  [1]: 0.875
        //     expectedSplitsInLevel[i] = (int)(1f * Mathf.Pow(2f, (float)i));
        // }
        // splitProbabilityInLevel[meanLevel - 1] = 7f / 8f; 
        // int k = meanLevel - 1; 
        // Debug.Log("splitProbabilityInLevel[" + k + "]: " + splitProbabilityInLevel[meanLevel - 1]); 
        // expectedSplitsInLevel[meanLevel - 1] = (int)Mathf.RoundToInt((7f / 8f) * Mathf.Pow(2f, (float)(meanLevel - 1))); 
        // for (int i = meanLevel; i < nrSplits; i++)
        // {
        //     splitProbabilityInLevel[i] = 1f / 8f;
        //     Debug.Log("splitProbabilityInLevel[" + i + "]: " + splitProbabilityInLevel[i]);
        //     expectedSplitsInLevel[i] = (int)(Mathf.RoundToInt(1f / 8f * Mathf.Pow(2f, (float)i)));
        // }
        // 
        // for (int i = 0; i < nrSplits; i++)
        // {
        //     Debug.Log("expectedSplitsInLevel[" + i + "]: " + expectedSplitsInLevel[i]); // [0]: 1  [1]: 2  [2]: 1
        // }
        // 
        // int splitCounter = 0;
        // int safetyLimit = 1000000;
        // int safetyCounter = 0;
        // int level = 0;
        // int[] splitsInLevel = new int[nrSplits];
        // for (int i = 0; i < nrSplits; i++)
        // {
        //     splitsInLevel[i] = 0;
        // }
        // while (splitCounter < nrSplits)
        // {
        //     Debug.Log("expectedSplitsInLevel[" + level + "]: " + expectedSplitsInLevel[level]); // [0]: 1  [1]: 2  [2]: 1
        // 
        //     bool[] isSplit = new bool[intPow(2, level)];
        //     for (int i = 0; i < intPow(2, level); i++)
        //     {
        //         isSplit[i] = false;
        //     }
        //     
        //     while(splitsInLevel[level] < expectedSplitsInLevel[level])
        //     {
        //         float r = ((float)(random.Next() % 100)) / 100f;
        //         int rnext = random.Next() % leafNodeParents.Count; // do not split nodes that have been split before!
        //         // todo: leafNodeParents can have 2 children -> 2 paths to split!
        //         
        //         if (isSplit[rnext] == false)
        //         {
        //             // split
        //             Debug.Log("split! rnext: " + rnext + ", in level " + level);
        //             leafNodeParents.Add(split(leafNodeParents[rnext], 0, 0.5f, splitAngle));
        //             isSplit[rnext] = true;
        //             
        //             splitsInLevel[level]++;
        //             splitCounter++;
        //             safetyCounter++;
        //         }
        // 
        // 
        //     }
        //     level++;
        // 
        //     Debug.Log("level++ -> " + level);
        //     if (level >= nrSplits)
        //     {
        //         Debug.Log("level " + level + "-> break");//
        //         break;
        //     }
        //     
        //     
        //     if (safetyCounter > safetyLimit)
        //     {
        //         Debug.Log("ERROR: safety limit reached!");
        //         break;
        //     }
        // }
        
    }


    public node split(node startNode, int nextIndex, float splitHeight, float splitAngle, float splitPointAngle, int level) // splitHeight: [0, 1]
    {
        Debug.Log("in split()!");
        // split after resampleSpline!  //  in resampleSpline(): t_value = (float)i / (float)n
        if (startNode.next.Count > 0 && nextIndex < startNode.next.Count)
        {
            int nrNodesToTip;
            nrNodesToTip = startNode.next[nextIndex].nodesToTip(0);
            
            if (splitHeight >= 0.999f)
            {
                splitHeight = 0.999f;
            }

            int splitAfterNodeNr = (int)((float)(nrNodesToTip) * splitHeight);

            if (nrNodesToTip > 0) //1)
            {
                if ((float)(nrNodesToTip) * splitHeight - (float)splitAfterNodeNr < 0.2f) 
                {
                    // split at existing node
                    Debug.Log("split at existing node!");

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
                    if (splitNode == rootNode)
                    {
                        Debug.Log("split at rootNode");
                    }
                    
                    if (splitNode == startNode)
                    {
                        Debug.Log("splitNode == startNode");
                    }
                    else
                    {
                        calculateSplitData(splitNode, splitAngle, splitPointAngle, level, splitMode.alternating);
                    }
                    return splitNode;

                }
                else
                {
                    Debug.Log("split at new node, splitAfterNodeNr: " + splitAfterNodeNr); // 0 | 0

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
                    
                    Vector3 newPoint = sampleSplineT(splitAfterNode.point, splitAfterNode.next[nextIndex].point, splitAfterNode.tangent[tangentIndex], 
                                                        splitAfterNode.next[nextIndex].tangent[0], (float)(nrNodesToTip) * splitHeight - (float)splitAfterNodeNr);
                    

                    Vector3 newTangent = sampleSplineTangentT(splitAfterNode.point, splitAfterNode.next[nextIndex].point, splitAfterNode.tangent[tangentIndex], 
                                                        splitAfterNode.next[nextIndex].tangent[0], (float)(nrNodesToTip) * splitHeight - (float)splitAfterNodeNr);
                    
                    Vector3 newCotangent = vLerp(splitAfterNode.cotangent, splitAfterNode.next[nextIndex].cotangent, (float)(nrNodesToTip) * splitHeight - (float)splitAfterNodeNr);

                    float newTval = fLerp(splitAfterNode.tVal, splitAfterNode.next[nextIndex].tVal, (float)(nrNodesToTip) * splitHeight - (float)splitAfterNodeNr);

                    node newSplitNode = new node(newPoint, newTangent, newCotangent, newTval, splitAfterNode.taper, this, splitAfterNode);
                    newSplitNode.next.Add(splitAfterNode.next[nextIndex]);
                    splitAfterNode.next[nextIndex] = newSplitNode;
                    
                    calculateSplitData(newSplitNode, splitAngle, splitPointAngle, level, splitMode.alternating);

                    return newSplitNode;
                }
            }
            
        }
        Debug.Log("in split() returning startNode");
        return startNode;
    }

    void calculateSplitData(node splitNode, float splitAngle, float splitPointAngle, int level, splitMode sMode)
    {
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
            case splitMode.alternating:
                splitAxis = norm(splitNode.cotangent);
                if (level % 2 == 1)
                {
                    splitAxis = Quaternion.AngleAxis(90f, splitNode.tangent[0]) * splitAxis;
                }
                break;

            case splitMode.horizontal:
                splitAxis = splitNode.cotangent; // TODO...
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

            node nodeA = new node(splitNode.point + Quaternion.AngleAxis(splitAngle, splitAxis) * relPos + curvOffset, tangentA, cotangentA, s.tVal, s.taper, this, s.parent);
            node nodeB = new node(splitNode.point + Quaternion.AngleAxis(-splitAngle, splitAxis) * relPos + curvOffset, tangentB, cotangentB, s.tVal, s.taper, this, s.parent);

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
        rootNode = new node(new Vector3(0f, 0f, 0f), new Vector3(0f, 1f, 0f), Vector3.Cross(treeGrowDir, new Vector3(treeGrowDir.x, 0f, treeGrowDir.z)), 0f, taper, this, null);
        //if (Mathf.Abs(treeGrowDir.x) > Mathf.Abs(treeGrowDir.z))
        //{
        //    if (treeGrowDir.x > 0)
        //    {
        //        rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(1f, 0f, 0f)));
        //    }
        //    else
        //    {
        //        rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(-1f, 0f, 0f)));
        //    }
        //}
        //else
        //{
        //    if (treeGrowDir.z > 0)
        //    {
        //        rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, 1f)));
        //    }
        //    else
        //    {
        //        rootNode.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, -1f)));
        //    }
        //}
        //rootNode.cotangent = Vector3.Cross(treeGrowDir, new Vector3(treeGrowDir.x, 0f, treeGrowDir.z));

        if (splitHeightInLevel == null)
        {
            Debug.Log("ERROR: splitHeightInLevel is null!");
        }
        if (splitHeightInLevel.Count < nrSplits)
        {
            int s = nrSplits - splitHeightInLevel.Count;
            for(int i = 0; i < s; i++)
            {
                splitHeightInLevel.Add(0.5f);
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
        
        rootNode.next.Add(new node(norm(treeGrowDir) * treeHeight, nextTangent, new Vector3(1f, 1f, 1f), 1f, taper, this, rootNode));
        rootNode.next[0].cotangent = norm(Vector3.Cross(rootNode.next[0].tangent[0], Vector3.Cross(rootNode.cotangent, rootNode.next[0].tangent[0])));

        rootNode.resampleSpline(resampleNr, noiseAmplitudeLower, noiseAmplitudeUpper, noiseScale);
        if (nrSplits > 0)
        {
            splitRecursive(rootNode, nrSplits, testSplitAngle, testSplitPointAngle);
        }

        Vector3 axis = rootNode.cotangent;
        
        rootNode.applyCurvature(splitCurvature, axis);
       
        addChildren();
        if (nrChildSplits.Count > 0)
        {
            if (nrChildSplits[0] > 0)
            {
                splitChildren(nrChildSplits[0], testSplitAngle, testSplitPointAngle);
            }
        }

        rootNode.shyBranches();
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
            if (sections == 0)
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

            float arcLength = 0f;

            for (int j = 0; j < sections + 1; j++)
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

                for (int i = 0; i <= 2 * stemRingResolution; i++)
                {
                    float angle = (Mathf.PI / (float)allSegments[s].stemRingResolution) * (float)i;

                    float f = (float)j / (float)(length / branchRingSpacing) * Mathf.Cos(angle) + fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing));
                    
                    Vector3 v = pos[j] + dirA[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / branchRingSpacing)) * Mathf.Cos(angle) +
                                         dirB[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / branchRingSpacing)) * Mathf.Sin(angle);

                    
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

            //for (int j = 0; j < sections + 1; j++)
            //{
            //    for (int i = 0; i <= 2 * st; i++)
            //    {
            //        // normals
            //        Vector3 n = new Vector3(0f, 0f, 0f);
            //
            //        if (j < sections)
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
            generateTriangles(sections, offset);
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
        
        //Gizmos.color = Color.blue;
        //for (int i = 0; i < vertices.Count; i++)
        //{
        //    Gizmos.DrawRay(vertices[i], normals[i] * normalGizmoSize);
        //}

        if (allSegments != null)
        {
            
            //Gizmos.color = new Color(1f, 1f, 0f);
            //foreach (Vector3 v in debugErrorPoints)
            //{
            //    Gizmos.DrawSphere(v, gizmoRadius * 2f);
            //}

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

    static Vector3 sampleSplineTangentC(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (3f * (1f - t) * (1f - t) * (controlB - controlA) + 6f * (1f - t) * t * (controlC - controlB) + 3f * t * t * (controlD - controlC));
        return norm(-3f * (1f - t) * (1f - t) * controlA + 3f * (3f * t * t - 4f * t + 1f) * controlB + 3f * (-3f * t * t + 2f * t) * controlC + 3f * t * t * controlD);
    }

    static Vector3 sampleSplineTangentT(Vector3 start, Vector3 end, Vector3 startTangent, Vector3 endTangent, float t)
    {
        Vector3 controlPt1 = start + startTangent * vLength(end - start) / 3f;
        Vector3 controlPt2 = end - endTangent * vLength(end - start) / 3f;

        return norm(-3f * (1f - t) * (1f - t) * start + 3f * (3f * t * t - 4f * t + 1f) * controlPt1 + 3f * (-3f * t * t + 2f * t) * controlPt2 + 3f * t * t * end);
    }

    static Vector3 sampleSplineCurvature(Vector3 controlA, Vector3 controlB, Vector3 controlC, Vector3 controlD, float t)
    {
        //return (6f * (1f - t) * (controlC - 2f * controlB + controlA) + 6f * t * (controlD - 2f * controlC + controlB));
        return (6f * (1f - t) * controlA + 3f * (6f * t - 4f) * controlB + 3f * (-6f * t + 2f) * controlC + 6f * t * controlD);
    }
}
