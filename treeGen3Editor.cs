using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
//using System.Collections.Generic;
//using Random = System.Random;
using UnityEditor;
using System.IO;

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

    static float treeHeight;
    public static float setTreeHeight;
    static Vector3 treeGrowDir;
    public static Vector3 setTreeGrowDir;
    static int treeShape;
    public static int setTreeShape;
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
    static int nrChildren;
    public static int setNrChildren;
    static float relChildLength;
    public static float setRelChildLength;
    static float verticalRange;
    public static float setVerticalRange;
    static float verticalAngleCrownStart;
    public static float setVerticalAngleCrownStart;
    static float verticalAngleCrownEnd;
    public static float setVerticalAngleCrownEnd;
    static float rotateAngle;
    public static float setRotateAngle;
    static int childrenStartLevel;
    public static int setChildrenStartLevel;
    static float childCurvature;
    public static float setChildCurvature;
    static int nrChildSplits;
    public static int setNrChildSplits;



    

    private SerializedProperty myFloatField;

    public treeData data;

    public string jsonString;
    public string loadFileName = "";
    public string saveFileName = "";

    private void OnEnable()
    {
        // myFloatField = serializedObject.FindProperty("treeHeight"); // TODO: serializedObject ... (s. chatgtp...)
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
            setTreeShape = data.treeShape;
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
        setTreeShape = EditorGUILayout.IntField("treeShape", setTreeShape);
        setTaper = EditorGUILayout.FloatField("taper", setTaper);
        setBranchTipRadius = EditorGUILayout.FloatField("branchTipRadius", setBranchTipRadius);
        setRingSpacing = EditorGUILayout.FloatField("ringSpacing", setRingSpacing);
        setStemRingResolution = EditorGUILayout.IntField("stemRingResolution", setStemRingResolution);
        setResampleNr = EditorGUILayout.IntField("resampleNr", setResampleNr);
        setNoiseAmplitudeLower = EditorGUILayout.FloatField("noiseAmplitudeLower", setNoiseAmplitudeLower);
        setNoiseAmplitudeUpper = EditorGUILayout.FloatField("noiseAmplitudeUpper", setNoiseAmplitudeUpper);
        setNoiseAmplitudeLowerUpperExponent = EditorGUILayout.FloatField("noiseAmplitudeLowerUpperExponent", setNoiseAmplitudeLowerUpperExponent);
        setNoiseScale = EditorGUILayout.FloatField("noiseScale", setNoiseScale);
        setSplitCurvature = EditorGUILayout.FloatField("splitCurvature", setSplitCurvature);
        setTestRecursionStop = EditorGUILayout.IntField("testRecursionStop", setTestRecursionStop);
        setNrSplits = EditorGUILayout.IntField("nrSplits", setNrSplits);
        setVariance = EditorGUILayout.FloatField("variance", setVariance);
        setCurvOffsetStrength = EditorGUILayout.FloatField("curvOffsetStrength", setCurvOffsetStrength);
        if (setSplitHeightInLevel == null)
        {
            setSplitHeightInLevel = new List<float>();
            setSplitHeightInLevel.Add(0.5f);
        }
        for (int i = 0; i < setSplitHeightInLevel.Count; i++)
        {
            setSplitHeightInLevel[i] = EditorGUILayout.FloatField("splitHeightInLevel " + i, setSplitHeightInLevel[i]);
        }
        if (GUILayout.Button("add Level"))
        {
            setSplitHeightInLevel.Add(0.5f);
        }

        setSplitHeightVariation = EditorGUILayout.FloatField("splitHeightVariation", setSplitHeightVariation);
        setTestSplitAngle = EditorGUILayout.FloatField("testSplitAngle", setTestSplitAngle);
        setTestSplitPointAngle = EditorGUILayout.FloatField("testSplitPointAngle", setTestSplitPointAngle);
        setNrChildren = EditorGUILayout.IntField("nrChildren", setNrChildren);
        setRelChildLength = EditorGUILayout.FloatField("relChildLength", setRelChildLength);
        setVerticalRange = EditorGUILayout.FloatField("verticalRange", setVerticalRange);
        setVerticalAngleCrownStart = EditorGUILayout.FloatField("verticalAngleCrownStart", setVerticalAngleCrownStart);
        setVerticalAngleCrownEnd = EditorGUILayout.FloatField("verticalAngleCrownEnd", setVerticalAngleCrownEnd);
        setRotateAngle = EditorGUILayout.FloatField("rotateAngle", setRotateAngle);
        setChildrenStartLevel = EditorGUILayout.IntField("childrenStartLevel", setChildrenStartLevel);
        setChildCurvature = EditorGUILayout.FloatField("childCurvature", setChildCurvature);
        setNrChildSplits = EditorGUILayout.IntField("nrChildSplits", setNrChildSplits);


        if (GUILayout.Button("set Tree parameters"))
        {
            data = new treeData();

            Debug.Log("set tree parameters...");
            // treeHeight = EditorGUILayout.FloatField("treeHeight", treeHeight);
            treeHeight = setTreeHeight;
            treeGenScript.treeHeight = setTreeHeight;
            data.treeHeight = setTreeHeight;

            treeGrowDir = setTreeGrowDir;
            treeGenScript.treeGrowDir = setTreeGrowDir;
            data.treeGrowDir = setTreeGrowDir;

            treeShape = setTreeShape;
            treeGenScript.setTreeShape(treeShape);
            data.treeShape = setTreeShape;
            
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
    public int nrChildren;
    public float relChildLength;
    public float verticalRange;
    public float verticalAngleCrownStart;
    public float verticalAngleCrownEnd;
    public float rotateAngle;
    public int childrenStartLevel;
    public float childCurvature;
    public int nrChildSplits;

    public treeData()
    {

    }
}
