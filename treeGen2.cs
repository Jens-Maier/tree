using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class node 
{
    public Vector3 point;
    public Vector3 tangent;
    public Vector3 cotangent;
    public List<node> next;
    public node parent;
    public float crossSectionArea;
    public int branchLevel;
    public treeGen2 gen;
    public List<List<node>> children;

    public node(Vector3 Point, treeGen2 g, node par, int level)
    {
        point = Point;
        crossSectionArea = 0f;
        branchLevel = level;
        next = new List<node>();
        gen = g;
        parent = par;
        children = new List<List<node>>(); // one list for each node in next 

        if (float.IsNaN(Point.x))
        {
            Debug.Log("node constructor: point is NaN!");
        }
        //else
        //{
        //    Debug.Log("node constructor: point is OK!" + point);
        //}
    }

    public void grow(Quaternion dir, float length, Vector3 prevPoint)
    {
        if (next.Count > 0)
        {
            next[0].grow(dir, length, point);
        }
        else
        {
            Vector3 newPoint = point + norm(dir * (point - prevPoint)) * length;
            next.Add(new node(newPoint, gen, this, branchLevel));
            children.Add(new List<node>());
            next[0].tangent = norm(next[0].point - point);
            tangent = norm(next[0].point - prevPoint);

            //cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent))); // test off

            next[0].cotangent = norm(Vector3.Cross(next[0].tangent, Vector3.Cross(cotangent, next[0].tangent)));
        }
        // Vector3 rotatedVector = Quaternion.AngleAxis(angleDeg, axis) * vector;
    }

    //TODO: combine children with split !
    public void addChildren(int numberChildren)
    {
        if (next.Count > 0)
        {
            int[] rVals = new int[next.Count]; // random number of children for each branc (foreach node in next, for splits...)
            int maxR = 0;
            for (int c = 0; c < next.Count; c++)
            {
                if (numberChildren > 0)
                {
                    float p = (float)gen.randomNumbers[gen.randomNumberIndex] / (float)gen.randomArraySize; // 0-1
                    gen.randomNumberIndex = gen.randomNumberIndex + 1;
                    float p1 = (float)gen.randomNumbers[gen.randomNumberIndex] / (float)gen.randomArraySize; // 0-1
                    gen.randomNumberIndex = gen.randomNumberIndex + 1;

                    rVals[c] = (int)((float)numberChildren * p);
                    if (maxR < rVals[c])
                    {
                        maxR = rVals[c];
                    }
                    Debug.Log("crossSectionArea " + crossSectionArea); // OK
                    Debug.Log("root crossSectionArea " + gen.root.crossSectionArea); // OK
                    if (crossSectionArea > 0f)
                    {
                        rVals[c] = (int)((float)(rVals[c]) / (crossSectionArea / gen.root.crossSectionArea + 1f));
                    }
                }
            }

            Vector3[,] startPoints = new Vector3[next.Count, maxR]; //start points for all children of all branches in next[]

            gen.debugListBlue.Add(point);
            gen.debugListBlue.Add(next[0].point);
            for (int c = 0; c < next.Count; c++)
            {
                for (int i = 0; i < rVals[c]; i++)
                {
                    startPoints[c, i] = sampleSpline(point,
                                                      point + vLength(next[c].point - point) * norm(tangent) * (1f / 3f),
                                                      next[c].point - vLength(next[c].point - point) * norm(next[c].tangent) * (1f / 3f),
                                                      next[c].point, (float)(i + 1) / (float)(rVals[c] + 1));

                    if (i > 0)
                    {
                        float random01 = (float)gen.randomNumbers[gen.randomNumberIndex] / (float)gen.randomArraySize;
                        gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;

                        startPoints[c, i] = sampleSpline(point,
                                                      point + vLength(next[c].point - point) * norm(tangent) * (1f / 3f),
                                                      next[c].point - vLength(next[c].point - point) * norm(next[c].tangent) * (1f / 3f),
                                                      next[c].point, ((float)(i + 1) + (random01 - 0.5f) * gen.randomChildBranchStartPointOffset) / (float)(rVals[c] + 1));
                    }
                    gen.debugList.Add(startPoints[c, i]);
                    
                    float startPointCrossSectionArea = fLerp(crossSectionArea, next[c].crossSectionArea, (float)(i + 1) / (float)(rVals[c] + 1)) * gen.childBrachThicknessScaling;
                    gen.debugListRadius.Add(Mathf.Sqrt(startPointCrossSectionArea));
                }
            }

            for (int c = 0; c < next.Count; c++)
            {
                Vector3 parentDir = norm(next[c].point - point);
                                
                for (int i = 0; i < rVals[c]; i++)
                {
                    // TODO: orientation rel to root
                    // -> outward vector, left, right
                    Vector3 outward = norm(new Vector3(parentDir.x, 0f, parentDir.z));
                    Vector3 outwardAxis = norm(Vector3.Cross(parentDir, outward));
                    //gen.tangentDebugLines.Add(new line(startPoints[c, i], startPoints[c, i] + outward)); // ???

                    Vector3 dir = norm(Quaternion.AngleAxis(fLerp(gen.childSplitAngleDegBottom, gen.childSplitAngleDegTop, (float)i / (float)rVals[c]), cotangent) * norm(parentDir)); // TODO: ((cotangent)) -> random angle!

                    dir = norm(Quaternion.AngleAxis(gen.childScrewAngle * i, tangent) * dir);

                    node n = new node(startPoints[c, i], gen, this, branchLevel + 1);
                    
                    n.tangent = dir;
                    n.cotangent = norm(Vector3.Cross(n.tangent, Vector3.Cross(cotangent, n.tangent)));

                    Vector3 newPoint = startPoints[c, i] + dir * fLerp(gen.childBranchLengthBottom, gen.childBranchLengthTop, (float)i / (float)rVals[c]);
                    node nextNode = new node(newPoint, gen, n, branchLevel + 1);
                    nextNode.tangent = n.tangent + gen.childCurvature * vLength(startPoints[c, i] - newPoint) * new Vector3(0f, 1f, 0f) / 3f;
                    nextNode.point = nextNode.point + gen.childCurvature * vLength(startPoints[c, i] - newPoint) * new Vector3(0f, 1f, 0f);

                    nextNode.cotangent = n.cotangent;

                    n.next.Add(nextNode);
                    
                    children[c].Add(n);
                    if (gen.tangentDebugLines != null)
                    {
                        gen.tangentDebugLines.Add(new line(children[c][i].point, children[c][i].next[0].point));
                    }


                }
            }

            //foreach (node nextNode in next)
            //{
            //    nextNode.addChildren(numberChildren);
            //}
        }
    }

    // TODO: combine children with split !
    //
    //  TODO: levels -> base, beanches, ...
    public void split(float length, Vector3 branchDir, Vector3 localDir, Vector3 prevPoint, Vector3 splitAxis, float splitRotation, float splitAngleDegA, float splitAngleDegB, bool left, bool center, bool right)
    {
        if (next.Count > 0)
        {
            int n = 0;
            //int safetyLimit = 1000;
            //int c = 0;
            while (n < next.Count) // TODO: only split some (center) branch !!!  // TODO: -> random!  TODO: -> center branch on different "level" than right/left -> 
                                                                                                          // -> split again only on one level  -> random!
                                                                                                          // -> new variable "branch level" in node
                                                                                                          // left, right: parent.branchLevel + 1
                                                                                                          // center: parent.branchLevel
                                                                                                          // split(...branchLvl...) {if (branchLevel == branchLvl)
                                                                                                          //                         {   -> split ... }
            {
                // Random.Range(): float: min and max inclusive || int: min inclusive, max exclusive
                //float splitRotationVariation = 0f;

                //Debug.Log("random " + gen.splitRotationVariation[gen.randomIndex]);

                //Debug.Log("randomNumbers size: " + gen.randomNumbers.Length);
                //Debug.Log("random index: " + gen.randomNumbers[n]);
                //Debug.Log("splitRotVar size: " + gen.splitRotationVariation.Length);
                
                //Debug.Log("randomNumberIndex: " + gen.randomNumbers[n]);
                //Debug.Log("random variation: " + gen.splitRotationVariation[gen.randomNumbers[n]]);
                next[n].split(length, branchDir, norm(next[n].point - point), point, splitAxis, splitRotation + gen.splitRotationVariation[gen.randomNumbers[gen.randomNumberIndex]], splitAngleDegA, splitAngleDegB, left, center, right);
                
                gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
                gen.randomIndex = (gen.randomIndex + 1) % gen.randomArraySize;
                n += 1;
            }
        }
        else
        {
            //Vector3 globalDir = branchDir;

            // use splitOrientationAngle -> relative to cotangent!

            //int splitThickness = 0;

            //if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize * (1f - gen.splitProbability))
            //{
            //    left = true;
            //    right = true;
            //    center = false;
            //    //splitThickness = 2;
            //}
            //else
            //{
            //    left = false;
            //    right = false;
            //    center = true;
            //    //splitThickness = 1;
            //}
            //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;

            //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
            //if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize * (1f - gen.splitProbability))
            //{
            //    right = true;
            //    splitThickness += 1;
            //}
            //else
            //{
            //    right = false;
            //}
            //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
            //if (left == false || right == false || gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize * (1f - gen.splitProbability))
            //{
            //    center = true;
            //    splitThickness += 1;
            //}
            //else
            //{
            //center = false;// do not use center (TODO: remove option)
            //}

            // thickness ... -> in own methode calculateThickness after branch splitting done! OK

            if (branchLevel < 3)
            {
                splitAxis = Vector3.Cross(Vector3.Cross(tangent, new Vector3(0f, 1f, 0f)), new Vector3(0f, 1f, 0f));
                if (splitAxis != new Vector3(0f, 0f, 0f))
                {
                    splitAxis = norm(splitAxis);
                }
                else
                {
                    splitAxis = new Vector3(1f, 0f, 0f);
                }

                Vector3 splitAxisLeft = Quaternion.AngleAxis(splitRotation, tangent) * splitAxis;
                Vector3 splitAxisRight;
                if (branchLevel == 0)
                {
                    splitAxisRight = Quaternion.AngleAxis(splitRotation, tangent) * splitAxis;
                }
                else
                {
                    splitAxisRight = Quaternion.AngleAxis(-splitRotation, tangent) * splitAxis;
                }
                //splitAxis = Quaternion.AngleAxis(splitRotation, tangent) * cotangent; // test! (???)

                Vector3 dirA = Quaternion.AngleAxis(splitAngleDegA, splitAxisLeft) * norm(tangent);
                Vector3 dirB = Quaternion.AngleAxis(-splitAngleDegB, splitAxisRight) * norm(tangent);

                //if (left) gen.randomNumbers[gen.randomNumberIndex] // randomSplitVariationArraySize
                if (left)
                {
                    Vector3 newPointA = point + dirA * length;
                    node nodeA = new node(newPointA, gen, this, branchLevel + 1);
                    //nodeA.tangent = norm(dirA);
                    nodeA.tangent = norm(nodeA.point - (point + norm(dirA) * length));
                    next.Add(nodeA);
                    children.Add(new List<node>());
                }
                //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;
                //if (right)
                if (right)
                {
                    Vector3 newPointB = point + dirB * length;
                    node nodeB = new node(newPointB, gen, this, branchLevel + 1);
                    //nodeB.tangent = norm(dirB);


                    nodeB.tangent = norm(nodeB.point - (point + norm(dirB) * length));
                    next.Add(nodeB);
                    children.Add(new List<node>());
                }
                //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;

                // do not use center (TODO: remove option)

                if (center)
                //if (gen.randomNumbers[gen.randomNumberIndex] > gen.randomArraySize / 2)
                {
                    Vector3 newPointC = point + localDir * length * 2f;
                    node nodeC = new node(newPointC, gen, this, branchLevel);
                    nodeC.tangent = norm(localDir);
                    next.Add(nodeC);
                    children.Add(new List<node>());
                }

                //gen.randomNumberIndex = (gen.randomNumberIndex + 1) % gen.randomNumbers.Length;

                if (left && right)
                {
                    tangent = (norm((next[0].point - point)) + norm((next[1].point - point))) / 2f;
                }

                int c = 0;
                if (right)
                {
                    if (gen.tangentDebugLines != null)
                    {
                        gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset, next[c].point)); // OK
                    }
                    next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset)); // -> * splitTangentOffset instead of / 3f

                    //next[c].tangent = norm(next[c].point - point);
                    if (left == false)
                    {
                        tangent = norm(next[c].point - prevPoint);
                    }
                    cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                    next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));

                    c += 1;
                }
                if (left)
                {
                    //gen.tangentDebugLines.Add(new line(point, next[1].point)); // OK
                    if (gen.tangentDebugLines != null)
                    {
                        gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset, next[c].point)); // OK
                    }

                    next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset));

                    //next[c].tangent = norm(next[c].point - point);

                    if (right == false)
                    {
                        tangent = norm(next[c].point - prevPoint);
                    }

                    cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                    next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));

                    c += 1;
                }
                if (center)
                {
                    if (gen.tangentDebugLines != null)
                    {
                        gen.tangentDebugLines.Add(new line(point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset, next[c].point)); // OK
                    }

                    next[c].tangent = norm(next[c].point - (point + norm(tangent) * vLength(next[c].point - point) * gen.splitTangentOffset));

                    //next[c].tangent = norm(next[c].point - point);

                    tangent = norm(next[c].point - prevPoint);

                    cotangent = norm(Vector3.Cross(tangent, Vector3.Cross(parent.cotangent, tangent)));

                    next[c].cotangent = norm(Vector3.Cross(next[c].tangent, Vector3.Cross(cotangent, next[c].tangent)));
                }

                // TODO: offset points up in direction of parent branch -> account for curve!

                //points.Add(newPointA);
                //points.Add(newPointB);
            }
        }
    }


    public float calculateThickness()
    {
        if (next.Count > 0 || children.Count > 0)
        {
            float sum = 0f;
            if (next.Count > 0)
            {
                foreach (node n in next)
                {
                    sum += n.calculateThickness();
                    sum += vLength(n.point - point) * gen.taper;
                }
            }
            if (children.Count > 0)
            {
                foreach (List<node> c in children)
                {
                    foreach (node n in c)
                    {
                        sum += n.calculateThickness();
                    }
                }
            }
            crossSectionArea = sum;
            return sum;
        }
        else
        {
            crossSectionArea = 0f;
            return 0f;
        }
        //int splits = next.Count;
        //
        //if (splits > 0)
        //{
        //    float taper = Mathf.Sqrt(1f / (float)splits);
        //    Debug.Log("taper: " + taper);
        //
        //    foreach (node n in next)
        //    {
        //        n.radius = radius * taper;
        //        n.calculateThickness(n.radius);
        //    }
        //}

    }

    public void getAllSegments(List<segment> allSegments, int sections, int ringRes)
    {
        //Debug.Log("new next node");
        foreach (node n in next)
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
            allSegments.Add(new segment(point, n.point, tangent, n.tangent, cotangent, n.cotangent, sections, Mathf.Sqrt(crossSectionArea), Mathf.Sqrt(n.crossSectionArea), ringRes, gen));
            n.getAllSegments(allSegments, sections, ringRes);
        }

        foreach (List<node> l in children)
        {
            foreach (node c in l)
            {
                c.getAllSegments(allSegments, sections, ringRes);
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
    public List<Vector2> UVs;
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
        UVs = new List<Vector2>();
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

    [Range(0f, 0.01f)]
    public float taper;

    public int levels; // -> children in node
    [Range(0, 40)]
    public int numberChildren;
    //[Range(0f, 1f)]
    public float childDistribution;
    public float childBrachThicknessScaling;
    [Range(-1f, 1f)]
    public float randomChildBranchStartPointOffset;
    public float childSplitAngleDegBottom;
    public float childSplitAngleDegTop;

    public float childBranchLengthBottom;
    public float childBranchLengthTop;

    public float childCurvature;

    public float childScrewAngle;

    [Range(1, 6)]
    public int maxNumberSplits;
    public List<float> splitAngleDegA;
    public List<float> splitAngleDegB;
    public List<float> splitRotation;

    public float splitLength;
    [Range(0f, (1f/3f))]
    public float splitTangentOffset;

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
    public List<float> debugListRadius;
    public List<Vector3> debugListRed;
    public List<Vector3> debugListGreen;
    public List<Vector3> debugListBlue;

    //public float radius;
    [Range(1, 10)]
    public int sections;
    [Range(2, 10)]
    public int stemRingResolution;

    public List<Vector3> vertices;
    public List<int> triangles;
    public List<Vector3> normals;
    public List<Vector2> UVs;

    public Mesh mesh;
    public MeshFilter meshFilter;

    public bool drawGizmos;
    public bool drawChildGizmos;
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
        debugListRadius = new List<float>();
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
            for (int i = 0; i < maxNumberSplits; i++)
            {
                splitRotation.Add(40f);
            }
        }
        else
        {
            if (splitRotation.Count < maxNumberSplits)
            {
                int count = splitRotation.Count;
                for (int i = 0; i < maxNumberSplits - count; i++)
                {
                    splitRotation.Add(40f);
                }
            }
        }
        if (splitAngleDegA == null)
        {
            splitAngleDegA = new List<float>();
            for (int i = 0; i < maxNumberSplits; i++)
            {
                splitAngleDegA.Add(50f);
            }
        }
        else
        {
            if (splitAngleDegA.Count < maxNumberSplits)
            {
                int count = splitAngleDegA.Count;
                for (int i = 0; i < maxNumberSplits - count; i++)
                {
                    splitAngleDegA.Add(50f);
                }
            }
        }

        if (splitAngleDegB == null)
        {
            splitAngleDegB = new List<float>();
            for (int i = 0; i < maxNumberSplits; i++)
            {
                splitAngleDegB.Add(50f);
            }
        }
        else
        {
            if (splitAngleDegB.Count < maxNumberSplits)
            {
                int count = splitAngleDegB.Count;
                for (int i = 0; i < maxNumberSplits - count; i++)
                {
                    splitAngleDegB.Add(50f);
                }
            }
        }

        tangentDebugLines = new List<line>();
        dirAdebugLines = new List<line>();
        dirBdebugLines = new List<line>();

        vertices = new List<Vector3>();
        triangles = new List<int>();
        normals = new List<Vector3>();
        UVs = new List<Vector2>();

        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();
    }


    // Update is called once per frame
    void Update()
    {
        randomIndex = 0;
        randomNumberIndex = 0;
        debugList.Clear();
        debugListRadius.Clear();
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
    
        if (splitAngleDegA.Count < maxNumberSplits)
        {
            int count = splitAngleDegA.Count;
            for (int i = 0; i < maxNumberSplits - count; i++)
            {
                splitAngleDegA.Add(40f);
            }
        }
    
        if (splitAngleDegB.Count < maxNumberSplits)
        {
            int count = splitAngleDegB.Count;
            for (int i = 0; i < maxNumberSplits - count; i++)
            {
                splitAngleDegB.Add(40f);
            }
        }
    
        if (splitRotation.Count < maxNumberSplits)
        {
            int count = splitRotation.Count;
            for (int i = 0; i < maxNumberSplits - count; i++)
            {
                splitRotation.Add(40f);
            }
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
    
        root = new node(new Vector3(0f, 0f, 0f), this, null, 0);
        root.next.Add(new node(norm(treeGrowDir) * treeHeight / 2f, this, root, 0)); // TODO: remove radius option -> is calculated!
        root.children.Add(new List<node>());
        root.tangent = norm(root.next[0].point - root.point);
        root.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(1f, 0f, 0f)));
        if (root.cotangent == new Vector3(0f, 0f, 0f))
        {
            root.cotangent = norm(Vector3.Cross(treeGrowDir, new Vector3(0f, 0f, 1f)));
        }
        root.next[0].tangent = norm(root.next[0].point - root.point);
        root.next[0].cotangent = norm(Vector3.Cross(root.next[0].tangent, Vector3.Cross(root.cotangent, root.next[0].tangent)));

        root.grow(Quaternion.identity, treeHeight / 2f, root.next[0].point);


        //root.grow(Quaternion.AngleAxis(0f, new Vector3(1f, 0f, 0f)), growLength, root.next[0].point);
        //root.grow(Quaternion.AngleAxis(0f, new Vector3(0f, 0f, 1f)), growLength, root.next[0].point);
        //root.grow(Quaternion.AngleAxis(0f, new Vector3(0f, 0f, 1f)), growLength, root.next[0].point);
        root.calculateThickness();


        // TODO: combine children with split !

        // root.split(splitLength * 0.7f, p - rp, p - rp, rp, new Vector3(1f, 0f, 0f), sr, saA, saB, true, true, true);
        // //
        root.next[0].addChildren(numberChildren);

        foreach (List<node> l in root.next[0].children) // TEST! ... // TODO!
        {
            foreach (node c in l)
            {
                c.split(splitLength * 0.7f, root.next[0].point - root.point, root.next[0].point - root.point, root.point, new Vector3(1f, 0f, 0f), splitRotation[1], splitAngleDegA[1], splitAngleDegB[1], false, true, true);
                c.split(splitLength * 1.3f, root.next[0].point - root.point, root.next[0].point - root.point, root.point, new Vector3(0f, 0f, 1f), splitRotation[2], splitAngleDegA[2], splitAngleDegB[2], false, true, true);
                c.split(splitLength * 0.7f, root.next[0].point - root.point, root.next[0].point - root.point, root.point, new Vector3(1f, 0f, 0f), splitRotation[3], splitAngleDegA[3], splitAngleDegB[3], false, true, true);
                c.split(splitLength * 0.7f, root.next[0].point - root.point, root.next[0].point - root.point, root.point, new Vector3(1f, 0f, 0f), splitRotation[3], splitAngleDegA[3], splitAngleDegB[3], true, false, true);
                c.split(splitLength * 0.7f, root.next[0].point - root.point, root.next[0].point - root.point, root.point, new Vector3(1f, 0f, 0f), splitRotation[3], splitAngleDegA[3], splitAngleDegB[3], false, true, true);
            }
        }
        // TODO: uneven crossSectionAreaSplitting! -> at childPoints!

        //for (int i = 0; i < maxNumberSplits; i++)
        //{
        //    root.split(splitLength * 0.7f, root.next[0].point - root.point, root.next[0].point - root.point, root.next[0].next[0].crossSectionArea, root.point, new Vector3(1f, 0f, 0f), splitRotation[i], splitAngleDegA[i], splitAngleDegB[i], true, false, true);
        //}

        root.calculateThickness();

        if (allSegments != null)
        {
            allSegments.Clear();
            allSegments = getAllSegments(sections);
        }
        //Debug.Log("allSegments Count: " + allSegments.Count);
    
        vertices.Clear();
        triangles.Clear();
        normals.Clear();
        UVs.Clear();
        foreach (segment s in allSegments)
        {
            //debugList.Add(s.start);
            //debugList.Add(s.end);
    
            vertices.AddRange(s.vertices);
            UVs.AddRange(s.UVs);
        }
        generateAllVerticesAndTriangles();
    
        //debugLines.Clear();
        //foreach (segment v in allSegments)
        //{
        //    debugLines.Add(new line(v.start, v.end));
        //}
    
        mesh.Clear(false);
        mesh.SetVertices(vertices);
        mesh.SetUVs(0, UVs);
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

        //Vector3 globalDir = norm(root.next[0].point - root.point);
        
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
            //debugListRed.Add(allSegments[s].start);
            //debugListRed.Add(allSegments[s].end);

            tangentDebugLines.Add(new line(allSegments[s].start, controlPt1));
            tangentDebugLines.Add(new line(allSegments[s].end, controlPt2));

            //debugListBlue.Add(controlPt1);
            //debugListBlue.Add(controlPt2);

            float arcLength = 0f;

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                if (float.IsNaN(allSegments[s].start.x))
                {
                    Debug.Log("ERROR allSegments[s].start is NaN!");
                }

                pos[j] = sampleSpline(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections);
                if (float.IsNaN(pos[j].x))
                {
                    Debug.Log("ERROR pos[j] is NaN!");
                }

                debugListGreen.Add(pos[j]);

                if (j > 0)
                {
                    arcLength += vLength(pos[j] - pos[j - 1]);
                }

                tangent[j] = norm(sampleSplineTangent(allSegments[s].start, controlPt1, controlPt2, allSegments[s].end, (float)j / (float)allSegments[s].sections));

                if (float.IsNaN(allSegments[s].start.x))
                {
                    Debug.Log("ERROR allSegments[s].start is NaN!");
                }
                //else
                //{
                //    Debug.Log("allSegments[s].start " + allSegments[s].start); // zero vector!
                //}

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

                for (int i = 0; i <= 2 * stemRingResolution; i++)
                {
                    float angle = (Mathf.PI / (float)allSegments[s].stemRingResolution) * (float)i;

                    if (float.IsNaN(tangent[j].x))
                    {
                        Debug.Log("ERROR tangent is NaN!"); // ERROR HERE !!!
                    }
                    if (float.IsNaN(pos[j].x))
                    {
                        Debug.Log("ERROR pos[j] is NaN!"); // ERROR HERE !!!
                    }
                    if (float.IsNaN(allSegments[s].startCotangent.x))
                    {
                        Debug.Log("ERROR allSegments[s].startCotangent is NaN!"); // OK
                    }
                    if (float.IsNaN(allSegments[s].endCotangent.x))
                    {
                        Debug.Log("ERROR allSegments[s].endCotangent is NaN!"); // OK
                    }
                    if (float.IsNaN(dirA[j].x)) // ERROR HERE !!!
                    {
                        Debug.Log("ERROR dirA[j] is NaN!");
                    }
                    if (float.IsNaN(dirB[j].x)) // ERROR HERE !!!
                    {
                        Debug.Log("ERROR dirB[j] is NaN!");
                    }
                    if (float.IsNaN(allSegments[s].startRadius))
                    {
                        Debug.Log("ERROR allSegments[s].startRadius is NaN!");
                    }
                    if (float.IsNaN(allSegments[s].endRadius))
                    {
                        Debug.Log("ERROR allSegments[s].endRadius is NaN!");
                    }
                    float f = (float)j / (float)(length / ringSpacing) * Mathf.Cos(angle) + fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing));
                    if (float.IsNaN(f))
                    {
                        Debug.Log("ERROR (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) + dirB[j] * fLerp(allSegments[s].startRadius is NaN!");
                    }
                    if (float.IsNaN((float)j / (float)(length / ringSpacing) * Mathf.Sin(angle)))
                    {
                        Debug.Log("(float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle) is NaN!");
                    }
                    if (float.IsNaN(angle))
                    {
                        Debug.Log("ERROR angle is NaN!");
                    }
                    if (float.IsNaN(arcLength))
                    {
                        Debug.Log("ERROR arcLength is NaN!");
                    }
                    
                    Vector3 v = pos[j] + dirA[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Cos(angle) +
                                dirB[j] * fLerp(allSegments[s].startRadius, allSegments[s].endRadius, (float)j / (float)(length / ringSpacing)) * Mathf.Sin(angle);

                    if (float.IsNaN(v.x)) // ERROR HERE !!!
                    {
                        Debug.Log("ERROR v is NaN!");
                    }
                    Vector2 uv = new Vector2(angle / (2f * Mathf.PI), arcLength);
                    if (i == 2 * stemRingResolution)
                    {
                        uv.x = 1f;
                    }
                    if (float.IsNaN(v.x))
                    {
                        Debug.Log("ERROR v is NaN!");
                    }
                    vertices.Add(v);
                    UVs.Add(uv);

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
                    // TODO: total arclength of segment -> divide by n so scale is even
                    // -> arclength offset for each section
                    //
                    //
                    //
                    //
                    //
                    //
                    //
                    //
                    //


                    counter += 1;
                }
            }

            int st = stemRingResolution;

            for (int j = 0; j < allSegments[s].sections + 1; j++)
            {
                for (int i = 0; i <= 2 * st; i++)
                {
                    // normals
                    Vector3 n;
                    if (j < allSegments[s].sections)
                    {
                        n = norm(Vector3.Cross(vertices[j * (2 * st + 1) + (i + 1) % (2 * st + 1)] - vertices[j * (2 * st + 1) + i],
                                               vertices[(j + 1) * (2 * st + 1) + i]                - vertices[j * (2 * st + 1) + i]) + //  |_

                                 Vector3.Cross(vertices[(j + 1) * (2 * st + 1) + i]                             - vertices[j * (2 * st + 1) + i],
                                               vertices[j * (2 * st + 1) + (i - 1 + 2 * st + 1) % (2 * st + 1)] - vertices[j * (2 * st + 1) + i]));  //  _|
                    }
                    else
                    {
                        n = norm(Vector3.Cross(vertices[(j - 1) * (2 * st + 1) + i]                - vertices[j * (2 * st + 1) + i],
                                               vertices[j * (2 * st + 1) + (i + 1) % (2 * st + 1)] - vertices[j * (2 * st + 1) + i]) +  //  |-

                                 Vector3.Cross(vertices[j * (2 * st + 1) + (i - 1 + 2 * st + 1) % (2 * st + 1)] - vertices[j * (2 * st + 1) + i],
                                               vertices[(j - 1) * (2 * st + 1) + i]                             - vertices[j * (2 * st + 1) + i]));  //  -|
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
        if (drawChildGizmos)
        {
            Gizmos.color = Color.red;
            if (debugList != null)
            {
                //if (debugList.Count > 0)
                //{
                //    Debug.Log("debugList count: " + debugList.Count);
                //}
                for (int i = 0; i < debugList.Count; i++)
                {
                    Gizmos.DrawSphere(debugList[i], debugListRadius[i]);
                }

                //foreach (Vector3 v in vertices)
                //{
                //    Gizmos.DrawSphere(v, 0.02f);
                //}
            }
        }

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
                    Gizmos.DrawSphere(v, 0.05f);
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
