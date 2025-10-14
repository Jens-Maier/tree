import bpy

from . import minimal_import_class

def register():
    print("register __init__")
    minimal_import_class.register()
    
def unregister():
    minimal_import_class.unregister()
    print("unregister __init__")
    