import bpy
import sys
import os
import importlib


# for testing...
#addon_dir = "/home/j/Downloads/treeGen_v5"

# for creating addon...
addon_dir = os.path.dirname(os.path.realpath(__file__))




# Dynamically add current folder to sys.path
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

if 'my_property' in sys.modules:  # For reliable reload during development
    del sys.modules['my_property']
    
import my_property


importlib.reload(my_property)

# Import property class from another file
from my_property import MyProperties



# Create a Blender PropertyGroup using the imported class value
class MinimalProps(bpy.types.PropertyGroup):
    my_int: bpy.props.IntProperty(
        name="My Int",
        default=MyProperties().default_value
    )

class MinimalPanel(bpy.types.Panel):
    bl_label = "Minimal Panel"
    bl_idname = "PT_MinimalPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Minimal'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.minimal_props, "my_int")
        layout.operator("object.my_operator", text="my Operator")
        
class MinimalOperator(bpy.types.Operator):
    bl_idname = "object.my_operator"
    bl_label = "My Operator"
    
    def execute(self, context):
        self.report({'INFO'}, "setting value in imported class to 4: ")
        MyProperties().default_value = 4
        self.report({'INFO'}, f"imported from MyProperties(): MyProperties().default_value: {MyProperties().default_value}")
        # only updated after reopening .blend file
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MinimalProps)
    bpy.types.Scene.minimal_props = bpy.props.PointerProperty(type=MinimalProps)
    bpy.utils.register_class(MinimalPanel)
    
    bpy.utils.register_class(MinimalOperator)

def unregister():
    bpy.utils.unregister_class(MinimalPanel)
    del bpy.types.Scene.minimal_props
    bpy.utils.unregister_class(MinimalProps)
    
    bpy.utils.unregister_class(MinimalOperator)

if __name__ == "__main__":
    register()