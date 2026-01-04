//using System.Numerics;
//using System.Numerics;
using UnityEngine;
using System.Collections.Generic;

namespace treeGenNamespace
{
    public class branchClusterSettings
    {
        public int nrBranches;
        public int treeShape;
        public int branchShape;
        public int branchType;
        public int whorlCountStart;
        public int whorlCountEnd;
        public float relBranchLength = 1f;
        public float relBranchLengthVariation;
        public int ringResolution = 6;
        public float branchesStartHeightGlobal;
        public float branchesEndHeightGlobal = 1f;
        public float branchesStartHeightCluster;
        public float branchesEndHeightCluster = 1f;
        public float branchesStartPointVariation;

        public float noiseAmplitudeHorizontalBranch;
        public float noiseAmplitudeVerticalBranch;
        public float noiseAmplitudeBranchGradient;
        public float noiseAmplitudeExponent = 1f;
        public float noiseScale = 1f;

        public float verticalAngleCrownStart;
        public float verticalAngleCrownEnd;
        public float verticalAngleBranchStart;
        public float verticalAngleBranchEnd;
        public int branchAngleMode;
        public float rotateAngleRange = 180f;
        public float rotateAngleOffset;
        public float rotateAngleCrownStart;
        public float rotateAngleCrownEnd;
        public float rotateAngleBranchStart;
        public float rotateAngleBranchEnd;
        public bool useFibonacciAngles;
        public int fibonacciNr;
        public float rotateAngleRangeFactor;
        public float reducedCurveStepCutoff;
        public float reducedCurveStepFactor;
        public float branchGlobalCurvatureStart;
        public float branchGlobalCurvatureEnd;
        public float branchCurvatureStart;
        public float branchCurvatureEnd;
        public float branchCurvatureOffset;

        public float nrSplitsPerBranch;
        public int branchSplitMode;
        public float branchSplitRotateAngle;
        public float branchSplitAxisVariation;
        public float branchSplitAngle;
        public float branchSplitPointAngle;
        public float splitsPerBranchVariation;
        public float branchVariance;
        public float outwardAttraction;
        public float branchSplitHeightVariation;
        public float branchSplitLengthVariation;
        public List<float> branchSplitHeightInLevel;
        public int maxSplitHeightUsed;



        public branchClusterSettings()
        {
            nrBranches = 0;
            branchSplitHeightInLevel = new List<float>();
        }
    }

    public class leafClusterSettings
    {
        public float leafDensity;
        public float leafSize;
        public float leafAspectRatio;
        public float leafStartHeightGlobal;
        public float leafEndHeightGlobal;
        public float leafStartHeightCluster;
        public float leafEndHeightCluster;
        public int leafType;
        public int leafWhorlCount;
        public int leafAngleMode;
        public float verticalAngleBranchStart;
        public float verticalAngleBranchEnd;
        public float rotateAngleBranchStart;
        public float rotateAngleBranchEnd;
        public float tiltAngleBranchStart;
        public float tiltAngleBranchEnd;
        public List<bool> leafParentClusters;


        public leafClusterSettings(int n)
        {
            leafDensity = 0f;
            leafParentClusters = new List<bool>();
            for (int i = 0; i <= n; i++)
            {
                if (i == 0)
                {
                    leafParentClusters.Add(true);
                }
                else
                {
                    leafParentClusters.Add(false);
                }
            }
        }
    }

    public class treeSettings
    {
        public float treeHeight = 10f;
        public Vector3 treeGrowDir = new Vector3(0f, 1f, 0f);
        public float taper = 0.1f;
        public List<float> taperFactorList;
        public UnityEngine.AnimationCurve taperCurve = UnityEngine.AnimationCurve.Linear(0f, 1f, 1f, 0f);
        public float branchTipRadius = 0.2f;
        public float ringSpacing = 1f;
        public int stemRingResolution = 6;
        public float resampleDistance = 2f;

        public float noiseAmplitudeVertical;
        public float noiseAmplitudeHorizontal;
        public float noiseAmplitudeGradient;
        public float noiseAmplitudeExponent;
        public float noiseScale;
        public int seed;

        public float curvatureStart;
        public float curvatureEnd;

        public int nrSplits;
        public float variance;
        public int stemSplitMode;
        public float stemSplitRotateAngle;
        public float curvOffsetStrength;
        public List<float> stemSplitHeightInLevel;
        public float splitHeightVariation;
        public float splitLengthVariation;
        public float stemSplitAngle = 30f;
        public float stemSplitPointAngle = 30f;
        public int maxSplitHeightUsed;

        public int nrBranchClusters;
        public List<List<bool>> parentClusterBoolListList;
        public List<branchClusterSettings> branchSettings;

        public int nrLeafClusters;
        public List<leafClusterSettings> leafSettings;


        public treeSettings()
        {
            Debug.Log("initialising treeSettings");
            stemSplitHeightInLevel = new List<float>();
            parentClusterBoolListList = new List<List<bool>>();
            taperFactorList = new List<float>();
            branchSettings = new List<branchClusterSettings>();
            leafSettings = new List<leafClusterSettings>();
        }
    }


}
