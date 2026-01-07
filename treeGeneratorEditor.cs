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
using System.Globalization;
using System.Diagnostics;
using Debug = UnityEngine.Debug;

namespace treeGenNamespace
{

    public enum shape
    {
        conical,
        spherical,
        hemispherical,
        inverseHemispherical,
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

    public enum angleModeLeaf
    {
        alternating,
        winding
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
        public List<branchTypes> leafType = new List<branchTypes>();
        public List<angleModeLeaf> leafAngleMode = new List<angleModeLeaf>();

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

        private static AnimationCurve taperCurve = AnimationCurve.Linear(0, 1, 1, 0);

        private static List<AnimationCurve> branchTaperCurve = new List<AnimationCurve>();
        

        public override void OnInspectorGUI()
        {
            treeGenerator treeGen = (treeGenerator)target;
            
            // ensure settings and dependent lists are initialized to avoid IndexOutOfRange when GUI indexes them
            if (settings == null)
                settings = new treeSettings();
            if (settings.branchSettings == null) settings.branchSettings = new List<branchClusterSettings>();
            if (settings.taperFactorList == null) settings.taperFactorList = new List<float>();
            if (settings.parentClusterBoolListList == null) settings.parentClusterBoolListList = new List<boolList>();
            if (settings.leafSettings == null) settings.leafSettings = new List<leafClusterSettings>();

            // expand outer collections to match nrBranchClusters
            while (settings.branchSettings.Count < settings.nrBranchClusters) settings.branchSettings.Add(new branchClusterSettings());
            while (settings.taperFactorList.Count < settings.nrBranchClusters) settings.taperFactorList.Add(1f);
            while (settings.parentClusterBoolListList.Count < settings.nrBranchClusters) settings.parentClusterBoolListList.Add(new boolList());

            // ensure auxiliary editor lists match as well
            while (treeShape.Count < settings.nrBranchClusters) treeShape.Add(shape.conical);
            while (branchShape.Count < settings.nrBranchClusters) branchShape.Add(shape.conical);
            while (branchType.Count < settings.nrBranchClusters) branchType.Add(branchTypes.single);
            while (branchAngleMode.Count < settings.nrBranchClusters) branchAngleMode.Add(angleMode.winding);
            while (branchSplitMode.Count < settings.nrBranchClusters) branchSplitMode.Add(splitMode.rotateAngle);
            while (showBranchCluster.Count < settings.nrBranchClusters) showBranchCluster.Add(true);
            while (showBranchClusterNoise.Count < settings.nrBranchClusters) showBranchClusterNoise.Add(true);
            while (showBranchClusterAngle.Count < settings.nrBranchClusters) showBranchClusterAngle.Add(true);
            while (showBranchClusterSplit.Count < settings.nrBranchClusters) showBranchClusterSplit.Add(true);
            while (branchTaperCurve.Count < settings.nrBranchClusters) branchTaperCurve.Add(AnimationCurve.Linear(0,1,1,0));

            // Ensure leafType and leafAngleMode lists are initialized and resized
            while (leafType.Count < settings.nrLeafClusters)
                leafType.Add(branchTypes.single);
            while (leafAngleMode.Count < settings.nrLeafClusters)
                leafAngleMode.Add(angleModeLeaf.alternating);

            while (leafType.Count > settings.nrLeafClusters)
                leafType.RemoveAt(leafType.Count - 1);
            while (leafAngleMode.Count > settings.nrLeafClusters)
                leafAngleMode.RemoveAt(leafAngleMode.Count - 1);

            // Ensure each leaf cluster's parent clusters are initialized
            foreach (var leafCluster in settings.leafSettings)
            {
                if (leafCluster.leafParentClusters == null)
                    leafCluster.leafParentClusters = new List<bool>();

                while (leafCluster.leafParentClusters.Count < settings.nrBranchClusters + 1)
                    leafCluster.leafParentClusters.Add(false);

                if (!leafCluster.leafParentClusters.Contains(true))
                    leafCluster.leafParentClusters[0] = true;
            }


            // ensure each inner bool list is initialized and has at least (i+1) entries before indexing
            for (int _i = 0; _i < settings.nrBranchClusters; _i++)
            {
                if (settings.parentClusterBoolListList[_i].b == null) settings.parentClusterBoolListList[_i].b = new List<bool>();
                while (settings.parentClusterBoolListList[_i].b.Count < _i + 1) settings.parentClusterBoolListList[_i].b.Add(false);
            }
            // ensure leaf parent lists sized to nrBranchClusters + 1
            foreach (var leaf in settings.leafSettings)
            {
                if (leaf.leafParentClusters == null) leaf.leafParentClusters = new List<bool>();
                while (leaf.leafParentClusters.Count < settings.nrBranchClusters + 1) leaf.leafParentClusters.Add(false);
            }
            
            if (GUILayout.Button("generate tree"))
            {
                Debug.Log("tree height: " + settings.treeHeight);
                Debug.Log("tree grow dir: " + settings.treeGrowDir);
                Debug.Log("stemSplitMode: " + settings.stemSplitMode);
                treeGen.settings = settings;
                treeGen.generateTree();

                for(int i = 0; i < settings.nrBranchClusters; i++)
                {
                    Debug.Log("maxSplitHeightUsed after generateTree: " + settings.branchSettings[i].maxSplitHeightUsed);
                }
            }

            if (GUILayout.Button("Save Properties"))
            {
                if (settings == null)
                {
                    settings = new treeSettings();
                }
                SaveSettingsToJson(settings);
            }

            if (GUILayout.Button("Load Properties"))
            {
                LoadSettingsFromJson();
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

                
                taperCurve = EditorGUILayout.CurveField("taper curve", taperCurve);
                if (settings != null)
                {
                    settings.taperCurve = taperCurve;
                }
                if (GUILayout.Button("Reset taper curve"))
                {
                    taperCurve = AnimationCurve.Linear(0f, 1f, 1f, 0f);
                    if (settings != null)
                    {
                        settings.taperCurve = taperCurve;
                    }

                    Debug.Log("curve at 0.25: " + taperCurve.Evaluate(0.25f));
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
                int newStemRingResolution = EditorGUILayout.IntField("Stem Ring Resolution", settings.stemRingResolution);
                if (newStemRingResolution >= 3)
                {
                    settings.stemRingResolution = newStemRingResolution;
                }
                else
                {
                    settings.stemRingResolution = 3;
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

                settings.noiseAmplitudeVertical = EditorGUILayout.FloatField("Noise Amplitude Vertical", settings.noiseAmplitudeVertical);
                settings.noiseAmplitudeHorizontal = EditorGUILayout.FloatField("Noise Amplitude Horizontal", settings.noiseAmplitudeHorizontal);
                settings.noiseAmplitudeGradient = EditorGUILayout.FloatField("Noise Amplitude Gradient", settings.noiseAmplitudeGradient);
                settings.noiseAmplitudeExponent = EditorGUILayout.FloatField("Noise Amplitude Exponent", settings.noiseAmplitudeExponent);
                settings.noiseScale = EditorGUILayout.FloatField("Noise Scale", settings.noiseScale);
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

                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Add split level"))
                {
                    settings.maxSplitHeightUsed += 1;
                    settings.stemSplitHeightInLevel.Add(0.5f);
                }
                if (GUILayout.Button("Remove"))
                {
                    if (settings.maxSplitHeightUsed > 0)
                    {
                        settings.maxSplitHeightUsed -= 1;
                    }
                    if (settings.stemSplitHeightInLevel.Count > 0)
                    {
                        settings.stemSplitHeightInLevel.RemoveAt(settings.stemSplitHeightInLevel.Count - 1);
                    }
                }
                EditorGUILayout.EndHorizontal();
                if (settings.maxSplitHeightUsed > 0)
                {
                    int l = settings.maxSplitHeightUsed;
                    if (l >= settings.stemSplitHeightInLevel.Count)
                    {
                        l = settings.maxSplitHeightUsed - 1;
                    }
                    for (int i = 0; i <= l; i++)
                    {
                        settings.stemSplitHeightInLevel[i] = EditorGUILayout.Slider("Level " + i, settings.stemSplitHeightInLevel[i], 0f, 1f);
                    }
                }
                else
                {
                    for (int i = 0; i < settings.stemSplitHeightInLevel.Count; i++)
                    {
                        settings.stemSplitHeightInLevel[i] = EditorGUILayout.Slider("Level " + i, settings.stemSplitHeightInLevel[i], 0f, 1f);
                    }
                }
                EditorGUILayout.EndVertical();

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
                    settings.taperFactorList.Add(1f);
                    settings.parentClusterBoolListList.Add(new boolList());
                    for (int i = 0; i < settings.nrBranchClusters; i++)
                    {
                        List<bool> boolList = settings.parentClusterBoolListList[settings.nrBranchClusters - 1].b;
                        boolList.Add(false);
                    }
                    settings.parentClusterBoolListList[settings.nrBranchClusters - 1].b[0] = true;

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
                    branchTaperCurve.Add(AnimationCurve.Linear(0, 1, 1, 0));
                    if (settings != null)
                    {
                        settings.branchSettings[settings.nrBranchClusters - 1].branchTaperCurve = UnityEngine.AnimationCurve.Linear(0f, 1f, 1f, 0f);
                    }
                    //Debug.Log("nrBranchClusters: " + settings.nrBranchClusters);

                    for (int l = 0; l < settings.leafSettings.Count; l++)
                    {
                        settings.leafSettings[l].leafParentClusters.Add(false);
                    }
                }
                if (GUILayout.Button("Remove"))
                {
                    if (settings.nrBranchClusters > 0)
                    {
                        settings.nrBranchClusters -= 1;
                        settings.branchSettings.RemoveAt(settings.branchSettings.Count - 1);
                        settings.taperFactorList.RemoveAt(settings.taperFactorList.Count - 1);
                        treeShape.RemoveAt(treeShape.Count - 1);
                        branchShape.RemoveAt(branchShape.Count - 1);
                        branchType.RemoveAt(branchType.Count - 1);
                        branchAngleMode.RemoveAt(branchAngleMode.Count - 1);
                        branchSplitMode.RemoveAt(branchSplitMode.Count - 1);
                        showBranchCluster.RemoveAt(showBranchCluster.Count - 1);
                        showBranchClusterNoise.RemoveAt(showBranchClusterNoise.Count - 1);
                        showBranchClusterSplit.RemoveAt(showBranchClusterSplit.Count - 1);
                        branchTaperCurve.RemoveAt(branchTaperCurve.Count - 1);

                        settings.parentClusterBoolListList.RemoveAt(settings.parentClusterBoolListList.Count - 1);

                        for (int l = 0; l < settings.leafSettings.Count; l++)
                        {
                            settings.leafSettings[l].leafParentClusters.RemoveAt(settings.leafSettings[l].leafParentClusters.Count - 1);
                        }
                    }
                    Debug.Log("nrBranchClusters: " + settings.nrBranchClusters);
                }

                EditorGUILayout.EndHorizontal();
                
                //Debug.Log("nrBranchClusters: " + settings.nrBranchClusters);
                // ensure parentClusterBoolListList exists and is large enough before indexing it
                if (settings.parentClusterBoolListList == null)
                {
                    settings.parentClusterBoolListList = new List<boolList>();
                }
                while (settings.parentClusterBoolListList.Count < settings.nrBranchClusters)
                {
                    settings.parentClusterBoolListList.Add(new boolList());
                }
                for (int _i = 0; _i < settings.nrBranchClusters; _i++)
                {
                    if (settings.parentClusterBoolListList[_i].b == null)
                    {
                        settings.parentClusterBoolListList[_i].b = new List<bool>();
                    }
                    while (settings.parentClusterBoolListList[_i].b.Count < _i + 1)
                    {
                        settings.parentClusterBoolListList[_i].b.Add(false);
                    }
                }

                for (int i = 0; i < settings.nrBranchClusters; i++)
                {
                    while (showBranchCluster.Count < settings.nrBranchClusters)
                    {
                        showBranchCluster.Add(true);
                    }
                    EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                    EditorGUI.indentLevel++;
                    //Debug.Log("showBranchCluster.Count: " + showBranchCluster.Count + "; i: " + i);
                    showBranchCluster[i] = EditorGUILayout.Foldout(showBranchCluster[i], "Branch cluster " + i, true);
                    

                    if (showBranchCluster[i] == true)
                    {

                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.LabelField("Parent Clusters"); // TODO: foldout... 
                        for (int n = 0; n < i + 1; n++)
                        {
                            if (n == 0)
                            {
                                //Debug.Log("parentClusterBoolListList.Count: " + settings.parentClusterBoolListList.Count + ", i: " + i);
                                settings.parentClusterBoolListList[i].b[n] = EditorGUILayout.Toggle("Stem", settings.parentClusterBoolListList[i].b[n]);
                            }
                            else
                            {
                                int m = n - 1;
                                settings.parentClusterBoolListList[i].b[n] = EditorGUILayout.Toggle("Branch cluster " + m, settings.parentClusterBoolListList[i].b[n]);
                            }
                        }
                        bool allFalse = true;
                        for (int n = 0; n < i + 1; n++)
                        {
                            if (settings.parentClusterBoolListList[i].b[n] == true)
                            {
                                allFalse = false;
                                break;
                            }
                        }
                        if (allFalse == true)
                        {
                            settings.parentClusterBoolListList[i].b[0] = true;
                        }

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
 
                        settings.taperFactorList[i] = EditorGUILayout.Slider("Taper factor", settings.taperFactorList[i], 0f, 1f);
 
                        settings.branchSettings[i].branchTaperCurve = EditorGUILayout.CurveField("taper curve", settings.branchSettings[i].branchTaperCurve);
                        if (GUILayout.Button("Reset taper curve"))
                        {
                            settings.branchSettings[i].branchTaperCurve = AnimationCurve.Linear(0f, 1f, 1f, 0f);
                        }

                        int ringResolution = EditorGUILayout.IntField("Ring resolution", settings.branchSettings[i].ringResolution);
                        if (ringResolution >= 3)
                        {
                            settings.branchSettings[i].ringResolution = ringResolution;
                        }
 
                        settings.branchSettings[i].branchesStartHeightGlobal = EditorGUILayout.Slider("Branches start height global", settings.branchSettings[i].branchesStartHeightGlobal, 0f, 1f);
                     
                        settings.branchSettings[i].branchesEndHeightGlobal = EditorGUILayout.Slider("Branches end height global", settings.branchSettings[i].branchesEndHeightGlobal, 0f, 1f);

                        if (i > 0)
                        {
                            settings.branchSettings[i].branchesStartHeightCluster = EditorGUILayout.Slider("Branches start height cluster", settings.branchSettings[i].branchesStartHeightCluster, 0f, 1f);

                            settings.branchSettings[i].branchesEndHeightCluster = EditorGUILayout.Slider("Branches end height cluster", settings.branchSettings[i].branchesEndHeightCluster, 0f, 1f);
                        }
 
                        settings.branchSettings[i].branchesStartPointVariation = EditorGUILayout.Slider("Branches start point variation", settings.branchSettings[i].branchesStartPointVariation, 0f, 1f);

                    }
                    EditorGUILayout.Space();
 
                    // Branch settings -> noise settings
                    while(showBranchClusterNoise.Count < settings.nrBranchClusters)
                    {
                        showBranchClusterNoise.Add(true);
                    }
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
                    while(showBranchClusterAngle.Count < settings.nrBranchClusters)
                    {
                        showBranchClusterAngle.Add(true);
                    }
                    showBranchClusterAngle[i] = EditorGUILayout.Foldout(showBranchClusterAngle[i], "Angle Settings", true);

                    if (showBranchClusterAngle[i] == true)
                    {
                        settings.branchSettings[i].verticalAngleCrownStart = EditorGUILayout.FloatField("Vertical angle crown start", settings. branchSettings[i].verticalAngleCrownStart);
                        settings.branchSettings[i].verticalAngleCrownEnd = EditorGUILayout.FloatField("Vertical angle crown end", settings.branchSettings[i].verticalAngleCrownEnd);
                        settings.branchSettings[i].verticalAngleBranchStart = EditorGUILayout.FloatField("Vertical angle branch start", settings.   branchSettings[i].verticalAngleBranchStart);
                        settings.branchSettings[i].verticalAngleBranchEnd = EditorGUILayout.FloatField("Vertical angle branch end", settings.branchSettings [i].verticalAngleBranchEnd);
    
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        branchAngleMode[i] = (angleMode)EditorGUILayout.EnumPopup("Branch angle mode", branchAngleMode[i]);
                        settings.branchSettings[i].branchAngleMode = (int)branchAngleMode[i];
                        if (branchAngleMode[i] == angleMode.symmetric)
                        {
                            settings.branchSettings[i].rotateAngleRange = EditorGUILayout.FloatField("Rotate angle range", settings.branchSettings[i].rotateAngleRange);
    
                            settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings.branchSettings[i].rotateAngleCrownStart);
                            settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings.branchSettings[i].rotateAngleCrownEnd);
                            settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.branchSettings[i].rotateAngleBranchStart);
                            settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.branchSettings [i].rotateAngleBranchEnd);
                        }
                        if (branchAngleMode[i] == angleMode.winding)
                        {
                            settings.branchSettings[i].useFibonacciAngles = EditorGUILayout.Toggle("Use Fibonacci angles", settings.branchSettings[i].useFibonacciAngles);
    
                            if (settings.branchSettings[i].useFibonacciAngles == true)
                            {
                                int fibonacciNr = EditorGUILayout.IntField("Fibonacci number", settings.branchSettings[i].fibonacciNr);
                                if (fibonacciNr >= 3)
                                {
                                    settings.branchSettings[i].fibonacciNr = fibonacciNr;
                                }
                                else
                                {
                                    settings.branchSettings[i].fibonacciNr = 3;
                                }
                            }
                            else
                            {
                                settings.branchSettings[i].rotateAngleRange = EditorGUILayout.FloatField("Rotate angle range", settings.branchSettings[i].rotateAngleRange);
                                settings.branchSettings[i].rotateAngleOffset = EditorGUILayout.FloatField("Rotate angle offset", settings.branchSettings[i].rotateAngleOffset);
    
                                settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings. branchSettings[i].rotateAngleCrownStart);
                                settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings. branchSettings[i].rotateAngleCrownEnd);
                                settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.branchSettings[i].rotateAngleBranchStart);
                                settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.   branchSettings[i].rotateAngleBranchEnd);
                            }
                        }
                        if (branchAngleMode[i] == angleMode.adaptiveWinding)
                        {
                            settings.branchSettings[i].rotateAngleCrownStart = EditorGUILayout.FloatField("Rotate angle crown start", settings. branchSettings[i].rotateAngleCrownStart);
                            settings.branchSettings[i].rotateAngleCrownEnd = EditorGUILayout.FloatField("Rotate angle crown end", settings.branchSettings   [i].rotateAngleCrownEnd);
                            settings.branchSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.       branchSettings[i].rotateAngleBranchStart);
                            settings.branchSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.branchSettings [i].rotateAngleBranchEnd);

                            settings.branchSettings[i].rotateAngleRangeFactor = EditorGUILayout.Slider("Rotate angle range factor", settings.branchSettings[i].rotateAngleRangeFactor, 0f, 2f);
                        }
                        EditorGUILayout.EndVertical();

                        float reducedCurveStepCutoff = EditorGUILayout.FloatField("Reduced curve step cutoff", settings.branchSettings[i].  reducedCurveStepCutoff);
                        if (reducedCurveStepCutoff >= 0f)
                        {
                            settings.branchSettings[i].reducedCurveStepCutoff = reducedCurveStepCutoff;
                        }
                        settings.branchSettings[i].reducedCurveStepFactor = EditorGUILayout.Slider("Reduced curve step factor", settings.branchSettings[i].reducedCurveStepFactor, 0f, 1f);

                        settings.branchSettings[i].branchGlobalCurvatureStart = EditorGUILayout.FloatField("Branch global curvature start", settings.branchSettings[i].branchGlobalCurvatureStart);
                        settings.branchSettings[i].branchGlobalCurvatureEnd = EditorGUILayout.FloatField("Branch global curvature end", settings.branchSettings[i].branchGlobalCurvatureEnd);
                        settings.branchSettings[i].branchCurvatureStart = EditorGUILayout.FloatField("Branch curvature start", settings.branchSettings[i].branchCurvatureStart);
                        settings.branchSettings[i].branchCurvatureEnd = EditorGUILayout.FloatField("Branch curvature end", settings.branchSettings[i].branchCurvatureEnd);
                        settings.branchSettings[i].branchCurvatureOffset = EditorGUILayout.FloatField("Branch curvature offset", settings.branchSettings[i].branchCurvatureOffset);
                        EditorGUILayout.Space();

                    }

                    while(showBranchClusterSplit.Count < settings.nrBranchClusters)
                    {
                        showBranchClusterSplit.Add(true);
                    }
                    // Branch settings -> split settings
                    showBranchClusterSplit[i] = EditorGUILayout.Foldout(showBranchClusterSplit[i], "Split Settings", true);

                    if (showBranchClusterSplit[i] == true)
                    {
                        settings.branchSettings[i].nrSplitsPerBranch = EditorGUILayout.FloatField("Nr splits per branch", settings.branchSettings[i].   nrSplitsPerBranch);
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        branchSplitMode[i] = (splitMode)EditorGUILayout.EnumPopup("Branch split mode", branchSplitMode[i]);
                        settings.branchSettings[i].branchSplitMode = (int)branchSplitMode[i];
                        if (branchSplitMode[i] == splitMode.rotateAngle)
                        {
                            settings.branchSettings[i].branchSplitRotateAngle = EditorGUILayout.FloatField("Branch split rotate angle", settings.   branchSettings[i].branchSplitRotateAngle);
                        }
                        else
                        {
                            settings.branchSettings[i].branchSplitAxisVariation = EditorGUILayout.FloatField("Branch split axis variation", settings.   branchSettings[i].branchSplitAxisVariation);
                        }
                        EditorGUILayout.EndVertical();
                        settings.branchSettings[i].branchSplitAngle = EditorGUILayout.FloatField("Branch split angle", settings.branchSettings[i].  branchSplitAngle);
                        settings.branchSettings[i].branchSplitPointAngle = EditorGUILayout.FloatField("Branch split point angle", settings.branchSettings[i].branchSplitPointAngle);
                        settings.branchSettings[i].splitsPerBranchVariation = EditorGUILayout.FloatField("Splits per branch variation", settings.   branchSettings[i].splitsPerBranchVariation);
                        settings.branchSettings[i].branchVariance = EditorGUILayout.FloatField("Branch variance", settings.branchSettings[i].   branchVariance);
                        settings.branchSettings[i].outwardAttraction = EditorGUILayout.FloatField("Outward attraction", settings.branchSettings[i]. outwardAttraction);
                        settings.branchSettings[i].branchSplitHeightVariation = EditorGUILayout.FloatField("Branch split height variation", settings.   branchSettings[i].branchSplitHeightVariation);
                        settings.branchSettings[i].branchSplitLengthVariation = EditorGUILayout.FloatField("Branch split length variation", settings.   branchSettings[i].branchSplitLengthVariation);

                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.BeginHorizontal();
                        if (GUILayout.Button("Add split level"))
                        {
                            settings.branchSettings[i].maxSplitHeightUsed += 1;
                            settings.branchSettings[i].branchSplitHeightInLevel.Add(0.5f);
                            Debug.Log("[" + i + "]: maxSplitHeightUsed: " + settings.branchSettings[i].maxSplitHeightUsed);
                        }
                        if (GUILayout.Button("Remove"))
                        {
                            if (settings.branchSettings[i].branchSplitHeightInLevel.Count > 0)
                            {
                                if (settings.branchSettings[i].maxSplitHeightUsed > 0)
                                {
                                    settings.branchSettings[i].maxSplitHeightUsed -= 1;
                                    settings.branchSettings[i].branchSplitHeightInLevel.RemoveAt(settings.branchSettings[i].branchSplitHeightInLevel.Count - 1);
                                }
                                else
                                {
                                    settings.branchSettings[i].branchSplitHeightInLevel.Clear();
                                }
                            }
                        }
                        EditorGUILayout.EndHorizontal();
                        
                        EditorGUILayout.LabelField("Max split height used: " + settings.branchSettings[i].maxSplitHeightUsed);

                        if (settings.branchSettings[i].maxSplitHeightUsed > 0)
                        {
                            for (int j = 0; j < settings.branchSettings[i].maxSplitHeightUsed; j++)
                            {
                                settings.branchSettings[i].branchSplitHeightInLevel[j] = EditorGUILayout.Slider("Level " + j, settings.branchSettings[i].branchSplitHeightInLevel[j], 0f, 1f);
                            }
                        }
                        else
                        {
                            for (int j = 0; j < settings.branchSettings[i].branchSplitHeightInLevel.Count; j++)
                            {
                                settings.branchSettings[i].branchSplitHeightInLevel[j] = EditorGUILayout.Slider("Level " + j, settings.branchSettings[i].branchSplitHeightInLevel[j], 0f, 1f);
                            }
                        }
                        
                        EditorGUI.indentLevel--;
                        EditorGUILayout.EndVertical();

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
                        settings.leafSettings.Add(new leafClusterSettings(settings.nrBranchClusters));
                        leafType.Add(branchTypes.single);
                        leafAngleMode.Add(angleModeLeaf.alternating);
                    }

                    if (GUILayout.Button("Remove"))
                    {
                        if (settings.leafSettings.Count > 0)
                        {
                            settings.nrLeafClusters -= 1;
                            settings.leafSettings.RemoveAt(settings.leafSettings.Count - 1);
                            leafType.RemoveAt(leafType.Count - 1);
                            leafAngleMode.RemoveAt(leafAngleMode.Count - 1);
                        }
                    }

                    EditorGUILayout.EndHorizontal();

                    for (int i = 0; i < settings.nrLeafClusters; i++)
                    {
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.LabelField("Leaf cluster " + i);
                        settings.leafSettings[i].leafDensity = EditorGUILayout.FloatField("Leaf density", settings.leafSettings[i].leafDensity);
                        settings.leafSettings[i].leafSize = EditorGUILayout.FloatField("Leaf size", settings.leafSettings[i].leafSize);
                        settings.leafSettings[i].leafAspectRatio = EditorGUILayout.FloatField("Leaf aspect ratio", settings.leafSettings[i].leafAspectRatio);
                        settings.leafSettings[i].leafStartHeightGlobal = EditorGUILayout.FloatField("Leaf start height global", settings.leafSettings[i].leafStartHeightGlobal);
                        settings.leafSettings[i].leafEndHeightGlobal = EditorGUILayout.FloatField("Leaf end height global", settings.leafSettings[i].leafEndHeightGlobal);
                        settings.leafSettings[i].leafStartHeightCluster = EditorGUILayout.FloatField("Leaf start height cluster", settings.leafSettings[i].leafStartHeightCluster);
                        settings.leafSettings[i].leafEndHeightCluster = EditorGUILayout.FloatField("Leaf end height cluster", settings.leafSettings[i].leafEndHeightCluster);
                        Debug.Log("leafType.Count: " + leafType.Count + ", nrLeafClusters: " + settings.nrLeafClusters);
                        leafType[i] = (branchTypes)EditorGUILayout.EnumPopup("Leaf type", leafType[i]);
                        settings.leafSettings[i].leafType = (int)leafType[i];
                        if (leafType[i] == branchTypes.whorled)
                        {
                            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                            settings.leafSettings[i].leafWhorlCount = EditorGUILayout.IntField("Leaf whorl count", settings.leafSettings[i].leafWhorlCount);
                            EditorGUILayout.EndVertical();
                        }
                        leafAngleMode[i] = (angleModeLeaf)EditorGUILayout.EnumPopup("Leaf angle mode", leafAngleMode[i]);
                        settings.leafSettings[i].leafAngleMode = (int)leafAngleMode[i];

                        settings.leafSettings[i].verticalAngleBranchStart = EditorGUILayout.FloatField("Vertical angle branch start", settings.leafSettings[i].verticalAngleBranchStart);
                        settings.leafSettings[i].verticalAngleBranchEnd = EditorGUILayout.FloatField("Vertical angle branch end", settings.leafSettings[i].verticalAngleBranchEnd);
                        settings.leafSettings[i].rotateAngleBranchStart = EditorGUILayout.FloatField("Rotate angle branch start", settings.leafSettings[i].rotateAngleBranchStart);
                        settings.leafSettings[i].rotateAngleBranchEnd = EditorGUILayout.FloatField("Rotate angle branch end", settings.leafSettings[i].rotateAngleBranchEnd);
                        settings.leafSettings[i].tiltAngleBranchStart = EditorGUILayout.FloatField("Tilt angle branch start", settings.leafSettings[i].tiltAngleBranchStart);
                        settings.leafSettings[i].tiltAngleBranchEnd = EditorGUILayout.FloatField("Tilt angle branch end", settings.leafSettings[i].tiltAngleBranchEnd);
                        
                        EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                        EditorGUILayout.LabelField("Parent Clusters"); // TODO: foldout... 
                        for (int n = 0; n < settings.leafSettings[i].leafParentClusters.Count; n++)
                        {
                            if (n == 0)
                            {
                                settings.leafSettings[i].leafParentClusters[n] = EditorGUILayout.Toggle("Stem", settings.leafSettings[i].leafParentClusters[n]);
                            }
                            else
                            {
                                int m = n - 1;
                                settings.leafSettings[i].leafParentClusters[n] = EditorGUILayout.Toggle("Branch cluster " + m, settings.leafSettings[i].leafParentClusters[n]);
                            }
                        }
                        bool allFalse = true;
                        for (int n = 0; n < settings.leafSettings[i].leafParentClusters.Count; n++)
                        {
                            if (settings.leafSettings[i].leafParentClusters[n] == true)
                            {
                                allFalse = false;
                                break;
                            }
                        }
                        if (allFalse == true)
                        {
                            settings.leafSettings[i].leafParentClusters[0] = true;
                        }

                        EditorGUILayout.EndVertical();

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

        private void SaveSettingsToJson(treeSettings settings)
        {
            for (int i = 0; i < settings.nrBranchClusters; i++)
            {
                while (settings.branchSettings[i].branchSplitHeightInLevel.Count > settings.branchSettings[i].maxSplitHeightUsed)
                {
                    settings.branchSettings[i].branchSplitHeightInLevel.RemoveAt(settings.branchSettings[i].branchSplitHeightInLevel.Count - 1);
                }
            }

            try
            {
                string jsonString = JsonUtility.ToJson(settings, true);
                string defaultName = "treeSettings.json";
                string path = EditorUtility.SaveFilePanel("Save Tree Settings", Application.dataPath, defaultName, "json");
                if (string.IsNullOrEmpty(path))
                {
                    return; // user cancelled
                }
                File.WriteAllText(path, jsonString);
                EditorUtility.DisplayDialog("Save Settings", "Settings saved to:\n" + path, "OK");
            }
            catch (System.Exception e)
            {
                EditorUtility.DisplayDialog("Save Settings - Error", "Failed to save settings:\n" + e.Message, "OK");
            }
        }

        private void LoadSettingsFromJson()
        {
            try
            {
                string path = EditorUtility.OpenFilePanel("Load Tree Settings", "", "json");
                if (path.Length != 0)
                {
                    string jsonString = File.ReadAllText(path);
                    settings = new treeSettings();
                    JsonUtility.FromJsonOverwrite(jsonString, settings);
                    if (settings.parentClusterBoolListList == null) 
                    {
                        settings.parentClusterBoolListList = new List<boolList>();
                    }
                    if (settings.branchSettings == null) 
                    {
                        settings.branchSettings = new List<branchClusterSettings>();
                    }
                    if (settings.taperFactorList == null) 
                    {
                        settings.taperFactorList = new List<float>();
                    }
                    if (settings.leafSettings == null) 
                    {
                        settings.leafSettings = new List<leafClusterSettings>();
                    }

                    while (settings.branchSettings.Count < settings.nrBranchClusters)
                    {
                        settings.branchSettings.Add(new branchClusterSettings());
                    }
                    while (settings.taperFactorList.Count < settings.nrBranchClusters)
                    {
                        settings.taperFactorList.Add(1f);
                    }
                    while (settings.parentClusterBoolListList.Count < settings.nrBranchClusters)
                    {
                        settings.parentClusterBoolListList.Add(new boolList());
                    }

                    for (int i = 0; i < settings.nrBranchClusters; i++)
                    {
                        if (settings.parentClusterBoolListList[i].b == null)
                        {
                            settings.parentClusterBoolListList[i].b = new List<bool>();
                        }
                        while (settings.parentClusterBoolListList[i].b.Count < i + 1)
                        {
                            settings.parentClusterBoolListList[i].b.Add(false);
                        }

                        // guarantee at least the "Stem" entry is true
                        bool anyTrue = false;
                        for (int n = 0; n < settings.parentClusterBoolListList[i].b.Count; n++)
                        {
                            if (settings.parentClusterBoolListList[i].b[n])
                            {
                                anyTrue = true;
                                break;
                            }
                        }
                        if (!anyTrue)
                        {
                            settings.parentClusterBoolListList[i].b[0] = true;
                        }
                    }

                    foreach (var leafCluster in settings.leafSettings)
                    {
                        if (leafCluster.leafParentClusters == null)
                        {
                            leafCluster.leafParentClusters = new List<bool>();
                        }
                        while (leafCluster.leafParentClusters.Count < settings.nrBranchClusters + 1)
                        {
                            leafCluster.leafParentClusters.Add(false);
                        }
                        if (!leafCluster.leafParentClusters.Contains(true))
                        {
                            Debug.Log("leaf parentCluste.Count: " + leafCluster.leafParentClusters.Count);
                            leafCluster.leafParentClusters[0] = true;
                        }
                    }

                    while (treeShape.Count < settings.nrBranchClusters)
                        treeShape.Add(shape.conical);
                    while (branchShape.Count < settings.nrBranchClusters)
                        branchShape.Add(shape.conical);
                    while (branchType.Count < settings.nrBranchClusters)
                        branchType.Add(branchTypes.single);
                    while (branchAngleMode.Count < settings.nrBranchClusters)
                        branchAngleMode.Add(angleMode.winding);
                    while (branchSplitMode.Count < settings.nrBranchClusters)
                        branchSplitMode.Add(splitMode.rotateAngle);
                    

                    while (leafType.Count < settings.nrLeafClusters)
                        leafType.Add(branchTypes.single);
                    while (leafAngleMode.Count < settings.nrLeafClusters)
                        leafAngleMode.Add(angleModeLeaf.alternating);
                    
                    while (treeShape.Count > settings.nrBranchClusters)
                        treeShape.RemoveAt(treeShape.Count - 1);
                    while (branchShape.Count > settings.nrBranchClusters)
                        branchShape.RemoveAt(branchShape.Count - 1);
                    while (branchType.Count > settings.nrBranchClusters)
                        branchType.RemoveAt(branchType.Count - 1);
                    while (branchAngleMode.Count > settings.nrBranchClusters)
                        branchAngleMode.RemoveAt(branchAngleMode.Count - 1);
                    while (branchSplitMode.Count > settings.nrBranchClusters)
                        branchSplitMode.RemoveAt(branchSplitMode.Count - 1);

                    while (leafType.Count > settings.nrLeafClusters)
                        leafType.RemoveAt(leafType.Count - 1);
                    while (leafAngleMode.Count > settings.nrLeafClusters)
                        leafAngleMode.RemoveAt(leafAngleMode.Count - 1);

                    for (int i = 0; i < settings.nrBranchClusters; i++)
                    {
                        treeShape[i] = (shape)settings.branchSettings[i].treeShape;
                        branchShape[i] = (shape)settings.branchSettings[i].branchShape;
                        branchType[i] = (branchTypes)settings.branchSettings[i].branchType;
                        branchAngleMode[i] = (angleMode)settings.branchSettings[i].branchAngleMode;
                        branchSplitMode[i] = (splitMode)settings.branchSettings[i].branchSplitMode;
                    }
                    for (int i = 0; i < settings.nrLeafClusters; i++)
                    {
                        leafType[i] = (branchTypes)settings.leafSettings[i].leafType;
                        leafAngleMode[i] = (angleModeLeaf)settings.leafSettings[i].leafAngleMode;
                    }

                }
            }
            catch (System.Exception e)
            {
                Debug.LogError(e.Message);
                EditorUtility.DisplayDialog("Load Settings - Error", "Failed to load settings:\n" + e.Message, "OK");
            }
        }

    }


}