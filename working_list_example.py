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

class OT_AddItem(bpy.types.Operator):
    bl_idname = "scene.add_mylist_item"
    bl_label = "Add Item"
    def execute(self, context):
        item = context.scene.myList.add()
        item.value = 42  # Or any value you want
        return {'FINISHED'}

class OT_RemoveItem(bpy.types.Operator):
    bl_idname = "scene.remove_mylist_item"
    bl_label = "Remove Item"
    index: bpy.props.IntProperty()
    def execute(self, context):
        mylist = context.scene.myList
        if len(mylist) > self.index:
            mylist.remove(self.index)
        return {'FINISHED'}

class UL_MyList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "value", text=f"Item {index}")

class PT_MyPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "PT_TestPanel"
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

def register():
    bpy.utils.register_class(IntProp)
    bpy.utils.register_class(OT_AddItem)
    bpy.utils.register_class(OT_RemoveItem)
    bpy.utils.register_class(UL_MyList)
    bpy.utils.register_class(PT_MyPanel)
    bpy.types.Scene.myList = bpy.props.CollectionProperty(type=IntProp)
    bpy.types.Scene.myList_index = bpy.props.IntProperty(default=0)

def unregister():
    bpy.utils.unregister_class(PT_MyPanel)
    bpy.utils.unregister_class(UL_MyList)
    bpy.utils.unregister_class(OT_RemoveItem)
    bpy.utils.unregister_class(OT_AddItem)
    bpy.utils.unregister_class(IntProp)
    del bpy.types.Scene.myList
    del bpy.types.Scene.myList_index

if __name__ == "__main__":
    register()