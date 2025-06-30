import bpy
from bpy.props import FloatProperty, BoolProperty

import bpy

def update_capsule_from_area(self, context):
    try:
        bpy.ops.object.create_capsule_from_area()
    except:
        pass


class SharedCapsuleSettings(bpy.types.PropertyGroup):
    height: FloatProperty(
        name="Khoảng cách tâm",
        default=30,
        min=1,
        description="Height of the central rectangle of capsule",
        update=update_capsule_from_area
    )
    horizontal: BoolProperty(
        name="Nằm ngang",
        default=False,
        description="Tạo viên nang nằm ngang (xoay theo trục X)",
        update=update_capsule_from_area
    )

def register():
    bpy.utils.register_class(SharedCapsuleSettings)
    bpy.types.Scene.shared_capsule_settings = bpy.props.PointerProperty(type=SharedCapsuleSettings)

def unregister():
    del bpy.types.Scene.shared_capsule_settings
    bpy.utils.unregister_class(SharedCapsuleSettings)
