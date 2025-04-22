using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
//using System.Collections.Generic;
//using Random = System.Random;
using UnityEditor;
using System.IO;
using Random = System.Random;

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

[CustomEditor(typeof(treeGen3))]
public class treeGen3Editor : Editor
{
    //public json treeData; // TODO: use json! (do not use scriptableObject to store data (scriptableObjects are read only!)

    static float gizmoRadius;
    static float setGizmoRadius;
    static float treeHeight;
    public static float setTreeHeight;
    static Vector3 treeGrowDir;
    public static Vector3 setTreeGrowDir;
    static int treeShape;
    public static shape setTreeShape;
    static float taper;
    public static float setTaper;
    static float branchTipRadius;
    public static float setBranchTipRadius;
    static float ringSpacing;
    public static float setRingSpacing;
    static int stemRingResolution;
    public static int setStemRingResolution;
    static int resampleNr;
    public static int setResampleNr;
    static float noiseAmplitudeLower;
    public static float setNoiseAmplitudeLower;
    static float noiseAmplitudeUpper;
    public static float setNoiseAmplitudeUpper;
    static float noiseAmplitudeLowerUpperExponent;
    public static float setNoiseAmplitudeLowerUpperExponent;
    static float noiseScale;
    public static float setNoiseScale;
    static float splitCurvature;
    public static float setSplitCurvature;
    static int testRecursionStop;
    public static int setTestRecursionStop;
    static int nrSplits;
    public static int setNrSplits;
    static float variance;
    public static float setVariance;
    static float curvOffsetStrength;
    public static float setCurvOffsetStrength;
    static List<float> splitHeightInLevel;
    public static List<float> setSplitHeightInLevel;
    static float splitHeightVariation;
    public static float setSplitHeightVariation;
    static float testSplitAngle;
    public static float setTestSplitAngle;
    static float testSplitPointAngle;
    public static float setTestSplitPointAngle;

    static int childLevels;
    public static int setChildLevels;

    static List<int> nrChildren;
    public static List<int> setNrChildren;
    static List<float> relChildLength;
    public static List<float> setRelChildLength;
    static List<float> verticalRange;
    public static List<float> setVerticalRange;
    static List<float> verticalAngleCrownStart;
    public static List<float> setVerticalAngleCrownStart;
    static List<float> verticalAngleCrownEnd;
    public static List<float> setVerticalAngleCrownEnd;
    static List<float> rotateAngle;
    public static List<float> setRotateAngle;
    static List<int> childrenStartLevel;
    public static List<int> setChildrenStartLevel;
    static List<float> childCurvature;
    public static List<float> setChildCurvature;
    static List<int> nrChildSplits;
    public static List<int> setNrChildSplits;

    static int seed;
    public static int setSeed;
    public Random random;
    public static bool setRandomize;

    

    private SerializedProperty myFloatField;

    public treeData data;

    public string jsonString;
    public string loadFileName = "";
    public string saveFileName = "";

    private void OnEnable()
    {
        // myFloatField = serializedObject.FindProperty("treeHeight"); // TODO: serializedObject ... (s. chatgtp...)
        random = new Random(64345);
    }


    public override void OnInspectorGUI()
    {
        treeGen3 treeGenScript = (treeGen3)target;

        
        loadFileName = EditorGUILayout.TextField("loadFile", loadFileName);

        if (GUILayout.Button("load Tree"))
        {
            Debug.Log("loadFileName: " + loadFileName);
            string path = "Assets/Resources/" + loadFileName + ".json";
            StreamReader reader = new StreamReader(path);
            jsonString = reader.ReadToEnd();
            Debug.Log("read string: " + jsonString);
            data = JsonUtility.FromJson<treeData>(jsonString);
            Debug.Log("data: treeHeight: " + data.treeHeight);

            treeHeight = data.treeHeight;
            setTreeHeight = data.treeHeight;
            treeGenScript.treeHeight = data.treeHeight;

            treeGrowDir = data.treeGrowDir;
            setTreeGrowDir = data.treeGrowDir;
            treeGenScript.treeGrowDir = data.treeGrowDir;

            treeShape = data.treeShape;
            setTreeShape = (shape)data.treeShape;
            treeGenScript.setTreeShape(data.treeShape);
            

            taper = data.taper;
            setTaper = data.taper;
            treeGenScript.taper = data.taper;

            branchTipRadius = data.branchTipRadius;
            setBranchTipRadius = data.branchTipRadius;
            treeGenScript.branchTipRadius = data.branchTipRadius;

            ringSpacing = data.ringSpacing;
            setRingSpacing = data.ringSpacing;
            treeGenScript.ringSpacing = data.ringSpacing;
            
            stemRingResolution = data.stemRingResolution;
            setStemRingResolution = data.stemRingResolution;
            treeGenScript.stemRingResolution = data.stemRingResolution;

            resampleNr = data.resampleNr;
            setResampleNr = data.resampleNr;
            treeGenScript.resampleNr = data.resampleNr;

            noiseAmplitudeLower = data.noiseAmplitudeLower;
            setNoiseAmplitudeLower = data.noiseAmplitudeLower;
            treeGenScript.noiseAmplitudeLower = data.noiseAmplitudeLower;

            noiseAmplitudeUpper = data.noiseAmplitudeUpper;
            setNoiseAmplitudeUpper = data.noiseAmplitudeUpper;
            treeGenScript.noiseAmplitudeUpper = data.noiseAmplitudeUpper;

            noiseAmplitudeLowerUpperExponent = data.noiseAmplitudeLowerUpperExponent;
            setNoiseAmplitudeLowerUpperExponent = data.noiseAmplitudeLowerUpperExponent;
            treeGenScript.noiseAmplitudeLowerUpperExponent = data.noiseAmplitudeLowerUpperExponent;

            noiseScale = data.noiseScale;
            setNoiseScale = data.noiseScale;
            treeGenScript.noiseScale = data.noiseScale;

            splitCurvature = data.splitCurvature;
            setSplitCurvature = data.splitCurvature;
            treeGenScript.splitCurvature = data.splitCurvature;

            testRecursionStop = data.testRecursionStop;
            setTestRecursionStop = data.testRecursionStop;
            treeGenScript.testRecursionStop = data.testRecursionStop;

            nrSplits = data.nrSplits;
            setNrSplits = data.nrSplits;
            treeGenScript.nrSplits = data.nrSplits;

            variance = data.variance;
            setVariance = data.variance;
            treeGenScript.variance = data.variance;

            curvOffsetStrength = data.curvOffsetStrength;
            setCurvOffsetStrength = data.curvOffsetStrength;
            treeGenScript.curvOffsetStrength = data.curvOffsetStrength;

            splitHeightInLevel = data.splitHeightInLevel;
            setSplitHeightInLevel = data.splitHeightInLevel;
            treeGenScript.splitHeightInLevel = data.splitHeightInLevel;

            splitHeightVariation = data.splitHeightVariation;
            setSplitHeightVariation = data.splitHeightVariation;
            treeGenScript.splitHeightVariation = data.splitHeightVariation;

            testSplitAngle = data.testSplitAngle;
            setTestSplitAngle = data.testSplitAngle;
            treeGenScript.testSplitAngle = data.testSplitAngle;

            testSplitPointAngle = data.testSplitPointAngle;
            setTestSplitPointAngle = data.testSplitPointAngle;
            treeGenScript.testSplitPointAngle = data.testSplitPointAngle;

            nrChildren = data.nrChildren;
            setNrChildren = data.nrChildren;
            treeGenScript.nrChildren = data.nrChildren;

            relChildLength = data.relChildLength;
            setRelChildLength = data.relChildLength;
            treeGenScript.relChildLength = data.relChildLength;

            verticalRange = data.verticalRange;
            setVerticalRange = data.verticalRange;
            treeGenScript.verticalRange = data.verticalRange;

            verticalAngleCrownStart = data.verticalAngleCrownStart;
            setVerticalAngleCrownStart = data.verticalAngleCrownStart;
            treeGenScript.verticalAngleCrownStart = data.verticalAngleCrownStart;

            verticalAngleCrownEnd = data.verticalAngleCrownEnd;
            setVerticalAngleCrownEnd = data.verticalAngleCrownEnd;
            treeGenScript.verticalAngleCrownEnd = data.verticalAngleCrownEnd;

            rotateAngle = data.rotateAngle;
            setRotateAngle = data.rotateAngle;
            treeGenScript.rotateAngle = data.rotateAngle;

            childrenStartLevel = data.childrenStartLevel;
            setChildrenStartLevel = data.childrenStartLevel;
            treeGenScript.childrenStartLevel = data.childrenStartLevel;

            childCurvature = data.childCurvature;
            setChildCurvature = data.childCurvature;
            treeGenScript.childCurvature = data.childCurvature;

            nrChildSplits = data.nrChildSplits;
            setNrChildSplits = data.nrChildSplits;
            treeGenScript.nrChildSplits = data.nrChildSplits;

            seed = data.seed;
            setSeed = data.seed;
            treeGenScript.seed = data.seed;



            treeGenScript.initTree();
            treeGenScript.updateTree();
        }

       
        saveFileName = EditorGUILayout.TextField("saveAs", saveFileName);

        

        if (GUILayout.Button("save Tree parameters"))
        {
            //data = new treeData();
            //data.treeHeight = treeHeight;

            jsonString = JsonUtility.ToJson(data);

            Debug.Log("myString: " + jsonString);
            Debug.Log("saveFileName: " + saveFileName);

            if (saveFileName != "")
            {
                string path = "Assets/Resources/" + saveFileName + ".json";
                StreamWriter writer = new StreamWriter(path, true);
                writer.Write(jsonString);
                writer.Close();
                Debug.Log("file saved as " + saveFileName + ".json");
            }
        }

        setGizmoRadius = EditorGUILayout.FloatField("gizmoRadius", setGizmoRadius);

        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("tree parameters");
        EditorGUILayout.Space();
        
        if (setTreeHeight == 0f)
        {
            setTreeHeight = 1f;
        }

        setTreeHeight = EditorGUILayout.FloatField("treeHeight", setTreeHeight);
        if (treeGrowDir == new Vector3(0f, 0f, 0f))
        {
            treeGrowDir = new Vector3(0f, 1f, 0f);
        }
        setTreeGrowDir = EditorGUILayout.Vector3Field("treeGrowDir", setTreeGrowDir);
        setTreeShape = (shape)EditorGUILayout.EnumPopup("treeShape", setTreeShape);
        setTaper = EditorGUILayout.FloatField("taper", setTaper);
        setBranchTipRadius = EditorGUILayout.FloatField("branchTipRadius", setBranchTipRadius);
        setRingSpacing = EditorGUILayout.FloatField("ringSpacing", setRingSpacing);
        setStemRingResolution = EditorGUILayout.IntField("stemRingResolution", setStemRingResolution);
        setResampleNr = EditorGUILayout.IntField("resampleNr", setResampleNr);
        
        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("noise settings");
        EditorGUILayout.Space();
        setNoiseAmplitudeLower = EditorGUILayout.FloatField("noiseAmplitudeLower", setNoiseAmplitudeLower);
        setNoiseAmplitudeUpper = EditorGUILayout.FloatField("noiseAmplitudeUpper", setNoiseAmplitudeUpper);
        setNoiseAmplitudeLowerUpperExponent = EditorGUILayout.FloatField("noiseAmplitudeLowerUpperExponent", setNoiseAmplitudeLowerUpperExponent);
        setNoiseScale = EditorGUILayout.FloatField("noiseScale", setNoiseScale);
        EditorGUILayout.Space();
        
        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("split settings");
        EditorGUILayout.Space();
        setNrSplits = EditorGUILayout.IntField("nrSplits", setNrSplits);
        setSplitCurvature = EditorGUILayout.FloatField("splitCurvature", setSplitCurvature);
        setTestRecursionStop = EditorGUILayout.IntField("testRecursionStop", setTestRecursionStop);
        setVariance = EditorGUILayout.FloatField("variance", setVariance);
        setCurvOffsetStrength = EditorGUILayout.FloatField("curvOffsetStrength", setCurvOffsetStrength);
        if (setSplitHeightInLevel == null)
        {
            setSplitHeightInLevel = new List<float>();
            //setSplitHeightInLevel.Add(0.5f);
        }
        int displayMax = setSplitHeightInLevel.Count < 10 ? setSplitHeightInLevel.Count : 10;
        for (int i = 0; i < displayMax; i++)
        {
            setSplitHeightInLevel[i] = EditorGUILayout.FloatField("splitHeightInLevel " + i, setSplitHeightInLevel[i]);
        }
        if (setSplitHeightInLevel.Count < 10)
        {
            if (GUILayout.Button("add split Level"))
            {
                setSplitHeightInLevel.Add(0.5f);
            }
        }

        setSplitHeightVariation = EditorGUILayout.FloatField("splitHeightVariation", setSplitHeightVariation);
        setTestSplitAngle = EditorGUILayout.FloatField("testSplitAngle", setTestSplitAngle);
        setTestSplitPointAngle = EditorGUILayout.FloatField("testSplitPointAngle", setTestSplitPointAngle);

        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("child settings");
        EditorGUILayout.Space();
        if (GUILayout.Button("add child Level"))
        {
            setChildLevels += 1;
            if (setNrChildren == null)
            {
                setNrChildren = new List<int>();
            }
            setNrChildren.Add(0);
            if (setRelChildLength == null)
            {
                setRelChildLength = new List<float>();
            }
            setRelChildLength.Add(1f);
            if (setVerticalRange == null)
            {
                setVerticalRange = new List<float>();
            }
            setVerticalRange.Add(0f);
            if (setVerticalAngleCrownStart == null)
            {
                setVerticalAngleCrownStart = new List<float>();
            }
            setVerticalAngleCrownStart.Add(0.5f);
            if (setVerticalAngleCrownEnd == null)
            {
                setVerticalAngleCrownEnd = new List<float>();
            }
            setVerticalAngleCrownEnd.Add(1f);
            if (setRotateAngle == null)
            {
                setRotateAngle = new List<float>();
            }
            setRotateAngle.Add(0f);
            if (setChildrenStartLevel == null)
            {
                setChildrenStartLevel = new List<int>();
            }
            setChildrenStartLevel.Add(0);
            if (setChildCurvature == null)
            {
                setChildCurvature = new List<float>();
            }
            setChildCurvature.Add(0f);
            if (setNrChildSplits == null)
            {
                setNrChildSplits = new List<int>();
            }
            setNrChildSplits.Add(0);
        }
        if (GUILayout.Button("remove child Level"))
        {
            if (setChildLevels > 0)
            {
                if (setNrChildren.Count > 0)
                {
                    setChildLevels -= 1;
                    setNrChildren.RemoveAt(setNrChildren.Count - 1);
                    setRelChildLength.RemoveAt(setRelChildLength.Count - 1);
                    setVerticalRange.RemoveAt(setVerticalRange.Count - 1);
                    setVerticalAngleCrownStart.RemoveAt(setVerticalAngleCrownStart.Count - 1);
                    setVerticalAngleCrownEnd.RemoveAt(setVerticalAngleCrownEnd.Count - 1);
                    setRotateAngle.RemoveAt(setRotateAngle.Count - 1);
                    setChildrenStartLevel.RemoveAt(setChildrenStartLevel.Count - 1);
                    setChildCurvature.RemoveAt(setChildCurvature.Count - 1);
                    setNrChildSplits.Remove(setNrChildSplits.Count - 1);
                }
                else
                {
                    Debug.Log("ERROR! nr child levels incorrect!");
                }
            }

        }
        //if (setChildLevels < 1)
        //{
        //    setChildLevels = 1;
        //    if (setNrChildren.Count < 1)
        //    {
        //        setNrChildren.Add(0);
        //        setRelChildLength.Add(1f);
        //        setVerticalRange.Add(0f);
        //        setVerticalAngleCrownStart.Add(0.5f);
        //        setVerticalAngleCrownEnd.Add(1f);
        //        setRotateAngle.Add(0f);
        //        setChildrenStartLevel.Add(0);
        //        setChildCurvature.Add(0f);
        //        setNrChildSplits.Add(0);
        //    }
        //}

        if (setNrChildren != null)
        {
            if (setNrChildren.Count == setChildLevels)
            {
                for (int i = 0; i < setChildLevels; i++)
                {
                    EditorGUILayout.LabelField("child level " + i);
                    setNrChildren[i] = EditorGUILayout.IntField("nrChildren", setNrChildren[i]);
                    setRelChildLength[i] = EditorGUILayout.FloatField("relChildLength", setRelChildLength[i]);
                    setVerticalRange[i] = EditorGUILayout.FloatField("verticalRange", setVerticalRange[i]);
                    setVerticalAngleCrownStart[i] = EditorGUILayout.FloatField("verticalAngleCrownStart", setVerticalAngleCrownStart[i]);
                    setVerticalAngleCrownEnd[i] = EditorGUILayout.FloatField("verticalAngleCrownEnd", setVerticalAngleCrownEnd[i]);
                    setRotateAngle[i] = EditorGUILayout.FloatField("rotateAngle", setRotateAngle[i]);
                    setChildrenStartLevel[i] = EditorGUILayout.IntField("childrenStartLevel", setChildrenStartLevel[i]);
                    setChildCurvature[i] = EditorGUILayout.FloatField("childCurvature", setChildCurvature[i]);
                    setNrChildSplits[i] = EditorGUILayout.IntField("nrChildSplits", setNrChildSplits[i]);
                    EditorGUILayout.Space();
                }
            }
            else
            {
                Debug.Log("ERROR! setChildLevels: " + setChildLevels + ", setNrChildrenCount: " + setNrChildren.Count);
            }
        }

        
        
        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        setRandomize = EditorGUILayout.Toggle("randomizeSeed", setRandomize);
        setSeed = EditorGUILayout.IntField("seed", setSeed);        

        if (GUILayout.Button("set Tree parameters"))
        {
            if (setRandomize == true)
            {
                //setSeed += 1;
                setSeed = random.Next();
                seed = setSeed;
                treeGenScript.seed = setSeed;
                data.seed = setSeed;
            }

            data = new treeData();

            Debug.Log("set tree parameters...");

            
            treeGenScript.gizmoRadius = setGizmoRadius;


            // treeHeight = EditorGUILayout.FloatField("treeHeight", treeHeight);
            treeHeight = setTreeHeight;
            treeGenScript.treeHeight = setTreeHeight;
            data.treeHeight = setTreeHeight;

            treeGrowDir = setTreeGrowDir;
            treeGenScript.treeGrowDir = setTreeGrowDir;
            data.treeGrowDir = setTreeGrowDir;

            treeShape = (int)setTreeShape;
            treeGenScript.setTreeShape(treeShape);
            data.treeShape = (int)setTreeShape;
            
            taper = setTaper;
            treeGenScript.taper = setTaper;
            data.taper = setTaper;
            
            branchTipRadius = setBranchTipRadius;
            treeGenScript.branchTipRadius = setBranchTipRadius;
            data.branchTipRadius = setBranchTipRadius;
            
            ringSpacing = setRingSpacing;
            treeGenScript.ringSpacing = setRingSpacing;
            data.ringSpacing = setRingSpacing;

            stemRingResolution = setStemRingResolution;
            treeGenScript.stemRingResolution = setStemRingResolution;
            data.stemRingResolution = setStemRingResolution;
            
            resampleNr = setResampleNr;
            treeGenScript.resampleNr = setResampleNr;
            data.resampleNr = setResampleNr;

            noiseAmplitudeLower = setNoiseAmplitudeLower;
            treeGenScript.noiseAmplitudeLower = setNoiseAmplitudeLower;
            data.noiseAmplitudeLower = setNoiseAmplitudeLower;

            noiseAmplitudeUpper = setNoiseAmplitudeUpper;
            treeGenScript.noiseAmplitudeUpper = setNoiseAmplitudeUpper;
            data.noiseAmplitudeUpper = setNoiseAmplitudeUpper;
            
            noiseAmplitudeLowerUpperExponent = setNoiseAmplitudeLowerUpperExponent;
            treeGenScript.noiseAmplitudeLowerUpperExponent = setNoiseAmplitudeLowerUpperExponent;
            data.noiseAmplitudeLowerUpperExponent = setNoiseAmplitudeLowerUpperExponent;
            
            noiseScale = setNoiseScale;
            treeGenScript.noiseScale = setNoiseScale;
            data.noiseScale = setNoiseScale;
            
            splitCurvature = setSplitCurvature;
            treeGenScript.splitCurvature = setSplitCurvature;
            data.splitCurvature = setSplitCurvature;
            
            testRecursionStop = setTestRecursionStop;
            treeGenScript.testRecursionStop = setTestRecursionStop;
            data.testRecursionStop = setTestRecursionStop;
            
            nrSplits = setNrSplits;
            treeGenScript.nrSplits = setNrSplits;
            data.nrSplits = setNrSplits;
            
            variance = setVariance;
            treeGenScript.variance = setVariance;
            data.variance = setVariance;
            
            curvOffsetStrength = setCurvOffsetStrength;
            treeGenScript.curvOffsetStrength = setCurvOffsetStrength;
            data.curvOffsetStrength = setCurvOffsetStrength;
            
            splitHeightInLevel = setSplitHeightInLevel;
            treeGenScript.splitHeightInLevel = setSplitHeightInLevel;
            data.splitHeightInLevel = setSplitHeightInLevel;
            
            splitHeightVariation = setSplitHeightVariation;
            treeGenScript.splitHeightVariation = setSplitHeightVariation;
            data.splitHeightVariation = setSplitHeightVariation;
            
            testSplitAngle = setTestSplitAngle;
            treeGenScript.testSplitAngle = setTestSplitAngle;
            data.testSplitAngle = setTestSplitAngle;
            
            testSplitPointAngle = setTestSplitPointAngle;
            treeGenScript.testSplitPointAngle = setTestSplitPointAngle;
            data.testSplitPointAngle = setTestSplitPointAngle;

            childLevels = setChildLevels;
            treeGenScript.nrChildLevels = childLevels;
            // TODO...

            nrChildren = setNrChildren;
            treeGenScript.nrChildren = setNrChildren;
            data.nrChildren = setNrChildren;
            
            relChildLength = setRelChildLength;
            treeGenScript.relChildLength = setRelChildLength;
            data.relChildLength = setRelChildLength;
            
            verticalRange = setVerticalRange;
            treeGenScript.verticalRange = setVerticalRange;
            data.verticalRange = setVerticalRange;
            
            verticalAngleCrownStart = setVerticalAngleCrownStart;
            treeGenScript.verticalAngleCrownStart = setVerticalAngleCrownStart;
            data.verticalAngleCrownStart = setVerticalAngleCrownStart;
            
            verticalAngleCrownEnd = setVerticalAngleCrownEnd;
            treeGenScript.verticalAngleCrownEnd = setVerticalAngleCrownEnd;
            data.verticalAngleCrownEnd = setVerticalAngleCrownEnd;
            
            rotateAngle = setRotateAngle;
            treeGenScript.rotateAngle = setRotateAngle;
            data.rotateAngle = setRotateAngle;
            
            childrenStartLevel = setChildrenStartLevel;
            treeGenScript.childrenStartLevel = setChildrenStartLevel;
            data.childrenStartLevel = setChildrenStartLevel;
            
            childCurvature = setChildCurvature;
            treeGenScript.childCurvature = setChildCurvature;
            data.childCurvature = setChildCurvature;
            
            nrChildSplits = setNrChildSplits;
            treeGenScript.nrChildSplits = setNrChildSplits;
            data.nrChildSplits = setNrChildSplits;

            seed = setSeed;
            treeGenScript.seed = setSeed;
            data.seed = setSeed;
            
            Debug.Log("init tree...");
            treeGenScript.initTree();
            Debug.Log("update tree...");
            treeGenScript.updateTree();
        }
        
    }
}

public class treeData
{
    public float treeHeight;
    public Vector3 treeGrowDir;
    public int treeShape;
    public float taper;
    public float branchTipRadius;
    public float ringSpacing;
    public int stemRingResolution;
    public int resampleNr;
    public float noiseAmplitudeLower;
    public float noiseAmplitudeUpper;
    public float noiseAmplitudeLowerUpperExponent;
    public float noiseScale;
    public float splitCurvature;
    public int testRecursionStop;
    public int nrSplits;
    public float variance;
    public float curvOffsetStrength;
    public List<float> splitHeightInLevel;
    public float splitHeightVariation;
    public float testSplitAngle;
    public float testSplitPointAngle;

    //
    // static int childLevels;
    // public static int setChildLevels;
// 
    // static List<int> nrChildren;
    // public static List<int> setNrChildren;
    // static List<float> relChildLength;
    // public static List<float> setRelChildLength;
    // static List<float> verticalRange;
    // public static List<float> setVerticalRange;
    // static List<float> verticalAngleCrownStart;
    // public static List<float> setVerticalAngleCrownStart;
    // static List<float> verticalAngleCrownEnd;
    // public static List<float> setVerticalAngleCrownEnd;
    // static List<float> rotateAngle;
    // public static List<float> setRotateAngle;
    // static List<int> childrenStartLevel;
    // public static List<int> setChildrenStartLevel;
    // static List<float> childCurvature;
    // public static List<float> setChildCurvature;
    // static List<int> nrChildSplits;
    // public static List<int> setNrChildSplits;
//
    public int childLevels;
    public List<int> nrChildren;
    public List<float> relChildLength;
    public List<float> verticalRange;
    public List<float> verticalAngleCrownStart;
    public List<float> verticalAngleCrownEnd;
    public List<float> rotateAngle;
    public List<int> childrenStartLevel;
    public List<float> childCurvature;
    public List<int> nrChildSplits;
    public int seed;

    public treeData()
    {

    }
}
