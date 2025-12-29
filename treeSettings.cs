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
        public float relBranchLength;
        public float relBranchLengthVariation;
        public float taperFactor;
        public int ringResolution;
        public float branchesStartHeightGlobal;
        public float branchesEndHeightGlobal;
        public float branchesStartHeightCluster;
        public float branchesEndHeightCluster;
        public float branchesStartPointVariation;

        public float noiseAmplitudeHorizontalBranch;
        public float noiseAmplitudeVerticalBranch;
        public float noiseAmplitudeBranchGradient;
        public float noiseAmplitudeExponent;
        public float noiseScale;

        public float verticalAngleCrownStart;
        public float verticalAngleCrownEnd;
        public float verticalAngleBranchStart;
        public float verticalAngleBranchEnd;
        public int branchAngleMode;
        public float rotateAngleRange;
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
        public float branchSplitRotateAnlge;
        public float branchSplitAxisVariation;
        public float branchSplitAngle;
        public float branchSplitPointAngle;
        public float splitsPerBranchVariation;
        public float branchVariance;
        public float outwardAttraction;
        public float branchSplitHeightVariation;
        public float branchSplitLengthVariation;




        public branchClusterSettings()
        {
            nrBranches = 0;
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
        public float tiltAnlgeBranchEnd;


        public leafClusterSettings()
        {
            leafDensity = 0f;
        }
    }

    public class treeSettings
    {
        public float treeHeight;
        public Vector3 treeGrowDir;
        public float taper;
        public float branchTipRadius;
        public float ringSpacing;
        public int stemRingRes;
        public float resampleDistance;

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
        public float splitHeightVariation;
        public float splitLengthVariation;
        public float stemSplitAngle;
        public float stemSplitPointAngle;

        public int nrBranchClusters;
        public List<branchClusterSettings> branchSettings;

        public int nrLeafClusters;
        public List<leafClusterSettings> leafSettings;


        public treeSettings()
        {
            Debug.Log("initialising treeSettings");
            branchSettings = new List<branchClusterSettings>();
            leafSettings = new List<leafClusterSettings>();
        }
    }


}
