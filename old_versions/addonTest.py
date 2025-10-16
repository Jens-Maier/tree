bl_info = {
    "name" : "Addon Test",
    "author" : "Jens", 
    "version" : (0,1),
    "blender" : (4,3,1),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Add Mesh",
}

import bpy
import math
import mathutils

#class MyProperties(bpy.types.PropertyGroup):
#    myFloat: bpy.props.FloatProperty(
#        name = "My Float",
#        description = "This is my float property",
#        default = 0.0,
#        min = 0.0, 
#        max = 20.0
#    )

class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "PT_TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text = "Tree Generator", icon = 'COLORSET_12_VEC')
        row = layout.row()
        row.operator("mesh.primitive_cube_add")
        row = layout.row()
        row.operator("transform.resize")
        row = layout.row()
        row.prop(obj, "scale")
        row = layout.row()
        
        row.prop(obj, "name")
        
#        layout.prop(context.scene, "myFloat")
        
       
class PanelA(bpy.types.Panel):
    bl_label = "Panel A"
    bl_idname = "PT_PanelA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text = "Panel A")
        
        
class PanelB(bpy.types.Panel):
    bl_label = "Panel B"
    bl_idname = "PT_PanelB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    bl_parent_id = 'PT_TestPanel'
    bl_optione = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text = "Panel B")
        bl_optione = {'DEFAULT_CLOSED'}
        row = layout.row()
        layout.prop(context.scene, "myFloat")
        row = layout.row()
        layout.prop(context.scene, "myInt")
        row = layout.row()
        layout.operator("object.operatorid", text = "MyCircleOperator")


class myOperator(bpy.types.Operator):
    bl_label = "operatorLabel"
    bl_idname = "object.operatorid"
    
    def execute (self, context):
        n = context.scene.myInt
        vertices = []
        vertices.append(bpy.context.scene.cursor.location)
        for i in range(n):
            angle = (2 * math.pi * i) / n
            x = math.cos(angle)
            y = math.sin(angle)
            v =  mathutils.Vector((x, y, 0.0))
            v = v + bpy.context.scene.cursor.location
            vertices.append(v)
            
        faces = []
        for i in range(1, n + 1):
            j = i + 1 if i < n else 1
            faces.append((0, i, j))
            
        meshData = bpy.data.meshes.new("myCircleMesh")
        meshData.from_pydata(vertices, [], faces)
        meshData.update()
        
        circleObj = bpy.data.objects.new("myCricleObject", meshData)
        bpy.context.collection.objects.link(circleObj)
        circleObj.select_set(True)
        
        return {'FINISHED'}
    
     #   Python: RuntimeError: class OBJECT_OT_operatorid, function execute: incompatible return value , , Function.result expected a set, not a NoneType

        
        
def register():
    bpy.utils.register_class(TestPanel)
    bpy.utils.register_class(PanelA)
    bpy.utils.register_class(PanelB)
    
    bpy.types.Scene.myFloat = bpy.props.FloatProperty(
        name = "myFloat", 
        description = "this is my float property", 
        default = 1.0, 
        min = 0.0, 
        soft_max = 10.0
    )
    
    bpy.types.Scene.myInt = bpy.props.IntProperty(
        name = "myInt",
        description = "resolution",
        default = 6,
        min = 3,
        soft_max = 10
    )
    bpy.utils.register_class(myOperator)
    
def unregister():
    bpy.utils.unregister_class(TestPanel)
    bpy.utils.unregister_class(PanelA)
    bpy.utils.unregister_class(PanelB)
    bpy.utils.unregister_class(myOperator)
    
    del bpy.types.Scene.myFlaot
    del bpy.types.Scene.myInt
    
if __name__ == "__main__":
    register()
    
