import bpy

class import_class():
    def __init__(self):
        self.x = 2
        print("in import_class: __init__(): self.x = 2")
        
    def register():
        print("in import_class: register()")
    
    def unregister():
        print("in import_class: unregister()")
        
# register and unregister in every class!


def register():
    print("register minimal_import_class")
    import_class.register()
    
def unregister():
    import_class.unregister()
    print("unregister minimal_import_class")
        
