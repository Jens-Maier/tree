
using System.Collections.Generic;
using System.Numerics;
using System;
using System.Security.AccessControl;
using System.Security.Cryptography.X509Certificates;
using UnityEngine;
using System.Drawing;

namespace treeGenNamespace
{

    public class segment
    {
        public int clusterIndex;
        public UnityEngine.Vector3 start;
        public UnityEngine.Vector3 end;
        public UnityEngine.Vector3 firstTangent;
        public UnityEngine.Vector3 startTangent;
        public UnityEngine.Vector3 endTangent;
        public UnityEngine.Vector3 startCotangent;
        public UnityEngine.Vector3 endCotangent;
        public float startRadius;
        public float endRadius;
        public float startTvalGlobal;
        public float endTvalGlobal;
        public float startTvalBranch;
        public float endTvalBranch;
        public int ringResolution;
        public bool connectedToPrevious;
        public float branchLength;
        public float longestBranchLengthInCluster;
        public float startTaper;
        public float endTaper;

        public segment(int ClusterIndex, UnityEngine.Vector3 Start, UnityEngine.Vector3 End, UnityEngine.Vector3 FirstTangent, UnityEngine.Vector3 StartTangent, UnityEngine.Vector3 EndTangent, UnityEngine.Vector3 StartCotangent, UnityEngine.Vector3 EndCotangent, float StartRadius, float EndRadius, float StartTvalGlobal, float EndTvalGlobal, float StartTvalBranch, float EndTvalBranch, int RingResolution, bool ConnectedToPrevious, float BranchLength, float LongestBranchLengthInCluster, float StartTaper, float EndTaper)
        {
            clusterIndex = ClusterIndex;
            start = Start;
            end = End;
            firstTangent = FirstTangent;
            startTangent = StartTangent;
            endTangent = EndTangent;
            startCotangent = StartCotangent;
            endCotangent = EndCotangent;
            startRadius = StartRadius;
            endRadius = EndRadius;
            startTvalGlobal = StartTvalGlobal;
            endTvalGlobal = EndTvalGlobal;
            startTvalBranch = StartTvalBranch;
            endTvalBranch = EndTvalBranch;
            ringResolution = RingResolution;
            connectedToPrevious = ConnectedToPrevious;
            branchLength = BranchLength;
            longestBranchLengthInCluster = LongestBranchLengthInCluster;
            startTaper = StartTaper;
            endTaper = EndTaper;
        }
    }

    public class node
    {
        public UnityEngine.Vector3 point;
        public float radius;
        public List<UnityEngine.Vector3> tangent;
        public UnityEngine.Vector3 cotangent;
        public int clusterIndex;
        public int ringResolution;
        public float taper;
        public float tValGlobal;
        public float tValBranch;
        public List<node> next;
        public List<List<node>> branches;
        public float branchLength;
        public bool isLastRotated = false;
        public List<UnityEngine.Vector3> outwardDir;
        public List<float> rotateAngleRange;


        public node(UnityEngine.Vector3 Point, float Radius, UnityEngine.Vector3 Cotangent, int ClusterIndex, int RingResolution, float Taper, float TvalGlobal, float TvalBranch,  float BranchLength)
        {
            point = Point;
            radius = Radius;
            tangent = new List<UnityEngine.Vector3>();
            cotangent = Cotangent;
            clusterIndex = ClusterIndex;
            ringResolution = RingResolution;
            taper = Taper;
            tValGlobal = TvalGlobal;
            tValBranch = TvalBranch;
            next = new List<node>();
            branches = new List<List<node>>();
            branchLength = BranchLength;
            isLastRotated = false;
            outwardDir = new List<UnityEngine.Vector3>();
            rotateAngleRange = new List<float>();
        }

        public void getAllSegments(node rootNode, List<segment> segments, bool connectedToPrev)
        {
            Debug.Log("in getAllSegments: point: " + point + ", next.Count: " + next.Count);
            //for n, nextNode in enumerate(self.next):
            //    longestBranchLengthInCluster = 1.0
            int n = 0;
            foreach (node nextNode in next)
            {
                if (next.Count > 1)
                {
                    Debug.Log("adding segment");
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[n + 1], 
                                            nextNode.tangent[0], 
                                            cotangent, 
                                            nextNode.cotangent, 
                                            radius, 
                                            nextNode.radius, 
                                            tValGlobal, 
                                            nextNode.tValGlobal, 
                                            tValBranch, 
                                            nextNode.tValBranch, 
                                            ringResolution, 
                                            false, 
                                            branchLength, 
                                            1f, // longestBranchLengthInCluster, 
                                            taper, 
                                            nextNode.taper));
                }
                else
                {
                    Debug.Log("adding segment: point: " + point);
                    Debug.Log("segments count before: " + segments.Count);
                    segments.Add(new segment(clusterIndex, 
                                            point, 
                                            nextNode.point, 
                                            tangent[0], // -> firstTangent = self.tangent[0] 
                                            tangent[0], 
                                            nextNode.tangent[0], 
                                            cotangent, 
                                            nextNode.cotangent, 
                                            radius, 
                                            nextNode.radius, 
                                            tValGlobal, 
                                            nextNode.tValGlobal, 
                                            tValBranch, 
                                            nextNode.tValBranch, 
                                            ringResolution, 
                                            connectedToPrev, 
                                            branchLength, 
                                            1f, // longestBranchLengthInCluster, 
                                            taper, 
                                            nextNode.taper));

                    nextNode.getAllSegments(rootNode, segments, true);
                }
                n += 1;
            }
        
            foreach (List<node> branchList in branches)
            {
                foreach (node b in branchList)
                {
                    b.getAllSegments(rootNode, segments, false);
                }
            }
        }
    }

    public class treeGenerator : MonoBehaviour
    {
        public treeSettings settings;
        public List<node> nodes;

        public List<segment> segments;

        public List<UnityEngine.Vector3> vertices = new List<UnityEngine.Vector3>();


        // nodes.append(node(Vector((0.0,0.0,0.0)), 0.1, Vector((1.0,0.0,0.0)), -1, stemRingRes, taper, 0.0, 0.0, height))
        // nodes[0].tangent.append(Vector((0.0,0.0,1.0)))
        // nodes[0].cotangent = Vector((1.0,0.0,0.0))
        // nodes.append(node(dir * height, 0.1, Vector((1.0,0.0,0.0)), -1, stemRingRes, taper, 1.0, 0.0, height))
        // nodes[1].tangent.append(Vector((0.0,0.0,1.0)))
        // nodes[1].cotangent = Vector((1.0,0.0,0.0))
        // nodes[0].next.append(nodes[1])
        // nodes[0].outwardDir.append(nodes[0].cotangent)
        // nodes[0].rotateAngleRange.append(math.pi)
        // nodes[1].outwardDir.append(nodes[0].cotangent)
        // nodes[1].rotateAngleRange.append(math.pi)


        public void generateTree()
        {
            Debug.Log("generateTree() in treeGenerator.cs");
            //settings = new treeSettings();
            nodes = new List<node>();
            nodes.Add(new node(new UnityEngine.Vector3(0f, 0f, 0f), 
                               0.1f, 
                               new UnityEngine.Vector3(1f, 0f, 0f), 
                               -1, 
                               settings.stemRingRes, 
                               settings.taper, 
                               0f, 
                               0f, 
                               settings.treeHeight));
    
            nodes[0].tangent.Add(new UnityEngine.Vector3(0f, 1f, 0f));
            nodes[0].cotangent = new UnityEngine.Vector3(1f, 0f, 0f);
    
            nodes.Add(new node(settings.treeGrowDir * settings.treeHeight, 
                               0.1f, 
                               new UnityEngine.Vector3(1f, 0f, 0f), 
                               -1, 
                               settings.stemRingRes, 
                               settings.taper, 
                               1.0f, 
                               0.0f, 
                               settings.treeHeight));
            
            nodes[1].tangent.Add(new UnityEngine.Vector3(0f, 1f, 0f));
            nodes[1].cotangent = new UnityEngine.Vector3(1f, 0f, 0f);

            nodes[0].next.Add(nodes[1]);

            Debug.Log("settings.treeGrowDir: " + settings.treeGrowDir);
            Debug.Log("settings.treeHeight: " + settings.treeHeight);

            foreach (node n in nodes)
            {
                Debug.Log("node: point: " + n.point);
            }

            segments = new List<segment>();
            nodes[0].getAllSegments(nodes[0], segments, false);

            foreach (segment s in segments)
            {
                Debug.Log("segment: start: " + s.start);
                Debug.Log("segment: end: " + s.end);
            }

            generateVerticesAndTriangles(segments, settings.ringSpacing, settings.branchTipRadius);
        }

        void generateVerticesAndTriangles(List<segment> segments, float ringSpacing, float branchTipRadius)
        {
            Debug.Log("in generateVerticesAndTriangles()");
            //List<UnityEngine.Vector3> vertices = new List<UnityEngine.Vector3>();
            vertices = new List<UnityEngine.Vector3>();
            List<UnityEngine.Vector3> normals = new List<UnityEngine.Vector3>();
            List<float> vertexTvalGlobal = new List<float>();
            List<float> vertexTvalBranch = new List<float>();
            List<float> ringAngle = new List<float>();
            List<int> triangles = new List<int>();

            int offset = 0;
            int counter = 0;

            int startSection = 0;

            for (int s = 0; s < segments.Count; s++)
            {
                float segmentLength = length(segments[s].end - segments[s].start);
                if (segmentLength > 0f)
                {
                    int sections = (int)MathF.Round(segmentLength / ringSpacing);
                    if (sections <= 0)
                    {
                        sections = 1;
                    }
                    float branchRingSpacing = segmentLength / sections;

                    if (s > 0)
                    {
                        if (segments[s].connectedToPrevious == true && segments[s - 1].connectedToPrevious == false) // only on first segment
                        {
                            startSection = 1;
                            offset -= segments[s].ringResolution + 1;
                        }

                        if (segments[s].connectedToPrevious == false)
                        {
                            startSection = 0;
                            offset = vertices.Count;
                        }
                    }

                    UnityEngine.Vector3 controlPt1 = segments[s].start + norm(segments[s].startTangent) * (segments[s].end - segments[s].start).magnitude / 3f;
                    UnityEngine.Vector3 controlPt2 = segments[s].end - norm(segments[s].endTangent) * (segments[s].end - segments[s].start).magnitude / 3f;

                    for (int section = startSection; section < sections + 1; section++)
                    {
                        UnityEngine.Vector3 pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / (float)sections);
                        UnityEngine.Vector3 tangent = sampleSplineTangentC(segments[s].start, controlPt1, controlPt2, segments[s].end, section / (float)sections);

                        if (section == 0)
                        {
                            tangent = segments[s].firstTangent;
                        }

                        UnityEngine.Vector3 dirA = lerp(segments[s].startCotangent, segments[s].endCotangent, section / (float)sections);
                        UnityEngine.Vector3 dirB = norm(UnityEngine.Vector3.Cross(tangent, dirA));
                        dirA = norm(UnityEngine.Vector3.Cross(dirB, tangent));

                        float tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (section / (float)sections);
                        float tValBranch = segments[s].startTvalBranch + (segments[s].endTvalBranch - segments[s].startTvalBranch) * (section / (float)sections);
                        float radius = 0f;
                        if (segments[s].clusterIndex == -1)
                        {
                            float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing));
                            // TODO: taper curve...
                            float normalizedCurve = (1f - branchTipRadius) * tVal + 1.0f - tVal;
                            radius = linearRadius * normalizedCurve;
                        }
                        else
                        {
                            float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, section / (segmentLength / branchRingSpacing));
                            // TODO: taper curve...
                            float normalizedCurve = (1f - branchTipRadius) * tVal + 1.0f - tValBranch;
                            radius = linearRadius * normalizedCurve;
                        }

                        for (int i = 0; i < segments[s].ringResolution + 1; i++)
                        {
                            float angle = 2f * MathF.PI * i / segments[s].ringResolution;
                            UnityEngine.Vector3 normalVector = dirA * radius * MathF.Cos(angle) + dirB * radius * MathF.Sin(angle);
                            UnityEngine.Vector3 v = pos + normalVector;

                            vertices.Add(v);
                            normals.Add(normalVector);
                            vertexTvalGlobal.Add(tVal);
                            if (segments[s].clusterIndex == -1)
                            {
                                vertexTvalBranch.Add(tVal);
                            }
                            else
                            {
                                vertexTvalBranch.Add(tValBranch);
                            }
                            ringAngle.Add(angle);

                            counter += 1;
                        }
                    }

                    for (int c = 0; c < sections; c++)
                    {
                        float tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / (float)sections);
                        float nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / (float)sections);

                        UnityEngine.Vector3 pos = sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / (float)sections);

                        float linearRadius = lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing));
                        // TODO: taper curve...
                        float normalizedCurve = (1f - branchTipRadius) * tVal + 1f - tVal;
                        float radius = linearRadius * normalizedCurve;

                        for (int j = 0; j < segments[s].ringResolution; j++)
                        {
                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + j);
                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1));
                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + (j + 1) % (segments[s].ringResolution + 1));

                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + j);
                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + (j + 1) % (segments[s].ringResolution + 1));
                            triangles.Add(offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + j);
                        }
                    }
                }
            }
            /*  
                for c in range(0, sections): 
                    tVal = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * (c / sections)
                    nextTval = segments[s].startTvalGlobal + (segments[s].endTvalGlobal - segments[s].startTvalGlobal) * ((c + 1) / sections)
                    
                    pos = treegen_utils.sampleSplineC(segments[s].start, controlPt1, controlPt2, segments[s].end, c / sections)
                    
                    linearRadius = treegen_utils.lerp(segments[s].startRadius, segments[s].endRadius, c / (segmentLength / branchRingSpacing))

                    if context.scene.treeSettings.useStemTaperCurve == True:
                        normalizedCurve = (1.0 - branchTipRadius) * tVal + treegen_utils.sampleCurveStem(treeGen, tVal)
                    else:
                        normalizedCurve = (1.0 - branchTipRadius) * tVal + 1.0 - tVal
                    
                    radius = linearRadius * normalizedCurve
                    
                    for j in range(0, segments[s].ringResolution):
                        faces.append((offset + c * (segments[s].ringResolution + 1) + j,
                                      offset + c * (segments[s].ringResolution + 1) + (j + 1) % (segments[s].ringResolution + 1), 
                                      offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + (j + 1) % (segments[s].ringResolution + 1), 
                                      offset + c * (segments[s].ringResolution + 1) + segments[s].ringResolution + 1 + j))
                        
                        #faceUVdata = []
                        #faceUVdata.append((uvStartOffset + ( j      * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength , (0 + c) / sections)) # 0
                        
                        #faceUVdata.append((uvStartOffset + ((j + 1) * radius + (segments[s].ringResolution / 2.0) * (startRadius - radius)) / segmentLength, (0 + c) / sections)) # 1
                        
                        #faceUVdata.append((uvStartOffset + ((j + 1) * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 7
                        
                        #faceUVdata.append((uvStartOffset + ( j      * nextRadius + (segments[s].ringResolution / 2.0) * (startRadius - nextRadius)) / segmentLength, (1 + c) / sections)) # 6
                        
                        #faceUVs.append(faceUVdata)
                
                #uvStartOffset += segments[s].startRadius * segments[s].ringResolution / segmentLength
                offset += counter
                counter = 0
            
        meshData = bpy.data.meshes.new("treeMesh")
        meshData.from_pydata(vertices, [], faces)
        
        ############################################################    
        custom_normals = [None] * len(meshData.loops)
        
        for poly in meshData.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = meshData.loops[loop_index].vertex_index
                custom_normals[loop_index] = normals[vertex_index]  # Your custom normal !!
    
        meshData['use_auto_smooth'] = True
        meshData.normals_split_custom_set(custom_normals)
        
        bmesh_obj = bmesh.new()
        bmesh_obj.from_mesh(meshData)
        
        for i, vertex in enumerate(bmesh_obj.verts):
            vertex.normal = normals[i]
        #############################################################
        # Update the mesh with the new normals
        bmesh_obj.to_mesh(meshData)
        bmesh_obj.free()
        meshData.update()
        
        
        #if len(meshData.uv_layers) == 0:
        #    meshData.uv_layers.new()
        
        #uvLayer = meshData.uv_layers.active
        #for i, face in enumerate(faces):
        #    uvLayer.data[meshData.polygons[i].loop_indices[0]].uv = (faceUVs[i][0][0], faceUVs[i][0][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[1]].uv = (faceUVs[i][1][0], faceUVs[i][1][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[2]].uv = (faceUVs[i][2][0], faceUVs[i][2][1])
        #    uvLayer.data[meshData.polygons[i].loop_indices[3]].uv = (faceUVs[i][3][0], faceUVs[i][3][1])
        
        meshData.update()
        
        
        for polygon in meshData.polygons:
            polygon.use_smooth = True
        
        name = "tree"
        if name in bpy.data.objects:
            bpy.data.objects[name].data = meshData
            treeObject = bpy.data.objects[name]
            treeObject.select_set(True)
            #self.report({'INFO'}, "Found object 'tree'!")
        else:
            treeObject = bpy.data.objects.new("tree", meshData)
            bpy.context.collection.objects.link(treeObject)
            treeObject.select_set(True)
            #self.report({'INFO'}, "Created new object!")
        
        bpy.context.view_layer.objects.active = treeObject
        
        bpy.ops.object.shade_auto_smooth(angle=0.01)
        
        mesh = treeObject.data
        
        if "tValGlobal" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="tValGlobal", domain='POINT', data_type='FLOAT')

        if "tValBranch" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="tValBranch", domain='POINT', data_type='FLOAT')
        
        if "ringAngle" not in mesh.attributes:
            bpy.ops.geometry.attribute_add(name="ringAngle", domain='POINT', data_type='FLOAT')
        
        tValGlobalAttribute = mesh.attributes["tValGlobal"]
        tValBranchAttribute = mesh.attributes["tValBranch"]
        ringAngleAttribute = mesh.attributes["ringAngle"]
        
        for i, vertex in enumerate(mesh.vertices):
            tValGlobalAttribute.data[i].value = vertexTvalGlobal[i]
            tValBranchAttribute.data[i].value = vertexTvalBranch[i]
            ringAngleAttribute.data[i].value = ringAngle[i] / (2.0 * math.pi)
        
        treeObject.data.materials.clear()
        treeObject.data.materials.append(barkMaterial)
            */
        }

        static UnityEngine.Vector3 norm(UnityEngine.Vector3 v)
        {
            if (v ==  new UnityEngine.Vector3(0f, 0f, 0f))
            {
                return v;
            }
            else
            {
                return v / v.magnitude;
            }
        }

        static float length(UnityEngine.Vector3 v)
        {
            return v.magnitude;
        }

        static UnityEngine.Vector3 sampleSplineC(UnityEngine.Vector3 controlPt0, UnityEngine.Vector3 controlPt1, UnityEngine.Vector3 controlPt2, UnityEngine.Vector3 controlPt3, float t)
        {
            return MathF.Pow(1.0f - t, 3.0f) * controlPt0 + 3.0f * MathF.Pow(1.0f - t, 2.0f) * t * controlPt1 + 3.0f * (1.0f- t) * t * t * controlPt2 + t * t * t * controlPt3;
        }

        static UnityEngine.Vector3 sampleSplineTangentC(UnityEngine.Vector3 controlPt0, UnityEngine.Vector3 controlPt1, UnityEngine.Vector3 controlPt2, UnityEngine.Vector3 controlPt3, float t)
        {
            return norm(-3.0f * MathF.Pow(1.0f - t, 2.0f) * controlPt0 + 3.0f * (3.0f * t * t - 4.0f * t + 1.0f) * controlPt1 + 3.0f * (-3.0f * t * t + 2.0f * t) * controlPt2 + 3.0f * t * t * controlPt3);
        }

        static UnityEngine.Vector3 lerp(UnityEngine.Vector3 a, UnityEngine.Vector3 b, float t)
        {
            return a + t * (b - a);
        }

        static float lerp(float a, float b, float t)
        {
            return a + t * (b - a);
        }


        void OnDrawGizmos()
        {
            if (nodes != null)
            {
                //foreach (node n in nodes)
                //{
                //    Gizmos.color = Color.red;
                //    Gizmos.DrawSphere(n.point, 0.2f);
                //}
                foreach (segment s in segments)
                {
                    Gizmos.color = UnityEngine.Color.red;
                    Gizmos.DrawSphere(s.start, 0.2f);
                    Gizmos.DrawSphere(s.end, 0.1f);
                }

                foreach (UnityEngine.Vector3 v in vertices)
                {
                    Gizmos.color = UnityEngine.Color.blue;
                    Gizmos.DrawSphere(v, 0.05f);
                }
            }
        }

    }



}