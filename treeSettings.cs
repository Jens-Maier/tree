//using System.Numerics;
using UnityEngine;

namespace treeGenNamespace
{
public class treeSettings
{
    public int stemRingRes;
    public float taper;
    public Vector3 treeGrowDir;
    public float height;

    public treeSettings()
    {
        stemRingRes = 6;
        Debug.Log("initialising treeSettings: stemRingRes = 6");
    }
}


}
