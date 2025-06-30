import bpy

class ExportPanel(bpy.types.Panel):
    bl_label = "EXPORT"
    bl_idname = "PT_ExportPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Công cụ xuất file")

def register():
    bpy.utils.register_class(ExportPanel)

def unregister():
    bpy.utils.unregister_class(ExportPanel)
