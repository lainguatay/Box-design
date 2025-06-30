import bpy

class THToolsPanel(bpy.types.Panel):
    bl_label = "TH TOOLS"
    bl_idname = "PT_THToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Công cụ vẽ thông hơi")

def register():
    bpy.utils.register_class(THToolsPanel)

def unregister():
    bpy.utils.unregister_class(THToolsPanel)
