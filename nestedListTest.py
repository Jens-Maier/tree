bl_info = {
    "name" : "nestedListTest",
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
    value: bpy.props.IntProperty(name = "intValue", default=0, min=0, soft_max=10)
    
class listProp(bpy.types.PropertyGroup):
    value: bpy.props.CollectionProperty(name = "listProperty", type=intProp)
    
    
class treeGenPanel(bpy.types.Panel):
    bl_label = "Tree Generator"
    bl_idname = "PT_TreeGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row(align = True)
        row.operator("scene.add_list_item", text="Add list")
        row = layout.row(align = True)
        row.operator("scene.remove_list_item", text="Remove list")
        
        
        #for i in range(len(context.scene.testList)):
        #    box = layout.box()
        #    split = box.split(factor=0.6)
        #    split.label(text=f"cluster {i}")
        #    split.prop(context.scene.testList[i], "value", text="")
            
        for i in range(len(context.scene.testListList)):
            layout.label(text=f"cluster {i}")
            row = layout.row(align = True)
            row.operator("scene.add_item", text="Add").index = i
            row = layout.row(align = True)
            row.operator("scene.remove_item", text="Remove").index = i
            
        
        
        
class addItem(bpy.types.Operator):
    bl_idname = "scene.add_item"
    bl_label = "Add item"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        testListItem = context.scene.testList[index]
        testListItem.add(2)
        return {'FINISHED'}
    
class removeItem(bpy.types.Operator):
    bl_idname = "scene.remove_item"
    bl_label = "Remove item"
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        if (len(context.scene.testList) > 0):
            context.scene.testList.remove(len(context.scene.testList) - 1)
        return {'FINISHED'}
    
class addListItem(bpy.types.Operator):
    bl_idname = "scene.add_list_item"
    bl_label = "Add list"
    
    def execute(self, context):
        listListItem = context.scene.testListList.add()
        return {'FINISHED'}
        
class removeListItem(bpy.types.Operator):
    bl_idname = "scene.remove_list_item"
    bl_label = "Remove list"
    
    def execute(self, context):
        if (len(context.scene.testListList) > 0):
            context.scene.testListList.remove(len(context.scene.testListList) - 1)
        return {'FINISHED'}

        
def register():
    #properties
    bpy.utils.register_class(intProp)
    bpy.utils.register_class(listProp)
    
    #panels
    bpy.utils.register_class(treeGenPanel)
    
    #operators
    bpy.utils.register_class(addItem)
    bpy.utils.register_class(removeItem)
    bpy.utils.register_class(addListItem)
    bpy.utils.register_class(removeListItem)
    
    
    #collections
    bpy.types.Scene.testList = bpy.props.CollectionProperty(type=intProp)
    bpy.types.Scene.itemIndex = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.testListList = bpy.props.CollectionProperty(type=listProp)
    
def unregister():
    #properties
    bpy.utils.unregister_class(intProp)
    bpy.utils.unregister_class(listProp)
    
    #operators
    bpy.utils.unregister_class(addItem)
    
    #panels
    bpy.utils.unregister_class(treeGenPanel)
    
    del bpy.types.Scene.testList
    del bpy.types.Scene.itemIndex
    
if __name__ == "__main__":
    register();