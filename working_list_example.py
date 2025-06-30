bl_info = {
    "name": "Addon Test2",
    "author": "Jens",
    "version": (0, 1),
    "blender": (4, 3, 1),
    "location": "View3d > Tool",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy

class IntProp(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name="intValue", default=0)
    
class FloatProp(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="floatValue", default=0.0)
    
class MyItem(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty(name="value")

class OT_AddItem(bpy.types.Operator):
    bl_idname = "scene.add_mylist_item"
    bl_label = "Add Item"
    def execute(self, context):
        item = context.scene.myList.add()
        floatItem = context.scene.syncList.add()
        item.value = 42  # Or any value you want
        floatItem.value = 0.5
        return {'FINISHED'}

class OT_RemoveItem(bpy.types.Operator):
    bl_idname = "scene.remove_mylist_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        mylist = context.scene.myList
        if len(mylist) > self.index:
            mylist.remove(self.index)
        floatList = context.scene.syncList
        if (len(floatList) > self.index):
            floatList.remove(self.index)
        return {'FINISHED'}

class UL_MyList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text="Item label")
        row = layout.row()
        layout.prop(item, "value", text=f"Item {index}")
        
class UL_SyncList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text="sync Item")
        row = layout.row()
        layout.prop(item, "value", text=f"item {index}")
        


class PT_MyPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "testPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("UL_MyList", "", scene, "myList", scene, "myList_index")

        row = layout.row(align=True)
        row.operator("scene.add_mylist_item", text="Add")
        row.operator("scene.remove_mylist_item", text="Remove").index = scene.myList_index

class PT_syncPanel(bpy.types.Panel):
    bl_label = "Sync Panel"
    bl_idname = "syncPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list("UL_SyncList", "", scene, "syncList", scene, "syncList_index")

class PT_dynamicPanel(bpy.types.Panel):
    bl_label = "Dynamic Panel"
    bl_idname = "dynamicPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'treeGen'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        items = scene.myList
        #n = scene.my_n
        n = len(items)
        
        syncItems = scene.syncList
        
        #layout.prop(scene, "my_n") # "Number of Panels"
        
        #layout.operator("scene.add_mylist_item", text="add List item")
        
        for i in range(n):
            if i < len(items):
                box = layout.box()
                box.label(text=f"Panel {i + 1}")
                #row = box.row()
                #row = layout.prop(items[i], "value1", text="Value 1")
                #layout.prop(context.scene, "value1")
                box.prop(items[i], "value", text="Value")
                box.prop(syncItems[i], "value", text="scnyValue")
            else:
                layout.label(text=f"Index {i} out of range")
    
#class listItemPanel(bpy.types.Panel):
#    bl_label = "List Item Panel"
#    bl_idname = "ListItemPanel"
#    bl_space_type = 'VIEW_3d'
#    bl_region_type = 'UI'
#    bl_category = 'treeGen'
#    
#    def draw(self, context):
#        for item in bpy.types.Scene.myList:
#            row = layout.row()
#            layout.prop(context.scene, item)

def register():
    bpy.utils.register_class(MyItem)
    bpy.utils.register_class(IntProp)
    bpy.utils.register_class(FloatProp)
    bpy.utils.register_class(OT_AddItem)
    bpy.utils.register_class(OT_RemoveItem)
    bpy.utils.register_class(UL_MyList)
    bpy.utils.register_class(UL_SyncList)
    bpy.utils.register_class(PT_MyPanel)
    bpy.utils.register_class(PT_syncPanel)
    bpy.utils.register_class(PT_dynamicPanel)
    bpy.types.Scene.my_n = bpy.props.IntProperty(name="Number of Panels", default=1, min=0)
    bpy.types.Scene.myList = bpy.props.CollectionProperty(type=IntProp)
    bpy.types.Scene.myList_index = bpy.props.IntProperty(default=0)
    bpy.types.Scene.syncList = bpy.props.CollectionProperty(type=FloatProp)
    bpy.types.Scene.syncList_index = bpy.props.IntProperty(default=0)
    

def unregister():
    bpy.utils.unregister_clas(MyItem)
    bpy.utils.unregister_class(PT_MyPanel)
    bpy.utils.unregister_class(PT_syncPanel)
    bpy.utils.unregister_class(UL_MyList)
    bpy.utils.unregister_class(UL_SyncList)
    bpy.utils.unregister_class(OT_RemoveItem)
    bpy.utils.unregister_class(OT_AddItem)
    bpy.utils.unregister_class(IntProp)
    bpy.utils.unregister_class(FloatProp)
    bpy.utils.unregister_class(PT_dynamicPanel)
    del bpy.types.Scene.my_n
    del bpy.types.Scene.myList
    del bpy.types.Scene.myList_index
    del bpy.types.Scene.syncList
    del bpy.types.Scene.syncList_index

if __name__ == "__main__":
    register()