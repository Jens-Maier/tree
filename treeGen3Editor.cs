#pragma warning disable IDE1006 // Naming Styles
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

public enum angleMode
{
    symmetric,
    winding
}

public enum splitMode
{
    rotateAngle,
    horizontal
}
//public enum splitMode
//{
//    rotateAngle, 
//    horizontal
//}

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
    public List<float> taperFactor;
    public static List<float> setTaperFactor;
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
    public static int shyBranchesIterations;
    public static int setShyBranchesIterations;
    public static float shyBranchesMaxDistance;
    public static float setShyBranchesMaxDistance;
    static int nrSplits;
    public static int setNrSplits;
    public int stemSplitMode;
    public static splitMode setStemSplitMode;
    public float stemSplitRotateAngle;
    public static float setStemSplitRotateAngle;
    static float variance;
    public static float setVariance;
    static float curvOffsetStrength;
    public static float setCurvOffsetStrength;
    static List<float> splitHeightInLevel;
    public static List<float> setSplitHeightInLevel;
    static List<List<float>> branchSplitHeightInLevel;
    public static List<List<float>> setBranchSplitHeightInLevel;
    static List<float> branchSplitHeightVariation;
    public static List<float> setBranchSplitHeightVariation;
    static float splitHeightVariation;
    public static float setSplitHeightVariation;
    static float testSplitAngle;
    public static float setTestSplitAngle;
    static float testSplitPointAngle;
    public static float setTestSplitPointAngle;

    static int branchClusters;
    public static int setBranchClusters;


    // static List<int> parentClusterIndex;
    // public static List<int> setParentClusterIndex;
    static List<List<bool>> parentClusterBools;
    public List<List<bool>> setParentClusterBools = new List<List<bool>>();
    static List<int> nrBranches;
    public static List<int> setNrBranches;
    public List<int> branchSplitMode;
    public static List<splitMode> setBranchSplitMode;
    public List<float> branchSplitRotateAngle;
    public static List<float> setBranchSplitRotateAngle;
    static List<float> relBranchLength;
    public static List<float> setRelBranchLength;
    static List<float> verticalRange;
    public static List<float> setVerticalRange;
    static List<float> verticalAngleCrownStart;
    public static List<float> setVerticalAngleCrownStart;
    static List<float> verticalAngleCrownEnd;
    public static List<float> setVerticalAngleCrownEnd;
    static List<float> rotateAngle;
    public static List<float> setRotateAngle;
    static List<float> rotateAngleRange;
    public static List<float> setRotateAngleRange;
    static List<float> branchesStartHeight;
    public static List<float> setBranchesStartHeight;
    static List<float> branchesEndHeight;
    public static List<float> setBranchesEndHeight;
    static List<float> branchCurvature;
    public static List<float> setBranchCurvature;
    static List<float> nrSplitsPerBranch;
    public static List<float> setNrSplitsPerBranch;
    static List<float> splitsPerBranchVariation;
    public static List<float> setSplitsPerBranchVariation;
    static List<int> branchAngleMode;
    public static List<angleMode> setBranchAngleMode;

    static int nrLeaves;
    public static int setNrLeaves;
    static float leafSize;
    public static float setLeafSize;

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

    //private List<string> dropdownItems = new List<string> { "1", "2", "3" }; // Initial dropdown items
    //private int selectedIndex = 0; // Currently selected index
    
    

    public override void OnInspectorGUI()
    {
        treeGen3 treeGenScript = (treeGen3)target;

        //// TEST drop down menu ----------- -> multiple branches per level possible ---------------------------------
        //
        //// Render the dropdown menu
        //selectedIndex = EditorGUILayout.Popup("Branches of Level", selectedIndex, dropdownItems.ToArray());
        //
        //// Button to add a new item
        //if (GUILayout.Button("Add Item"))
        //{
        //    if (!dropdownItems.Contains((dropdownItems.Count + 1).ToString())) // Avoid duplicates
        //    {
        //        dropdownItems.Add((dropdownItems.Count + 1).ToString());
        //    }
        //}
        //if (GUILayout.Button("Remove Item"))
        //{
        //    if (dropdownItems.Count > 1)
        //    {
        //        if (selectedIndex < dropdownItems.Count - 1)
        //        {
        //            dropdownItems.RemoveAt(dropdownItems.Count - 1);
        //        }
        //    }
        //}
        //
        //// Display the selected item
        //EditorGUILayout.LabelField("Selected Item: " + dropdownItems[selectedIndex]);

        // Call base inspector GUI
        // base.OnInspectorGUI();

        // -> TODO: branch layers -> affect level ...

        // ------------------------------------------------------------------

        
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

            taperFactor = data.taperFactor;
            setTaperFactor = data.taperFactor;
            treeGenScript.taperFactor = data.taperFactor;

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

            shyBranchesIterations = data.shyBranchesIterations;
            setShyBranchesIterations = data.shyBranchesIterations;
            treeGenScript.shyBranchesIterations = data.shyBranchesIterations;

            shyBranchesMaxDistance = data.shyBranchesMaxDistance;
            setShyBranchesMaxDistance = data.shyBranchesMaxDistance;
            treeGenScript.shyBranchesMaxDistance = data.shyBranchesMaxDistance;

            nrSplits = data.nrSplits;
            setNrSplits = data.nrSplits;
            treeGenScript.nrSplits = data.nrSplits;

            variance = data.variance;
            setVariance = data.variance;
            treeGenScript.variance = data.variance;

            stemSplitMode = data.stemSplitMode;
            setStemSplitMode = (splitMode)data.stemSplitMode;
            treeGenScript.setStemSplitMode(data.stemSplitMode);
            
            stemSplitRotateAngle = data.stemSplitRotateAngle;
            setStemSplitRotateAngle = data.stemSplitRotateAngle;
            treeGenScript.stemSplitRotateAngle = data.stemSplitRotateAngle;

            curvOffsetStrength = data.curvOffsetStrength;
            setCurvOffsetStrength = data.curvOffsetStrength;
            treeGenScript.curvOffsetStrength = data.curvOffsetStrength;

            splitHeightInLevel = data.splitHeightInLevel;
            setSplitHeightInLevel = data.splitHeightInLevel;
            treeGenScript.splitHeightInLevel = data.splitHeightInLevel;

            branchSplitHeightInLevel = data.branchSplitHeightInLevel;
            setBranchSplitHeightInLevel = data.branchSplitHeightInLevel;
            treeGenScript.branchSplitHeightInLevel = data.branchSplitHeightInLevel;

            branchSplitHeightVariation = data.branchSplitHeightVariation;
            setBranchSplitHeightVariation = data.branchSplitHeightVariation;
            treeGenScript.branchSplitHeightVariation = data.branchSplitHeightVariation;

            splitHeightVariation = data.splitHeightVariation;
            setSplitHeightVariation = data.splitHeightVariation;
            treeGenScript.splitHeightVariation = data.splitHeightVariation;

            testSplitAngle = data.testSplitAngle;
            setTestSplitAngle = data.testSplitAngle;
            treeGenScript.testSplitAngle = data.testSplitAngle;

            testSplitPointAngle = data.testSplitPointAngle;
            setTestSplitPointAngle = data.testSplitPointAngle;
            treeGenScript.testSplitPointAngle = data.testSplitPointAngle;

            // parentClusterIndex = data.parentClusterIndex;
            // setParentClusterIndex = data.parentClusterIndex;
            // treeGenScript.parentClusterIndex = data.parentClusterIndex;

            parentClusterBools = data.parentClusterBools;
            setParentClusterBools = data.parentClusterBools;
            treeGenScript.parentClusterBools = data.parentClusterBools;

            nrBranches = data.nrBranches;
            setNrBranches = data.nrBranches;
            treeGenScript.nrBranches = data.nrBranches;

            branchSplitMode = data.branchSplitMode;
            if (setBranchSplitMode == null)
            {
                setBranchSplitMode = new List<splitMode>();
            }
            foreach (int mode in data.branchSplitMode)
            {
                setBranchSplitMode.Add((splitMode)mode);
            }
            //setBranchSplitMode = data.branchSplitMode;
            if (data.branchSplitMode == null)
            {
                List<int> newBranchSplitMode = new List<int>();
                for (int i = 0; i < nrBranches.Count; i++)
                {
                    newBranchSplitMode.Add(1);
                }
                treeGenScript.setBranchSplitMode(newBranchSplitMode);
            }
            else
            {
                treeGenScript.setBranchSplitMode(data.branchSplitMode);
            }

            branchSplitRotateAngle = data.branchSplitRotateAngle;
            setBranchSplitRotateAngle = data.branchSplitRotateAngle;
            treeGenScript.branchSplitRotateAngle = data.branchSplitRotateAngle;

            // if (setBranchSplitRotateAngle == null)
            // {
            //     setBranchSplitRotateAngle = new List<float>();
            // }
            // if (data.branchSplitRotateAngle == null)
            // {
            //     List<float> newBranchSplitRotateAngle = new List<float>();
            //     for (int i = 0; i < nrBranches.Count; i++)
            //     {
            //         newBranchSplitRotateAngle.Add(0f);
            //     }
            //     treeGenScript.branchSplitRotateAngle = newBranchSplitRotateAngle;
            // }
            // else
            // {
            //     treeGenScript.branchSplitRotateAngle = data.branchSplitRotateAngle;
            // }


            // branchAngleMode = data.branchAngleMode;
            // if (setBranchAngleMode == null)
            // {
            //     setBranchAngleMode = new List<angleMode>();
            // }
            // foreach (int mode in data.branchAngleMode)
            // {
            //     setBranchAngleMode.Add((angleMode)mode);
            // }
            // treeGenScript.setBranchAngleMode(data.branchAngleMode);

            relBranchLength = data.relBranchLength;
            setRelBranchLength = data.relBranchLength;
            treeGenScript.relBranchLength = data.relBranchLength;

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

            rotateAngleRange = data.rotateAngleRange;
            setRotateAngleRange = data.rotateAngleRange;
            treeGenScript.rotateAngleRange = data.rotateAngleRange;

            branchesStartHeight = data.branchesStartHeight;
            setBranchesStartHeight = data.branchesStartHeight;
            treeGenScript.branchesStartHeight = data.branchesStartHeight;

            branchesEndHeight = data.branchesEndHeight;
            setBranchesEndHeight = data.branchesEndHeight;
            treeGenScript.branchesEndHeight = data.branchesEndHeight;

            branchCurvature = data.branchCurvature;
            setBranchCurvature = data.branchCurvature;
            treeGenScript.branchCurvature = data.branchCurvature;

            nrSplitsPerBranch = data.nrSplitsPerBranch;
            setNrSplitsPerBranch = data.nrSplitsPerBranch;
            treeGenScript.nrSplitsPerBranch = data.nrSplitsPerBranch;

            setSplitsPerBranchVariation = data.splitsPerBranchVariation;
            setSplitsPerBranchVariation = data.splitsPerBranchVariation;
            treeGenScript.splitsPerBranchVariation = data.splitsPerBranchVariation;

            // treeShape = data.treeShape;
            // setTreeShape = (shape)data.treeShape;
            // treeGenScript.setTreeShape(data.treeShape);
            // 

            branchAngleMode = data.branchAngleMode;
            if (setBranchAngleMode == null)
            {
                setBranchAngleMode = new List<angleMode>();
            }
            foreach (int mode in data.branchAngleMode)
            {
                setBranchAngleMode.Add((angleMode)mode);
            }
            treeGenScript.setBranchAngleMode(data.branchAngleMode);

            leafSize = data.leafSize;
            setLeafSize = data.leafSize;
            treeGenScript.leafSize = data.leafSize;
            
            nrLeaves = data.nrLeaves;
            setNrLeaves = data.nrLeaves;
            treeGenScript.nrLeaves = data.nrLeaves;

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
                StreamWriter writer = new StreamWriter(path, false);
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
        setShyBranchesIterations = EditorGUILayout.IntField("shyBranchesIterations", setShyBranchesIterations);
        setShyBranchesMaxDistance = EditorGUILayout.FloatField("shyBranchesMaxDistance", setShyBranchesMaxDistance);
        setNrSplits = EditorGUILayout.IntField("nrSplits", setNrSplits);
        setSplitCurvature = EditorGUILayout.FloatField("splitCurvature", setSplitCurvature);
        setTestRecursionStop = EditorGUILayout.IntField("testRecursionStop", setTestRecursionStop);
        setVariance = EditorGUILayout.FloatField("variance", setVariance);
        setStemSplitMode = (splitMode)EditorGUILayout.EnumPopup("stemSplitMode", setStemSplitMode);
        if (setStemSplitMode == splitMode.rotateAngle)
        {
            setStemSplitRotateAngle = EditorGUILayout.FloatField("stemSplitRotateAngle", setStemSplitRotateAngle);
        }
        else
        {
            setStemSplitRotateAngle = 0f;
        }
        setCurvOffsetStrength = EditorGUILayout.FloatField("curvOffsetStrength", setCurvOffsetStrength);
        if (setSplitHeightInLevel == null)
        {
            setSplitHeightInLevel = new List<float>();
            //setSplitHeightInLevel.Add(0.5f);
        }
        int displayMax = setSplitHeightInLevel.Count < 10 ? setSplitHeightInLevel.Count : 10;
        for (int i = 0; i < displayMax; i++)
        {
            setSplitHeightInLevel[i] = EditorGUILayout.Slider("splitHeightInLevel " + i, setSplitHeightInLevel[i], 0f, 1f);
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

        EditorGUILayout.LabelField("------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("branch settings");
        EditorGUILayout.Space();
        if (GUILayout.Button("add branch Cluster"))
        {
            setBranchClusters += 1;
            // if (setParentClusterIndex == null)
            // {
            //     setParentClusterIndex = new List<int>();
            // }
            // setParentClusterIndex.Add(0);
            if (setParentClusterBools == null)
            {
                setParentClusterBools = new List<List<bool>>();
            }
            setParentClusterBools.Add(new List<bool>());

            if (setNrBranches == null)
            {
                setNrBranches = new List<int>();
            }
            setNrBranches.Add(0);
            if (setBranchSplitMode == null)
            {
                setBranchSplitMode = new List<splitMode>();
            }
            setBranchSplitMode.Add(splitMode.horizontal);

            if (setBranchSplitRotateAngle == null)
            {
                setBranchSplitRotateAngle = new List<float>();
            }
            setBranchSplitRotateAngle.Add(0f);

            if (setRelBranchLength == null)
            {
                setRelBranchLength = new List<float>();
            }
            setRelBranchLength.Add(1f);
            if (setTaperFactor == null)
            {
                setTaperFactor = new List<float>();
            }
            setTaperFactor.Add(1f);
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
            if (setRotateAngleRange == null)
            {
                setRotateAngleRange = new List<float>();
            }
            setRotateAngleRange.Add(0f);
            if (setBranchesStartHeight == null)
            {
                setBranchesStartHeight = new List<float>();
            }
            setBranchesStartHeight.Add(0f);
            if (setBranchesEndHeight == null)
            {
                setBranchesEndHeight = new List<float>();
            }
            setBranchesEndHeight.Add(999f);
            if (setBranchCurvature == null)
            {
                setBranchCurvature = new List<float>();
            }
            setBranchCurvature.Add(0f);
            if (setNrSplitsPerBranch == null)
            {
                setNrSplitsPerBranch = new List<float>();
            }
            setNrSplitsPerBranch.Add(0);
            if (setSplitsPerBranchVariation == null)
            {
                setSplitsPerBranchVariation = new List<float>();
            }
            setSplitsPerBranchVariation.Add(0f);

            if (setBranchSplitHeightInLevel == null)
            {
                setBranchSplitHeightInLevel = new List<List<float>>();
            }

            if (setBranchSplitHeightVariation == null)
            {
                setBranchSplitHeightVariation = new List<float>();
            }
            setBranchSplitHeightVariation.Add(0.5f);

            if (setBranchAngleMode == null)
            {
                setBranchAngleMode = new List<angleMode>();
            }
            setBranchAngleMode.Add(angleMode.winding);

            
        }
        if (GUILayout.Button("remove branch Cluster"))
        {
            if (setBranchClusters > 0)
            {
                if (setNrBranches.Count > 0)
                {
                    setBranchClusters -= 1;
                    // setParentClusterIndex.RemoveAt(setParentClusterIndex.Count - 1);
                    setParentClusterBools.RemoveAt(setParentClusterBools.Count - 1);
                    setNrBranches.RemoveAt(setNrBranches.Count - 1);
                    setBranchSplitMode.RemoveAt(setBranchSplitMode.Count - 1);
                    setRelBranchLength.RemoveAt(setRelBranchLength.Count - 1);
                    setTaperFactor.RemoveAt(setTaperFactor.Count - 1);
                    setVerticalRange.RemoveAt(setVerticalRange.Count - 1);
                    setVerticalAngleCrownStart.RemoveAt(setVerticalAngleCrownStart.Count - 1);
                    setVerticalAngleCrownEnd.RemoveAt(setVerticalAngleCrownEnd.Count - 1);
                    setRotateAngle.RemoveAt(setRotateAngle.Count - 1);
                    setRotateAngleRange.RemoveAt(setRotateAngleRange.Count - 1);
                    setBranchesStartHeight.RemoveAt(setBranchesStartHeight.Count - 1);
                    setBranchesEndHeight.RemoveAt(setBranchesEndHeight.Count - 1);
                    setBranchCurvature.RemoveAt(setBranchCurvature.Count - 1);
                    setNrSplitsPerBranch.RemoveAt(setNrSplitsPerBranch.Count - 1);
                    setSplitsPerBranchVariation.RemoveAt(setSplitsPerBranchVariation.Count - 1);
                    setBranchSplitHeightInLevel.RemoveAt(setBranchSplitHeightInLevel.Count - 1);
                    setBranchSplitHeightVariation.RemoveAt(setBranchSplitHeightVariation.Count - 1);
                    setBranchAngleMode.RemoveAt(setBranchAngleMode.Count - 1);
                }
                else
                {
                    Debug.Log("ERROR! nr branch levels incorrect!");
                }
            }

        }

        if (setNrBranches != null)
        {
            if (setNrBranches.Count == setBranchClusters)
            {
                for (int i = 0; i < setBranchClusters; i++)
                {
                    EditorGUILayout.LabelField("branch cluster: " + i);

                    List<string> items = new List<string>();
                    items.Add("stem");
                    if (i > 0)
                    {
                        for (int j = 0; j < i; j++)
                        {
                            items.Add(j.ToString());
                        }
                    }

                    // if (setParentClusterIndex == null)
                    // {
                    //     Debug.Log("ERROR! setParentClusterIndex == null");
                    // }
                    // if (setParentClusterIndex.Count < i + 1)
                    // {
                    //     Debug.Log("ERROR! setParentClusterIndex.Count < i + 1");
                    // }
                    // 
                    // setParentClusterIndex[i] = EditorGUILayout.Popup("Parent Cluster", setParentClusterIndex[i], items.ToArray());

                    //Debug.Log("items.Count: " + items.Count + ", setParentClusterIndex.Count: " + setParentClusterIndex.Count + ", parentClusterIndex level " + i + ": " + setParentClusterIndex[i]);
                    // "stem" -> 0
                    // "0"    -> 1
                    // "1"    -> 2


                    //--test
                    
                    if (setParentClusterBools == null)
                    {
                        setParentClusterBools = new List<List<bool>>();
                        setParentClusterBools.Add(new List<bool>());
                    }
                    
                    // Ensure bool list is the correct size
                    while (setParentClusterBools.Count <= i)
                    {
                        setParentClusterBools.Add(new List<bool>());
                    }
                    while (setParentClusterBools[i].Count < items.Count)
                    {
                        setParentClusterBools[i].Add(false);
                    }
                    while (setParentClusterBools[i].Count > items.Count)
                    {
                        setParentClusterBools[i].RemoveAt(setParentClusterBools[i].Count - 1);
                    }

                    // Draw checkboxes
                    EditorGUILayout.LabelField("Parent Clusters:");
                    for (int k = 0; k < items.Count; k++)
                    {
                        setParentClusterBools[i][k] = EditorGUILayout.ToggleLeft(items[k], setParentClusterBools[i][k]);
                    }

                    bool allFalse = true;
                    foreach (bool b in setParentClusterBools[i])
                    {
                    if (b == true)
                    {
                        allFalse = false;
                        break;
                    }
                    }
                    if (allFalse == true)
                    {
                        setParentClusterBools[i][0] = true;
                    }
                    
                    setNrBranches[i] = EditorGUILayout.IntField("nrBranches", setNrBranches[i]);
                    setBranchSplitMode[i] = (splitMode)EditorGUILayout.EnumPopup("branchSplitMode", setBranchSplitMode[i]);
                    if (setBranchSplitMode[i] == splitMode.rotateAngle)
                    {
                        setBranchSplitRotateAngle[i] = EditorGUILayout.FloatField("branchSplitRotateAngle", setBranchSplitRotateAngle[i]);
                    }
                    else
                    {
                        setBranchSplitRotateAngle[i] = 0f;
                    }
                    setRelBranchLength[i] = EditorGUILayout.FloatField("relBranchLength", setRelBranchLength[i]);
                    setTaperFactor[i] = EditorGUILayout.Slider("taperFactor", setTaperFactor[i], 0f, 1f);
                    setVerticalRange[i] = EditorGUILayout.FloatField("verticalRange", setVerticalRange[i]);
                    setVerticalAngleCrownStart[i] = EditorGUILayout.FloatField("verticalAngleCrownStart", setVerticalAngleCrownStart[i]);
                    setVerticalAngleCrownEnd[i] = EditorGUILayout.FloatField("verticalAngleCrownEnd", setVerticalAngleCrownEnd[i]);
                    setRotateAngle[i] = EditorGUILayout.FloatField("rotateAngle", setRotateAngle[i]);
                    setRotateAngleRange[i] = EditorGUILayout.FloatField("rotateAngleRange", setRotateAngleRange[i]);
                    setBranchesStartHeight[i] = EditorGUILayout.Slider("branchesStartHeight", setBranchesStartHeight[i], 0f, 1f);
                    setBranchesEndHeight[i] = EditorGUILayout.Slider("branchesEndHeight", setBranchesEndHeight[i], 0f, 1f);
                    setBranchCurvature[i] = EditorGUILayout.FloatField("branchCurvature", setBranchCurvature[i]);
                    
                    if (setBranchSplitHeightVariation == null)
                    {
                        setBranchSplitHeightVariation = new List<float>();
                    }
                    setNrSplitsPerBranch[i] = EditorGUILayout.FloatField("nrSplitsPerBranch", setNrSplitsPerBranch[i]);
                    setSplitsPerBranchVariation[i] = EditorGUILayout.FloatField("splitsPerBranchVariation", setSplitsPerBranchVariation[i]);
                    setBranchSplitHeightVariation[i] = EditorGUILayout.FloatField("branchSplitHeightVariation", setBranchSplitHeightVariation[i]);
                    
                    if (setBranchSplitHeightInLevel == null)
                    {
                        setBranchSplitHeightInLevel = new List<List<float>>();
                    }
                    

                    //if (setBranchSplitHeightInLevel.Count < 10) // TEST OFF
                    //{
                    if (GUILayout.Button("add branch split Level"))
                    {
                        if (setBranchSplitHeightInLevel.Count < i + 1)
                        {
                            setBranchSplitHeightInLevel.Add(new List<float>());
                        }
                        setBranchSplitHeightInLevel[i].Add(0.5f);

                        setBranchSplitHeightVariation.Add(0f);
                        
                        Debug.Log("add branch split level, branch level: " + i + ", setBranchSplitHeightInLevel.Count: " + setBranchSplitHeightInLevel.Count + 
                        ", setBranchSplitHeightInLevel[0].Count: " + setBranchSplitHeightInLevel[i].Count);
                        
                    }
                    //}

                    if (setBranchSplitHeightInLevel.Count > i)
                    {
                        int branchDisplayMax = setBranchSplitHeightInLevel[i].Count < 10 ? setBranchSplitHeightInLevel[i].Count : 10;

                        for (int c = 0; c < branchDisplayMax; c++)
                        {
                            setBranchSplitHeightInLevel[i][c] = EditorGUILayout.Slider("branchSplitHeightInLevel " + i, setBranchSplitHeightInLevel[i][c], 0f, 1f);
                        }
                    }

                    if (setBranchAngleMode == null)
                    {
                        setBranchAngleMode = new List<angleMode>();
                    }
                    if (setBranchAngleMode.Count < i + 1)
                    {
                        setBranchAngleMode.Add(angleMode.winding);
                    }
                    setBranchAngleMode[i] = (angleMode)EditorGUILayout.EnumPopup("branchAngleMode", setBranchAngleMode[i]);
                    

                    EditorGUILayout.Space();
                }
            }
            else
            {
                Debug.Log("ERROR! setBranchClusters: " + setBranchClusters + ", setNrBranchesCount: " + setNrBranches.Count);
                setBranchClusters = 0;
                setNrBranches.Clear();
            }
        }


        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        EditorGUILayout.LabelField("leaf settings");
        setNrLeaves = EditorGUILayout.IntField("nrLeaves", setNrLeaves);
        setLeafSize = EditorGUILayout.FloatField("leafSize", setLeafSize);
        
        
        EditorGUILayout.LabelField("-------------------------------------------------------------------------------------------------------------------------------");
        setRandomize = EditorGUILayout.Toggle("randomizeSeed", setRandomize);
        setSeed = EditorGUILayout.IntField("seed", setSeed);        

        if (GUILayout.Button("set Tree parameters"))
        {
            data = new treeData();
            
            if (setRandomize == true)
            {
                //setSeed += 1;
                setSeed = random.Next();
                seed = setSeed;
                treeGenScript.seed = setSeed;
                data.seed = setSeed;
            }


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

            shyBranchesIterations = setShyBranchesIterations;
            treeGenScript.shyBranchesIterations = setShyBranchesIterations;
            data.shyBranchesIterations = setShyBranchesIterations;

            shyBranchesMaxDistance = setShyBranchesMaxDistance;
            treeGenScript.shyBranchesMaxDistance = setShyBranchesMaxDistance;
            data.shyBranchesMaxDistance = setShyBranchesMaxDistance;
            
            nrSplits = setNrSplits;
            treeGenScript.nrSplits = setNrSplits;
            data.nrSplits = setNrSplits;
            
            variance = setVariance;
            treeGenScript.variance = setVariance;
            data.variance = setVariance;

            stemSplitMode = (int)setStemSplitMode;
            treeGenScript.setStemSplitMode(stemSplitMode);
            data.stemSplitMode = (int)setStemSplitMode;

            stemSplitRotateAngle = setStemSplitRotateAngle;
            treeGenScript.stemSplitRotateAngle = setStemSplitRotateAngle;
            data.stemSplitRotateAngle = setStemSplitRotateAngle;
            
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

            branchClusters = setBranchClusters;
            treeGenScript.nrBranchClusters = setBranchClusters;
            data.branchClusters = setBranchClusters;
            
            branchSplitHeightInLevel = setBranchSplitHeightInLevel;
            treeGenScript.branchSplitHeightInLevel = setBranchSplitHeightInLevel;
            data.branchSplitHeightInLevel = setBranchSplitHeightInLevel;

            branchSplitHeightVariation = setBranchSplitHeightVariation;
            treeGenScript.branchSplitHeightVariation = setBranchSplitHeightVariation;
            data.branchSplitHeightVariation = setBranchSplitHeightVariation;

            // parentClusterIndex = setParentClusterIndex;
            // treeGenScript.parentClusterIndex = setParentClusterIndex;
            // data.parentClusterIndex = setParentClusterIndex;

            parentClusterBools = setParentClusterBools;
            treeGenScript.parentClusterBools = setParentClusterBools;
            data.parentClusterBools = setParentClusterBools;

            nrBranches = setNrBranches;
            treeGenScript.nrBranches = setNrBranches;
            data.nrBranches = setNrBranches;

            // branchSplitMode = setBranchSplitMode;
            // treeGenScript.branchSplitMode = setBranchSplitMode;
            // data.branchSplitMode = setBranchSplitMode;
            if (branchSplitMode == null)
            {
                branchSplitMode = new List<int>();
            }
            else
            {
                branchSplitMode.Clear();
            }

            if (setBranchSplitMode != null)
            {
                foreach (splitMode mode in setBranchSplitMode)
                {
                    branchSplitMode.Add((int)mode);
                }
                treeGenScript.setBranchSplitMode(branchSplitMode);
                data.branchSplitMode = branchSplitMode;
            }

            // if (branchAngleMode == null)
            // {
            //     branchAngleMode = new List<int>();
            // }
            // else
            // {
            //     branchAngleMode.Clear();
            // }
            // 
            // if (setBranchAngleMode != null)
            // {
            //     foreach (angleMode mode in setBranchAngleMode)
            //     {
            //         branchAngleMode.Add((int)mode);
            //     }
            //     treeGenScript.setBranchAngleMode(branchAngleMode);
            //     data.branchAngleMode = branchAngleMode;
            // }

            relBranchLength = setRelBranchLength;
            treeGenScript.relBranchLength = setRelBranchLength;
            data.relBranchLength = setRelBranchLength;

            taperFactor = setTaperFactor;
            treeGenScript.taperFactor = setTaperFactor;
            data.taperFactor = setTaperFactor;
            
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

            rotateAngleRange = setRotateAngleRange;
            treeGenScript.rotateAngleRange = setRotateAngleRange;
            data.rotateAngleRange = setRotateAngleRange;
            
            branchesStartHeight = setBranchesStartHeight;
            treeGenScript.branchesStartHeight = setBranchesStartHeight;
            data.branchesStartHeight = setBranchesStartHeight;

            branchesEndHeight = setBranchesEndHeight;
            treeGenScript.branchesEndHeight = setBranchesEndHeight;
            data.branchesEndHeight = setBranchesEndHeight;
            
            branchCurvature = setBranchCurvature;
            treeGenScript.branchCurvature = setBranchCurvature;
            data.branchCurvature = setBranchCurvature;
            
            nrSplitsPerBranch = setNrSplitsPerBranch;
            treeGenScript.nrSplitsPerBranch = setNrSplitsPerBranch;
            data.nrSplitsPerBranch = setNrSplitsPerBranch;

            splitsPerBranchVariation = setSplitsPerBranchVariation;
            treeGenScript.splitsPerBranchVariation = setSplitsPerBranchVariation;
            data.splitsPerBranchVariation = setSplitsPerBranchVariation;

            if (branchAngleMode == null)
            {
                branchAngleMode = new List<int>();
            }
            else
            {
                branchAngleMode.Clear();
            }

            if (setBranchAngleMode != null)
            {
                foreach (angleMode mode in setBranchAngleMode)
                {
                    branchAngleMode.Add((int)mode);
                }
                treeGenScript.setBranchAngleMode(branchAngleMode);
                data.branchAngleMode = branchAngleMode;
            }

            nrLeaves = setNrLeaves;
            treeGenScript.nrLeaves = setNrLeaves;
            data.nrLeaves = setNrLeaves;

            leafSize = setLeafSize;
            treeGenScript.leafSize = setLeafSize;
            data.leafSize = setLeafSize;

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
    //void OnDrawGizmos()
    //{
    //    Debug.Log("OnDrawGizmos");
    //    Gizmos.color = Color.red;
    //    Gizmos.DrawSphere(new Vector3(0f, 0f, 0f), 10f);
    //}

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
    public int shyBranchesIterations;
    public float shyBranchesMaxDistance;
    public int nrSplits;
    public int stemSplitMode;
    public float stemSplitRotateAngle;
    public float variance;
    public float curvOffsetStrength;
    public List<float> splitHeightInLevel;
    public List<List<float>> branchSplitHeightInLevel;
    public List<float> branchSplitHeightVariation;
    public float splitHeightVariation;
    public float testSplitAngle;
    public float testSplitPointAngle;


    public int branchClusters;
    // public List<int> parentClusterIndex;
    public List<List<bool>> parentClusterBools;
    public List<int> nrBranches;
    public List<int> branchSplitMode;
    public List<float> branchSplitRotateAngle;
    public List<float> relBranchLength;
    public List<float> taperFactor;
    public List<float> verticalRange;
    public List<float> verticalAngleCrownStart;
    public List<float> verticalAngleCrownEnd;
    public List<float> rotateAngle;
    public List<float> rotateAngleRange;
    public List<float> branchesStartHeight;
    public List<float> branchesEndHeight;
    public List<float> branchCurvature;
    public List<float> nrSplitsPerBranch;
    public List<float> splitsPerBranchVariation;
    public List<int> branchAngleMode;
    public int nrLeaves;
    public float leafSize;
    public int seed;

    public treeData()
    {

    }

    
}
