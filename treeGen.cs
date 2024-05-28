using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class treeGen : MonoBehaviour
{
    public float stemRadius;
    public int stemRingResolution; // #vertices = 2 * stemRingResolution
    
    public float length;
    public float ringSpacing;

    public List<Vector3> vertices;
    public List<int> triangles;

    public GameObject selfGameObject;
    public Mesh mesh;
    public MeshFilter meshFilter;

    // Start is called before the first frame update
    void Start()
    {
        meshFilter = GetComponent<MeshFilter>();

        mesh = new Mesh();

        // TODO: spline!!! -> branch segment class! start direction, curvature, branch angle...

        for (int j = 0; j <= (int)(length / ringSpacing); j++)
        {
            for (int i = 0; i < 2 * stemRingResolution; i++)
            {
                float angle = (Mathf.PI / (float)stemRingResolution) * (float)i;

                Vector3 v = new Vector3(stemRadius * ((length / ringSpacing) - (float)j) * Mathf.Cos(angle), 
                                       (float)j * ringSpacing, 
                                       stemRadius * ((length / ringSpacing) - (float)j) * Mathf.Sin(angle));
                
                vertices.Add(v);
            }
        }

        for (int j = 0; j < (int)(length / ringSpacing); j++)
        {
            for (int i = 0; i < 2 * stemRingResolution; i++)
            {
                if (j % 2 == 1)
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                    else
                    {
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                }
                else
                {
                    if (i % 2 == 1)
                    {
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));

                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                    }
                    else
                    {
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + i);
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);

                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + ((i + 1) % (2 * stemRingResolution)));
                        triangles.Add(j * 2 * stemRingResolution + (i + 1) % (2 * stemRingResolution));
                        triangles.Add(j * 2 * stemRingResolution + 2 * stemRingResolution + i);
                    }
                }
            }
        }

        mesh.SetVertices(vertices);
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;
    }

    void generateTree()
    {

    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        foreach (Vector3 v in vertices)
        {
            Gizmos.DrawSphere(v, 0.005f);
        }
    }


    // Update is called once per frame
    void Update()
    {
        
    }
}
