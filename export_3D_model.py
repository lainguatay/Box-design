import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty
)
from bpy.types import Operator, Panel, PropertyGroup

# Dữ liệu cấu hình export
class ExportSettings(PropertyGroup):
    export_path: StringProperty(
        name="Export Path",
        subtype="DIR_PATH",
        default="//"
    )
    export_format: EnumProperty(
        name="Format",
        items=[
            ("STL", "STL", ""),
            ("PLY", "PLY", ""),
            ("OBJ", "OBJ", ""),
        ],
        default="STL"
    )
    use_ascii_format: BoolProperty(name="ASCII Format", default=False)
    use_uv: BoolProperty(name="Export UV", default=True)
    use_normals: BoolProperty(name="Export Normals", default=True)
    use_colors: BoolProperty(name="Export Colors", default=False)
    use_copy_textures: BoolProperty(name="Copy Textures", default=False)
    use_scene_scale: BoolProperty(name="Use Scene Scale", default=False)

# Giao diện trên Sidebar
class VIEW3D_PT_export_panel(Panel):
    bl_label = "Export 3D Model"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Box Design"
    bl_parent_id = "PT_ExportPanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.print_3d

        layout.prop(props, "export_path")
        layout.prop(props, "export_format")
#       layout.prop(props, "use_ascii_format")

        if props.export_format != "STL":
            layout.prop(props, "use_uv")
            layout.prop(props, "use_normals")
            layout.prop(props, "use_colors")

        if props.export_format == "OBJ":
            layout.prop(props, "use_copy_textures")

 #      layout.prop(props, "use_scene_scale")
        layout.operator("export_scene.print3d_export", text="Export")


# Đăng ký
classes = (
    ExportSettings,
    VIEW3D_PT_export_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.print_3d = bpy.props.PointerProperty(type=ExportSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.print_3d


if __name__ == "__main__":
    register()
