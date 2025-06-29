bl_info = {
    "name" : "Addon Test2",
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


class intProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name = "intValue", default = 0)
    
class addmylistoperator(bpy.types.Operator):
    bl_label = "list test"
    bl_idname = "object.listoperatortest" # only lower case letters allowed!
    # operator bl_idname has to start with object.
    
    def execute (self, context):
         # TEST: adding items
        print("TEST: adding value")
        lst = bpy.context.scene.myList
        print(lst)
        item = bpy.context.scene.myList.add()
        item.value = 42
    
        print("added value: ")
        print(bpy.context.scene.myList[0].value)
    
        print("test")
        testItem1 = bpy.context.scene.myList.add()
        testItem1.value = 42
        print(bpy.context.scene.myList[0]) #bpy.context.scene.myList
        return {'FINISHED'}

class myPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "PT_TestPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        row = self.layout.row()
        #for item in bpy.types.Scene.myList:
        #    item = bpy.props.IntProperty(
        #        name = "item", 
        #        default = 0
        #    )
            
        self.layout.prop(context.scene, "listProperty.intList")
        row = self.layout.row()
        self.layout.operator("object.listoperatortest", text="add Item to list")
    
    
def register():
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(addmylistoperator)
    bpy.utils.register_class(myPanel)
    
    bpy.types.Scene.myList = bpy.props.CollectionProperty(type=intProp)
    
    print("Adding value")
    
    item = bpy.context.scene.myList.add()
    item.value = 42
    
    print(item.value) 
    
    
def unregister():
    bpy.utils.unregister_class(myPanel)
    
if __name__ == "__main__":
    register()
    