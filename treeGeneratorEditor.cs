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

namespace treeGenNamespace
{

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
        winding, 
        adaptiveWinding
    }

    public enum splitMode
    {
        rotateAngle,
        horizontal
    }

    public enum branchTypes
    {
        single,
        opposite,
        whorled
    }


    [CustomEditor(typeof(treeGenerator))]
    public class treeGeneratorEditor : Editor
    {
        //public json treeData; // TODO: use json! (do not use scriptableObject to store data (scriptableObjects are read only!)

        //public static float setTreeHeight;
        public static treeSettings settings;
        public splitMode stemSplitMode;
        public List<shape> treeShape = new List<shape>();
        public List<shape> branchShape = new List<shape>();
        public List<branchTypes> branchType = new List<branchTypes>();
        public List<angleMode> branchAngleMode = new List<angleMode>();
        public List<splitMode> branchSplitMode = new List<splitMode>();

        private static bool showTreeSettings = true;
        private static bool showNoiseSettings = true;
        private static bool showAngleSettings = true;
        private static bool showSplitSettings = true;
        private static bool showBranchSettings = true;
        private static bool showLeafSettings = true;

        private static List<bool> showBranchCluster = new List<bool>();
        private static List<bool> showBranchClusterNoise = new List<bool>();
        private static List<bool> showBranchClusterAngle = new List<bool>();
        private static List<bool> showBranchClusterSplit = new List<bool>();
        

        public override void OnInspectorGUI()
        {
            treeGenerator treeGen = (treeGenerator)target;
            
            if (GUILayout.Button("generate tree"))
            {
                Debug.Log("tree height: " + settings.treeHeight);
                Debug.Log("tree grow dir: " + settings.treeGrowDir);
                Debug.Log("stemSplitMode: " + settings.stemSplitMode);
                treeGen.settings = settings;
                treeGen.generateTree();
            }

            // Tree Settings
            showTreeSettings = EditorGUILayout.Foldout(showTreeSettings, "Tree Settings", true);

            if (showTreeSettings)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);

                if (settings == null)
                {
                    settings = new treeSettings();
                }

                if (settings.treeHeight == 0f)
                {
                    settings.treeHeight = 1f;
                }

                float newTreeHeight = EditorGUILayout.FloatField("tree Height", settings.treeHeight);
                if (newTreeHeight >= 0f)
                {
                    settings.treeHeight = newTreeHeight;
                }
                settings.treeGrowDir = EditorGUILayout.Vector3Field("tree Grow Direction", settings.treeGrowDir);
                float newTaper = EditorGUILayout.FloatField("taper", settings.taper);
                if (newTaper >= 0f)
                {
                    settings.taper = newTaper;
                }
                float newBranchTipRadius = EditorGUILayout.FloatField("branch Tip Radius", settings.branchTipRadius);
                if (newBranchTipRadius >= 0f)
                {
                    settings.branchTipRadius = newBranchTipRadius;
                }
                float newRingSpacing = EditorGUILayout.FloatField("Ring Spacing", settings.ringSpacing);
                if (newRingSpacing > 0f)
                {
                    settings.ringSpacing = newRingSpacing;
                }
                int newStemRingRes = EditorGUILayout.IntField("Stem Ring Resolution", settings.stemRingRes);
                if (newStemRingRes >= 3)
                {
                    settings.stemRingRes = newStemRingRes;
                }
                else
                {
                    settings.stemRingRes = 3;
                }
                float newResampleDistance = EditorGUILayout.FloatField("Resample Distance", settings.resampleDistance);
                if (newResampleDistance > 0f)
                {
                    settings.resampleDistance = newResampleDistance;
                }
                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.Space();

            // Noise Settings
            showNoiseSettings = EditorGUILayout.Foldout(showNoiseSettings, "Noise Settings", true);

            if (showNoiseSettings)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);

                settings.noiseAmplitudeVertical = EditorGUILayout.FloatField("Noise Amplitude   Vertical", settings.noiseAmplitudeVertical);
                settings.noiseAmplitudeHorizontal = EditorGUILayout.FloatField("Noise   Amplitude Horizontal", settings.noiseAmplitudeHorizontal);
                settings.noiseAmplitudeGradient = EditorGUILayout.FloatField("Noise Amplitude   Gradient", settings.noiseAmplitudeGradient);
                settings.noiseAmplitudeExponent = EditorGUILayout.FloatField("Noise Amplitude   Exponent", settings.noiseAmplitudeExponent);
                settings.noiseScale = EditorGUILayout.FloatField("Noise Scale", settings.   noiseScale);
                settings.seed = EditorGUILayout.IntField("Seed", settings.seed);

                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.Space();

            // Angle Settings
            showAngleSettings = EditorGUILayout.Foldout(showAngleSettings, "Angle Settings", true);

            if (showAngleSettings)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                settings.curvatureStart = EditorGUILayout.FloatField("Curvature Start", settings.curvatureStart);
                settings.curvatureEnd = EditorGUILayout.FloatField("Curvature End", settings.curvatureEnd);

                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.Space();

            // Split Settings
            showSplitSettings = EditorGUILayout.Foldout(showSplitSettings, "Split Settings", true);

            if (showSplitSettings)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                settings.nrSplits = EditorGUILayout.IntField("Number of Splits", settings.nrSplits);
                settings.variance = EditorGUILayout.FloatField("Variance", settings.variance);
                stemSplitMode = (splitMode)EditorGUILayout.EnumPopup("stemSplitMode", stemSplitMode);
                settings.stemSplitMode = (int)stemSplitMode;
                if (settings.stemSplitMode == 0)
                {
                    settings.stemSplitRotateAngle = EditorGUILayout.FloatField("Stem Split Rotate Angle", settings.stemSplitRotateAngle);
                    // TODO: stem split axis variation (s. branches...)
                }
                settings.curvOffsetStrength = EditorGUILayout.FloatField("Curvature Offset Strength", settings.curvOffsetStrength);
                settings.splitHeightVariation = EditorGUILayout.FloatField("Split Height Variation", settings.splitHeightVariation);
                settings.splitLengthVariation = EditorGUILayout.FloatField("Split Length Variation", settings.splitLengthVariation);
                settings.stemSplitAngle = EditorGUILayout.FloatField("Stem Split Angle", settings.stemSplitAngle);
                settings.stemSplitPointAngle = EditorGUILayout.FloatField("Stem Split Point Anlge", settings.stemSplitPointAngle);
                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.Space();

            showBranchSettings = EditorGUILayout.Foldout(showBranchSettings, "Branch Settings", true);

            // Branch Settings
            if (showBranchSettings)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
 
                EditorGUILayout.BeginHorizontal();
 
                if (GUILayout.Button("Add"))
                {
                    settings.nrBranchClusters += 1;
                    settings.branchSettings.Add(new branchClusterSettings());
                    if (treeShape == null)
                    {
                        treeShape = new List<shape>();
                    }
                    if (branchShape == null)
                    {
                        branchShape = new List<shape>();
                    }
                    treeShape.Add(shape.conical);
                    branchShape.Add(shape.conical);
                    branchType.Add(branchTypes.single);
                    branchAngleMode.Add(angleMode.winding);
                    branchSplitMode.Add(splitMode.rotateAngle);
                    showBranchCluster.Add(true);
                    showBranchClusterNoise.Add(true);
                    showBranchClusterAngle.Add(true);
                    showBranchClusterSplit.Add(true);
                    Debug.Log("nrBranchClusters: " + settings.nrBranchClusters);
                }
                if (GUILayout.Button("Remove"))
                {
                    if (settings.nrBranchClusters > 0)
                    {
                        settings.nrBranchClusters -= 1;
                        settings.branchSettings.RemoveAt(settings.branchSettings.Count - 1);
                        treeShape.RemoveAt(treeShape.Count - 1);
                        branchShape.RemoveAt(branchShape.Count - 1);
                        branchType.RemoveAt(branchType.Count - 1);
                        branchAngleMode.RemoveAt(branchAngleMode.Count - 1);
                        branchSplitMode.RemoveAt(branchSplitMode.Count - 1);
                        showBranchCluster.RemoveAt(showBranchCluster.Count - 1);
                        showBranchClusterNoise.RemoveAt(showBranchClusterNoise.Count - 1);
                        showBranchClusterSplit.RemoveAt(showBranchClusterSplit.Count - 1);
                    }
                    Debug.Log("nrBranchClusters: " + settings.nrBranchClusters);
                }

                EditorGUILayout.EndHorizontal();

                for (int i = 0; i < settings.nrBranchClusters; i++)
                {
                    EditorGUILayout.BeginVertical(EditorStyles.helpBox);

                    showBranchCluster[i] = EditorGUILayout.Foldout(showBranchCluster[i], "Branch cluster " + i, true);

                    if (showBranchCluster[i] == true)
                    {

                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.LabelField("Parent Clusters"); // TODO: foldout... 
                        EditorGUILayout.EndVertical();
    
                        int newNrBranches = EditorGUILayout.IntField("Number of branches", settings.branchSettings[i].nrBranches);
                        if (newNrBranches >= 0)
                        {
                            settings.branchSettings[i].nrBranches = newNrBranches;
                        }

                        treeShape[i] = (shape)EditorGUILayout.EnumPopup("treeShape", treeShape[i]);
                        settings.branchSettings[i].treeShape = (int)treeShape[i];

                        branchShape[i] = (shape)EditorGUILayout.EnumPopup("branchShape", branchShape[i]);
                        settings.branchSettings[i].branchShape = (int)branchShape[i];
    
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        branchType[i] = (branchTypes)EditorGUILayout.EnumPopup("branchType", branchType[i]);
                        settings.branchSettings[i].branchType = (int)branchType[i];
                        if (branchType[i] == branchTypes.whorled)
                        {
                            int newWhorlCountStart = EditorGUILayout.IntField("Branch whorl count start", settings.branchSettings[i].whorlCountStart);
                            if (newWhorlCountStart >= 1)
                            {
                                settings.branchSettings[i].whorlCountStart = newWhorlCountStart;
                            }
                            else
                            {
                                settings.branchSettings[i].whorlCountStart = 1;
                            }
                            int newWhorlCountEnd = EditorGUILayout.IntField("Branch whorl count end", settings.branchSettings[i].whorlCountEnd);
                            if (newWhorlCountEnd >= 1)
                            {
                                settings.branchSettings[i].whorlCountEnd = newWhorlCountEnd;
                            }
                            else
                            {
                                settings.branchSettings[i].whorlCountEnd = 1;
                            }
                        }
                        EditorGUILayout.EndVertical();
 
                        float relBranchLength = EditorGUILayout.Slider("Relative branch length", settings.branchSettings[i].relBranchLength, 0f, 1f);
                        if (relBranchLength >= 0f && relBranchLength <= 1f)
                        {
                            settings.branchSettings[i].relBranchLength = relBranchLength;
                        }
                        //else
                        //{
                        //    settings.branchSettings[i].relBranchLength = 1f;
                        //}
 
                        float relBranchLengthVariation = EditorGUILayout.Slider("Relative branch length variation", settings.branchSettings[i].relBranchLengthVariation, 0f, 1f);
                        if (relBranchLengthVariation >= 0f && relBranchLengthVariation <= 1f)
                        {
                            settings.branchSettings[i].relBranchLengthVariation = relBranchLengthVariation;
                        }
 
                        settings.branchSettings[i].taperFactor = EditorGUILayout.Slider("Taper factor", settings.branchSettings[i].taperFactor, 0f, 1f);
 
                        int ringResolution = EditorGUILayout.IntField("Ring resolution", settings.branchSettings[i].ringResolution);
                        if (ringResolution >= 3)
                        {
                            settings.branchSettings[i].ringResolution = ringResolution;
                        }
 
                        settings.branchSettings[i].branchesStartHeightGlobal = EditorGUILayout.Slider("Branches start height global", settings.branchSettings[i].branchesStartHeightGlobal, 0f, 1f);
                     
                        settings.branchSettings[i].branchesEndHeightGlobal = EditorGUILayout.Slider("Branches end height global", settings.branchSettings[i].branchesEndHeightGlobal, 0f, 1f);
 
                        settings.branchSettings[i].branchesStartPointVariation = EditorGUILayout.Slider("Branches start point variation", settings.branchSettings[i].branchesStartPointVariation, 0f, 1f);

                    }
                    EditorGUILayout.Space();
 
                    // Branch settings -> noise settings
                    showBranchClusterNoise[i] = EditorGUILayout.Foldout(showBranchClusterNoise[i], "Noise Settings", true);

                    if (showBranchClusterNoise[i] == true)
                    {
                        float noiseAmplitudeHorizontalBranch = EditorGUILayout.FloatField("Noise Amplitude Horizontal", settings.branchSettings[i]. noiseAmplitudeHorizontalBranch);
                        if (noiseAmplitudeHorizontalBranch >= 0f)
                        {
                            settings.branchSettings[i].noiseAmplitudeHorizontalBranch = noiseAmplitudeHorizontalBranch;
                        }
    
                        float noiseAmplitudeVerticalBranch = EditorGUILayout.FloatField("Noise Amplitude Vertical", settings.branchSettings[i]. noiseAmplitudeVerticalBranch);
                        if (noiseAmplitudeVerticalBranch >= 0f)
                        {
                            settings.branchSettings[i].noiseAmplitudeVerticalBranch = noiseAmplitudeVerticalBranch;
                        }
    
                        float noiseAmplitudeBranchGradient = EditorGUILayout.FloatField("Noise Amplitude Gradient", settings.branchSettings[i]. noiseAmplitudeBranchGradient);
                        if (noiseAmplitudeBranchGradient >= 0f)
                        {
                            settings.branchSettings[i].noiseAmplitudeBranchGradient = noiseAmplitudeBranchGradient;
                        }
    
                        float noiseAmplitudeExponent = EditorGUILayout.FloatField("Noise Amplitude Exponent", settings.branchSettings[i].   noiseAmplitudeExponent);
                        if (noiseAmplitudeExponent >= 0f)
                        {
                            settings.branchSettings[i].noiseAmplitudeExponent = noiseAmplitudeExponent;
                        }
    
                        float noiseScale = EditorGUILayout.FloatField("Noise Scale", settings.branchSettings[i].noiseScale);
                        if (noiseScale >= 0f)
                        {
                            settings.branchSettings[i].noiseScale = noiseScale;
                        }
                        EditorGUILayout.Space();
                    }
 
                    // Branch settings -> angle settings

                    showBranchClusterAngle[i] = EditorGUILayout.Foldout(showBranchClusterAngle[i], "Angle Settings", true);

                    if (showBranchClusterAngle[i] == true)
                    {
                        EditorGUILayout.LabelField("Angle settings");
                        settings.branchSettings[i].verticalAngleCrownStart = EditorGUILayout.FloatField("Vertical angle crown start", settings. branchSettings[i].verticalAngleCrownStart);
                        settings.branchSettings[i].verticalAngleCrownEnd = EditorGUILayout.FloatField("Vertical angle crown end", settings.branchSettings   [i].verticalAngleCrownEnd);
                        settings.branchSettings[i].verticalAngleBranchStart = EditorGUILayout.FloatField("Vertical angle branch start", settings.   branchSettings[i].verticalAngleBranchStart);
                        settings.branchSettings[i].verticalAngleBranchEnd = EditorGUILayout.FloatField("Vertical angle branch end", settings.branchSettings [i].verticalAngleBranchEnd);
    
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        branchAngleMode[i] = (angleMode)EditorGUILayout.EnumPopup("Branch angle mode", branchAngleMode[i]);
                        settings.branchSettings[i].branchAngleMode = (int)branchAngleMode[i];
                        if (branchAngleMode[i] == angleMode.symmetric)
                        {
                            settings.branchSettings[i].rotateAngleRange = EditorGUILayout.FloatField("Rotate angle range", settings.branchSettings[i].  rotateAngleRange);
    
                            settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings. branchSettings[i].rotateAngleCrownStart);
                            settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings.branchSettings   [i].rotateAngleCrownEnd);
                            settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.   branchSettings[i].rotateAngleBranchStart);
                            settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.branchSettings [i].rotateAngleBranchEnd);
                        }
                        if (branchAngleMode[i] == angleMode.winding)
                        {
                            settings.branchSettings[i].useFibonacciAngles = EditorGUILayout.Toggle("Use Fibonacci angles", settings.branchSettings[i].  useFibonacciAngles);
    
                            if (settings.branchSettings[i].useFibonacciAngles == true)
                            {
                                int fibonacciNr = EditorGUILayout.IntField("Fibonacci number", settings.branchSettings[i].fibonacciNr);
                                if (fibonacciNr >= 3)
                                {
                                    settings.branchSettings[i].fibonacciNr = fibonacciNr;
                                }
                            }
                            else
                            {
                                settings.branchSettings[i].rotateAngleRange = EditorGUILayout.FloatField("Rotate angle range", settings.branchSettings[i].  rotateAngleRange);
                                settings.branchSettings[i].rotateAngleOffset = EditorGUILayout.FloatField("Rotate angle offset", settings.branchSettings[i].    rotateAngleOffset);
    
                                settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings. branchSettings[i].rotateAngleCrownStart);
                                settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings. branchSettings[i].rotateAngleCrownEnd);
                                settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.       branchSettings[i].rotateAngleBranchStart);
                                settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.   branchSettings[i].rotateAngleBranchEnd);
                            }
                        }
                        if (branchAngleMode[i] == angleMode.adaptiveWinding)
                        {
                            settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings. branchSettings[i].rotateAngleCrownStart);
                            settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings.branchSettings   [i].rotateAngleCrownEnd);
                            settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.       branchSettings[i].rotateAngleBranchStart);
                            settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.branchSettings [i].rotateAngleBranchEnd);

                            settings.branchSettings[i].rotateAngleRangeFactor = EditorGUILayout.Slider("Rotate angle range factor", settings.branchSettings [i].rotateAngleRangeFactor, 0f, 1f);
                        }
                        EditorGUILayout.EndVertical();

                        float reducedCurveStepCutoff = EditorGUILayout.FloatField("Reduced curve step cutoff", settings.branchSettings[i].  reducedCurveStepCutoff);
                        if (reducedCurveStepCutoff >= 0f)
                        {
                            settings.branchSettings[i].reducedCurveStepCutoff = reducedCurveStepCutoff;
                        }
                        settings.branchSettings[i].reducedCurveStepFactor = EditorGUILayout.Slider("Reduced curve step factor", settings.branchSettings[i]. reducedCurveStepFactor, 0f, 1f);

                        settings.branchSettings[i].branchGlobalCurvatureStart = EditorGUILayout.FloatField("Branch global curvature start", settings.   branchSettings[i].branchGlobalCurvatureStart);
                        settings.branchSettings[i].branchGlobalCurvatureEnd = EditorGUILayout.FloatField("Branch global curvature end", settings.   branchSettings[i].branchGlobalCurvatureEnd);
                        settings.branchSettings[i].branchCurvatureStart = EditorGUILayout.FloatField("Branch curvature start", settings.branchSettings[i].  branchCurvatureStart);
                        settings.branchSettings[i].branchCurvatureEnd = EditorGUILayout.FloatField("Branch curvature end", settings.branchSettings[i].  branchCurvatureEnd);
                        settings.branchSettings[i].branchCurvatureOffset = EditorGUILayout.FloatField("Branch curvature offset", settings.branchSettings[i].    branchCurvatureOffset);
                        EditorGUILayout.Space();

                    }

                    // Branch settings -> split settings
                    showBranchClusterSplit[i] = EditorGUILayout.Foldout(showBranchClusterSplit[i], "Split Settings", true);

                    if (showBranchClusterSplit[i] == true)
                    {
                        EditorGUILayout.LabelField("Split settings");
                        settings.branchSettings[i].nrSplitsPerBranch = EditorGUILayout.FloatField("Nr splits per branch", settings.branchSettings[i].   nrSplitsPerBranch);
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        branchSplitMode[i] = (splitMode)EditorGUILayout.EnumPopup("Branch split mode", branchSplitMode[i]);
                        settings.branchSettings[i].branchSplitMode = (int)branchSplitMode[i];
                        if (branchSplitMode[i] == splitMode.rotateAngle)
                        {
                            settings.branchSettings[i].branchSplitRotateAnlge = EditorGUILayout.FloatField("Branch split rotate angle", settings.   branchSettings[i].branchSplitRotateAnlge);
                        }
                        else
                        {
                            settings.branchSettings[i].branchSplitAxisVariation = EditorGUILayout.FloatField("Branch split axis variation", settings.   branchSettings[i].branchSplitAxisVariation);
                        }
                        EditorGUILayout.EndVertical();
                        settings.branchSettings[i].branchSplitAngle = EditorGUILayout.FloatField("Branch split angle", settings.branchSettings[i].  branchSplitAngle);
                        settings.branchSettings[i].branchSplitPointAngle = EditorGUILayout.FloatField("Branch split point angle", settings.branchSettings   [i].branchSplitPointAngle);
                        settings.branchSettings[i].splitsPerBranchVariation = EditorGUILayout.FloatField("Splits per branch variation", settings.   branchSettings[i].splitsPerBranchVariation);
                        settings.branchSettings[i].branchVariance = EditorGUILayout.FloatField("Branch variance", settings.branchSettings[i].   branchVariance);
                        settings.branchSettings[i].outwardAttraction = EditorGUILayout.FloatField("Outward attraction", settings.branchSettings[i]. outwardAttraction);
                        settings.branchSettings[i].branchSplitHeightVariation = EditorGUILayout.FloatField("Branch split height variation", settings.   branchSettings[i].branchSplitHeightVariation);
                        settings.branchSettings[i].branchSplitLengthVariation = EditorGUILayout.FloatField("Branch split length variation", settings.   branchSettings[i].branchSplitLengthVariation);
    
    
                        //treeShape[i] = (shape)EditorGUILayout.EnumPopup("treeShape", treeShape[i]);
                        //settings.branchSettings[i].treeShape = (int)treeShape[i];

                    }

                   EditorGUILayout.EndVertical();
                }

                EditorGUILayout.EndVertical();

                EditorGUILayout.Space();

                showLeafSettings = EditorGUILayout.Foldout(showLeafSettings, "Leaf Settings", true);

                // Leaf Settings
                if (showLeafSettings)
                {
                    EditorGUILayout.BeginVertical(EditorStyles.helpBox);

                    EditorGUILayout.BeginHorizontal();

                    if (GUILayout.Button("Add"))
                    {
                        settings.nrLeafClusters += 1;
                        settings.leafSettings.Add(new leafClusterSettings());
                    }

                    if (GUILayout.Button("Remove"))
                    {
                        if (settings.leafSettings.Count > 0)
                        {
                            settings.nrLeafClusters -= 1;
                            settings.leafSettings.RemoveAt(settings.leafSettings.Count - 1);
                        }
                    }

                    EditorGUILayout.EndHorizontal();

                    for (int i = 0; i < settings.nrLeafClusters; i++)
                    {
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.LabelField("Leaf cluster " + i);
                        EditorGUILayout.EndVertical();
                    }
                    EditorGUILayout.EndVertical();
                }

            }


        // public float treeHeight;
        // public Vector3 treeGrowDir;
        // public float taper;
        // public float branchTipRadius;
        // public float ringSpacing;
        // public int stemRingRes;
        // public float resampleDistance;

        }

    }


}