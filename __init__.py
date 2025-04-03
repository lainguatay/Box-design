bl_info = {
    "name": "Box Design Tool",
    "author": "Lại Ngứa Tay",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI",
    "description": "Bevel Object",
    "category": "Add Mesh",
}

import bpy
from . import scale_to_volume, solidify_modifier, settings

def register():
    scale_to_volume.register()
    solidify_modifier.register()
    settings.register()

def unregister():
    scale_to_volume.unregister()
    solidify_modifier.unregister()
    settings.unregister()

if __name__ == "__main__":
    register()

