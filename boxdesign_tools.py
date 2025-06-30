import bpy

class BoxToolsPanel(bpy.types.Panel):
    bl_label = "BOX TOOLS"
    bl_idname = "PT_BoxToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Công cụ vẽ box")

def register():
    bpy.utils.register_class(BoxToolsPanel)

def unregister():
    bpy.utils.unregister_class(BoxToolsPanel)
